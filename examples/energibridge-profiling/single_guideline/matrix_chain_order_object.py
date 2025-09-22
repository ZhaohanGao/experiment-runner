# mcm_chain_oo.py
import os, sys, time, random
from typing import List, Tuple

def matrix_chain_order(array: List[int]) -> Tuple[List[List[int]], List[List[int]]]:
    n=len(array)
    if n<2:
        z=[[0]*n for _ in range(n)]; return z,[row[:] for row in z]
    if n==2:
        z=[[0]*n for _ in range(n)]; return z,[row[:] for row in z]

    INF = sys.maxsize
    nn = n*n
    dp  = [0]*nn
    sol = [0]*nn
    def idx(i,j): return i*n + j

    for i in range(n):
        for j in range(n):
            dp[idx(i,j)] = 0 if i==j else 0  # we'll set real values below
    # Initialize off-diagonal with INF
    for i in range(1,n):
        for j in range(i+1,n):
            dp[idx(i,j)] = INF

    for chain_len in range(2,n):
        for a in range(1, n - chain_len + 1):
            b = a + chain_len - 1
            best = dp[idx(a,b)]
            ai_1 = array[a-1]; ab = array[b]
            base_a = a*n
            for c in range(a, b):
                cost = dp[base_a + c] + dp[(c+1)*n + b] + ai_1 * array[c] * ab
                if cost < best:
                    best = cost; sol[idx(a,b)] = c
            dp[idx(a,b)] = best

    # to 2D lists
    matrix2 = [[dp[i*n + j] for j in range(n)] for i in range(n)]
    sol2    = [[sol[i*n + j] for j in range(n)] for i in range(n)]
    return matrix2, sol2

def reconstruct_parenthesization(sol,i,j):
    if i==j: return f"A{i}"
    k=sol[i][j]
    return f"( {reconstruct_parenthesization(sol,i,k)} {reconstruct_parenthesization(sol,k+1,j)} )"

def make_dims(n,mode,seed,dmin,dmax):
    if mode=="example": return [30,35,15,5,10,20,25]
    if n<=0: return []
    if mode=="random":
        rng=random.Random(seed); return [rng.randint(dmin,dmax) for _ in range(n)]
    return list(range(1,n+1))

if __name__=="__main__":
    if len(sys.argv)<2: print("Error: Provide output path"); sys.exit(1)
    out=sys.argv[1]
    N = int(os.getenv("MCM_N", "64000"))                    # length of dims list
    GEN = os.getenv("MCM_GEN", "example").lower()       # "example" | "range" | "random"
    MIN_DIM = int(os.getenv("MCM_MIN_DIM", "5"))
    MAX_DIM = int(os.getenv("MCM_MAX_DIM", "50"))
    SEED = int(os.getenv("MCM_SEED", "12345"))
    RUNS = int(os.getenv("MCM_RUNS", "300000"))

    dims=make_dims(N,GEN,SEED,MIN_DIM,MAX_DIM)
    _ = matrix_chain_order(dims)

    t0=time.perf_counter()
    for _ in range(RUNS):
        _ = matrix_chain_order(dims)
    dur=time.perf_counter()-t0
    with open(out,"w") as f: f.write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
