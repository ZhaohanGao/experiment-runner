# fibonacci_co_native.py
# Categories: Code Optimization, Native Code
import os, sys, time
from typing import Tuple
try:
    from numba import njit  # Native Code (G15)
except Exception:
    njit = None

# ---------- Fibonacci ----------
def _fib_pair_py(n: int) -> Tuple[int, int]:
    # Fast-doubling (Code Optimization)
    if n == 0:
        return (0, 1)
    a, b = _fib_pair_py(n >> 1)
    c = a * (2*b - a)
    d = a*a + b*b
    return (d, c + d) if (n & 1) else (c, d)

if njit:
    @njit(cache=True, fastmath=False)  # Native Code
    def _fib_pair_jit(n: int) -> Tuple[int, int]:
        if n == 0:
            return (0, 1)
        a, b = _fib_pair_jit(n >> 1)
        c = a * (2*b - a)
        d = a*a + b*b
        return (d, c + d) if (n & 1) else (c, d)

def fib_doubling(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if njit:
        return _fib_pair_jit(n)[0]
    return _fib_pair_py(n)[0]

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
