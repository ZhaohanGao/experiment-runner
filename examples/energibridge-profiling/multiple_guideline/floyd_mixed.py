# Guideline used: Code Optimization (G1, G3, G4, G6, G7, G28) • Native Code / HPC (G15, G17, G24) • Function Calls (G19)
import os
import sys
import time
import math
import numpy as np

# --------------------------
# Native-code path (G15,G17) via Numba; optional
# --------------------------
NUMBA_AVAILABLE = False
FW_BACKEND = os.getenv("FW_BACKEND", "numba")  # "numba" | "numpy"
try:
    if FW_BACKEND == "numba":
        from numba import njit  # G15
        NUMBA_AVAILABLE = True
except Exception:
    NUMBA_AVAILABLE = False
    FW_BACKEND = "numpy"

# --------------------------
# Graph generation (G7,G24,G28)
# Bulk, vectorized creation of a random weighted directed graph
# --------------------------
def make_random_graph_np(n: int, density: float, w_min: int = 1, w_max: int = 10, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # Start with +inf, 0 on diagonal (G24)
    dp = np.full((n, n), np.inf, dtype=np.float64)
    np.fill_diagonal(dp, 0.0)
    # Bernoulli mask for edges, without self loops (G7)
    mask = rng.random((n, n)) < density
    np.fill_diagonal(mask, False)
    # Integer weights in bulk, then cast (G7,G24)
    # We only write where mask=True to minimize memory traffic (G28)
    weights = rng.integers(low=w_min, high=w_max + 1, size=(n, n), dtype=np.int32)
    dp[mask] = weights[mask].astype(np.float64, copy=False)
    return dp

# --------------------------
# Floyd–Warshall backends
# --------------------------
if NUMBA_AVAILABLE:
    @njit(cache=True, fastmath=False)  # G15 exactness; G17 keeps heavy ops inside JIT region
    def floyd_warshall_numba(dp: np.ndarray) -> None:
        n = dp.shape[0]
        inf = math.inf  # G1
        # Store loop ranges once (G3)
        for k in range(n):
            # Cache the k-th row address (G1)
            # Inner checks short-circuit when dik/dkj are inf (G3,G4)
            for i in range(n):
                dik = dp[i, k]
                if dik == inf:
                    continue  # G3 early-continue
                for j in range(n):
                    dkj = dp[k, j]
                    if dkj == inf:
                        continue
                    alt = dik + dkj
                    if alt < dp[i, j]:
                        dp[i, j] = alt
else:
    floyd_warshall_numba = None  # type: ignore


def floyd_warshall_numpy(dp: np.ndarray) -> None:
    """
    NumPy-broadcast FW (G24,G28): dp = min(dp, dp[:,k][:,None] + dp[k,:][None,:]) per k,
    performed in-place as much as possible.
    """
    n = dp.shape[0]
    for k in range(n):
        # Local binds to reduce lookups (G1,G19)
        col = dp[:, k:k+1]    # shape (n,1)
        row = dp[k:k+1, :]    # shape (1,n)
        # Compute candidate matrix in bulk (G24), then fused min (G28)
        cand = col + row
        # In-place minimum where beneficial (avoid writing unchanged cells) (G28)
        np.minimum(dp, cand, out=dp)


# --------------------------
# Runner (drop-in CLI)
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide an output file path as a command-line argument.")
        sys.exit(1)
    output_file_path = sys.argv[1]

    # Tunables (kept explicit for reproducibility; set via env if needed)
    n = int(os.getenv("FW_N", "500"))
    density = float(os.getenv("FW_DENSITY", "0.1"))
    runs = int(os.getenv("FW_RUNS", "1"))
    seed = int(os.getenv("FW_SEED", "12345"))

    # Build one base graph; copy per run (G6 avoid recompute)
    base_dp = make_random_graph_np(n, density, seed=seed)

    # Warmup JIT once outside timing (G6)
    if FW_BACKEND == "numba" and floyd_warshall_numba is not None:
        tmp = base_dp.copy()
        floyd_warshall_numba(tmp)  # compile now
        del tmp

    t0 = time.perf_counter()
    for _ in range(runs):
        dp = base_dp.copy()  # G6: copy once per run
        if FW_BACKEND == "numba" and floyd_warshall_numba is not None:
            floyd_warshall_numba(dp)  # G15/G17
        else:
            floyd_warshall_numpy(dp)  # G24/G28
    duration = time.perf_counter() - t0

    with open(output_file_path, "w") as f:
        f.write(str(duration))
    print(f"Script finished. Duration: {duration:.4f}s. Result saved to {output_file_path}")
