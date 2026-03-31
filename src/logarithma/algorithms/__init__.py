"""
LOGARITHMA Algorithms Module
===========================

Graph algorithms collection including shortest paths,
traversal algorithms, MST, network flow, and graph properties.

Modules:
    shortest_path   — Dijkstra, A*, Bellman-Ford, Bidirectional Dijkstra
    traversal       — BFS, DFS, cycle detection
    mst             — Kruskal, Prim
    network_flow    — Edmonds-Karp max flow
    graph_properties — Tarjan SCC, Topological Sort
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
from .mst import kruskal_mst, prim_mst
from .network_flow import max_flow
from .graph_properties import tarjan_scc, topological_sort
from .exceptions import NotDAGError, UndirectedGraphRequiredError

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
    # MST
    'kruskal_mst',
    'prim_mst',
    # Network Flow
    'max_flow',
    # Graph Properties
    'tarjan_scc',
    'topological_sort',
    # Exceptions
    'GraphError',
    'EmptyGraphError',
    'NodeNotFoundError',
    'NegativeWeightError',
    'NegativeCycleError',
    'InvalidModeError',
    'NotDAGError',
    'UndirectedGraphRequiredError',
]
