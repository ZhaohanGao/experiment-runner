# bucket_sort.py
import random
import time
import sys  # Import the sys module to access command-line arguments
import os   # Import os for path manipulation

def bucket_sort(arr: list) -> list:
    # ... (bucket_sort function remains the same) ...
    if not arr:
        return []

    max_val, min_val = max(arr), min(arr)
    if max_val == min_val:
        return arr

    bucket_count = len(arr)
    buckets = [[] for _ in range(bucket_count)]
    val_range = max_val - min_val

    for num in arr:
        index = int((num - min_val) / val_range * (bucket_count - 1))
        buckets[index].append(num)

    sorted_arr = []
    for bucket in buckets:
        sorted_arr.extend(sorted(bucket))
    return sorted_arr


if __name__ == "__main__":
    # Check if an output file path was provided
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
        
    output_file_path = sys.argv[1] # Get the path from the command line

    data_size = 10000

    num_executions = 5

    test_data = [random.randint(0, 10000) for _ in range(data_size)]
    
    start_time = time.time() 

    for _ in range(num_executions):
        data_to_sort = test_data.copy()
        bucket_sort(data_to_sort)
    
    end_time = time.time()

    duration = end_time - start_time

    # Write the result to the path provided by RunnerConfig
    with open(output_file_path, "w") as f:
        f.write(str(duration))
    
    print(f"Script finished. Duration: {duration:.2f}s. Result saved to {output_file_path}")