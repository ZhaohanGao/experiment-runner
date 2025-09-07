from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
import time
import numpy as np
import subprocess # Added for running external commands
import re         # Added for parsing text output

class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    name:                       str             = "process_specific_experiment"
    results_output_path:        Path            = ROOT_DIR / 'experiments'
    operation_type:             OperationType   = OperationType.AUTO
    time_between_runs_in_ms:    int             = 1000

    def __init__(self):
        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN       , self.before_run       ),
            (RunnerEvents.START_RUN        , self.start_run        ),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT         , self.interact         ),
            (RunnerEvents.STOP_MEASUREMENT , self.stop_measurement ),
            (RunnerEvents.STOP_RUN         , self.stop_run         ),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT , self.after_experiment )
        ])
        self.run_table_model = None
        
        self.workload_process = None
        self.cpu_process = None
        self.gpu_process = None
        
        ## MOD: Updated log message for new tools
        output.console_log("Custom config for Linux (using perf, pidstat, nvtop) loaded")

    def create_run_table_model(self) -> RunTableModel:
        factor1 = FactorModel("test_factor", [1, 2, 3, 4, 5])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            data_columns=["joules", "avg_cpu", "avg_gpu", "cpu_seconds"]
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        pass

    def before_run(self) -> None:
        pass

    def start_run(self, context: RunnerContext) -> None:
        pass

    def start_measurement(self, context: RunnerContext) -> None:
        ## MOD: Added 'taskset' to pin the workload to a specific CPU core (e.g., core 7).
        output.console_log("Starting workload (heavy_work.py) wrapped in perf and pinned to a CPU core...")
        
        perf_log_path = context.run_dir / "perf_output.txt"
        
        # We will pin the command to CPU core 7
        cpu_to_use = '7'
        
        # taskset -c <core> your_command...
        workload_command = [
            'taskset', '-c', cpu_to_use,
            'perf', 'stat', '-e', 'power/energy-pkg/',
            'python', 'heavy_work.py'
        ]
        self.workload_process = subprocess.Popen(
            workload_command,
            stdout=open(perf_log_path, 'w'),
            stderr=subprocess.STDOUT
        )

    def interact(self, context: RunnerContext) -> None:
        ## MOD: This function now finds the child process PID to monitor.
        if not self.workload_process:
            output.console_log("ERROR: Workload process not started.")
            return

        parent_pid = self.workload_process.pid
        child_pid = None

        # Give the child process a moment to spawn
        time.sleep(0.2)

        try:
            # Use pgrep to find the child PID of the 'perf' process
            pgrep_cmd = ['pgrep', '-P', str(parent_pid)]
            result = subprocess.run(pgrep_cmd, capture_output=True, text=True, check=True)
            child_pid_str = result.stdout.strip()
            if not child_pid_str:
                raise ValueError("pgrep did not find a child process.")
            child_pid = int(child_pid_str)
            output.console_log(f"Found perf parent PID: {parent_pid}, monitoring python child PID: {child_pid}...")
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
            output.console_log(f"ERROR: Could not find child process for PID {parent_pid}. Error: {e}")
            output.console_log("Workload may have finished too quickly or failed to start.")
            self.workload_process.wait() # Still wait for the main process to clean up
            return

        # --- Start monitoring using the child_pid ---
        cpu_log_path = context.run_dir / "cpu_usage.txt"
        gpu_log_path = context.run_dir / "gpu_usage.txt"

        cpu_command = ['pidstat', '-p', str(child_pid), '1']
        self.cpu_process = subprocess.Popen(
            cpu_command, stdout=open(cpu_log_path, 'w'), stderr=subprocess.STDOUT
        )

        gpu_command = ['nvtop', '-b', '-p', str(child_pid), '-d', '1']
        self.gpu_process = subprocess.Popen(
            gpu_command, stdout=open(gpu_log_path, 'w'), stderr=subprocess.STDOUT
        )

        output.console_log("Waiting for workload to complete...")
        self.workload_process.wait()
        output.console_log("Workload finished.")

    def stop_measurement(self, context: RunnerContext) -> None:
        ## This function remains the same, it correctly terminates the new processes.
        output.console_log("Stopping measurement processes...")
        if self.cpu_process:
            self.cpu_process.terminate()
            self.cpu_process.wait()
        if self.gpu_process:
            self.gpu_process.terminate()
            self.gpu_process.wait()

    def stop_run(self, context: RunnerContext) -> None:
        pass

    ## MOD: Rewritten to parse pidstat output
    def _parse_cpu_usage(self, file_path: Path) -> float:
        try:
            with open(file_path, 'r') as f:
                lines = [line for line in f if line.strip()] # Read non-empty lines

            if not lines:
                return 0.0

            # Find the header row and the index of the '%CPU' column
            header_line = ""
            for line in lines:
                if "PID" in line and "%CPU" in line:
                    header_line = line
                    break
            
            if not header_line:
                output.console_log(f"ERROR: Could not find header row in {file_path}")
                return -1.0
            
            headers = header_line.split()
            try:
                cpu_column_index = headers.index("%CPU")
            except ValueError:
                output.console_log(f"ERROR: Could not find '%CPU' column in {file_path}")
                return -1.0

            # Parse the data lines using the found index
            cpu_percentages = []
            for line in lines:
                if "PID" in line or "Average" in line:
                    continue # Skip header/footer lines
                
                try:
                    parts = line.split()
                    cpu_val_str = parts[cpu_column_index].replace(',', '.')
                    cpu_percentages.append(float(cpu_val_str))
                except (ValueError, IndexError):
                    # This will skip any malformed lines
                    continue
            
            if not cpu_percentages:
                return 0.0
            
            return np.mean(cpu_percentages)
        except (FileNotFoundError, Exception) as e:
            output.console_log(f"ERROR: Could not parse CPU usage with pidstat: {e}")
            return -1.0

    ## MOD: Rewritten to parse nvtop output
    def _parse_gpu_usage(self, file_path: Path) -> float:
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            utilizations = []
            # Regex to find lines with a PID and extract the GPU utilization percentage
            pattern = re.compile(r'PID\s+\d+\s+\(.*\)\s+on\s+GPU\s+\d+:\s+(\d+)\s+%\s+GPU-Util')
            
            matches = pattern.findall(content)
            if not matches:
                output.console_log(f"WARNING: No GPU usage found for process in {file_path}. The process might not have used the GPU.")
                return 0.0

            for val in matches:
                utilizations.append(float(val))

            return np.mean(utilizations)
        except (FileNotFoundError, Exception) as e:
            output.console_log(f"ERROR: Could not parse GPU usage with nvtop: {e}")
            return -1.0

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, Any]]:
        perf_log_path = context.run_dir / "perf_output.txt"
        cpu_log_path = context.run_dir / "cpu_usage.txt"
        gpu_log_path = context.run_dir / "gpu_usage.txt"
        
        # 1. Parse energy from perf output (remains the same)
        joules = 0.0
        try:
            with open(perf_log_path, 'r') as f:
                perf_output = f.read()
            
            match = re.search(r'(\d+\.\d+)\s+Joules\s+power/energy-pkg/', perf_output)
            if match:
                joules = float(match.group(1))
            else:
                output.console_log(f"WARNING: Could not parse Joules from {perf_log_path}.")
        except FileNotFoundError:
            output.console_log(f"ERROR: Perf output file not found at {perf_log_path}")

        # 2. Parse CPU and GPU usage using the updated helper functions
        avg_cpu = self._parse_cpu_usage(cpu_log_path)
        avg_gpu = self._parse_gpu_usage(gpu_log_path)

        return {
            "joules": joules,
            "avg_cpu": avg_cpu,
            "avg_gpu": avg_gpu,
        }

    def after_experiment(self) -> None:
        pass

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None