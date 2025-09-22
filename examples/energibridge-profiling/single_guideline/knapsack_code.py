# knapsack_experiment_codeopt.py
import os, sys, time, random

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    rng = random.Random(seed)
    # G7: generate in batches via list comprehensions
    weights = [rng.randint(w_min, w_max) for _ in range(n)]
    values  = [rng.randint(v_min, v_max) for _ in range(n)]
    return weights, values

def knapsack(capacity, wt, val):
    n = len(wt)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    rng_n = range(1, n+1)            # G3: store loop ranges once
    rng_c = range(1, capacity+1)
    for i in rng_n:
        wi = wt[i-1]                 # G1: cache hot reads
        vi = val[i-1]
        prev = dp[i-1]
        cur  = dp[i]
        for w in rng_c:
            best = prev[w]
            # G4: short-circuit guard
            if wi <= w:
                cand = vi + prev[w-wi]
                if cand > best:
                    best = cand
            cur[w] = best
    return dp[n][capacity], dp

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument."); sys.exit(1)
    output = sys.argv[1]

    # Tunables (keep same knobs)
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
        best, dp = knapsack(cap, wt, val)
    dur = time.perf_counter() - t0
    open(output, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {output}")
