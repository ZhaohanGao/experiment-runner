# fibonacci_native_func.py
# Categories: Native Code, Function Calls
import os, sys, time
from functools import lru_cache

try:
    from numba import njit          # Native Code (G15)
except Exception:
    njit = None

if njit:
    @njit(cache=True, fastmath=False)   # Native Code
    def _fib_iter(n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
else:
    def _fib_iter(n: int) -> int:       # Pure Python fallback
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

@lru_cache(maxsize=None)                 # Function Calls: memoization (G18)
def fib_doubling(n: int) -> int:
    # name kept for harness compatibility
    if n < 0:
        raise ValueError("n must be non-negative")
    return _fib_iter(n)

# ---------- Benchmark harness ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Provide output file path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FIB_N", "200000"))
    runs = int(os.getenv("FIB_RUNS", "100"))
    _ = fib_doubling(min(n, 200000))   # warm-up
    t0 = time.perf_counter()
    for _ in range(runs):
        _last = fib_doubling(n)
    dur = time.perf_counter() - t0
    open(out, "w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
