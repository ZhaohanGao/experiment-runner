from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ProgressManager.Output.OutputProcedure import OutputProcedure as output
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
import re
import os
import signal
import pandas as pd
import time
import subprocess
import shlex


class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    
    # MODIFICATION 1: Define ONLY ONE script to run for this experiment.
    # To run a different script, change this line and run the experiment again.
    SCRIPT_TO_RUN: str = os.getenv('SCRIPT_TO_RUN', 'bubble_sort.py')
    # SCRIPT_TO_RUN: str = "quick_sort.py" # <-- Example for the next run

    # Define how many times to repeat the experiment for the script above.
    REPETITIONS: int = 2

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name: str = "" # This will be set dynamically below
    results_output_path:        Path             = ROOT_DIR / 'experiments'
    operation_type:             OperationType   = OperationType.AUTO
    time_between_runs_in_ms:    int             = 1000

    def __init__(self):
        """Executes immediately after program start, on config load"""

        # MODIFICATION 2: Generate a unique folder name for the single script being tested.
        script_stem = Path(self.SCRIPT_TO_RUN).stem
        self.name = f"{script_stem}_experiment_{self.timestamp}"

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
        self.all_run_data = []
        output.console_log("Custom config loaded")
        output.console_log(f"Experiment name set to: {self.name}")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here."""
        # MODIFICATION 3: Factors are now simpler as we are only running one script.
        repetition_factor = FactorModel("repetition", list(range(1, self.REPETITIONS + 1)))
        sampling_factor = FactorModel("sampling", [1000])

        self.run_table_model = RunTableModel(
            factors=[repetition_factor, sampling_factor],
            data_columns=['execution_time_s', 'cpu_usage_percent', 'memory_usage_mb', 'cpu_energy_j']
        )
        return self.run_table_model

    def start_measurement(self, context: RunnerContext) -> None:
            # MODIFICATION 4: The script path is now taken directly from the class variable.
            script_to_run_path = self.ROOT_DIR / self.SCRIPT_TO_RUN
            repetition_num = context.execute_run['repetition']
            
            output.console_log(f"Starting measurement for '{self.SCRIPT_TO_RUN}' (Repetition #{repetition_num})")

            script_output_path = context.run_dir / "execution_time.txt"
            sampling_interval = context.execute_run['sampling']

            profiler_cmd = f'sudo energibridge \
                            --interval {sampling_interval} \
                            --output {context.run_dir / "energibridge.csv"} \
                            --summary \
                            /home/pluxbox/Desktop/experiment-runner/venv/bin/python {script_to_run_path} {script_output_path}'

            energibridge_log = open(f'{context.run_dir}/energibridge.log', 'w')
            self.profiler = subprocess.Popen(shlex.split(profiler_cmd), stdout=energibridge_log)
    
    def after_experiment(self) -> None:
        """Saves the aggregated results into a single CSV inside the experiment's folder."""
        if not self.all_run_data:
            output.console_log("No data was collected, skipping CSV export.")
            return

        results_df = pd.DataFrame(self.all_run_data)
        
        # MODIFICATION 5: Simplified saving. No need to split files as this whole folder is for one script.
        script_stem = Path(self.SCRIPT_TO_RUN).stem
        output_filename = f"{script_stem}_final_results.csv"
        output_file_path = self.experiment_path / output_filename
        
        results_df.to_csv(output_file_path, index=False)
        output.console_log(f"✅ Experiment results successfully saved to: {output_file_path}")

    # No changes needed for the methods below this line
    # ... (before_experiment, before_run, start_run, interact, etc.) ...
    
    def before_experiment(self) -> None:
        pass

    def before_run(self) -> None:
        pass

    def start_run(self, context: RunnerContext) -> None:
            if not hasattr(self, 'experiment_path'):
                self.experiment_path = context.experiment_path

    def interact(self, context: RunnerContext) -> None:
        output.console_log("Waiting for the process to complete...")
        self.profiler.wait()
        output.console_log("Process finished.")

    def stop_measurement(self, context: RunnerContext) -> None:
        pass

    def stop_run(self, context: RunnerContext) -> None:
        pass
    
    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, Any]]:
        try:
            script_output_path = context.run_dir / "execution_time.txt"
            with open(script_output_path, 'r') as f:
                execution_time_s = float(f.read().strip())

            csv_path = context.run_dir / "energibridge.csv"
            df = pd.read_csv(csv_path, on_bad_lines='skip')
            df.dropna(inplace=True)

            cpu_usage_cols = [col for col in df.columns if 'CPU_USAGE' in col]
            overall_avg_cpu_usage = df[cpu_usage_cols].mean().mean() if cpu_usage_cols else 0
            avg_memory_usage_bytes = df['USED_MEMORY'].mean()
            avg_memory_usage_mb = avg_memory_usage_bytes / (1024 * 1024)
            cpu_energy = df['CPU_ENERGY (J)'].iloc[-1] - df['CPU_ENERGY (J)'].iloc[0]

            run_data = {
                'execution_time_s': round(execution_time_s, 3),
                'cpu_usage_percent': round(overall_avg_cpu_usage, 3),
                'memory_usage_mb': round(avg_memory_usage_mb, 3),
                'cpu_energy_j': round(cpu_energy, 3)
            }
            
            # We manually add the script name to the data for clarity in the final CSV
            full_run_details = {**context.execute_run, **run_data}
            full_run_details['script_name'] = self.SCRIPT_TO_RUN
            self.all_run_data.append(full_run_details)
            return run_data
        except (FileNotFoundError, IndexError, KeyError, ValueError) as e:
            output.console_log(f"❌ Error processing {csv_path}: {type(e).__name__}: {e}")
            return None
        except Exception as e:
            output.console_log(f"❌ Unexpected error processing data: {type(e).__name__}: {e}")
            return None

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None