# floyd_warshall_funcalls.py
# Usage: python floyd_warshall_funcalls.py /tmp/out.txt
import os, sys, time, random, math

def make_random_graph(n, density, w_min=1, w_max=10, seed=42):
    rng = random.Random(seed)
    dp = [[math.inf]*n for _ in range(n)]
    for i in range(n): dp[i][i] = 0
    for u in range(n):
        rowu = dp[u]
        for v in range(n):
            if u == v: continue
            if rng.random() < density:
                w = rng.randint(w_min, w_max)
                if w < rowu[v]: rowu[v] = w
    return dp

def floyd_warshall_inline(dp):
    N = len(dp)
    rng = range(N)
    for k in rng:
        dp_k = dp[k]
        for i in rng:
            dik = dp[i][k]
            if dik == math.inf: continue
            rowi = dp[i]
            for j in rng:
                alt = dik + dp_k[j]
                if alt < rowi[j]:
                    rowi[j] = alt

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FW_N","500"))
    density = float(os.getenv("FW_DENSITY","0.1"))
    w_min = int(os.getenv("FW_W_MIN","1"))
    w_max = int(os.getenv("FW_W_MAX","10"))
    runs = int(os.getenv("FW_RUNS","1"))
    seed = int(os.getenv("FW_SEED","12345"))

    base_dp = make_random_graph(n, density, w_min, w_max, seed)
    t0 = time.perf_counter()
    for _ in range(runs):
        dp = [row[:] for row in base_dp]
        floyd_warshall_inline(dp)
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.4f}s. Result saved to {out}")
