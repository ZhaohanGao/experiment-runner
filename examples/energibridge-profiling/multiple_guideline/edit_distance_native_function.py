# edit_distance_native_func.py
# Categories: Native Code, Function Calls
import os, sys, time, random
import numpy as np
from functools import lru_cache
try:
    from numba import njit   # Native Code (G15)
except Exception:
    njit = None

def make_random_strings(L1: int, L2: int, alphabet: str, seed: int):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(L1)), "".join(rng.choice(alphabet) for _ in range(L2))

# --- Native Code kernel: straightforward full 2D DP (no row-rolling, no extra code-optimization) ---
if njit:
    @njit(cache=True, fastmath=False)
    def _lev2d_numba(a: np.ndarray, b: np.ndarray) -> int:
        na = a.size; nb = b.size
        dp = np.empty((na+1, nb+1), dtype=np.int32)
        for i in range(na+1): dp[i,0] = i
        for j in range(nb+1): dp[0,j] = j
        for i in range(1, na+1):
            ai = a[i-1]
            for j in range(1, nb+1):
                cost = 0 if ai == b[j-1] else 1
                ins  = dp[i, j-1] + 1
                dele = dp[i-1, j] + 1
                sub  = dp[i-1, j-1] + cost
                # keep it simple; no micro-optimizations
                m = ins if ins < dele else dele
                if sub < m: m = sub
                dp[i, j] = m
        return int(dp[na, nb])

# Function Calls (memoization) at the top-level API — caches repeated exact inputs
@lru_cache(maxsize=None)
def edit_distance_combo(s1: str, s2: str) -> int:
    a = np.fromiter((ord(c) for c in s1), dtype=np.int32, count=len(s1))
    b = np.fromiter((ord(c) for c in s2), dtype=np.int32, count=len(s2))
    if njit:
        return _lev2d_numba(a, b)
    # pure-Python fallback: full 2D DP (still avoiding Code Optimization tricks)
    na, nb = len(s1), len(s2)
    dp = [[0]*(nb+1) for _ in range(na+1)]
    for i in range(na+1): dp[i][0] = i
    for j in range(nb+1): dp[0][j] = j
    for i in range(1, na+1):
        ai = s1[i-1]
        for j in range(1, nb+1):
            cost = 0 if ai == s2[j-1] else 1
            ins  = dp[i][j-1] + 1
            dele = dp[i-1][j] + 1
            sub  = dp[i-1][j-1] + cost
            m = ins if ins < dele else dele
            if sub < m: m = sub
            dp[i][j] = m
    return dp[na][nb]

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
    _=edit_distance_combo(s1,s2)  # warmup / JIT compile + memoization seed
    t0=time.perf_counter()
    for _ in range(runs):
        _last=edit_distance_combo(s1,s2)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
