"""
Breaking Barrier SSSP Benchmark
================================

Compare breaking_barrier_sssp vs Dijkstra across different graph sizes
and densities.

Usage:
    cd tests/benchmarks
    python benchmark_breaking_barrier.py

    # With plot output:
    python benchmark_breaking_barrier.py --plot
"""

import argparse
import sys
import time
import random

import networkx as nx

sys.path.insert(0, ".")

import logarithma as lg


# ---------------------------------------------------------------------------
# Graph generators
# ---------------------------------------------------------------------------

def make_sparse_digraph(n: int, seed: int = 42) -> nx.DiGraph:
    """Random directed sparse graph: m ≈ 2n edges."""
    rng = random.Random(seed)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    # Ensure connectivity: chain
    for i in range(n - 1):
        G.add_edge(i, i + 1, weight=round(rng.uniform(0.1, 10.0), 3))
    # Extra random edges up to 2n total
    extra = n
    attempts = 0
    while G.number_of_edges() < n + extra and attempts < n * 10:
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v, weight=round(rng.uniform(0.1, 10.0), 3))
        attempts += 1
    return G


def make_medium_digraph(n: int, seed: int = 42) -> nx.DiGraph:
    """Medium-density directed graph: m ≈ 5n edges."""
    rng = random.Random(seed)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i in range(n - 1):
        G.add_edge(i, i + 1, weight=round(rng.uniform(0.1, 10.0), 3))
    target_edges = 5 * n
    attempts = 0
    while G.number_of_edges() < target_edges and attempts < n * 20:
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v, weight=round(rng.uniform(0.1, 10.0), 3))
        attempts += 1
    return G


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def timed(fn, *args, runs: int = 3):
    """Return (mean_seconds, result) over `runs` calls."""
    times = []
    result = None
    for _ in range(runs):
        t0 = time.perf_counter()
        result = fn(*args)
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times), result


# ---------------------------------------------------------------------------
# Correctness check
# ---------------------------------------------------------------------------

def verify_equal(dist_bb, dist_dijk, n: int, label: str) -> bool:
    """Return True iff both distance dicts agree on all nodes."""
    ok = True
    for node in range(n):
        d_bb = dist_bb.get(node, float('inf'))
        d_dijk = dist_dijk.get(node, float('inf'))
        if abs(d_bb - d_dijk) > 1e-9:
            print(f"  MISMATCH at {node}: bb={d_bb:.6f}  dijk={d_dijk:.6f}  [{label}]")
            ok = False
    return ok


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------

def run_benchmark(sizes, graph_type: str = "sparse", runs: int = 3, plot: bool = False):
    print()
    print("=" * 68)
    print(f"  Breaking Barrier SSSP vs Dijkstra  ({graph_type} graphs)")
    print("=" * 68)
    print(f"  {'n':>6}  {'m':>7}  {'Dijkstra (ms)':>14}  {'BreakBarrier (ms)':>18}  {'Ratio':>7}  OK")
    print("-" * 68)

    dijk_times = []
    bb_times = []
    ns = []

    make_graph = make_sparse_digraph if graph_type == "sparse" else make_medium_digraph

    for n in sizes:
        G = make_graph(n)
        m = G.number_of_edges()
        source = 0

        t_dijk, dist_dijk = timed(lg.dijkstra, G, source, runs=runs)
        t_bb, dist_bb = timed(lg.breaking_barrier_sssp, G, source, runs=runs)

        ok = verify_equal(dist_bb, dist_dijk, n, f"n={n}")
        ok_str = "Yes" if ok else "FAIL"
        ratio = t_bb / t_dijk if t_dijk > 0 else float('inf')

        print(
            f"  {n:>6}  {m:>7}  {t_dijk * 1000:>14.2f}  "
            f"{t_bb * 1000:>18.2f}  {ratio:>7.2f}x  {ok_str}"
        )

        ns.append(n)
        dijk_times.append(t_dijk * 1000)
        bb_times.append(t_bb * 1000)

    print("=" * 68)
    print()

    if plot:
        _plot_results(ns, dijk_times, bb_times, graph_type)

    return ns, dijk_times, bb_times


def _plot_results(ns, dijk_times, bb_times, graph_type):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available — skipping plot.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.plot(ns, dijk_times, "o-", color="#3498db", label="Dijkstra", linewidth=2)
    ax1.plot(ns, bb_times, "s-", color="#e74c3c", label="Breaking Barrier", linewidth=2)
    ax1.set_xlabel("n (vertices)")
    ax1.set_ylabel("Time (ms)")
    ax1.set_title(f"Runtime comparison ({graph_type} graphs)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ratios = [bb / dijk if dijk > 0 else float('inf') for bb, dijk in zip(bb_times, dijk_times)]
    ax2.plot(ns, ratios, "D-", color="#2ecc71", linewidth=2)
    ax2.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7, label="1x (Dijkstra)")
    ax2.set_xlabel("n (vertices)")
    ax2.set_ylabel("Ratio (BB / Dijkstra)")
    ax2.set_title("Speed ratio (lower = Breaking Barrier faster)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.suptitle(
        "Breaking Barrier SSSP vs Dijkstra\n"
        "O(m log\u00b2\u00b3 n) vs O(m + n log n)",
        fontsize=13, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(f"benchmark_breaking_barrier_{graph_type}.png", dpi=150, bbox_inches="tight")
    print(f"Plot saved: benchmark_breaking_barrier_{graph_type}.png")
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Breaking Barrier SSSP benchmark")
    parser.add_argument("--plot", action="store_true", help="Generate plots")
    parser.add_argument("--runs", type=int, default=3, help="Runs per size (default: 3)")
    args = parser.parse_args()

    SPARSE_SIZES = [50, 100, 200, 500, 1000, 2000]
    MEDIUM_SIZES = [50, 100, 200, 500, 1000]

    run_benchmark(SPARSE_SIZES, graph_type="sparse", runs=args.runs, plot=args.plot)
    run_benchmark(MEDIUM_SIZES, graph_type="medium", runs=args.runs, plot=args.plot)
