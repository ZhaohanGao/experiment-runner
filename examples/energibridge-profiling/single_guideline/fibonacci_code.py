# fib_codeopt.py
# Usage: python fib_codeopt.py /tmp/out.txt
import os, sys, time, functools
from collections.abc import Iterator
from math import sqrt

def fib_iterative_yield(n: int) -> Iterator[int]:
    if n < 0: raise ValueError("n is negative")
    a = 0; b = 1
    yield a
    for _ in range(n):
        yield b
        a, b = b, a + b

def fib_iterative(n: int) -> list[int]:
    if n < 0: raise ValueError("n is negative")
    if n == 0: return [0]
    # Preallocate (G7) instead of repeated append
    out = [0]*(n+1)
    out[0] = 0; out[1] = 1
    for i in range(2, n+1):
        out[i] = out[i-1] + out[i-2]
    return out

def fib_recursive_cached(n: int) -> list[int]:
    @functools.cache
    def f(i: int) -> int:
        if i < 2: return i
        return f(i-1)+f(i-2)
    if n < 0: raise ValueError("n is negative")
    return [f(i) for i in range(n+1)]

def fib_memoization(n: int) -> list[int]:
    if n < 0: raise ValueError("n is negative")
    cache = {0:0, 1:1, 2:1}
    def g(i:int)->int:
        v = cache.get(i)
        if v is not None: return v
        v = g(i-1)+g(i-2); cache[i]=v; return v
    return [g(i) for i in range(n+1)]

def fib_binet(n: int) -> list[int]:
    if n < 0: raise ValueError("n is negative")
    if n >= 1475: raise ValueError("n is too large")
    rt5 = sqrt(5.0)
    phi = (1.0 + rt5)/2.0
    return [round((phi**i)/rt5) for i in range(n+1)]

def fib_matrix(n: int) -> int:
    if n < 0: raise ValueError("n is negative")
    if n == 0: return 0
    # Pure-Python 2x2 integer matrices
    a,b,c,d = 1,1,1,0   # base
    ra,rb,rc,rd = 1,0,0,1   # identity
    p = n-1
    while p:
        if p & 1:
            ra,rb,rc,rd = ra*a + rb*c, ra*b + rb*d, rc*a + rd*c, rc*b + rd*d
        a,b,c,d = a*a + b*c, a*b + b*d, c*a + d*c, c*b + d*d
        p >>= 1
    return ra  # F(n)

def run_backend(backend: str, n: int):
    b = backend.lower()
    if b == "iter_yield":
        last = 0
        for v in fib_iterative_yield(n): last = v
        return last
    if b == "iter":
        return fib_iterative(n)[-1]
    if b == "recursive_cached":
        return fib_recursive_cached(n)[-1]
    if b == "memo":
        return fib_memoization(n)[-1]
    if b == "binet":
        return fib_binet(n)[-1]
    if b == "matrix":
        return fib_matrix(n)
    raise ValueError(f"Unknown backend {backend}")

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output file path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FIB_N","200000"))
    runs = int(os.getenv("FIB_RUNS","100"))
    backend = os.getenv("FIB_BACKEND","iter").lower()

    if backend == "binet" and n >= 1475:
        print("Error: FIB_BACKEND=binet requires FIB_N < 1475"); sys.exit(1)

    # Warmup (not timed)
    _ = run_backend(backend, min(n, 2000) if backend in {"memo","recursive_cached"} else min(n, 200000))

    t0 = time.perf_counter()
    for _ in range(runs):
        _last = run_backend(backend, n)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
