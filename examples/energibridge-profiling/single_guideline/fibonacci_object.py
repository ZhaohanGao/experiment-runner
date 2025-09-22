# fib_oo.py
# Usage: python fib_oo.py /tmp/out.txt
import os, sys, time

def fib_iter_list(n: int) -> int:
    if n < 0: raise ValueError("n is negative")
    if n == 0: return 0
    out = [0]*(n+1)         # preallocate
    out[0]=0; out[1]=1
    for i in range(2, n+1):
        out[i] = out[i-1] + out[i-2]
    return out[-1]

def fib_iter_nth(n: int) -> int:
    if n < 0: raise ValueError("n is negative")
    a = 0; b = 1
    for _ in range(n):
        a, b = b, a + b
    return a

def run_backend(backend: str, n: int):
    b=backend.lower()
    if b == "iter":      return fib_iter_list(n)  # sequence (object-heavy)
    if b == "iter_nth":  return fib_iter_nth(n)   # object-light
    raise ValueError("Use FIB_BACKEND=iter or iter_nth for fib_oo.py")

if __name__=="__main__":
    if len(sys.argv)<2: print("Error: Provide output file path"); sys.exit(1)
    out=sys.argv[1]
    n=int(os.getenv("FIB_N","200000"))
    runs=int(os.getenv("FIB_RUNS","3"))
    backend=os.getenv("FIB_BACKEND","iter_nth")
    _=run_backend(backend, min(n,50000))
    t0=time.perf_counter()
    for _ in range(runs):
        _last=run_backend(backend, n)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
