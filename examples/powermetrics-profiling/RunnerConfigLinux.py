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
    name:                       str             = "new_runner_experiment_linux"
    results_output_path:        Path             = ROOT_DIR / 'experiments'
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
        
        ## MOD: Added process holders for all measurement tools
        self.workload_process = None
        self.cpu_process = None
        self.gpu_process = None
        
        output.console_log("Custom config for Linux (using perf, mpstat, nvidia-smi) loaded")

    def create_run_table_model(self) -> RunTableModel:
        factor1 = FactorModel("test_factor", [1, 2])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            data_columns=["joules", "avg_cpu", "avg_gpu"]
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        pass

    def before_run(self) -> None:
        pass

    def start_run(self, context: RunnerContext) -> None:
        pass

    def start_measurement(self, context: RunnerContext) -> None:
        ## MOD: This function is now responsible for starting all monitoring tools
        output.console_log("Starting measurements...")

        # Define paths for all log files
        perf_log_path = context.run_dir / "perf_output.txt"
        cpu_log_path = context.run_dir / "cpu_usage.txt"
        gpu_log_path = context.run_dir / "gpu_usage.txt"

        # 1. Start CPU monitoring (mpstat) in the background
        # Polls every 1 second (-P ALL for all cores)
        cpu_command = ['mpstat', '-P', 'ALL', '1']
        self.cpu_process = subprocess.Popen(
            cpu_command,
            stdout=open(cpu_log_path, 'w'),
            stderr=subprocess.STDOUT
        )

        # 2. Start GPU monitoring (nvidia-smi) in the background
        # Polls GPU utilization every 1 second
        gpu_command = [
            'rocm-smi',
            '--showuse', '--csv' 
        ]
        self.gpu_process = subprocess.Popen(
            gpu_command,
            stdout=open(gpu_log_path, 'w'),
            stderr=subprocess.STDOUT
        )

        # 3. Start the main workload wrapped with perf
        workload_command = [
            'perf', 'stat', '-a', '-e', 'power/energy-pkg/',
            'python', 'heavy_work.py'
        ]
        self.workload_process = subprocess.Popen(
            workload_command,
            stdout=open(perf_log_path, 'w'),
            stderr=subprocess.STDOUT
        )

    def interact(self, context: RunnerContext) -> None:
        ## MOD: We only wait for the main workload to finish.
        output.console_log("Waiting for workload (heavy_work.py) to complete...")
        if self.workload_process:
            self.workload_process.wait()
        output.console_log("Workload finished.")

    def stop_measurement(self, context: RunnerContext) -> None:
        ## MOD: We must now explicitly stop the background monitoring tools.
        output.console_log("Stopping measurement processes...")
        if self.cpu_process:
            self.cpu_process.terminate()
            self.cpu_process.wait() # Wait to avoid zombie processes
        if self.gpu_process:
            self.gpu_process.terminate()
            self.gpu_process.wait()

    def stop_run(self, context: RunnerContext) -> None:
        pass

    ## MOD: Helper function to parse mpstat output
    def _parse_cpu_usage(self, file_path: Path) -> float:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            idle_percentages = []
            for line in lines:
                # Look for the 'all' CPU summary line, which contains averages
                if 'all' in line:
                    try:
                        # The last column in mpstat output is %idle
                        idle_val = float(line.split()[-1])
                        idle_percentages.append(idle_val)
                    except (ValueError, IndexError):
                        continue
            
            if not idle_percentages:
                return -1.0
            
            # Average CPU usage is 100 - average idle percentage
            avg_idle = np.mean(idle_percentages)
            return 100.0 - avg_idle
        except (FileNotFoundError, Exception) as e:
            output.console_log(f"ERROR: Could not parse CPU usage: {e}")
            return -1.0

    ## MOD: Helper function to parse rocm-smi's CSV output
    def _parse_gpu_usage(self, file_path: Path) -> float:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            utilizations = []
            # Start loop from the second line to skip the header
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue # Skip empty lines

                try:
                    # Split the CSV line, e.g., "0,15" -> ["0", "15"]
                    parts = line.split(',')
                    # The usage percentage is the second column
                    gpu_use_percent = float(parts[1])
                    utilizations.append(gpu_use_percent)
                except (ValueError, IndexError):
                    # This will skip any malformed lines in the output
                    output.console_log(f"WARNING: Could not parse GPU usage from line: '{line}'")
                    continue

            if not utilizations:
                return -1.0

            return np.mean(utilizations)
        except (FileNotFoundError, Exception) as e:
            output.console_log(f"ERROR: Could not parse GPU usage: {e}")
            return -1.0

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, Any]]:
        ## MOD: Updated to parse all three log files
        perf_log_path = context.run_dir / "perf_output.txt"
        cpu_log_path = context.run_dir / "cpu_usage.txt"
        gpu_log_path = context.run_dir / "gpu_usage.txt"
        
        # 1. Parse energy from perf output
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

        # 2. Parse CPU and GPU usage using helper functions
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