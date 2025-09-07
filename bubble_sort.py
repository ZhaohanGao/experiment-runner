# bubble_sort.py
import time
import random

def bubble_sort(arr: list) -> list:
    """
    Sorts a list in ascending order using the Bubble Sort algorithm.
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

if __name__ == "__main__":
    # WARNING: Bubble sort is O(n^2). A large data_size will result in
    # extremely long execution times for this loop.
    data_size = 250
    num_executions = 100000
    
    # Generate one master list to be used for all sorts
    print(f"Generating test data with {data_size} items...")
    test_data = [random.randint(0, 10000) for _ in range(data_size)]
    
    print(f"Executing Bubble Sort {num_executions} times...")
    print("This may take several minutes. Please be patient. ⏳")

    start_time = time.time()
    for i in range(num_executions):
        # We must copy the data each time to ensure we are not
        # sorting an already-sorted list.
        data_to_sort = test_data.copy()
        bubble_sort(data_to_sort)

    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nTotal time for {num_executions} executions: {total_time:.4f} seconds.")
    print(f"Average time per sort: {(total_time / num_executions) * 1e6:.4f} microseconds.")