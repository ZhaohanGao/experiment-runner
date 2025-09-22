# levenshtein_native.py
# Usage: python levenshtein_native.py /tmp/out.txt
import os, sys, time, random
NUMBA_OK = True
try:
    import numpy as np
    from numba import njit
except Exception:
    NUMBA_OK = False
    np = None
    njit = None

def make_strings(m, n, seed, alphabet, mode):
    rng = random.Random(seed)
    if not alphabet: alphabet = "abcdefghijklmnopqrstuvwxyz"
    if mode == "repeat":
        return "a"*m, "b"*n
    if mode == "random":
        return ("".join(rng.choice(alphabet) for _ in range(m)),
                "".join(rng.choice(alphabet) for _ in range(n)))
    base = "".join(rng.choice(alphabet) for _ in range(max(m, n)))
    s1 = base[:m]; s2 = list(base[:n])
    edits = max(1, len(s2)//100)
    for _ in range(edits):
        if not s2: break
        j = rng.randrange(len(s2)); op = rng.choice(("sub","ins","del"))
        if op=="sub": s2[j] = rng.choice(alphabet)
        elif op=="ins": s2.insert(j, rng.choice(alphabet))
        else: del s2[j]
    return s1, "".join(s2)

if NUMBA_OK:
    @njit(cache=True, fastmath=False)
    def lev_numba(a_codes, b_codes) -> int:
        na = a_codes.size; nb = b_codes.size
        if nb == 0: return na
        prev = np.empty(nb+1, dtype=np.int64)
        for j in range(nb+1): prev[j] = j
        cur = np.empty(nb+1, dtype=np.int64)
        for i in range(1, na+1):
            cur[0] = i
            ai = a_codes[i-1]
            for j in range(1, nb+1):
                cost = 0 if ai == b_codes[j-1] else 1
                ins = prev[j] + 1
                dele = cur[j-1] + 1
                sub = prev[j-1] + cost
                # cur[j] = min(ins, dele, sub)
                if ins < dele:
                    cur[j] = ins if ins < sub else sub
                else:
                    cur[j] = dele if dele < sub else sub
            # swap
            for j in range(nb+1):
                prev[j] = cur[j]
        return prev[nb]

def levenshtein_native(s1: str, s2: str) -> int:
    if not NUMBA_OK:
        # tiny pure-Python fallback
        if len(s1) < len(s2): s1, s2 = s2, s1
        if len(s2)==0: return len(s1)
        prev = list(range(len(s2)+1))
        for i, c1 in enumerate(s1,1):
            cur = [i] + [0]*len(s2)
            for j, c2 in enumerate(s2,1):
                ins = prev[j] + 1
                dele = cur[j-1] + 1
                sub = prev[j-1] + (c1 != c2)
                cur[j] = ins if ins < dele else (dele if dele < sub else sub)
            prev = cur
        return prev[-1]
    # map to small ints for JIT
    # (simple mapping: ord values)
    a_codes = np.fromiter((ord(c) for c in s1), dtype=np.int64, count=len(s1))
    b_codes = np.fromiter((ord(c) for c in s2), dtype=np.int64, count=len(s2))
    return int(lev_numba(a_codes, b_codes))

if __name__ == "__main__":
    if len(sys.argv)<2: print("Error: Provide output path"); sys.exit(1)
    out=sys.argv[1]
    M=int(os.getenv("ED_M","5000")); N=int(os.getenv("ED_N","5000"))
    RUNS=int(os.getenv("ED_RUNS","1")); SEED=int(os.getenv("ED_SEED","12345"))
    ALPHA=os.getenv("ED_ALPHA","abcdefghijklmnopqrstuvwxyz")
    GEN=os.getenv("ED_GEN","random").lower()

    s1, s2 = make_strings(M, N, SEED, ALPHA, GEN)
    _ = levenshtein_native(s1, s2)  # JIT warmup
    t0=time.perf_counter()
    for _ in range(RUNS):
        _last = levenshtein_native(s1, s2)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
