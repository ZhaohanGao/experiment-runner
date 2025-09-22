# knapsack_experiment_funcalls.py
import os, sys, time, random

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    rng = random.Random(seed)
    return [rng.randint(w_min, w_max) for _ in range(n)], [rng.randint(v_min, v_max) for _ in range(n)]

def knapsack_inline(capacity, wt, val):
    # Inline everything; avoid helper calls in the hot loop (G19)
    n = len(wt)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    rng_n = range(1, n+1)
    rng_c = range(1, capacity+1)
    for i in rng_n:
        wi = wt[i-1]; vi = val[i-1]
        prev = dp[i-1]; cur = dp[i]
        for w in rng_c:
            best = prev[w]
            if wi <= w:
                cand = vi + prev[w-wi]
                if cand > best: best = cand
            cur[w] = best
    return dp[n][capacity]

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
        _best = knapsack_inline(cap, wt, val)
    dur = time.perf_counter() - t0
    open(output, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {output}")
