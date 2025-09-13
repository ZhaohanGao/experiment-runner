# bucket_sort.py
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
    data_size = 250
    num_executions = 300000

    test_data = [random.randint(0, 10000) for _ in range(data_size)]
    
    for _ in range(num_executions):
        data_to_sort = test_data.copy()
        bucket_sort(data_to_sort)