# fib_experiment.py
# Usage: python fib_experiment.py /tmp/out.txt
import os
import sys
import time
import functools
from collections.abc import Iterator
from math import sqrt

import numpy as np
from numpy import ndarray


def fib_iterative_yield(n: int) -> Iterator[int]:
    if n < 0:
        raise ValueError("n is negative")
    a, b = 0, 1
    yield a
    for _ in range(n):
        yield b
        a, b = b, a + b


def fib_iterative(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n is negative")
    if n == 0:
        return [0]
    fib = [0, 1]
    for _ in range(n - 1):
        fib.append(fib[-1] + fib[-2])
    return fib


def fib_recursive(n: int) -> list[int]:
    def fib_recursive_term(i: int) -> int:
        if i < 0:
            raise ValueError("n is negative")
        if i < 2:
            return i
        return fib_recursive_term(i - 1) + fib_recursive_term(i - 2)

    if n < 0:
        raise ValueError("n is negative")
    return [fib_recursive_term(i) for i in range(n + 1)]


def fib_recursive_cached(n: int) -> list[int]:
    @functools.cache
    def fib_recursive_term(i: int) -> int:
        if i < 0:
            raise ValueError("n is negative")
        if i < 2:
            return i
        return fib_recursive_term(i - 1) + fib_recursive_term(i - 2)

    if n < 0:
        raise ValueError("n is negative")
    return [fib_recursive_term(i) for i in range(n + 1)]


def fib_memoization(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n is negative")
    cache: dict[int, int] = {0: 0, 1: 1, 2: 1}

    def rec_fn_memoized(num: int) -> int:
        if num in cache:
            return cache[num]
        value = rec_fn_memoized(num - 1) + rec_fn_memoized(num - 2)
        cache[num] = value
        return value

    return [rec_fn_memoized(i) for i in range(n + 1)]


def fib_binet(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n is negative")
    if n >= 1475:
        raise ValueError("n is too large")
    sqrt_5 = sqrt(5)
    phi = (1 + sqrt_5) / 2
    return [round(phi**i / sqrt_5) for i in range(n + 1)]


def matrix_pow_np(m: ndarray, power: int) -> ndarray:
    result = np.array([[1, 0], [0, 1]], dtype=int)
    base = m
    if power < 0:
        raise ValueError("power is negative")
    while power:
        if power % 2 == 1:
            result = np.dot(result, base)
        base = np.dot(base, base)
        power //= 2
    return result


def fib_matrix_np(n: int) -> int:
    if n < 0:
        raise ValueError("n is negative")
    if n == 0:
        return 0
    m = np.array([[1, 1], [1, 0]], dtype=int)
    result = matrix_pow_np(m, n - 1)
    return int(result[0, 0])


def run_backend(backend: str, n: int):
    """
    Executes the selected backend for input n and returns a value just to
    keep Python from optimizing away the work. The return value is not used.
    """
    b = backend.lower()
    if b == "iter_yield":
        # fully consume the generator so the work is done
        out = list(fib_iterative_yield(n))
        return out[-1] if out else 0
    elif b == "iter":
        out = fib_iterative(n)
        return out[-1]
    elif b == "recursive":
        out = fib_recursive(n)
        return out[-1]
    elif b == "recursive_cached":
        out = fib_recursive_cached(n)
        return out[-1]
    elif b == "memo":
        out = fib_memoization(n)
        return out[-1]
    elif b == "binet":
        out = fib_binet(n)
        return out[-1]
    elif b == "matrix":
        return fib_matrix_np(n)
    else:
        raise ValueError(f"Unknown FIB_BACKEND: {backend}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables via environment variables
    n = int(os.getenv("FIB_N", "200000"))
    runs = int(os.getenv("FIB_RUNS", "100"))
    backend = os.getenv("FIB_BACKEND", "iter").lower()  # iter_yield|iter|recursive|recursive_cached|memo|binet|matrix

    # Gentle reminders for dangerous combos (no optimization, just sanity)
    if backend == "recursive" and n > 35:
        # The naive recursive approach is exponential; large n will take a very long time.
        print(f"Warning: FIB_BACKEND=recursive with n={n} may be extremely slow.", flush=True)
    if backend == "binet" and n >= 1475:
        print("Error: FIB_BACKEND=binet requires FIB_N < 1475 due to float limits.")
        sys.exit(1)

    # Warmup outside timing (helps stabilize measurements)
    _ = run_backend(backend, min(n, 100) if backend == "recursive" else n)

    # Timed section
    t0 = time.perf_counter()
    last_val = None
    for _ in range(runs):
        last_val = run_backend(backend, n)
    duration = time.perf_counter() - t0

    # Persist duration
    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")
