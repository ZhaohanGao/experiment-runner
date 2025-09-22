# fw_oo_minimal.py
import os, sys, time, random, math

def make_dp(n, density, wmin=1, wmax=10, seed=42):
    rng = random.Random(seed)
    dp = [[math.inf]*n for _ in range(n)]
    for i in range(n): dp[i][i]=0.0
    r = rng.random; ri=rng.randint
    for u in range(n):
        for v in range(n):
            if u!=v and r()<density:
                w = float(ri(wmin, wmax))
                if w < dp[u][v]: dp[u][v]=w
    return dp

def fw(dp):
    n=len(dp); inf=math.inf; R=range(n)
    for k in R:
        dk=dp[k]
        for i in R:
            dik=dp[i][k]
            if dik==inf: continue
            ri=dp[i]
            for j in R:
                dkj=dk[j]
                if dkj==inf: continue
                alt=dik+dkj
                if alt<ri[j]: ri[j]=alt

if __name__=="__main__":
    if len(sys.argv)<2: print("need output path"); sys.exit(1)
    out=sys.argv[1]; n=500; density=0.1; runs=1; seed=12345
    base=make_dp(n,density,seed=seed)
    t0=time.perf_counter()
    for _ in range(runs):
        dp=[row[:] for row in base]
        fw(dp)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"{dur:.4f}s")
