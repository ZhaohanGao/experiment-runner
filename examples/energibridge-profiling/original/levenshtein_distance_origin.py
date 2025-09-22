# levenshtein_experiment.py
# Usage: python levenshtein_experiment.py /tmp/out.txt
import os
import sys
import time
from collections.abc import Callable
from typing import Tuple
import random


# -----------------------------
# Original algorithms (unaltered)
# -----------------------------
def levenshtein_distance(first_word: str, second_word: str) -> int:
    """
    Classic row-rolling Levenshtein distance (insert/delete/substitute, unit costs).
    """
    # Ensure the longer word comes first to minimize memory
    if len(first_word) < len(second_word):
        return levenshtein_distance(second_word, first_word)

    if len(second_word) == 0:
        return len(first_word)

    previous_row = list(range(len(second_word) + 1))

    for i, c1 in enumerate(first_word):
        current_row = [i + 1]
        for j, c2 in enumerate(second_word):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def levenshtein_distance_optimized(first_word: str, second_word: str) -> int:
    """
    Same DP but writes into a pre-sized current_row for each i.
    """
    if len(first_word) < len(second_word):
        return levenshtein_distance_optimized(second_word, first_word)

    if len(second_word) == 0:
        return len(first_word)

    previous_row = list(range(len(second_word) + 1))

    for i, c1 in enumerate(first_word):
        current_row = [i + 1] + [0] * len(second_word)
        for j, c2 in enumerate(second_word):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row[j + 1] = min(insertions, deletions, substitutions)
        previous_row = current_row

    return previous_row[-1]


# -----------------------------
# Experiment harness
# -----------------------------
def make_strings(m: int, n: int, seed: int, alphabet: str, mode: str) -> Tuple[str, str]:
    """
    Build two strings according to mode.
      - random: fully random s1 (len m) and s2 (len n)
      - similar: s2 starts as s1[0:n], then apply ~1% random edits
      - repeat: s1 = 'a'*m, s2 = 'b'*n
    """
    rng = random.Random(seed)
    if not alphabet:
        alphabet = "abcdefghijklmnopqrstuvwxyz"

    if mode == "repeat":
        return ("a" * m, "b" * n)

    if mode == "random":
        s1 = "".join(rng.choice(alphabet) for _ in range(m))
        s2 = "".join(rng.choice(alphabet) for _ in range(n))
        return s1, s2

    # "similar": start close, then perturb s2 slightly
    base = "".join(rng.choice(alphabet) for _ in range(max(m, n)))
    s1 = base[:m]
    s2 = list(base[:n])

    # ~1% edits on s2
    edits = max(1, n // 100)
    for _ in range(edits):
        if n == 0:
            break
        j = rng.randrange(n)
        op = rng.choice(("sub", "ins", "del"))
        if op == "sub":
            s2[j] = rng.choice(alphabet)
        elif op == "ins":
            s2.insert(j, rng.choice(alphabet))
            n += 1
        else:  # del
            del s2[j]
            n -= 1
            if n == 0:
                break
    return s1, "".join(s2)


def run_backend(backend: str, s1: str, s2: str) -> int:
    b = backend.lower()
    if b == "classic":
        return levenshtein_distance(s1, s2)
    if b == "optimized":
        return levenshtein_distance_optimized(s1, s2)
    raise ValueError(f"Unknown ED_BACKEND: {backend!r}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables via environment variables
    M = int(os.getenv("ED_M", "5000"))
    N = int(os.getenv("ED_N", "5000"))
    RUNS = int(os.getenv("ED_RUNS", "1"))
    SEED = int(os.getenv("ED_SEED", "12345"))
    ALPHA = os.getenv("ED_ALPHA", "abcdefghijklmnopqrstuvwxyz")
    BACKEND = os.getenv("ED_BACKEND", "optimized")  # "classic" | "optimized"
    GEN = os.getenv("ED_GEN", "random").lower()     # "random" | "similar" | "repeat"

    # Generate inputs
    s1, s2 = make_strings(M, N, SEED, ALPHA, GEN)

    # Warmup (stabilize measurements)
    _ = run_backend(BACKEND, s1, s2)

    # Timed section
    t0 = time.perf_counter()
    last = None
    for _ in range(RUNS):
        last = run_backend(BACKEND, s1, s2)
    duration = time.perf_counter() - t0

    # Persist duration
    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.6f}s. Result saved to {output_file_path}")
