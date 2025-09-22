# floyd_warshall_oo.py
# Usage: python floyd_warshall_oo.py /tmp/out.txt
import os, sys, time, random, math

def make_random_graph_flat(n, density, w_min=1, w_max=10, seed=42):
    rng = random.Random(seed)
    inf = math.inf
    dp = [inf]*(n*n)
    def idx(i,j): return i*n + j
    for i in range(n): dp[idx(i,i)] = 0
    for u in range(n):
        base = u*n
        for v in range(n):
            if u == v: continue
            if rng.random() < density:
                w = rng.randint(w_min, w_max)
                if w < dp[base + v]: dp[base + v] = w
    return dp

def floyd_warshall_flat(dp, n):
    def idx(i,j): return i*n + j
    inf = math.inf
    for k in range(n):
        for i in range(n):
            dik = dp[idx(i,k)]
            if dik == inf: continue
            base_i = i*n
            base_k = k*n
            for j in range(n):
                alt = dik + dp[base_k + j]
                if alt < dp[base_i + j]:
                    dp[base_i + j] = alt

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FW_N","500"))
    density = float(os.getenv("FW_DENSITY","0.1"))
    w_min = int(os.getenv("FW_W_MIN","1"))
    w_max = int(os.getenv("FW_W_MAX","10"))
    runs = int(os.getenv("FW_RUNS","1"))
    seed = int(os.getenv("FW_SEED","12345"))

    base_dp = make_random_graph_flat(n, density, w_min, w_max, seed)
    t0 = time.perf_counter()
    for _ in range(runs):
        dp = base_dp[:]  # copy flat buffer
        floyd_warshall_flat(dp, n)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.4f}s. Result saved to {out}")
