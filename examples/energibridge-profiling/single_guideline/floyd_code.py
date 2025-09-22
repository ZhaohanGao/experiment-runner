# floyd_warshall_experiment_optimized.py
import os
import sys
import time
import random
import math


class Graph:
    __slots__ = ("n", "dp")  # G1: reduce instance dict lookup overhead

    def __init__(self, n: int = 0):  # nodes 0..n-1
        self.n = n
        inf = math.inf  # G1: cache attribute lookups
        # dp[i][j] holds shortest-known distance; start with inf except diagonal
        dp = [[inf] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 0
        self.dp = dp

    def add_edge(self, u: int, v: int, w: float) -> None:
        """
        Adds a directed edge from node u to node v with weight w.
        """
        # G1: local binds for fast lookups
        dp_uv = self.dp[u][v]
        if w < dp_uv:
            self.dp[u][v] = w

    def floyd_warshall(self) -> None:
        """
        Computes all-pairs shortest paths.
        """
        n = self.n
        dp = self.dp  # G1: local bind

        inf = math.inf  # G1: cache
        range_n = range(n)  # G3: store loop end condition

        # Standard triple loop with inner-loop locality optimizations
        for k in range_n:
            dp_k = dp[k]  # G1: local bind
            for i in range_n:
                dik = dp[i][k]
                if dik == inf:  # G3: early continue (unswitch on inf)
                    continue
                row_i = dp[i]  # G1: local bind
                # Inner loop: keep local references to speed up
                for j in range_n:
                    # G3: small branch to skip useless work when dp_k[j] is inf
                    dkj = dp_k[j]
                    if dkj == inf:
                        continue
                    alt = dik + dkj
                    if alt < row_i[j]:
                        row_i[j] = alt

    def show_min(self, u: int, v: int):
        return self.dp[u][v]


def make_random_graph(
    n: int,
    density: float,
    w_min: int = 1,
    w_max: int = 10,
    seed: int = 42,
) -> Graph:
    """
    Create a directed graph with approximately `density` fraction of possible edges.
    No self-loops (diagonal remains 0).
    """
    rng = random.Random(seed)
    rand = rng.random       # G1: cache method lookups
    randint = rng.randint   # G1
    g = Graph(n)
    add_edge = g.add_edge   # G1
    range_n = range(n)      # G3

    # G4: short-circuit logical op to avoid calling rand() on diagonal cells
    for u in range_n:
        for v in range_n:
            if u != v and rand() < density:  # rand() is never called when u == v
                add_edge(u, v, randint(w_min, w_max))
    return g


if __name__ == "__main__":
    # Optional: run doctests when EXP_DOCTEST=1
    if os.getenv("EXP_DOCTEST", "0") == "1":
        import doctest
        doctest.testmod()

    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)

    output_file_path = sys.argv[1]

    # Tunables via environment variables (kept literal for reproducibility here)
    n = 500
    density = 0.1
    runs = 1
    seed = 12345

    # Build the same graph once for fairness; each run operates on a fresh copy
    base_graph = make_random_graph(n, density, seed=seed)

    # G6: measure only the compute portion, avoid extra work in the timed window
    t0 = time.perf_counter()  # steadier clock than time.time()

    for _ in range(runs):
        # G6: copy only what's needed; reuse Graph structure without __init__ work
        g = Graph.__new__(Graph)   # avoid re-building an inf-initialized matrix we overwrite
        g.n = n
        # Deep copy of rows (fast path for list of lists)
        g.dp = [row[:] for row in base_graph.dp]
        g.floyd_warshall()

    duration = time.perf_counter() - t0

    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.4f}s. Result saved to {output_file_path}")
