import heapq
import time
import sys
from typing import Dict, List, Tuple

# -------------------------
# G21: Proxy (with Flyweight IDs)
# -------------------------

class GraphProxy:
    """
    Proxy around the user-provided dict graph that lazily builds
    a compact, indexed representation (Flyweight node IDs).
    """
    __slots__ = ("_orig", "_built", "name2id", "id2name", "adj_by_id")

    def __init__(self, graph: Dict[str, List[Tuple[str, int]]]):
        self._orig = graph
        self._built = False
        self.name2id: Dict[str, int] = {}
        self.id2name: List[str] = []
        self.adj_by_id: List[Tuple[Tuple[int, int], ...]] = []

    def _build_index(self) -> None:
        if self._built:
            return
        # Assign stable int IDs (Flyweight)
        for u in self._orig.keys():
            if u not in self.name2id:
                self.name2id[u] = len(self.name2id)
                self.id2name.append(u)
            for v, _ in self._orig[u]:
                if v not in self.name2id:
                    self.name2id[v] = len(self.name2id)
                    self.id2name.append(v)

        n = len(self.name2id)
        adj: List[List[Tuple[int, int]]] = [[] for _ in range(n)]
        # Build adjacency once; store immutable rows to avoid per-run churn
        for u_name, edges in self._orig.items():
            u = self.name2id[u_name]
            row = adj[u]
            for v_name, c in edges:
                row.append((self.name2id[v_name], c))

        self.adj_by_id = [tuple(row) for row in adj]
        self._built = True

    def get_id(self, name: str) -> int:
        if not self._built:
            self._build_index()
        return self.name2id[name]

    def neighbors(self, u_id: int) -> Tuple[Tuple[int, int], ...]:
        if not self._built:
            self._build_index()
        return self.adj_by_id[u_id]

    def size(self) -> int:
        if not self._built:
            self._build_index()
        return len(self.adj_by_id)

# Module-level cache: one proxy per graph object (by id)
_GRAPH_PROXY_CACHE: Dict[int, GraphProxy] = {}

def _get_proxy(graph: Dict[str, List[Tuple[str, int]]]) -> GraphProxy:
    gid = id(graph)
    proxy = _GRAPH_PROXY_CACHE.get(gid)
    if proxy is None:
        proxy = GraphProxy(graph)
        _GRAPH_PROXY_CACHE[gid] = proxy
    return proxy

# -------------------------
# Public API (unchanged signature)
# Only G20/G21 applied inside
# -------------------------

def dijkstra(graph: dict, start: str, end: str) -> int:
    """
    Return the cost of the shortest path between start and end.
    G20: lists instead of dict/set; minimal allocations per call.
    G21: use GraphProxy + Flyweight node IDs.
    """
    proxy = _get_proxy(graph)
    n = proxy.size()
    s = proxy.get_id(start)
    t = proxy.get_id(end)

    INF = 10**15
    dist = [INF] * n          # G20: fixed-size list
    visited = [False] * n     # G20: fixed-size list

    dist[s] = 0
    heap: List[Tuple[int, int]] = [(0, s)]  # minimal tuple

    while heap:
        cost, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        if u == t:
            return cost
        for v, w in proxy.neighbors(u):
            if visited[v]:
                continue
            nc = cost + w
            if nc < dist[v]:
                dist[v] = nc
                heapq.heappush(heap, (nc, v))

    return -1

# -------------------------
# Your graph & main stay the same
# -------------------------

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
        ('Lagos', 'SanFrancisco'),
    ]

    # Sanity check
    for s, e in test_cases:
        _ = dijkstra(test_graph, s, e)

    start_time = time.time()
    for _ in range(num_executions):
        for s, e in test_cases:
            _ = dijkstra(test_graph, s, e)
    end_time = time.time()

    duration = end_time - start_time
    with open(output_file_path, "w") as f:
        f.write(str(duration))
