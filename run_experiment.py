import subprocess
import os

# ================================ DEFINE YOUR EXPERIMENTS HERE ================================

# Add all the python scripts you want to test to this list.
SCRIPTS_TO_RUN = [
    "original/dijkstra_origin.py",
    "single_guideline/dijkstra_code.py",
    "single_guideline/dijkstra_multi.py",
    "single_guideline/dijkstra_native.py",
    "single_guideline/dijkstra_function.py",
    "single_guideline/dijkstra_object.py",
    "single_guideline/dijkstra_network.py",
    "single_guideline/dijkstra_other.py",
    "multiple_guideline/dijkstra_mixed.py",
    "original/floyd_origin.py",
    "single_guideline/floyd_code.py",
    "single_guideline/floyd_function.py",
    "single_guideline/floyd_multi.py",
    "single_guideline/floyd_native.py"
    "single_guideline/floyd_object.py",
    "single_guideline/floyd_other.py"
    "multiple_guideline/floyd_mixed.py",
    "original/knapsack_origin.py",
    "single_guideline/knapsack_code.py",
    "single_guideline/knapsack_function.py",
    "single_guideline/knapsack_native.py",
    "single_guideline/knapsack_object.py",
    "single_guideline/knapsack_other.py",
    "multiple_guideline/knapsack_mixed.py",
    "original/edit_distance_origin.py",
    "single_guideline/edit_distance_code.py",
    "single_guideline/edit_distance_function.py",
    "single_guideline/edit_distance_native.py",
    "single_guideline/edit_distance_object.py",
    "single_guideline/edit_distance_other.py",
    "multiple_guideline/edit_distance_mixed.py",
    "original/longest_common_subsequence_origin.py",
    "single_guideline/longest_common_subsequence_code.py",
    "single_guideline/longest_common_subsequence_function.py",
    "single_guideline/longest_common_subsequence_native.py",
    "single_guideline/longest_common_subsequence_object.py",
    "single_guideline/longest_common_subsequence_other.py",
    "multiple_guideline/longest_common_subsequence_mixed.py",
    "original/matrix_chain_multiplication_origin.py",
    "single_guideline/matrix_chain_multiplication_code.py",
    "single_guideline/matrix_chain_multiplication_function.py",
    "single_guideline/matrix_chain_multiplication_native.py",
    "single_guideline/matrix_chain_multiplication_object.py",
    "single_guideline/matrix_chain_multiplication_other.py",
    "multiple_guideline/matrix_chain_multiplication_mixed.py",
    "original/matrix_chain_order_origin.py",
    "single_guideline/matrix_chain_order_code.py",
    "single_guideline/matrix_chain_order_function.py",
    "single_guideline/matrix_chain_order_native.py",
    "single_guideline/matrix_chain_order_object.py",
    "single_guideline/matrix_chain_order_other.py",
    "multiple_guideline/matrix_chain_order_mixed.py",
    "original/rod_cutting_origin.py",
    "single_guideline/rod_cutting_code.py",
    "single_guideline/rod_cutting_function.py",
    "single_guideline/rod_cutting_native.py",
    "single_guideline/rod_cutting_object.py",
    "single_guideline/rod_cutting_other.py",
    "multiple_guideline/rod_cutting_mixed.py",
    "original/fibonacci_origin.py",
    "single_guideline/fibonacci_code.py",
    "single_guideline/fibonacci_function.py",
    "single_guideline/fibonacci_native.py",
    "single_guideline/fibonacci_object.py",
    "single_guideline/fibonacci_other.py",
    "multiple_guideline/fibonacci_mixed.py",
    "original/levenshtein_distance_origin.py",
    "single_guideline/levenshtein_distance_code.py",
    "single_guideline/levenshtein_distance_function.py",
    "single_guideline/levenshtein_distance_native.py",
    "single_guideline/levenshtein_distance_object.py",
    "single_guideline/levenshtein_distance_other.py",
    "multiple_guideline/levenshtein_distance_mixed.py"
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