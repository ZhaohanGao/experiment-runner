# bubble_sort.py
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
    data_size = 250
    num_executions = 100000
    
    test_data = [random.randint(0, 10000) for _ in range(data_size)]
   
    for i in range(num_executions):
        data_to_sort = test_data.copy()
        bubble_sort(data_to_sort)