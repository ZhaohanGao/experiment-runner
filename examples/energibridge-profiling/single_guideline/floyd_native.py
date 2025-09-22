# fw_numba.py
import os, sys, time, math, random
import numpy as np
from numba import njit, prange

@njit(cache=True, fastmath=False)  # exact arithmetic; flip to True if you accept tiny FP diffs
def fw_numba(dp):
    n = dp.shape[0]
    inf = np.inf
    for k in range(n):
        # parallelize rows i for fixed k (safe)
        for i in prange(n):
            dik = dp[i, k]
            if dik == inf:
                continue
            for j in range(n):
                dkj = dp[k, j]
                if dkj == inf:
                    continue
                alt = dik + dkj
                if alt < dp[i, j]:
                    dp[i, j] = alt

def make_random_graph(n, density, wmin=1, wmax=10, seed=42):
    rng = random.Random(seed)
    dp = np.full((n, n), np.inf, dtype=np.float64)
    np.fill_diagonal(dp, 0.0)
    for u in range(n):
        for v in range(n):
            if u != v and rng.random() < density:
                w = rng.randint(wmin, wmax)
                if w < dp[u, v]:
                    dp[u, v] = float(w)
    return dp

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument."); sys.exit(1)
    out = sys.argv[1]
    n=500; density=0.1; runs=1; seed=12345
    base = make_random_graph(n, density, seed=seed)
    t0 = time.perf_counter()
    for _ in range(runs):
        dp = base.copy()
        fw_numba(dp)
    dur = time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Done in {dur:.4f}s -> {out}")
