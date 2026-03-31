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

Planned:
    breaking_barrier_sssp — O(m + n log log n), directed SSSP (Duan et al. 2025)
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
    # Exceptions
    'GraphError',
    'EmptyGraphError',
    'NodeNotFoundError',
    'NegativeWeightError',
    'NegativeCycleError',
    'InvalidModeError',
]
