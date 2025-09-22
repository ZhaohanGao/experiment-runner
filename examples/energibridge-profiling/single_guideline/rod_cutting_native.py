# floyd_warshall_native.py
# Usage: python floyd_warshall_native.py /tmp/out.txt
import os, sys, time, random, math

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
    dp = [[float('inf')]*n for _ in range(n)]
    for i in range(n): dp[i][i] = 0.0
    for u in range(n):
        for v in range(n):
            if u == v: continue
            if rng.random() < density:
                w = rng.randint(w_min, w_max)
                if w < dp[u][v]: dp[u][v] = float(w)
    return np.array(dp, dtype=np.float64)

if NUMBA_OK:
    @njit(cache=True, fastmath=False)
    def floyd_warshall_numba(dp):
        n = dp.shape[0]
        for k in range(n):
            for i in range(n):
                dik = dp[i, k]
                if dik == np.inf:
                    continue
                for j in range(n):
                    alt = dik + dp[k, j]
                    if alt < dp[i, j]:
                        dp[i, j] = alt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Provide output file path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FW_N", "500"))
    density = float(os.getenv("FW_DENSITY", "0.1"))
    w_min = int(os.getenv("FW_W_MIN", "1"))
    w_max = int(os.getenv("FW_W_MAX", "10"))
    runs = int(os.getenv("FW_RUNS", "1"))
    seed = int(os.getenv("FW_SEED", "12345"))

    if not NUMBA_OK:
        print("Numba/NumPy not available; falling back to pure Python may be slow.")
    base_dp = make_random_graph_np(n, density, w_min, w_max, seed)

    # warmup/JIT
    if NUMBA_OK:
        warm = base_dp.copy()
        floyd_warshall_numba(warm)

    t0 = time.perf_counter()
    for _ in range(runs):
        dp = base_dp.copy()
        if NUMBA_OK:
            floyd_warshall_numba(dp)
        else:
            # tiny fallback: pure python triple loop
            dp_list = dp.tolist()
            N = len(dp_list)
            for k in range(N):
                for i in range(N):
                    dik = dp_list[i][k]
                    if dik == math.inf: continue
                    for j in range(N):
                        alt = dik + dp_list[k][j]
                        if alt < dp_list[i][j]:
                            dp_list[i][j] = alt
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.4f}s. Result saved to {out}")
