# floyd_warshall_experiment_mt.py
import os
import sys
import time
import math
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import shared_memory, cpu_count

# =============== Low-level shared-memory helpers ===============

def _flat_idx(n: int, i: int, j: int) -> int:
    return i * n + j

def _worker_update_chunk(n: int, k: int, start_i: int, end_i: int,
                         shm_name: str, dtype_size: int = 8) -> None:
    """
    Worker: update rows [start_i, end_i) for fixed k in-place on a shared
    1D float buffer (row-major n x n). Each process writes disjoint rows.
    """
    # G8 + G14: attach to shared memory (cached, shared data)
    shm = shared_memory.SharedMemory(name=shm_name)
    # Create a memoryview to avoid copying
    buf = shm.buf
    # Handy locals to cut attribute lookups
    inf = math.inf
    n_local = n
    k_off = _flat_idx(n_local, 0, 0)  # just to keep signature parity

    # Pull out the k-th row once (still reading from shared memory)
    # We'll index directly every time to avoid copying a whole row (keeps memory down).
    # For tight loops in Python, local-binding of names matters.
    for i in range(start_i, end_i):
        dik = _get(buf, n_local, i, k)
        if dik == inf:
            continue
        row_i_off = i * n_local
        # Iterate columns j
        base_k_off = k * n_local
        for j in range(n_local):
            dkj = _get_off(buf, base_k_off + j)
            if dkj == inf:
                continue
            alt = dik + dkj
            # Compare & update dp[i][j]
            ij_off = row_i_off + j
            cur = _get_off(buf, ij_off)
            if alt < cur:
                _set_off(buf, ij_off, alt)

    # Detach (do not close or unlink here—parent owns lifecycle)
    shm.close()

def _get(buf, n, i, j):
    # Read float64 at index (i,j)
    off = (i * n + j) * 8
    return float.fromhex(buf[off:off+8].tobytes().hex())

def _get_off(buf, off_idx):
    off = off_idx * 8
    return float.fromhex(buf[off:off+8].tobytes().hex())

def _set_off(buf, off_idx, val):
    off = off_idx * 8
    b = float(val).hex()
    # Convert hex-string back to bytes representing float64
    # We avoid struct to keep everything stdlib; hex<- ->bytes round-trip
    # NOTE: hex string includes '0x...'—we need actual IEEE bytes. Use struct for clarity.
    import struct
    buf[off:off+8] = struct.pack('>d', val)  # big-endian for consistency

# Using struct is clearer & faster; override helpers with struct-based variants:
import struct
def _get(buf, n, i, j):
    off = (i * n + j) * 8
    return struct.unpack('>d', buf[off:off+8])[0]

def _get_off(buf, off_idx):
    off = off_idx * 8
    return struct.unpack('>d', buf[off:off+8])[0]

def _set_off(buf, off_idx, val):
    off = off_idx * 8
    buf[off:off+8] = struct.pack('>d', val)

# =============== Graph & generator (unchanged interface) ===============

class Graph:
    __slots__ = ("n", "dp")  # small perf win

    def __init__(self, n=0):
        self.n = n
        inf = math.inf
        dp = [[inf] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 0.0
        self.dp = dp

    def add_edge(self, u, v, w):
        if w < self.dp[u][v]:
            self.dp[u][v] = float(w)

    def floyd_warshall_parallel(self, max_workers=None, chunk_size=None):
        """
        Parallel Floyd–Warshall:
        - For each k, split rows i into chunks and update in parallel.
        - Shared memory holds an n*n float64 matrix in row-major order.
        """
        n = self.n
        # Flatten to 1D float64 buffer
        flat = [x for row in self.dp for x in row]
        # Backing shared memory (size in bytes)
        shm_size = n * n * 8
        shm = shared_memory.SharedMemory(create=True, size=shm_size)
        try:
            # Initialize shared buffer
            buf = shm.buf
            # Bulk pack via struct for speed
            off = 0
            pack = struct.pack
            for val in flat:
                buf[off:off+8] = pack('>d', val)
                off += 8

            if max_workers is None:
                max_workers = max(1, min(cpu_count(), 32))  # sensible cap
            if chunk_size is None:
                # Heuristic: ~8 chunks per worker to enable work-stealing (G12)
                chunks = max_workers * 8
                chunk_size = max(1, (n + chunks - 1) // chunks)

            # G12: dynamic scheduling via ProcessPoolExecutor
            # Each k iteration forms a barrier: all row updates must complete
            # before moving to next k.
            for k in range(n):
                futures = []
                with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    i0 = 0
                    while i0 < n:
                        i1 = min(n, i0 + chunk_size)
                        # Submit chunk task
                        futures.append(
                            ex.submit(_worker_update_chunk, n, k, i0, i1, shm.name, 8)
                        )
                        i0 = i1

                    # Wait for all chunks (implicit barrier for this k)
                    for fut in as_completed(futures):
                        fut.result()

            # Copy back to nested list
            out = []
            unpack = struct.unpack
            pos = 0
            for i in range(n):
                row = []
                for j in range(n):
                    row.append(unpack('>d', buf[pos:pos+8])[0])
                    pos += 8
                out.append(row)
            self.dp = out
        finally:
            # Cleanup shared memory
            shm.close()
            shm.unlink()

    # Keep a serial version if you want to compare
    def floyd_warshall(self):
        n = self.n
        dp = self.dp
        inf = math.inf
        for k in range(n):
            dp_k = dp[k]
            for i in range(n):
                dik = dp[i][k]
                if dik == inf:
                    continue
                row_i = dp[i]
                for j in range(n):
                    dkj = dp_k[j]
                    if dkj == inf:
                        continue
                    alt = dik + dkj
                    if alt < row_i[j]:
                        row_i[j] = alt

    def show_min(self, u, v):
        return self.dp[u][v]


def make_random_graph(n: int, density: float, w_min: int = 1, w_max: int = 10, seed: int = 42) -> Graph:
    rng = random.Random(seed)
    rand = rng.random
    randint = rng.randint
    g = Graph(n)
    add = g.add_edge
    for u in range(n):
        for v in range(n):
            if u != v and rand() < density:
                add(u, v, randint(w_min, w_max))
    return g


# =============== Runner ===============

if __name__ == "__main__":
    # Doctests optional
    if os.getenv("EXP_DOCTEST", "0") == "1":
        import doctest
        doctest.testmod()

    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)

    output_file_path = sys.argv[1]

    # Tunables (set via env if desired)
    n = int(os.getenv("FW_N", "500"))
    density = float(os.getenv("FW_DENSITY", "0.1"))
    runs = int(os.getenv("FW_RUNS", "1"))
    seed = int(os.getenv("FW_SEED", "12345"))
    max_workers_env = os.getenv("FW_WORKERS")
    max_workers = int(max_workers_env) if max_workers_env else None
    chunk_env = os.getenv("FW_CHUNK")
    chunk_size = int(chunk_env) if chunk_env else None

    base_graph = make_random_graph(n, density, seed=seed)

    t0 = time.perf_counter()
    for _ in range(runs):
        # Fresh copy per run
        g = Graph(n)
        g.dp = [row[:] for row in base_graph.dp]
        # Parallel FW (G8, G12, G14)
        g.floyd_warshall_parallel(max_workers=max_workers, chunk_size=chunk_size)
    duration = time.perf_counter() - t0

    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.4f}s. Result saved to {output_file_path}")
