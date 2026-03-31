"""
LOGARITHMA Algorithms Module
===========================

Graph algorithms collection including shortest paths,
traversal algorithms, and advanced optimization algorithms.

Modules:
    shortest_path — Dijkstra, A*, Bellman-Ford, Bidirectional Dijkstra
    traversal     — BFS, DFS, cycle detection
"""

from .shortest_path import (
    dijkstra,
    dijkstra_with_path,
    astar,
    astar_with_stats,
    euclidean_heuristic,
    manhattan_heuristic,
    haversine_heuristic,
    zero_heuristic,
    bellman_ford,
    bellman_ford_path,
    bidirectional_dijkstra,
    # Exceptions
    GraphError,
    EmptyGraphError,
    NodeNotFoundError,
    NegativeWeightError,
    NegativeCycleError,
    InvalidModeError,
)
from .traversal import bfs, bfs_path, dfs, dfs_path, detect_cycle

__all__ = [
    # Shortest Path
    'dijkstra',
    'dijkstra_with_path',
    'astar',
    'astar_with_stats',
    'euclidean_heuristic',
    'manhattan_heuristic',
    'haversine_heuristic',
    'zero_heuristic',
    'bellman_ford',
    'bellman_ford_path',
    'bidirectional_dijkstra',
    # Traversal
    'bfs',
    'bfs_path',
    'dfs',
    'dfs_path',
    'detect_cycle',
    # Exceptions
    'GraphError',
    'EmptyGraphError',
    'NodeNotFoundError',
    'NegativeWeightError',
    'NegativeCycleError',
    'InvalidModeError',
]
