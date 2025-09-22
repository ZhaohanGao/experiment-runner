# edit_distance_other.py
import os, sys, time, random
import numpy as np

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

def edit_distance_numpy(a: str, b: str) -> int:
    m, n = len(a), len(b)
    # dp has shape (m+1, n+1)
    dp = np.empty((m+1, n+1), dtype=np.int32)
    dp[0, :] = np.arange(n+1, dtype=np.int32)
    dp[:, 0] = np.arange(m+1, dtype=np.int32)

    b_arr = np.frombuffer(b.encode('utf-8'), dtype=np.uint8)  # lightweight char array
    for i in range(1, m+1):
        ai = ord(a[i-1])
        # cost vector: 0 where equal, 1 otherwise
        cost = (b_arr != ai).astype(np.int32)

        # Three candidates (vectorized over j=1..n)
        ins  = dp[i, :-1] + 1         # insertion: dp[i][j-1] + 1
        dele = dp[i-1, 1:] + 1        # deletion : dp[i-1][j] + 1
        rep  = dp[i-1, :-1] + cost    # replace  : dp[i-1][j-1] + cost

        dp[i, 1:] = np.minimum(np.minimum(ins, dele), rep)

    return int(dp[m, n])

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

    # Warmup
    _ = edit_distance_numpy(s1, s2)

    t0 = time.perf_counter()
    for _ in range(runs):
        _res = edit_distance_numpy(s1, s2)
    dur = time.perf_counter() - t0
    with open(out, "w") as f: f.write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
