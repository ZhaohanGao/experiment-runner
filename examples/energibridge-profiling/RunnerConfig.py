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
    """The name of the experiment."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name: str = f"new_runner_experiment_{timestamp}"

    """The path in which Experiment Runner will create a folder with the name `self.name`, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path:        Path             = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use `OperationType.AUTO`."""
    operation_type:             OperationType   = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms:    int             = 1000

    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
    def __init__(self):
        """Executes immediately after program start, on config load"""

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
        self.run_table_model = None  # Initialized later
        
        # This list will store the data dictionary from each run
        self.all_run_data = []
        
        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        sampling_factor = FactorModel("sampling", [100, 200, 300, 400, 500, 600])
        # sampling_factor = FactorModel("sampling", [100])
        self.run_table_model = RunTableModel(
            factors = [sampling_factor],
            # CORRECTED data_columns based on the provided CSV
            data_columns=['execution_time_s', 'cpu_usage_percent', 'memory_usage_mb', 
                        'cpu_energy_j']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""
        pass

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        pass

    def start_run(self, context: RunnerContext) -> None:
            """Perform any activity required for starting the run here.
            For example, starting the target system to measure.
            Activities after starting the run should also be performed here."""
            # This is a robust way to ensure the experiment_path is set on the instance
            # from the context provided by the runner framework.
            if not hasattr(self, 'experiment_path'):
                self.experiment_path = context.experiment_path

    def start_measurement(self, context: RunnerContext) -> None:
        """Perform any activity required for starting measurements."""
        sampling_interval = context.execute_run['sampling']

        profiler_cmd = f'sudo energibridge \
                        --interval {sampling_interval} \
                        --max-execution 20 \
                        --output {context.run_dir / "energibridge.csv"} \
                        --summary \
                        python3 examples/energibridge-profiling/primer.py'
        
        energibridge_log = open(f'{context.run_dir}/energibridge.log', 'w')
        self.profiler = subprocess.Popen(shlex.split(profiler_cmd), stdout=energibridge_log)

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""
        output.console_log("Running program for 20 seconds")
        time.sleep(20)

    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""
        self.profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        pass
    
    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, Any]]:
            """
            Parse and process measurement data to calculate key performance metrics.
            """
            try:
                csv_path = context.run_dir / "energibridge.csv"
                
                if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
                    output.console_log(f"Warning: energibridge.csv is missing or empty in {context.run_dir}")
                    return None

                df = pd.read_csv(csv_path, on_bad_lines='skip')
                df.dropna(inplace=True)

                if df.empty:
                    output.console_log(f"Warning: CSV file {csv_path} is empty after cleaning.")
                    return None

                # --- 1. Execution Time ---
                execution_time_ns = df['Time'].iloc[-1] - df['Time'].iloc[0]
                execution_time_s = execution_time_ns / 1_000_000_000

                # --- 2. CPU Usage ---
                cpu_usage_cols = [col for col in df.columns if 'CPU_USAGE' in col]
                overall_avg_cpu_usage = df[cpu_usage_cols].mean().mean() if cpu_usage_cols else 0

                # --- 3. Memory Usage ---
                avg_memory_usage_bytes = df['USED_MEMORY'].mean()
                avg_memory_usage_mb = avg_memory_usage_bytes / (1024 * 1024)

                # --- 4. Energy Consumption ---
                cpu_energy = df['CPU_ENERGY (J)'].iloc[-1] - df['CPU_ENERGY (J)'].iloc[0]
                
                run_data = {
                    'execution_time_s': round(execution_time_s, 3),
                    'cpu_usage_percent': round(overall_avg_cpu_usage, 3),
                    'memory_usage_mb': round(avg_memory_usage_mb, 3),
                    'cpu_energy_j': round(cpu_energy, 3)
                }
                
                full_run_details = {**context.execute_run, **run_data}
                self.all_run_data.append(full_run_details)
                
                return run_data

            except (FileNotFoundError, IndexError, KeyError, ValueError) as e:
                # IMPROVED LOGGING: This will now print the exact error message
                # e.g., "KeyError: 'CPU_ENERGY (J)'"
                output.console_log(f"❌ An error occurred while processing {csv_path}: {type(e).__name__}: {e}")
                # For deeper debugging, you can print the available columns:
                if 'df' in locals() and not df.empty:
                    output.console_log(f"Available columns are: {list(df.columns)}")
                return None

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here. This is the ideal place
        to save aggregated results. Invoked only once during the lifetime of the program."""
        if not self.all_run_data:
            output.console_log("No data was collected, skipping CSV export.")
            return

        # Create a pandas DataFrame from our list of collected run data
        results_df = pd.DataFrame(self.all_run_data)

        # Define the output path for the results CSV file inside the experiment's main folder
        output_file_path = self.experiment_path / 'experiment_results.csv'
        
        # Write the DataFrame to a CSV file, excluding the default pandas index
        results_df.to_csv(output_file_path, index=False)
        
        output.console_log(f"✅ Experiment results successfully saved to: {output_file_path}")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None