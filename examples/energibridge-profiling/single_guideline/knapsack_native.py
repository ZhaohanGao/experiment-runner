# knapsack_experiment_native.py
import os, sys, time, random
try:
    from numba import njit
except Exception:
    njit = None

def make_random_instance(n, cap, w_min=1, w_max=15, v_min=1, v_max=100, seed=42):
    rng = random.Random(seed)
    weights = [rng.randint(w_min, w_max) for _ in range(n)]
    values  = [rng.randint(v_min, v_max) for _ in range(n)]
    return weights, values

if njit:
    @njit(cache=True, fastmath=False)  # G15; G17: no heavy library calls in loop
    def knapsack_numba(capacity, wt, val):
        n = len(wt)
        dp_prev = [0]*(capacity+1)
        dp_cur  = [0]*(capacity+1)
        for i in range(1, n+1):
            wi = wt[i-1]
            vi = val[i-1]
            for w in range(1, capacity+1):
                best = dp_prev[w]
                if wi <= w:
                    cand = vi + dp_prev[w-wi]
                    if cand > best:
                        best = cand
                dp_cur[w] = best
            dp_prev, dp_cur = dp_cur, dp_prev
        return dp_prev[capacity]
else:
    def knapsack_numba(capacity, wt, val):
        # Fallback: plain Python (kept minimal)
        n = len(wt)
        dp_prev = [0]*(capacity+1)
        dp_cur  = [0]*(capacity+1)
        for i in range(1, n+1):
            wi = wt[i-1]; vi = val[i-1]
            for w in range(1, capacity+1):
                best = dp_prev[w]
                if wi <= w:
                    cand = vi + dp_prev[w-wi]
                    if cand > best: best = cand
                dp_cur[w] = best
            dp_prev, dp_cur = dp_cur, dp_prev
        return dp_prev[capacity]

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

    # JIT warmup (outside timing)
    _ = knapsack_numba(cap, wt, val)

    t0 = time.perf_counter()
    for _ in range(runs):
        _best = knapsack_numba(cap, wt, val)
    dur = time.perf_counter() - t0
    open(output, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {output}")
