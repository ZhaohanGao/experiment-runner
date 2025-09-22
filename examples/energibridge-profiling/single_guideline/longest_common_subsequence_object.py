# lcs_oo.py
import os, sys, time, random

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

def lcs_rolling(x, y):
    # ensure y is shorter to minimize memory
    if len(y) > len(x):
        x, y = y, x
    m, n = len(x), len(y)
    prev = [0]*(n+1)
    cur  = [0]*(n+1)
    for i in range(1, m+1):
        xi = x[i-1]
        for j in range(1, n+1):
            if xi == y[j-1]:
                cur[j] = prev[j-1] + 1
            else:
                a, b = prev[j], cur[j-1]
                cur[j] = a if a >= b else b
        prev, cur = cur, prev
    return prev[n]

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    L1 = int(os.getenv("LCS_L1", "5000"))
    L2 = int(os.getenv("LCS_L2", "5000"))
    alphabet = os.getenv("LCS_ALPHABET", "abcdefghijklmnopqrstuvwxyz")
    runs = int(os.getenv("LCS_RUNS", "1"))
    seed = int(os.getenv("LCS_SEED", "12345"))
    s1, s2 = make_random_strings(L1, L2, alphabet, seed)

    t0 = time.perf_counter()
    for _ in range(runs):
        _res = lcs_rolling(s1, s2)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
