# mcm_chain_codeopt.py
import os, sys, time, random
from typing import List, Tuple

def matrix_chain_order(array: List[int]) -> Tuple[List[List[int]], List[List[int]]]:
    n = len(array)
    if n < 2:
        z = [[0]*n for _ in range(n)]
        return z, [row[:] for row in z]
    if n == 2:
        z = [[0]*n for _ in range(n)]
        return z, [row[:] for row in z]

    matrix = [[0]*n for _ in range(n)]
    sol    = [[0]*n for _ in range(n)]
    INF = sys.maxsize
    rng_len = range(2, n)                  # G3
    for chain_len in rng_len:
        last_a = n - chain_len + 1
        for a in range(1, last_a):
            b = a + chain_len - 1
            best = INF
            ai_1 = array[a - 1]            # G1: cache
            ab   = array[b]
            row_a = matrix[a]
            for c in range(a, b):
                cost = row_a[c] + matrix[c + 1][b] + ai_1 * array[c] * ab
                if cost < best:
                    best = cost
                    sol[a][b] = c
            row_a[b] = best
    return matrix, sol

def reconstruct_parenthesization(sol: List[List[int]], i: int, j: int) -> str:
    if i == j: return f"A{i}"
    k = sol[i][j]
    return f"( {reconstruct_parenthesization(sol, i, k)} {reconstruct_parenthesization(sol, k+1, j)} )"

def make_dims(n: int, mode: str, seed: int, dmin: int, dmax: int) -> List[int]:
    if mode == "example": return [30,35,15,5,10,20,25]
    if n <= 0: return []
    if mode == "random":
        rng = random.Random(seed)
        return [rng.randint(dmin, dmax) for _ in range(n)]
    return list(range(1, n+1))

if __name__ == "__main__":
    if len(sys.argv)<2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    N = int(os.getenv("MCM_N", "64000"))                    # length of dims list
    GEN = os.getenv("MCM_GEN", "example").lower()       # "example" | "range" | "random"
    MIN_DIM = int(os.getenv("MCM_MIN_DIM", "5"))
    MAX_DIM = int(os.getenv("MCM_MAX_DIM", "50"))
    SEED = int(os.getenv("MCM_SEED", "12345"))
    RUNS = int(os.getenv("MCM_RUNS", "300000"))

    dims = make_dims(N, GEN, SEED, MIN_DIM, MAX_DIM)

    _ = matrix_chain_order(dims)  # warmup

    t0 = time.perf_counter()
    last = None
    for _ in range(RUNS):
        last = matrix_chain_order(dims)
    dur = time.perf_counter() - t0

    with open(out,"w") as f: f.write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
