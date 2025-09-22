# lcs_native.py
import os, sys, time, random
try:
    from numba import njit
except Exception:
    njit = None

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

if njit:
    @njit(cache=True, fastmath=False)  # G15 exact; G17 no heavy calls inside loop
    def lcs_numba(x, y):
        m, n = len(x), len(y)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(1, m+1):
            xi = x[i-1]
            row, prow = dp[i], dp[i-1]
            for j in range(1, n+1):
                if xi == y[j-1]:
                    row[j] = prow[j-1] + 1
                else:
                    a, b = prow[j], row[j-1]
                    row[j] = a if a >= b else b
        return dp[m][n]
else:
    def lcs_numba(x, y):
        m, n = len(x), len(y)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(1, m+1):
            xi = x[i-1]; row, prow = dp[i], dp[i-1]
            for j in range(1, n+1):
                if xi == y[j-1]:
                    row[j] = prow[j-1] + 1
                else:
                    a, b = prow[j], row[j-1]
                    row[j] = a if a >= b else b
        return dp[m][n]

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    L1 = int(os.getenv("LCS_L1", "5000"))
    L2 = int(os.getenv("LCS_L2", "5000"))
    alphabet = os.getenv("LCS_ALPHABET", "abcdefghijklmnopqrstuvwxyz")
    runs = int(os.getenv("LCS_RUNS", "1"))
    seed = int(os.getenv("LCS_SEED", "12345"))
    s1, s2 = make_random_strings(L1, L2, alphabet, seed)

    _ = lcs_numba(s1, s2)  # JIT warmup
    t0 = time.perf_counter()
    for _ in range(runs):
        _res = lcs_numba(s1, s2)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
