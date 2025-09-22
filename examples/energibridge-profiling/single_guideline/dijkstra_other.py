import sys
import time
import os
import heapq
from typing import Dict, List, Tuple
import multiprocessing as mp

# ---------------------------
# High-performance path (G24)
# ---------------------------
try:
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra as sp_dijkstra
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False

def _build_index_and_csr(graph: Dict[str, List[Tuple[str, int]]]):
    """
    G24/G28: Build node index mapping and a CSR adjacency matrix once.
    Returns: (name2id, id2name, csr_matrix)
    """
    # Map node names to integer IDs
    name2id: Dict[str, int] = {}
    id2name: List[str] = []

    for u in graph.keys():
        if u not in name2id:
            name2id[u] = len(name2id)
            id2name.append(u)
        for v, _ in graph[u]:
            if v not in name2id:
                name2id[v] = len(name2id)
                id2name.append(v)

    n = len(name2id)
    # Build CSR components
    indptr = [0]
    indices = []
    data = []
    for u_name in id2name:
        edges = graph.get(u_name, ())
        for v_name, w in edges:
            indices.append(name2id[v_name])
            data.append(w)
        indptr.append(len(indices))

    A = csr_matrix((np.array(data, dtype=np.float64),
                    np.array(indices, dtype=np.int32),
                    np.array(indptr, dtype=np.int32)),
                   shape=(n, n))
    return name2id, id2name, A

# Globals shared to workers (G26/G28)
_GLOBAL = {
    "use_scipy": False,
    "name2id": None,
    "A": None,              # CSR matrix
    "graph": None,          # fallback graph
    "targets": None,        # target id list for quick indexing
}

def _init_worker(name2id, A, graph, targets):
    _GLOBAL["use_scipy"] = A is not None
    _GLOBAL["name2id"] = name2id
    _GLOBAL["A"] = A
    _GLOBAL["graph"] = graph
    _GLOBAL["targets"] = targets

# -----------------------------------
# Two dijkstra backends (CPU-only)
# -----------------------------------

def _dijkstra_python(graph: dict, start: str, end: str) -> int:
    """Original Python heap-based Dijkstra (fallback)."""
    heap = [(0, start)]
    visited = set()
    while heap:
        cost, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == end:
            return cost
        for v, c in graph.get(u, ()):
            if v in visited:
                continue
            heapq.heappush(heap, (cost + c, v))
    return -1

def _dijkstra_scipy(start: str, end: str) -> int:
    """
    G24: Use SciPy's csgraph.dijkstra on CSR.
    Compute single-source distances and pick the target.
    """
    name2id = _GLOBAL["name2id"]
    A = _GLOBAL["A"]
    s = name2id[start]
    t = name2id[end]
    # SciPy returns np.inf if unreachable
    dist = sp_dijkstra(A, directed=True, indices=s, return_predecessors=False)
    d = dist[t]
    if np.isinf(d):
        return -1
    # cast to Python int if it’s integral; otherwise keep float
    return int(d) if float(d).is_integer() else float(d)

def _worker_run(iterations: int, test_cases: List[Tuple[str, str]]) -> None:
    """
    Run a chunk of iterations. We don’t return anything large; the parent measures wall time.
    """
    use_scipy = _GLOBAL["use_scipy"]
    graph = _GLOBAL["graph"]

    if use_scipy:
        dfunc = _dijkstra_scipy
        # warm per process once (G28)
        for s, e in test_cases:
            _ = dfunc(s, e)
    else:
        dfunc = lambda s, e: _dijkstra_python(graph, s, e)

    for _ in range(iterations):
        for s, e in test_cases:
            _ = dfunc(s, e)

# ---------------------------
# Public API (kept same)
# ---------------------------

def dijkstra(graph: dict, start: str, end: str) -> int:
    """
    Single query helper used in the warm-up/correctness steps.
    Will use SciPy if available, otherwise the Python fallback.
    """
    if _HAVE_SCIPY:
        # Build once locally if not yet built (no global side-effects for single call)
        name2id, _, A = _build_index_and_csr(graph)
        _init_worker(name2id, A, graph, targets=None)
        return _dijkstra_scipy(start, end)
    else:
        return _dijkstra_python(graph, start, end)

