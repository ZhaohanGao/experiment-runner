# fib_other.py
# Usage: python fib_other.py /tmp/out.txt
import os, sys, time
import numpy as np

def matrix_pow_object(m: np.ndarray, p: int) -> np.ndarray:
    if p < 0: raise ValueError("power is negative")
    # dtype=object to hold unbounded ints
    res = np.array([[1,0],[0,1]], dtype=object)
    base = m
    while p:
        if p & 1:
            res = res.dot(base)    # bulk op (G24/G28)
        base = base.dot(base)
        p >>= 1
    return res

def fib_matrix_np_object(n: int) -> int:
    if n < 0: raise ValueError("n is negative")
    if n == 0: return 0
    m = np.array([[1,1],[1,0]], dtype=object)
    r = matrix_pow_object(m, n-1)
    return int(r[0,0])

if __name__=="__main__":
    if len(sys.argv)<2: print("Error: Provide output file path"); sys.exit(1)
    out=sys.argv[1]
    n=int(os.getenv("FIB_N","200000"))
    runs=int(os.getenv("FIB_RUNS","100"))
    backend=os.getenv("FIB_BACKEND","matrix").lower()
    if backend!="matrix":
        print("fib_other.py supports FIB_BACKEND=matrix only."); open(out,"w").write("0.0"); sys.exit(0)

    _=fib_matrix_np_object(min(n, 10000))  # warmup

    t0=time.perf_counter()
    for _ in range(runs):
        _last=fib_matrix_np_object(n)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
