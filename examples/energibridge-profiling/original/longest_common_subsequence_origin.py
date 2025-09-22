# lcs_experiment.py
# Usage: python lcs_experiment.py /tmp/out.txt
import os
import sys
import time
import random
from typing import Tuple, List


def make_random_strings(L1: int, L2: int, alphabet: str, seed: int) -> Tuple[str, str]:
    rng = random.Random(seed)
    s1 = "".join(rng.choice(alphabet) for _ in range(L1))
    s2 = "".join(rng.choice(alphabet) for _ in range(L2))
    return s1, s2


# ---------------------------
# Baseline 2D DP (length + optional reconstruction)
# ---------------------------
def lcs_2d(x: str, y: str) -> Tuple[int, List[List[int]]]:
    m, n = len(x), len(y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # classic fill
    for i in range(1, m + 1):
        xi = x[i - 1]
        row = dp[i]
        row_prev = dp[i - 1]
        for j in range(1, n + 1):
            if xi == y[j - 1]:
                row[j] = row_prev[j - 1] + 1
            else:
                # manual max avoids function call overhead
                a = row_prev[j]
                b = row[j - 1]
                row[j] = a if a >= b else b
    return dp[m][n], dp


def reconstruct_lcs(dp: List[List[int]], x: str, y: str) -> str:
    """Reconstruct one LCS from a filled 2D dp table (not timed)."""
    m, n = len(x), len(y)
    i, j = m, n
    out_chars = []
    while i > 0 and j > 0:
        if x[i - 1] == y[j - 1]:
            out_chars.append(x[i - 1])
            i -= 1
            j -= 1
        else:
            if dp[i - 1][j] >= dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
    return "".join(reversed(out_chars))


# ---------------------------
# 1D rolling rows (length only)
# ---------------------------
def lcs_1d(x: str, y: str) -> int:
    """
    Space-optimized LCS: O(min(m,n)) space, O(m*n) time.
    Computes length only (no reconstruction).
    """
    # Make y the shorter string to reduce memory
    if len(y) > len(x):
        x, y = y, x  # swap so len(y) <= len(x)
    m, n = len(x), len(y)
    prev = [0] * (n + 1)
    cur = [0] * (n + 1)
    for i in range(1, m + 1):
        xi = x[i - 1]
        for j in range(1, n + 1):
            if xi == y[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                # max(prev[j], cur[j-1])
                a = prev[j]
                b = cur[j - 1]
                cur[j] = a if a >= b else b
        prev, cur = cur, prev
    return prev[n]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables (env)
    L1 = int(os.getenv("LCS_L1", "5000"))
    L2 = int(os.getenv("LCS_L2", "5000"))
    alphabet = os.getenv("LCS_ALPHABET", "abcdefghijklmnopqrstuvwxyz")
    runs = int(os.getenv("LCS_RUNS", "1"))
    seed = int(os.getenv("LCS_SEED", "12345"))
    backend = os.getenv("LCS_BACKEND", "2d").lower()   # "2d" | "1d"
    recon = int(os.getenv("LCS_RECON", "0"))            # 0 | 1 (only meaningful for 2d)

    # Instance
    s1, s2 = make_random_strings(L1, L2, alphabet, seed)

    # Warmup once (outside timing) for fair JIT/interpreter effects
    if backend == "1d":
        _ = lcs_1d(s1, s2)
    else:
        _len, _dp = lcs_2d(s1, s2)

    # Timed section
    t0 = time.perf_counter()
    last_len = None
    last_dp = None
    for _ in range(runs):
        if backend == "1d":
            last_len = lcs_1d(s1, s2)
            last_dp = None
        else:
            last_len, last_dp = lcs_2d(s1, s2)
    duration = time.perf_counter() - t0

    # Optional reconstruction (kept OUTSIDE timing)
    if backend == "2d" and recon and last_dp is not None:
        seq = reconstruct_lcs(last_dp, s1, s2)
        # You can print or assert here if you want validation:
        # print(f"LCS length={last_len}, seq_sample='{seq[:50]}'")

    # Persist duration
    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")
