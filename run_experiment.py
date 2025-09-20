import subprocess
import os

# ================================ DEFINE YOUR EXPERIMENTS HERE ================================

# Add all the python scripts you want to test to this list.
SCRIPTS_TO_RUN = [
    "bubble_sort.py",
    "bucket_sort.py"
]

# ==============================================================================================


def run_experiment(script_name: str):
    """Sets the environment variable and runs the experiment for a single script."""
    print("="*60)
    print(f"🚀 Starting experiment for: {script_name}")
    print("="*60)
    
    # Copy the current environment and set the SCRIPT_TO_RUN variable
    # This tells RunnerConfig.py which script to use.
    env = os.environ.copy()
    env["SCRIPT_TO_RUN"] = script_name
    
    # Define the command to run the experiment runner
    # Make sure this path is correct for your project structure.
    command = [
        "python",
        "experiment-runner/",
        "examples/energibridge-profiling/RunnerConfig.py"
    ]
    
    try:
        # Run the command with the modified environment
        # `check=True` will raise an error if the experiment fails
        subprocess.run(command, env=env, check=True)
        print(f"\n✅ Experiment for {script_name} completed successfully.")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find the runner script at '{' '.join(command)}'.")
        print("Please check if the path is correct.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Experiment for {script_name} failed with exit code {e.returncode}.")
        
    print("-" * 60 + "\n")


if __name__ == "__main__":
    print("Starting batch of experiments...")
    for script in SCRIPTS_TO_RUN:
        run_experiment(script)
    print("🎉 All experiments have been completed!")