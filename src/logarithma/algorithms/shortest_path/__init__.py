"""
Shortest Path Algorithms
========================

Collection of shortest path algorithms for graph analysis.

Available algorithms:
    dijkstra              — O(E + V log V), non-negative weights
    dijkstra_with_path    — Dijkstra with path reconstruction
    astar                 — O(b^d), heuristic-guided, non-negative weights
    astar_with_stats      — A* with node-expansion diagnostics
    bellman_ford          — O(VE), supports negative weights + cycle detection
    bellman_ford_path     — Bellman-Ford with path reconstruction
    bidirectional_dijkstra— O(E + V log V), ~2x faster for point-to-point
    breaking_barrier_sssp — O(m log^{2/3} n), directed SSSP (Duan et al. 2025)
    floyd_warshall        — O(V³), all-pairs SP, supports negative weights
    floyd_warshall_path   — Floyd-Warshall with path reconstruction
    johnson               — O(V² log V + VE), all-pairs SP for sparse graphs
    johnson_path          — Johnson's with path reconstruction
"""

from .dijkstra import dijkstra, dijkstra_with_path
from .astar import (
    astar,
    astar_with_stats,
    euclidean_heuristic,
    manhattan_heuristic,
    haversine_heuristic,
    zero_heuristic,
)
from .bellman_ford import bellman_ford, bellman_ford_path
from logarithma.algorithms.exceptions import (
    GraphError,
    EmptyGraphError,
    NodeNotFoundError,
    NegativeWeightError,
    NegativeCycleError,
    InvalidModeError,
)
from .bidirectional_dijkstra import bidirectional_dijkstra
from .breaking_barrier import breaking_barrier_sssp
from .floyd_warshall import floyd_warshall, floyd_warshall_path
from .johnson import johnson, johnson_path

__all__ = [
    # Dijkstra
    'dijkstra',
    'dijkstra_with_path',
    # A*
    'astar',
    'astar_with_stats',
    'euclidean_heuristic',
    'manhattan_heuristic',
    'haversine_heuristic',
    'zero_heuristic',
    # Bellman-Ford
    'bellman_ford',
    'bellman_ford_path',
    # Bidirectional Dijkstra
    'bidirectional_dijkstra',
    # Breaking the Sorting Barrier
    'breaking_barrier_sssp',
    # All-Pairs Shortest Path
    'floyd_warshall',
    'floyd_warshall_path',
    'johnson',
    'johnson_path',
    # Exceptions
    'GraphError',
    'EmptyGraphError',
    'NodeNotFoundError',
    'NegativeWeightError',
    'NegativeCycleError',
    'InvalidModeError',
]
