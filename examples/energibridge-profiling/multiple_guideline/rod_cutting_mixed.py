# floyd_warshall_combo.py
# Usage: python floyd_warshall_combo.py /tmp/out.txt
import os, sys, time, random

NUMBA_OK = True
try:
    import numpy as np
    from numba import njit
except Exception:
    NUMBA_OK = False
    np = None
    njit = None

def make_random_graph_np(n, density, w_min=1, w_max=10, seed=42):
    rng = random.Random(seed)
    inf = np.inf
    dp = np.full((n, n), inf, dtype=np.float64)
    for i in range(n): dp[i, i] = 0.0
    for u in range(n):
        for v in range(n):
            if u == v: continue
            if rng.random() < density:
                w = rng.randint(w_min, w_max)
                if w < dp[u, v]: dp[u, v] = float(w)
    return dp

if NUMBA_OK:
    @njit(cache=True, fastmath=False)
    def fw_flat(dp_flat, n):
        # dp_flat is a 1D float64 array of size n*n
        inf = np.inf
        for k in range(n):
            base_k = k * n
            for i in range(n):
                dik = dp_flat[i*n + k]
                if dik == inf: continue
                base_i = i * n
                for j in range(n):
                    alt = dik + dp_flat[base_k + j]
                    if alt < dp_flat[base_i + j]:
                        dp_flat[base_i + j] = alt

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FW_N","500"))
    density = float(os.getenv("FW_DENSITY","0.1"))
    w_min = int(os.getenv("FW_W_MIN","1"))
    w_max = int(os.getenv("FW_W_MAX","10"))
    runs = int(os.getenv("FW_RUNS","1"))
    seed = int(os.getenv("FW_SEED","12345"))

    if not NUMBA_OK:
        print("Numba/NumPy not available; combo falls back to NumPy broadcasting.")
        import math
        base_dp = make_random_graph_np(n, density, w_min, w_max, seed)
        t0 = time.perf_counter()
        for _ in range(runs):
            dp = base_dp.copy()
            for k in range(n):
                dp[:] = np.minimum(dp, dp[:, k][:, None] + dp[k, :][None, :])
        dur = time.perf_counter() - t0
        open(out,"w").write(str(dur))
        print(f"Script finished. Duration: {dur:.4f}s. Result saved to {out}")
        sys.exit(0)

    base_dp = make_random_graph_np(n, density, w_min, w_max, seed)
    base_flat = base_dp.ravel().copy()

    # warmup/JIT
    warm = base_flat.copy()
    fw_flat(warm, n)

    t0 = time.perf_counter()
    for _ in range(runs):
        dp_flat = base_flat.copy()
        fw_flat(dp_flat, n)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.4f}s. Result saved to {out}")
