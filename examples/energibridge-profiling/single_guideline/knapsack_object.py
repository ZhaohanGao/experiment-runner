# knapsack_experiment_oo.py
import os, sys, time, random

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    rng = random.Random(seed)
    return [rng.randint(w_min, w_max) for _ in range(n)], [rng.randint(v_min, v_max) for _ in range(n)]

def knapsack_1d(capacity, wt, val):
    # G20: fewer objects — single 1D array
    dp = [0]*(capacity+1)
    n = len(wt)
    for i in range(1, n+1):
        wi = wt[i-1]; vi = val[i-1]
        # back-to-front to preserve 0-1 semantics
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

    t0 = time.perf_counter()
    for _ in range(runs):
        _best = knapsack_1d(cap, wt, val)
    dur = time.perf_counter() - t0
    open(output, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {output}")
