# bucket_sort.py
import time
import random

def bucket_sort(arr: list) -> list:
    """
    Sorts a list using the Bucket Sort algorithm.
    """
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
    # Bucket sort is much more efficient and can handle a larger list.
    data_size = 250
    num_executions = 100000

    # Generate one master list to be used for all sorts
    print(f"Generating test data with {data_size} items...")
    test_data = [random.randint(0, 10000) for _ in range(data_size)]

    print(f"Executing Bucket Sort {num_executions} times...")
    
    start_time = time.time()
    for _ in range(num_executions):
        # We must copy the data each time to ensure we are sorting
        # the original unsorted list in every iteration.
        data_to_sort = test_data.copy()
        bucket_sort(data_to_sort)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\nTotal time for {num_executions} executions: {total_time:.4f} seconds.")
    print(f"Average time per sort: {(total_time / num_executions) * 1e6:.4f} microseconds.")