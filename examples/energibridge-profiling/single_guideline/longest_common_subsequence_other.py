# lcs_other.py (fixed)
import os, sys, time, random
import numpy as np

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

def lcs_numpy(x: str, y: str) -> int:
    m, n = len(x), len(y)
    # 2 rolling rows in int32 to save memory
    prev = np.zeros(n + 1, dtype=np.int32)
    cur  = np.zeros(n + 1, dtype=np.int32)

    # represent y as a uint8 array for fast per-char compare
    y_arr = np.frombuffer(y.encode("utf-8"), dtype=np.uint8)

    for i in range(1, m + 1):
        xi = ord(x[i - 1])
        match = (y_arr == xi).astype(np.int32)            # shape: (n,)
        # base[j] = max(prev[j], prev[j-1] + match[j]) for j=1..n
        base = np.maximum(prev[1:], prev[:-1] + match)     # shape: (n,)
        # fold in left dependency via cumulative max:
        cur[1:] = np.maximum.accumulate(base)              # shape: (n,)
        # swap rows
        prev, cur = cur, prev

    return int(prev[n])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]

    L1 = int(os.getenv("LCS_L1", "5000"))
    L2 = int(os.getenv("LCS_L2", "5000"))
    alphabet = os.getenv("LCS_ALPHABET", "abcdefghijklmnopqrstuvwxyz")
    runs = int(os.getenv("LCS_RUNS", "1"))
    seed = int(os.getenv("LCS_SEED", "12345"))

    s1, s2 = make_random_strings(L1, L2, alphabet, seed)

    # Warmup
    _ = lcs_numpy(s1, s2)

    t0 = time.perf_counter()
    for _ in range(runs):
        _res = lcs_numpy(s1, s2)
    dur = time.perf_counter() - t0

    with open(out, "w") as f:
        f.write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
