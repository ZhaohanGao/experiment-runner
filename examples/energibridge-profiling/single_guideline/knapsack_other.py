# knapsack_experiment_other.py
import os, sys, time, random
import numpy as np

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    rng = random.Random(seed)
    weights = [rng.randint(w_min, w_max) for _ in range(n)]
    values  = [rng.randint(v_min, v_max) for _ in range(n)]
    return weights, values

def knapsack_numpy(capacity, wt, val):
    # G24+G28: vectorized 1D DP with slices
    dp = np.zeros(capacity+1, dtype=np.int64)
    for wi, vi in zip(wt, val):
        if wi <= capacity:
            # dp[w:] = max(dp[w:], dp[:-w] + v)
            dp[wi:] = np.maximum(dp[wi:], dp[:-wi] + vi)
    return int(dp[capacity])

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
        _best = knapsack_numpy(cap, wt, val)
    dur = time.perf_counter() - t0
    with open(output, "w") as f: f.write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {output}")
