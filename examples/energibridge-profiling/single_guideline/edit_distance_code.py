# edit_distance_codeopt.py
import os, sys, time, random

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    s1 = "".join(rng.choice(alphabet) for _ in range(L1))
    s2 = "".join(rng.choice(alphabet) for _ in range(L2))
    return s1, s2

def edit_distance_codeopt(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0]*(n+1) for _ in range(m+1)]
    # G7: bulk-ish init via loops, but simple
    for j in range(n+1): dp[0][j] = j
    for i in range(m+1): dp[i][0] = i

    rng_i = range(1, m+1)   # G3
    rng_j = range(1, n+1)   # G3
    for i in rng_i:
        ai = a[i-1]         # G1
        row = dp[i]
        prow = dp[i-1]
        for j in rng_j:
            if ai == b[j-1]:           # G4 short-circuit when equal
                row[j] = prow[j-1]
            else:
                ins = row[j-1] + 1
                dele = prow[j] + 1
                rep = prow[j-1] + 1
                # G1: no extra min calls beyond necessary
                row[j] = ins if ins < dele else dele
                if rep < row[j]:
                    row[j] = rep
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

    # Warmup (outside timing)
    _ = edit_distance_codeopt(s1, s2)

    t0 = time.perf_counter()
    for _ in range(runs):
        _res = edit_distance_codeopt(s1, s2)
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
