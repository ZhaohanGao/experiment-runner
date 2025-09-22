# floyd_warshall_experiment.py
import os
import sys
import time
import random
import math


class Graph:
    def __init__(self, n=0):  # nodes 0..n-1
        self.n = n
        # dp[i][j] holds shortest-known distance; start with inf except diagonal
        self.dp = [[math.inf] * n for _ in range(n)]
        for i in range(n):
            self.dp[i][i] = 0

    def add_edge(self, u, v, w):
        """
        Adds a directed edge from node u to node v with weight w.

        >>> g = Graph(3)
        >>> g.add_edge(0, 1, 5)
        >>> g.dp[0][1]
        5
        """
        if w < self.dp[u][v]:
            self.dp[u][v] = w

    def floyd_warshall(self):
        """
        Computes all-pairs shortest paths.

        >>> g = Graph(3)
        >>> g.add_edge(0, 1, 1)
        >>> g.add_edge(1, 2, 2)
        >>> g.floyd_warshall()
        >>> g.show_min(0, 2)
        3
        >>> g.show_min(2, 0)
        inf
        """
        n = self.n
        dp = self.dp  # local bind for speed
        for k in range(n):
            dp_k = dp[k]
            for i in range(n):
                dik = dp[i][k]
                if dik == math.inf:
                    continue
                row_i = dp[i]
                # manual unrolling not needed; keep clear
                for j in range(n):
                    alt = dik + dp_k[j]
                    if alt < row_i[j]:
                        row_i[j] = alt

    def show_min(self, u, v):
        """
        Returns the minimum distance from node u to node v.

        >>> g = Graph(3)
        >>> g.add_edge(0, 1, 3)
        >>> g.add_edge(1, 2, 4)
        >>> g.floyd_warshall()
        >>> g.show_min(0, 2)
        7
        >>> g.show_min(1, 0)
        inf
        """
        return self.dp[u][v]


def make_random_graph(n: int, density: float, w_min: int = 1, w_max: int = 10, seed: int = 42) -> Graph:
    """
    Create a directed graph with approximately `density` fraction of possible edges.
    density in [0,1]. No self-loops (diagonal remains 0).
    """
    rng = random.Random(seed)
    g = Graph(n)
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if rng.random() < density:
                g.add_edge(u, v, rng.randint(w_min, w_max))
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

    # Tunables via environment variables
    n = 500
    density = 0.1
    runs = 1
    seed = 12345

    # Build the same graph once for fairness; each run operates on a fresh copy
    base_graph = make_random_graph(n, density, seed=seed)

    start = time.time()
    for r in range(runs):
        # copy dp matrix so each run starts identical (deep copy)
        g = Graph(n)
        g.dp = [row[:] for row in base_graph.dp]
        g.floyd_warshall()
    duration = time.time() - start

    with open(output_file_path, "w") as f:
        f.write(str(duration))

    print(f"Script finished. Duration: {duration:.4f}s. Result saved to {output_file_path}")
