# edit_distance_experiment.py
# Usage: python edit_distance_experiment.py /tmp/out.txt
import os
import sys
import time
import random


class EditDistance:
    """
    Provides top-down (memoized) and bottom-up edit distance.
    """

    def __init__(self):
        self.word1 = ""
        self.word2 = ""
        self.dp = []

    # --- Top-down (memoized) ---
    def __min_dist_top_down_dp(self, m: int, n: int) -> int:
        if m == -1:
            return n + 1
        elif n == -1:
            return m + 1
        elif self.dp[m][n] > -1:
            return self.dp[m][n]
        else:
            if self.word1[m] == self.word2[n]:
                self.dp[m][n] = self.__min_dist_top_down_dp(m - 1, n - 1)
            else:
                insert = self.__min_dist_top_down_dp(m, n - 1)
                delete = self.__min_dist_top_down_dp(m - 1, n)
                replace = self.__min_dist_top_down_dp(m - 1, n - 1)
                self.dp[m][n] = 1 + min(insert, delete, replace)
            return self.dp[m][n]

    def min_dist_top_down(self, word1: str, word2: str) -> int:
        self.word1 = word1
        self.word2 = word2
        # dp sized to characters (not including base -1 row/col)
        self.dp = [[-1 for _ in range(len(word2))] for _ in range(len(word1))]
        return self.__min_dist_top_down_dp(len(word1) - 1, len(word2) - 1)

    # --- Bottom-up ---
    def min_dist_bottom_up(self, word1: str, word2: str) -> int:
        self.word1 = word1
        self.word2 = word2
        m = len(word1)
        n = len(word2)
        self.dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:  # first string empty
                    self.dp[i][j] = j
                elif j == 0:  # second string empty
                    self.dp[i][j] = i
                elif word1[i - 1] == word2[j - 1]:
                    self.dp[i][j] = self.dp[i - 1][j - 1]
                else:
                    insert = self.dp[i][j - 1]
                    delete = self.dp[i - 1][j]
                    replace = self.dp[i - 1][j - 1]
                    self.dp[i][j] = 1 + min(insert, delete, replace)
        return self.dp[m][n]


def _make_random_strings(L1: int, L2: int, alphabet: str, seed: int):
    rng = random.Random(seed)
    s1 = "".join(rng.choice(alphabet) for _ in range(L1))
    s2 = "".join(rng.choice(alphabet) for _ in range(L2))
    return s1, s2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables via environment variables (same pattern as your other experiments)
    L1 = int(os.getenv("ED_L1", "3000"))
    L2 = int(os.getenv("ED_L2", "3000"))
    alphabet = os.getenv("ED_ALPHABET", "abcdefghijklmnopqrstuvwxyz")
    runs = int(os.getenv("ED_RUNS", "1"))
    seed = int(os.getenv("ED_SEED", "12345"))
    backend = os.getenv("ED_BACKEND", "bottomup").lower()  # "bottomup" | "topdown"

    s1, s2 = _make_random_strings(L1, L2, alphabet, seed)

    solver = EditDistance()

    # Warmup once outside timing (ensures fair timing if interpreter does any caching)
    if backend == "topdown":
        _ = solver.min_dist_top_down(s1, s2)
    else:
        _ = solver.min_dist_bottom_up(s1, s2)

    t0 = time.perf_counter()
    for _ in range(runs):
        if backend == "topdown":
            _res = solver.min_dist_top_down(s1, s2)
        else:
            _res = solver.min_dist_bottom_up(s1, s2)
    duration = time.perf_counter() - t0

    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")
