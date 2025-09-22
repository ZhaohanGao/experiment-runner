# mcm_chain_experiment.py
# Usage: python mcm_chain_experiment.py /tmp/out.txt
import os
import sys
import time
import random
from typing import List, Tuple


def matrix_chain_order(array: List[int]) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Dynamic Programming solution (bottom-up) that returns:
      - matrix: DP table of minimal costs
      - sol:    split positions to reconstruct an optimal parenthesization

    Indices follow the classic convention where matrix i has shape
    (array[i-1] x array[i]) and valid subproblems are for i,j in [1..n-1].
    """
    n = len(array)
    # Handle tiny inputs explicitly
    if n < 2:
        # No matrix at all (cost 0)
        return [[0 for _ in range(n)] for _ in range(n)], [[0 for _ in range(n)] for _ in range(n)]
    if n == 2:
        # Single matrix (cost 0)
        mat = [[0 for _ in range(n)] for _ in range(n)]
        sol = [[0 for _ in range(n)] for _ in range(n)]
        return mat, sol

    import sys as _sys
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    sol = [[0 for _ in range(n)] for _ in range(n)]

    for chain_length in range(2, n):
        for a in range(1, n - chain_length + 1):
            b = a + chain_length - 1
            matrix[a][b] = _sys.maxsize
            for c in range(a, b):
                cost = matrix[a][c] + matrix[c + 1][b] + array[a - 1] * array[c] * array[b]
                if cost < matrix[a][b]:
                    matrix[a][b] = cost
                    sol[a][b] = c
    return matrix, sol


def reconstruct_parenthesization(sol: List[List[int]], i: int, j: int) -> str:
    """
    Build an optimal parenthesization string using the 'sol' table.
    (Not timed; for validation/printing only.)
    """
    if i == j:
        return f"A{i}"
    k = sol[i][j]
    left = reconstruct_parenthesization(sol, i, k)
    right = reconstruct_parenthesization(sol, k + 1, j)
    return f"( {left} {right} )"


def make_dims(n: int, mode: str, seed: int, dmin: int, dmax: int) -> List[int]:
    """
    Produce a dimension list of length n.
    - mode="example": returns [30, 35, 15, 5, 10, 20, 25] and ignores n
    - mode="range":   [1, 2, ..., n]
    - mode="random":  random ints in [dmin, dmax]
    """
    if mode == "example":
        return [30, 35, 15, 5, 10, 20, 25]
    if n <= 0:
        return []
    if mode == "random":
        rng = random.Random(seed)
        return [rng.randint(dmin, dmax) for _ in range(n)]
    # default: "range"
    return list(range(1, n + 1))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables via environment variables
    N = int(os.getenv("MCM_N", "64000"))                    # length of dims list
    GEN = os.getenv("MCM_GEN", "example").lower()       # "example" | "range" | "random"
    MIN_DIM = int(os.getenv("MCM_MIN_DIM", "5"))
    MAX_DIM = int(os.getenv("MCM_MAX_DIM", "50"))
    SEED = int(os.getenv("MCM_SEED", "12345"))
    RUNS = int(os.getenv("MCM_RUNS", "300000"))

    dims = make_dims(N, GEN, SEED, MIN_DIM, MAX_DIM)

    # Warmup outside the timing window
    _matrix, _sol = matrix_chain_order(dims)

    # Timed section
    t0 = time.perf_counter()
    last_matrix = None
    last_sol = None
    for _ in range(RUNS):
        last_matrix, last_sol = matrix_chain_order(dims)
    duration = time.perf_counter() - t0

    # Persist duration
    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")

    # Optional: print the minimal cost and one optimal parenthesization (not timed)
    if last_matrix is not None and last_sol is not None and len(dims) >= 2:
        n = len(dims)
        min_cost = last_matrix[1][n - 1]
        paren = reconstruct_parenthesization(last_sol, 1, n - 1)
        # Comment these out if you want a completely quiet experiment run
        # print("Min multiplications:", min_cost)
        # print("One optimal parenthesization:", paren)
