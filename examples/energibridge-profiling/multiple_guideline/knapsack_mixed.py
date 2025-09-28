# Guideline used: Code Optimization (G1, G3) • Native Code (G15, G17) • Object Orientation (G20)
import os, sys, time, random
try:
    from numba import njit
except Exception:
    njit = None

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    # Simple Python generator; you could switch to NumPy for bulk draws if desired
    rng = random.Random(seed)
    return [rng.randint(w_min, w_max) for _ in range(n)], [rng.randint(v_min, v_max) for _ in range(n)]

if njit:
    @njit(cache=True, fastmath=False)  # G15; keep exact; G17: loop is pure arithmetic
    def knapsack_jit(capacity, wt, val):
        # G20: 1D DP to reduce objects; G1/G3: cache locals/loop bounds
        dp = [0]*(capacity+1)
        n  = len(wt)
        for i in range(n):
            wi = wt[i]; vi = val[i]
            for w in range(capacity, wi-1, -1):
                cand = vi + dp[w-wi]
                if cand > dp[w]:
                    dp[w] = cand
        return dp[capacity]
else:
    def knapsack_jit(capacity, wt, val):
        dp = [0]*(capacity+1)
        n  = len(wt)
        for i in range(n):
            wi = wt[i]; vi = val[i]
            for w in range(capacity, wi-1, -1):
                cand = vi + dp[w-wi]
                if cand > dp[w]:
                    dp[w] = cand
        return dp[capacity]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument."); sys.exit(1)
    output = sys.argv[1]

    n    = int(os.getenv("KS_N", "2000"))
    cap  = int(os.getenv("KS_CAP", "5000"))
    wmin = int(os.getenv("KS_W_MIN", "1"))
    wmax = int(os.getenv("KS_W_MAX", "15"))
    vmin = int(os.getenv("KS_V_MIN", "1"))
    vmax = int(os.getenv("KS_V_MAX", "100"))
    runs = int(os.getenv("KS_RUNS", "1"))
    seed = int(os.getenv("KS_SEED", "12345"))

    wt, val = make_random_instance(n, cap, wmin, wmax, vmin, vmax, seed)

    # Warm up JIT outside timing
    _ = knapsack_jit(cap, wt, val)

    t0 = time.perf_counter()
    for _ in range(runs):
        _best = knapsack_jit(cap, wt, val)
    dur = time.perf_counter() - t0
    with open(output, "w") as f: f.write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {output}")
