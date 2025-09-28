# Guideline used: Code Optimization (G6, G28) • Native Code (G15, G17) • Function Calls (G19)

import os, sys, time
try:
    import gmpy2
    HAVE_GMPY2=True
except Exception:
    HAVE_GMPY2=False

def fib_doubling(n:int)->int:
    if n<0: raise ValueError("n is negative")
    if n==0: return 0
    if HAVE_GMPY2:
        mpz=gmpy2.mpz
        def fd(k):
            if k==0: return (mpz(0), mpz(1))
            a,b=fd(k>>1)
            c=a*((b<<1)-a)
            d=a*a + b*b
            return ( (d, c+d) if (k & 1) else (c, d) )
        return int(fd(n)[0])
    else:
        def fd(k):
            if k==0: return (0,1)
            a,b=fd(k>>1)
            c=a*((b<<1)-a)
            d=a*a + b*b
            return ( (d, c+d) if (k & 1) else (c, d) )
        return fd(n)[0]

if __name__=="__main__":
    if len(sys.argv)<2: print("Error: Provide output file path"); sys.exit(1)
    out=sys.argv[1]
    n=int(os.getenv("FIB_N","200000"))
    runs=int(os.getenv("FIB_RUNS","100"))
    _=fib_doubling(min(n,200000))  # warmup
    t0=time.perf_counter()
    for _ in range(runs):
        _last=fib_doubling(n)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
