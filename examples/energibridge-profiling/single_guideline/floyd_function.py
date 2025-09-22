# fw_functioncall_lean.py
import os, sys, time, math, random

def make_random_graph(n, density, wmin=1, wmax=10, seed=42):
    rng = random.Random(seed)
    dp = [[math.inf]*n for _ in range(n)]
    for i in range(n): dp[i][i] = 0.0
    r = rng.random; ri = rng.randint
    for u in range(n):
        for v in range(n):
            if u!=v and r()<density:
                w = float(ri(wmin, wmax))
                duv = dp[u][v]
                if w < duv: dp[u][v] = w
    return dp

def fw_inline(dp):
    n = len(dp); inf = math.inf
    rng_n = range(n)
    for k in rng_n:
        dp_k = dp[k]
        for i in rng_n:
            dik = dp[i][k]
            if dik == inf: continue
            row_i = dp[i]
            for j in rng_n:
                dkj = dp_k[j]
                if dkj == inf: continue
                alt = dik + dkj
                if alt < row_i[j]:
                    row_i[j] = alt

if __name__ == "__main__":
    if len(sys.argv)<2: print("need output path"); sys.exit(1)
    out = sys.argv[1]
    n=500; density=0.1; runs=1; seed=12345
    base = make_random_graph(n, density, seed=seed)
    t0 = time.perf_counter()
    for _ in range(runs):
        g = [row[:] for row in base]
        fw_inline(g)
    dur = time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"{dur:.4f}s")
