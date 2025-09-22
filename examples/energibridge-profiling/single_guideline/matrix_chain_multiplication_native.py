# mcm_native.py
import os, sys, time, random
from functools import cache
from typing import List

NUMBA_OK = True
try:
    import numpy as np
    from numba import njit
except Exception:
    NUMBA_OK = False
    np = None
    njit = None

if NUMBA_OK:
    @njit(cache=True, fastmath=False)
    def _mcm_dp_numba(arr_np: np.ndarray) -> int:
        n = arr_np.size
        INF = 1 << 60
        dp = np.empty((n, n), dtype=np.int64)
        for i in range(n):
            for j in range(n):
                dp[i, j] = INF
        for i in range(1, n):
            dp[i, i] = 0
        for i in range(n-1, 0, -1):
            ai_1 = arr_np[i-1]
            for j in range(i+1, n):
                aj = arr_np[j]
                best = dp[i, j]
                for k in range(i, j):
                    cost = dp[i, k] + dp[k+1, j] + ai_1 * arr_np[k] * aj
                    if cost < best:
                        best = cost
                dp[i, j] = best
        return int(dp[1, n-1])

def matrix_chain_multiply(arr: List[int]) -> int:
    if len(arr) < 2: return 0
    if NUMBA_OK:
        return _mcm_dp_numba(np.asarray(arr, dtype=np.int64))
    # fallback (unoptimized)
    from sys import maxsize
    n = len(arr)
    dp = [[maxsize]*n for _ in range(n)]
    for i in range(1, n): dp[i][i]=0
    for i in range(n-1, 0, -1):
        for j in range(i+1, n):
            best = dp[i][j]
            for k in range(i, j):
                cost = dp[i][k] + dp[k+1][j] + arr[i-1]*arr[k]*arr[j]
                if cost < best: best = cost
            dp[i][j] = best
    return dp[1][n-1]

def matrix_chain_order(dims: List[int]) -> int:
    @cache
    def a(i: int, j: int) -> int:
        return min((a(i,k)+dims[i]*dims[k]*dims[j]+a(k,j) for k in range(i+1,j)), default=0)
    return a(0, len(dims)-1)

def make_dims(n: int, mode: str, seed: int, dmin: int, dmax: int) -> List[int]:
    if n <= 0: return []
    if mode == "random":
        rng = random.Random(seed); return [rng.randint(dmin, dmax) for _ in range(n)]
    return list(range(1, n+1))

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Please provide an output file path as a command-line argument."); sys.exit(1)
    out = sys.argv[1]
    N = int(os.getenv("MCM_N", "800")); GEN = os.getenv("MCM_GEN", "range").lower()
    MIN_DIM = int(os.getenv("MCM_MIN_DIM", "5")); MAX_DIM = int(os.getenv("MCM_MAX_DIM", "50"))
    SEED = int(os.getenv("MCM_SEED", "12345")); RUNS = int(os.getenv("MCM_RUNS", "1"))
    BACKEND = os.getenv("MCM_BACKEND", "dp").lower()
    dims = make_dims(N, GEN, SEED, MIN_DIM, MAX_DIM)

    _ = matrix_chain_multiply(dims) if BACKEND=="dp" else matrix_chain_order(dims)  # warmup / JIT

    t0 = time.perf_counter()
    for _ in range(RUNS):
        _res = matrix_chain_multiply(dims) if BACKEND=="dp" else matrix_chain_order(dims)
    dur = time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
