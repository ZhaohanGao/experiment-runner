import random
import time
import sys  # Import the sys module to access command-line arguments
import os   # Import os for path manipulation

def bubble_sort(arr: list) -> list:
    if not arr:
        return []

    n = len(arr)
    # Traverse through all array elements
    for i in range(n):
        # A flag to optimize the sort. If no swaps occur in a pass,
        # the list is already sorted and we can exit early.
        swapped = False
        # Last i elements are already in place, so the inner loop
        # can avoid looking at them.
        for j in range(0, n-i-1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        # If no two elements were swapped by inner loop, then break
        if not swapped:
            break
            
    return arr


if __name__ == "__main__":
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
        bubble_sort(data_to_sort)
    
    end_time = time.time()

    duration = end_time - start_time

    # Write the result to the path provided by RunnerConfig
    with open(output_file_path, "w") as f:
        f.write(str(duration))
    
    print(f"Script finished. Duration: {duration:.2f}s. Result saved to {output_file_path}")
