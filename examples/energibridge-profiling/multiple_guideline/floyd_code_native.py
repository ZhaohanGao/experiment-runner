# floyd_co_native.py
# Categories: Code Optimization, Native Code
import os, sys, time, random
import math
import numpy as np
try:
    from numba import njit
except Exception:
    njit = None

def make_random_graph_py(n: int, density: float, w_min=1, w_max=10, seed=42) -> np.ndarray:
    rng = random.Random(seed)
    dp = np.full((n, n), math.inf, dtype=np.float64)
    for i in range(n): dp[i, i] = 0.0
    for u in range(n):
        for v in range(n):
            if u == v: continue
            if rng.random() < density:
                w = rng.randint(w_min, w_max)
                if w < dp[u, v]:
                    dp[u, v] = float(w)
    return dp

if njit:
    @njit(cache=True, fastmath=False)
    def fw_flat_optimized(dp_flat: np.ndarray, n: int) -> None:
        # Code Optimization: early-continue on inf, cached bases, flat indexing
        inf = math.inf
        for k in range(n):
            base_k = k * n
            for i in range(n):
                dik = dp_flat[i*n + k]
                if dik == inf:  # early continue
                    continue
                base_i = i * n
                for j in range(n):
                    dkj = dp_flat[base_k + j]
                    if dkj == inf:
                        continue
                    alt = dik + dkj
                    if alt < dp_flat[base_i + j]:
                        dp_flat[base_i + j] = alt

def floyd_combo(dp: np.ndarray) -> None:
    if njit:
        arr = dp.ravel().copy()
        fw_flat_optimized(arr, dp.shape[0])
        dp[:] = arr.reshape(dp.shape)
        return
    # Fallback pure Python (still Code Optimization)
    n = dp.shape[0]; inf = math.inf
    for k in range(n):
        for i in range(n):
            dik = dp[i, k]
            if dik == inf: continue
            for j in range(n):
                dkj = dp[k, j]
                if dkj == inf: continue
                alt = dik + dkj
                if alt < dp[i, j]: dp[i, j] = alt

# --- Benchmark harness ---
if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output file path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FW_N","500"))
    density = float(os.getenv("FW_DENSITY","0.1"))
    runs = int(os.getenv("FW_RUNS","1"))
    seed = int(os.getenv("FW_SEED","12345"))
    base = make_random_graph_py(n, density, seed=seed)
    _ = floyd_combo(base.copy())  # warmup / JIT
    t0 = time.perf_counter()
    for _ in range(runs):
        dp = base.copy()
        floyd_combo(dp)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.4f}s. Result saved to {out}")
