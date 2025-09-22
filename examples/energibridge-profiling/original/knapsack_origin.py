# knapsack_experiment_plain.py
# Usage: python knapsack_experiment_plain.py /tmp/out.txt
import os
import sys
import time
import random


def make_random_instance(n: int,
                         cap: int,
                         w_min: int = 1,
                         w_max: int = 15,
                         v_min: int = 1,
                         v_max: int = 100,
                         seed: int = 42):
    """
    Generate a random 0-1 knapsack instance with n items.
    """
    rng = random.Random(seed)
    weights = [rng.randint(w_min, w_max) for _ in range(n)]
    values = [rng.randint(v_min, v_max) for _ in range(n)]
    return weights, values


def knapsack(capacity: int, wt: list, val: list):
    """
    Standard dynamic programming solution to the 0-1 knapsack problem.
    Builds a full (n+1) x (capacity+1) DP table.
    """
    n = len(wt)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if wt[i - 1] <= w:
                dp[i][w] = max(val[i - 1] + dp[i - 1][w - wt[i - 1]], dp[i - 1][w])
            else:
                dp[i][w] = dp[i - 1][w]
    return dp[n][capacity], dp


def reconstruct_solution(dp: list, wt: list, capacity: int):
    """
    Reconstruct one optimal subset of items (1-based indices) from the DP table.
    """
    n = len(wt)
    w = capacity
    chosen = set()
    i = n
    while i > 0 and w > 0:
        if dp[i][w] != dp[i - 1][w]:
            chosen.add(i)
            w -= wt[i - 1]
        i -= 1
    return chosen


if __name__ == "__main__":
    if os.getenv("EXP_DOCTEST", "0") == "1":
        import doctest
        doctest.testmod()

    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables via environment variables
    n = 2000
    cap = 5000
    w_min = int(os.getenv("KS_W_MIN", "1"))
    w_max = int(os.getenv("KS_W_MAX", "15"))
    v_min = int(os.getenv("KS_V_MIN", "1"))
    v_max = int(os.getenv("KS_V_MAX", "100"))
    runs = int(os.getenv("KS_RUNS", "1"))
    seed = int(os.getenv("KS_SEED", "12345"))

    wt, val = make_random_instance(n, cap, w_min, w_max, v_min, v_max, seed)

    t0 = time.perf_counter()
    best_val = None
    for _ in range(runs):
        best_val, dp_table = knapsack(cap, wt, val)
        # reconstruction kept inside, but not used in timing
        _chosen = reconstruct_solution(dp_table, wt, cap)
    duration = time.perf_counter() - t0

    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")
