# edit_distance_oo.py
import os, sys, time, random

def make_random_strings(L1, L2, alphabet, seed):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

def edit_distance_rolling(a: str, b: str) -> int:
    m, n = len(a), len(b)
    prev = list(range(n+1))    # dp for row i-1
    cur  = [0]*(n+1)           # dp for row i
    for i in range(1, m+1):
        cur[0] = i
        ai = a[i-1]
        for j in range(1, n+1):
            if ai == b[j-1]:
                cur[j] = prev[j-1]
            else:
                ins = cur[j-1] + 1
                dele = prev[j] + 1
                rep = prev[j-1] + 1
                best = ins if ins < dele else dele
                if rep < best: best = rep
                cur[j] = best
        prev, cur = cur, prev  # swap buffers
    return prev[n]

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

    t0 = time.perf_counter()
    for _ in range(runs):
        _res = edit_distance_rolling(s1, s2)
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
