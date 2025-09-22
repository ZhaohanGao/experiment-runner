# fw_numpy.py
import os, sys, time, random, numpy as np

def make_random_graph(n, density, wmin=1, wmax=10, seed=42):
    rng = random.Random(seed)
    dp = np.full((n,n), np.inf, dtype=np.float64)
    np.fill_diagonal(dp, 0.0)
    # simple python fill; for huge n, vectorized sampling can be used
    for u in range(n):
        for v in range(n):
            if u!=v and rng.random()<density:
                w = rng.randint(wmin,wmax)
                if w < dp[u,v]: dp[u,v] = float(w)
    return dp

if __name__ == "__main__":
    if len(sys.argv)<2: print("need output path"); sys.exit(1)
    out=sys.argv[1]; n=500; density=0.1; runs=1; seed=12345
    base = make_random_graph(n, density, seed=seed)

    t0 = time.perf_counter()
    for _ in range(runs):
        dp = base.copy()
        # Floyd–Warshall via broadcasting:
        # dp = min(dp, dp[:,k,None] + dp[None,k,:]) for each k
        for k in range(n):
            dp = np.minimum(dp, dp[:, [k]] + dp[[k], :])
    dur = time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"{dur:.4f}s")
