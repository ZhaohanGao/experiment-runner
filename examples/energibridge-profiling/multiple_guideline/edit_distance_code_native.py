# edit_distance_co_native.py
# Categories: Code Optimization, Native Code
import os, sys, time, random
import numpy as np
try:
    from numba import njit   # Native Code (G15)
except Exception:
    njit = None

def make_random_strings(L1: int, L2: int, alphabet: str, seed: int):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

# --- Code Optimization: row-rolling DP. Native path via Numba on int32 arrays ---
if njit:
    @njit(cache=True, fastmath=False)
    def _lev_rows_numba(a: np.ndarray, b: np.ndarray) -> int:
        na = a.size; nb = b.size
        if nb == 0: return na
        prev = np.empty(nb+1, dtype=np.int32)
        cur  = np.empty(nb+1, dtype=np.int32)
        for j in range(nb+1): prev[j] = j
        for i in range(1, na+1):
            cur[0] = i
            ai = a[i-1]
            for j in range(1, nb+1):
                cost = 0 if ai == b[j-1] else 1
                ins  = prev[j] + 1
                dele = cur[j-1] + 1
                sub  = prev[j-1] + cost
                # manual ternary min; no function-calls category tricks
                if ins < dele:
                    cur[j] = ins if ins < sub else sub
                else:
                    cur[j] = dele if dele < sub else sub
            for j in range(nb+1):
                prev[j] = cur[j]
        return int(prev[nb])

def edit_distance_combo(s1: str, s2: str) -> int:
    # convert to int32 arrays once for JIT kernel
    a = np.fromiter((ord(c) for c in s1), dtype=np.int32, count=len(s1))
    b = np.fromiter((ord(c) for c in s2), dtype=np.int32, count=len(s2))
    if njit:
        return _lev_rows_numba(a, b)
    # pure-Python fallback (still Code Optimization: row-rolling)
    na, nb = len(s1), len(s2)
    if nb == 0: return na
    prev = list(range(nb+1))
    cur  = [0]*(nb+1)
    for i in range(1, na+1):
        cur[0] = i
        ai = s1[i-1]
        for j in range(1, nb+1):
            cost = 0 if ai == s2[j-1] else 1
            ins  = prev[j] + 1
            dele = cur[j-1] + 1
            sub  = prev[j-1] + cost
            cur[j] = ins if ins < dele else dele
            if sub < cur[j]: cur[j] = sub
        prev, cur = cur, prev
    return prev[nb]

# --- Benchmark harness (keep as requested) ---
if __name__=="__main__":
    if len(sys.argv)<2: print("Error: Provide output file path"); sys.exit(1)
    out=sys.argv[1]
    L1=int(os.getenv("ED_L1","3000"))
    L2=int(os.getenv("ED_L2","3000"))
    alphabet=os.getenv("ED_ALPHABET","abcdefghijklmnopqrstuvwxyz")
    runs=int(os.getenv("ED_RUNS","1"))
    seed=int(os.getenv("ED_SEED","12345"))
    s1,s2=make_random_strings(L1,L2,alphabet,seed)
    _=edit_distance_combo(s1,s2)  # warmup / JIT compile
    t0=time.perf_counter()
    for _ in range(runs):
        _last=edit_distance_combo(s1,s2)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
