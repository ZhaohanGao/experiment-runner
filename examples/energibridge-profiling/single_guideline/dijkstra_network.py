import heapq
import time
import sys
import os
import gzip
import json

def dijkstra(graph: dict, start: str, end: str) -> int:
    """Return the cost of the shortest path between vertices start and end."""
    heap = [(0, start)]  # (cost from start node, current node)
    visited = set()
    while heap:
        (cost, u) = heapq.heappop(heap)
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

def _write_text_auto(path: str, text: str) -> None:
    """G22: compress if path endswith .gz or COMPRESS_OUTPUT=1."""
    compress = path.endswith(".gz") or os.getenv("COMPRESS_OUTPUT") == "1"
    if compress:
        # mtime=0 -> deterministic gzip for better cache hits when transferring
        with gzip.open(path, "wt", compresslevel=6, mtime=0, encoding="utf-8") as f:
            f.write(text)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

def _export_payload_if_requested(graph: dict, test_cases, num_exec: int, out_path_env: str = "EXPORT_PAYLOAD_PATH") -> None:
    """
    G22+G23: emit a compact, reproducible, compressed payload (gzipped JSON)
    for remote/cloud execution to avoid re-sending bulky code and minimize bandwidth.
    """
    export_path = os.getenv(out_path_env)
    if not export_path:
        return
    payload = {
        "graph": graph,              # small enough; if huge, consider adjacency-only
        "test_cases": test_cases,
        "num_executions": num_exec,
        "version": 1,
    }
    with gzip.open(export_path, "wt", compresslevel=6, mtime=0, encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))  # compact JSON

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

    # Optional export for cloud/offload (G23) using compressed payload (G22)
    _export_payload_if_requested(test_graph, test_cases, num_executions)

    # Warm-up to avoid measuring interpreter cold start
    for start_node, end_node in test_cases:
        _ = dijkstra(test_graph, start_node, end_node)

    start_time = time.time()
    for _ in range(num_executions):
        for start_node, end_node in test_cases:
            _ = dijkstra(test_graph, start_node, end_node)
    end_time = time.time()

    duration = end_time - start_time
    _write_text_auto(output_file_path, str(duration))
