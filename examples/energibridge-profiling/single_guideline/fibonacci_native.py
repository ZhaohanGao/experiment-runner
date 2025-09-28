# fib_native.py
# Usage: python fib_native.py /tmp/out.txt
import os, sys, time

try:
    import gmpy2
    HAVE_GMPY2 = True
except Exception:
    HAVE_GMPY2 = False

def fib_doubling_py(n: int) -> int:
    if n < 0: raise ValueError("n is negative")
    if n == 0: return 0
    # returns (F(n), F(n+1))
    def fd(k: int):
        if k == 0: return (0,1)
        a,b = fd(k>>1)
        c = a * ( (b << 1) - a )
        d = a*a + b*b
        if k & 1:
            return (d, c + d)
        else:
            return (c, d)
    return fd(n)[0]

def fib_doubling_gmpy2(n: int) -> int:
    if n < 0: raise ValueError("n is negative")
    if n == 0: return 0
    def fd(k):
        if k == 0: return (gmpy2.mpz(0), gmpy2.mpz(1))
        a,b = fd(k>>1)
        c = a * ((b<<1) - a)
        d = a*a + b*b
        return ( (d, c+d) if (k & 1) else (c, d) )
    return int(fd(n)[0])

def run_backend(backend: str, n: int):
    b = backend.lower()
    if b == "doubling":
        if HAVE_GMPY2:
            return fib_doubling_gmpy2(n)
        else:
            return fib_doubling_py(n)
    elif b == "matrix":
        # tiny integer-only matrix power
        if n < 0: raise ValueError("n is negative")
        if n == 0: return 0
        a,b,c,d = 1,1,1,0
        ra,rb,rc,rd = 1,0,0,1
        p = n-1
        while p:
            if p & 1:
                ra,rb,rc,rd = ra*a + rb*c, ra*b + rb*d, rc*a + rd*c, rc*b + rd*d
            a,b,c,d = a*a + b*c, a*b + b*d, c*a + d*c, c*b + d*d
            p >>= 1
        return ra
    else:
        raise ValueError("Use FIB_BACKEND=doubling or matrix for fib_native.py")

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Error: Provide output path"); sys.exit(1)
    out = sys.argv[1]
    n = int(os.getenv("FIB_N","200000"))
    runs = int(os.getenv("FIB_RUNS","100"))
    backend = os.getenv("FIB_BACKEND","doubling")

    # Warmup
    _ = run_backend(backend, min(n, 200000))

    t0 = time.perf_counter()
    for _ in range(runs):
        _last = run_backend(backend, n)
    dur = time.perf_counter() - t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
