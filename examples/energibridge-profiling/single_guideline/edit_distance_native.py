# edit_distance_native.py
import os, sys, time, random
try:
    from numba import njit
except Exception:
    njit = None

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

if njit:
    @njit(cache=True, fastmath=False)  # G15/G17
    def edit_distance_numba(a, b):
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for j in range(n+1): dp[0][j] = j
        for i in range(m+1): dp[i][0] = i
        for i in range(1, m+1):
            ai = a[i-1]
            row = dp[i]
            prow = dp[i-1]
            for j in range(1, n+1):
                if ai == b[j-1]:
                    row[j] = prow[j-1]
                else:
                    ins = row[j-1] + 1
                    dele = prow[j] + 1
                    rep = prow[j-1] + 1
                    # manual min
                    best = ins if ins < dele else dele
                    if rep < best: best = rep
                    row[j] = best
        return dp[m][n]
else:
    def edit_distance_numba(a, b):
        # Plain Python fallback
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for j in range(n+1): dp[0][j] = j
        for i in range(m+1): dp[i][0] = i
        for i in range(1, m+1):
            ai = a[i-1]; row = dp[i]; prow = dp[i-1]
            for j in range(1, n+1):
                if ai == b[j-1]:
                    row[j] = prow[j-1]
                else:
                    ins = row[j-1] + 1; dele = prow[j] + 1; rep = prow[j-1] + 1
                    best = ins if ins < dele else dele
                    if rep < best: best = rep
                    row[j] = best
        return dp[m][n]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument."); sys.exit(1)
    out = sys.argv[1]
    L1 = int(os.getenv("ED_L1", "3000"))
    L2 = int(os.getenv("ED_L2", "3000"))
    alphabet = os.getenv("ED_ALPHABET", "abcdefghijklmnopqrstuvwxyz")
    runs = int(os.getenv("ED_RUNS", "1"))
    seed = int(os.getenv("ED_SEED", "12345"))

    s1, s2 = make_random_strings(L1, L2, alphabet, seed)

    _ = edit_distance_numba(s1, s2)  # JIT warmup

    t0 = time.perf_counter()
    for _ in range(runs):
        _res = edit_distance_numba(s1, s2)
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
