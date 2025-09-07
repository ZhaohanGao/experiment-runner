# heavy_work.py
def calculate_something():
    """A simple function that uses the CPU."""
    total = 0
    for i in range(40_000_000):
        total += i
    print(f"Calculation finished. Total: {total}")

if __name__ == "__main__":
    calculate_something()