# # bubble_sort.py
# import random

# def bubble_sort(arr: list) -> list:
#     """
#     Sorts a list in ascending order using the Bubble Sort algorithm.
#     """
#     n = len(arr)
#     for i in range(n):
#         swapped = False
#         for j in range(0, n - i - 1):
#             if arr[j] > arr[j + 1]:
#                 arr[j], arr[j + 1] = arr[j + 1], arr[j]
#                 swapped = True
#         if not swapped:
#             break
#     return arr

# if __name__ == "__main__":
#     data_size = 250
#     num_executions = 1000
    
#     test_data = [random.randint(0, 10000) for _ in range(data_size)]
   
#     for i in range(num_executions):
#         data_to_sort = test_data.copy()
#         bubble_sort(data_to_sort)

import random
import multiprocessing
import time

def bubble_sort(arr: list) -> list:
    """
    Sorts a list in ascending order using the Bubble Sort algorithm.
    This function remains unchanged as it's our basic unit of work.
    """
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# --- NEW: Worker function for our processes ---
# Each process will run this function. It takes a placeholder argument '_'
# because the map function requires it, but we don't use it.
def perform_sort(_):
    """
    Creates a copy of the test data and sorts it.
    This is the target function for each worker process.
    """
    data_to_sort = test_data.copy()
    bubble_sort(data_to_sort)
    # The result isn't returned, we're just creating CPU load.


# The main execution block MUST be protected by if __name__ == "__main__":
# This prevents child processes from re-importing and re-executing the main script's code.
if __name__ == "__main__":
    data_size = 250
    num_executions = 1000
    
    # Use the number of available CPU cores for our process pool
    # Your taskset command will restrict which cores these processes can actually use.
    num_processes = multiprocessing.cpu_count()

    print(f"Starting multi-process sort...")
    print(f"Data Size: {data_size}")
    print(f"Total Executions: {num_executions}")
    print(f"Worker Processes: {num_processes}")
    
    # This data is created once in the main process. Child processes on Linux/macOS
    # will inherit it efficiently (copy-on-write).
    test_data = [random.randint(0, 10000) for _ in range(data_size)]
   
    start_time = time.time()

    # A Pool represents a pool of worker processes. The 'with' statement
    # ensures the pool is properly closed when we're done.
    with multiprocessing.Pool(processes=num_processes) as pool:
        # pool.map distributes the 'perform_sort' task across the worker processes.
        # It calls perform_sort() for each item in range(num_executions).
        # This is a blocking call; it will wait until all 1000 tasks are complete.
        pool.map(perform_sort, range(num_executions))

    end_time = time.time()
    print(f"All {num_executions} sorts completed in {end_time - start_time:.2f} seconds.")