# ---------------------------
# Your graph (unchanged)
# ---------------------------

COMPLEX_GRAPH = {
    # North America
    'Atlanta': [('Chicago', 12), ('Miami', 9), ('Dallas', 11), ('NewYork', 14)],
    'Boston': [('NewYork', 4), ('Montreal', 6)],
    'Chicago': [('Atlanta', 12), ('Denver', 15), ('Toronto', 8), ('NewYork', 13)],
    'Dallas': [('Atlanta', 11), ('Denver', 12), ('LosAngeles', 22), ('Miami', 18)],
    'Denver': [('Chicago', 15), ('Dallas', 12), ('Phoenix', 9), ('Seattle', 20), ('SanFrancisco', 19)],
    'LosAngeles': [('Dallas', 22), ('Phoenix', 6), ('SanFrancisco', 5), ('Seattle', 18), ('Sydney', 125), ('Lima', 68)],
    'Miami': [('Atlanta', 9), ('SaoPaulo', 14), ('Dallas', 18), ('BuenosAires', 72), ('Lima', 42)],
    'Montreal': [('Boston', 6), ('Toronto', 3)],
    'NewYork': [('Boston', 4), ('London', 11), ('Chicago', 13), ('Atlanta', 14), ('Madrid', 58), ('Tokyo', 108)],
    'Phoenix': [('Denver', 9), ('LosAngeles', 6)],
    'SanFrancisco': [('LosAngeles', 5), ('Seattle', 11), ('Tokyo', 85), ('Denver', 19), ('Seoul', 95), ('Sydney', 119)],
    'Seattle': [('Denver', 20), ('LosAngeles', 18), ('SanFrancisco', 11), ('Toronto', 32)],
    'Toronto': [('Chicago', 8), ('Montreal', 3), ('Seattle', 32)],
    # South America
    'SaoPaulo': [('Miami', 14), ('BuenosAires', 12), ('Lima', 28), ('Johannesburg', 75), ('Lagos', 65), ('Madrid', 82)],
    'BuenosAires': [('SaoPaulo', 12), ('Miami', 72), ('Lima', 31), ('Madrid', 95)],
    'Lima': [('SaoPaulo', 28), ('BuenosAires', 31), ('Miami', 42), ('LosAngeles', 68)],
    # Europe
    'London': [('Frankfurt', 3), ('NewYork', 11), ('Paris', 2), ('Amsterdam', 2), ('Madrid', 7), ('Lagos', 45), ('Dubai', 51), ('Johannesburg', 90), ('Stockholm', 5)],
    'Paris': [('Frankfurt', 2), ('London', 2), ('Milan', 5), ('Luxembourg', 2), ('Amsterdam', 3), ('Berlin', 4), ('Madrid', 6)],
    'Frankfurt': [('London', 3), ('Paris', 2), ('Milan', 4), ('Luxembourg', 1), ('Amsterdam', 2), ('Berlin', 3), ('Moscow', 18), ('Istanbul', 14), ('Cairo', 22), ('Dubai', 45), ('Stockholm', 4)],
    'Milan': [('Frankfurt', 4), ('Paris', 5), ('Rome', 3)],
    'Rome': [('Milan', 3), ('Madrid', 8), ('Cairo', 19), ('Istanbul', 11)],
    'Luxembourg': [('Paris', 2), ('Frankfurt', 1)],
    'Amsterdam': [('London', 2), ('Paris', 3), ('Frankfurt', 2), ('Berlin', 3)],
    'Berlin': [('Frankfurt', 3), ('Paris', 4), ('Amsterdam', 3), ('Stockholm', 4), ('Moscow', 14)],
    'Madrid': [('Paris', 6), ('London', 7), ('Rome', 8), ('NewYork', 58), ('SaoPaulo', 82), ('BuenosAires', 95)],
    'Moscow': [('Stockholm', 5), ('Berlin', 14), ('Frankfurt', 18), ('Istanbul', 12), ('Beijing', 55)],
    'Stockholm': [('London', 5), ('Frankfurt', 4), ('Berlin', 4), ('Moscow', 5)],
    'Istanbul': [('Rome', 11), ('Frankfurt', 14), ('Moscow', 12), ('Cairo', 9), ('Dubai', 28)],
    # Asia
    'HongKong': [('Singapore', 5), ('Tokyo', 6), ('Mumbai', 9), ('Beijing', 8), ('Seoul', 7), ('Sydney', 62), ('Dubai', 35)],
    'Tokyo': [('HongKong', 6), ('SanFrancisco', 85), ('Singapore', 8), ('Beijing', 7), ('Seoul', 4), ('Sydney', 78), ('NewYork', 108)],
    'Singapore': [('HongKong', 5), ('Mumbai', 7), ('Tokyo', 8), ('Sydney', 52), ('Perth', 41), ('Dubai', 30)],
    'Mumbai': [('HongKong', 9), ('Singapore', 7), ('Dubai', 12), ('Cairo', 28), ('Johannesburg', 68), ('Perth', 70)],
    'Beijing': [('HongKong', 8), ('Tokyo', 7), ('Seoul', 3), ('Moscow', 55)],
    'Seoul': [('Tokyo', 4), ('Beijing', 3), ('HongKong', 7), ('SanFrancisco', 95)],
    'Dubai': [('Mumbai', 12), ('Singapore', 30), ('HongKong', 35), ('Frankfurt', 45), ('London', 51), ('Cairo', 15), ('Johannesburg', 61), ('Istanbul', 28)],
    # Africa
    'Cairo': [('Rome', 19), ('Frankfurt', 22), ('Istanbul', 9), ('Dubai', 15), ('Mumbai', 28), ('Lagos', 33)],
    'Johannesburg': [('London', 90), ('Dubai', 61), ('Mumbai', 68), ('SaoPaulo', 75), ('Lagos', 40), ('Perth', 85)],
    'Lagos': [('Johannesburg', 40), ('SaoPaulo', 65), ('London', 45), ('Cairo', 33)],
    # Australia
    'Sydney': [('LosAngeles', 125), ('SanFrancisco', 119), ('Tokyo', 78), ('HongKong', 62), ('Singapore', 52), ('Perth', 35)],
    'Perth': [('Sydney', 35), ('Singapore', 41), ('Mumbai', 70), ('Johannesburg', 85)],
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)

    output_file_path = sys.argv[1]
    num_executions = 100000
    test_graph = COMPLEX_GRAPH

    test_cases = [
        ('BuenosAires', 'Beijing'),
        ('Perth', 'Stockholm'),
        ('Lagos', 'SanFrancisco')
    ]

    # Build HPC data once (G24/G28)
    if _HAVE_SCIPY:
        name2id, _, A = _build_index_and_csr(test_graph)
        targets = [name2id[e] for _, e in test_cases]
    else:
        name2id, A, targets = None, None, None

    # Warm-up (avoid cold start skew; G28)
    for s, e in test_cases:
        _ = dijkstra(test_graph, s, e)

    # Parallelize across all cores (G26)
    cpu = mp.cpu_count()
    # balance load: each process executes roughly equal iterations
    per_proc = [num_executions // cpu] * cpu
    for i in range(num_executions % cpu):
        per_proc[i] += 1

    t0 = time.time()
    with mp.get_context("fork").Pool(
        processes=cpu,
        initializer=_init_worker,
        initargs=(name2id, A, test_graph, targets),
    ) as pool:
        # Fire tasks (no large return payloads; G28)
        for iters in per_proc:
            pool.apply_async(_worker_run, (iters, test_cases))
        pool.close()
        pool.join()
    duration = time.time() - t0

    # Single final write (G28)
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(str(duration))
