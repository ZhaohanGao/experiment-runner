# knapsack_co_native.py
# Categories: Code Optimization, Native Code
import os, sys, time, random
try:
    from numba import njit  # Native Code (G15)
except Exception:
    njit = None

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    rng = random.Random(seed)
    return [rng.randint(w_min, w_max) for _ in range(n)], [rng.randint(v_min, v_max) for _ in range(n)]

if njit:
    @njit(cache=True, fastmath=False)
    def _knapsack_1d(capacity, wt, val):
        # Code Optimization: 1D DP, iterate weight backward
        dp = [0]*(capacity+1)
        n = len(wt)
        for i in range(n):
            wi = wt[i]; vi = val[i]
            for w in range(capacity, wi-1, -1):
                cand = vi + dp[w-wi]
                if cand > dp[w]:
                    dp[w] = cand
        return dp[capacity]
else:
    def _knapsack_1d(capacity, wt, val):
        dp = [0]*(capacity+1)
        n = len(wt)
        for i in range(n):
            wi = wt[i]; vi = val[i]
            for w in range(capacity, wi-1, -1):
                cand = vi + dp[w-wi]
                if cand > dp[w]:
                    dp[w] = cand
        return dp[capacity]

def knapsack_combo(capacity, wt, val):
    return _knapsack_1d(capacity, wt, val)

# --- Benchmark harness ---
if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output file path"); sys.exit(1)
    out = sys.argv[1]
    n    = int(os.getenv("KS_N", "2000"))
    cap  = int(os.getenv("KS_CAP", "5000"))
    wmin = int(os.getenv("KS_W_MIN", "1"))
    wmax = int(os.getenv("KS_W_MAX", "15"))
    vmin = int(os.getenv("KS_V_MIN", "1"))
    vmax = int(os.getenv("KS_V_MAX", "100"))
    runs = int(os.getenv("KS_RUNS", "1"))
    seed = int(os.getenv("KS_SEED", "12345"))

    wt, val = make_random_instance(n, cap, wmin, wmax, vmin, vmax, seed)
    _ = knapsack_combo(cap, wt, val)  # warmup / JIT

    t0 = time.perf_counter()
    for _ in range(runs):
        _best = knapsack_combo(cap, wt, val)
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
