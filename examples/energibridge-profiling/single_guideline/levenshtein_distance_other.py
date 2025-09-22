# levenshtein_other.py
# Usage: python levenshtein_other.py /tmp/out.txt
import os, sys, time, random
import numpy as np

def make_strings(m,n,seed,alphabet,mode):
    rng=random.Random(seed)
    if not alphabet: alphabet="abcdefghijklmnopqrstuvwxyz"
    if mode=="repeat": return "a"*m,"b"*n
    if mode=="random":
        return ("".join(rng.choice(alphabet) for _ in range(m)),
                "".join(rng.choice(alphabet) for _ in range(n)))
    base="".join(rng.choice(alphabet) for _ in range(max(m,n)))
    s1=base[:m]; s2=list(base[:n])
    edits=max(1,len(s2)//100)
    for _ in range(edits):
        if not s2: break
        j=rng.randrange(len(s2)); op=rng.choice(("sub","ins","del"))
        if op=="sub": s2[j]=rng.choice(alphabet)
        elif op=="ins": s2.insert(j,rng.choice(alphabet))
        else: del s2[j]
    return s1,"".join(s2)

def levenshtein_numpy(a: str, b: str) -> int:
    if len(a)<len(b): a,b=b,a
    nb=len(b)
    if nb==0: return len(a)
    prev = np.arange(nb+1, dtype=np.int64)
    # Pre-encode b for vectorized comparison
    b_arr = np.frombuffer(b.encode('latin1','ignore'), dtype=np.uint8)
    for i, ca in enumerate(a,1):
        cur = np.empty(nb+1, dtype=np.int64)
        cur[0] = i
        ai = ord(ca) & 0xFF
        # cost vector: 0 when equal, 1 otherwise
        cost = (b_arr != ai).astype(np.int64)
        # Three candidates: insertion, deletion, substitution
        ins = prev[1:] + 1
        dele = cur[:-1] + 1
        sub = prev[:-1] + cost
        cur[1:] = np.minimum.reduce([ins, dele, sub])
        prev = cur
    return int(prev[-1])

if __name__=="__main__":
    if len(sys.argv)<2: print("Error: Provide output path"); sys.exit(1)
    out=sys.argv[1]
    M=int(os.getenv("ED_M","5000")); N=int(os.getenv("ED_N","5000"))
    RUNS=int(os.getenv("ED_RUNS","1")); SEED=int(os.getenv("ED_SEED","12345"))
    ALPHA=os.getenv("ED_ALPHA","abcdefghijklmnopqrstuvwxyz")
    GEN=os.getenv("ED_GEN","random").lower()

    s1,s2=make_strings(M,N,SEED,ALPHA,GEN)
    _=levenshtein_numpy(s1,s2)  # warmup
    t0=time.perf_counter()
    for _ in range(RUNS):
        _last=levenshtein_numpy(s1,s2)
    dur=time.perf_counter()-t0
    open(out,"w").write(str(dur))
    print(f"Script finished. Duration: {dur:.6f}s. Result saved to {out}")
