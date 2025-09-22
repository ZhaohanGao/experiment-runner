# mcm_experiment_plain.py
# Usage: python mcm_experiment_plain.py /tmp/out.txt
import os
import sys
import time
import random
from functools import cache
from sys import maxsize
from typing import List


def matrix_chain_multiply(arr: List[int]) -> int:
    """
    Bottom-up DP:
    Given dims arr where matrix i has shape (arr[i-1] x arr[i]),
    return the minimum scalar multiplications to multiply the chain.
    """
    if len(arr) < 2:
        return 0
    n = len(arr)
    dp = [[maxsize for _ in range(n)] for _ in range(n)]
    for i in range(n - 1, 0, -1):
        for j in range(i, n):
            if i == j:
                dp[i][j] = 0
                continue
            for k in range(i, j):
                dp[i][j] = min(
                    dp[i][j],
                    dp[i][k] + dp[k + 1][j] + arr[i - 1] * arr[k] * arr[j],
                )
    return dp[1][n - 1]


def matrix_chain_order(dims: List[int]) -> int:
    """
    Top-down with caching (recursive).
    Returns minimal scalar multiplications over dims.
    """

    @cache
    def a(i: int, j: int) -> int:
        return min(
            (a(i, k) + dims[i] * dims[k] * dims[j] + a(k, j) for k in range(i + 1, j)),
            default=0,
        )

    return a(0, len(dims) - 1)


def make_dims(n: int, mode: str, seed: int, dmin: int, dmax: int) -> List[int]:
    """
    Produce a dimension list of length n.
    - mode="range": [1, 2, ..., n]
    - mode="random": random ints in [dmin, dmax]
    """
    if n <= 0:
        return []
    if mode == "random":
        rng = random.Random(seed)
        return [rng.randint(dmin, dmax) for _ in range(n)]
    else:
        return list(range(1, n + 1))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables via environment variables
    N = int(os.getenv("MCM_N", "800"))                 # length of dims list
    GEN = os.getenv("MCM_GEN", "range").lower()        # "range" | "random"
    MIN_DIM = int(os.getenv("MCM_MIN_DIM", "5"))
    MAX_DIM = int(os.getenv("MCM_MAX_DIM", "50"))
    SEED = int(os.getenv("MCM_SEED", "12345"))
    RUNS = int(os.getenv("MCM_RUNS", "1"))
    BACKEND = os.getenv("MCM_BACKEND", "dp").lower()   # "dp" | "recursive"

    dims = make_dims(N, GEN, SEED, MIN_DIM, MAX_DIM)

    # (Optional) You can uncomment to quickly sanity-check very small inputs.
    # if N <= 5:
    #     print("dims:", dims)

    # Time only the compute
    t0 = time.perf_counter()
    last = None
    for _ in range(RUNS):
        if BACKEND == "recursive":
            last = matrix_chain_order(dims)
        else:
            last = matrix_chain_multiply(dims)
    duration = time.perf_counter() - t0

    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")
    # If you want to also see the computed minimal cost, uncomment:
    # print("Min multiplications:", last)
