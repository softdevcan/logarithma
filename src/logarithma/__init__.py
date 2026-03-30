"""
LOGARITHMA - Graph Algorithms Library
=====================================

High-performance graph algorithms library.
Primary goal: implement the Breaking the Sorting Barrier SSSP algorithm
(Duan et al., 2025 — arXiv:2504.17033v2).

Quick Start:
    >>> import logarithma as lg
    >>> import networkx as nx
    >>>
    >>> G = nx.Graph()
    >>> G.add_edge('A', 'B', weight=4)
    >>> G.add_edge('A', 'C', weight=2)
    >>> G.add_edge('B', 'C', weight=1)
    >>>
    >>> # Dijkstra — general shortest paths
    >>> distances = lg.dijkstra(G, 'A')
    >>>
    >>> # A* — heuristic-guided point-to-point
    >>> from logarithma import astar, euclidean_heuristic
    >>> pos = {'A': (0,0), 'B': (1,0), 'C': (0,1)}
    >>> result = astar(G, 'A', 'C', heuristic=euclidean_heuristic(pos))
    >>>
    >>> # Bellman-Ford — negative-weight edges
    >>> DG = nx.DiGraph()
    >>> DG.add_edge('X', 'Y', weight=-2)
    >>> result = lg.bellman_ford(DG, 'X')
    >>>
    >>> # Bidirectional Dijkstra — fast point-to-point
    >>> result = lg.bidirectional_dijkstra(G, 'A', 'C')
"""

__version__ = "0.3.0"
__author__ = "Can AKYILDIRIM"

from .algorithms import (
    # Dijkstra
    dijkstra,
    dijkstra_with_path,
    # A*
    astar,
    astar_with_stats,
    euclidean_heuristic,
    manhattan_heuristic,
    haversine_heuristic,
    zero_heuristic,
    # Bellman-Ford
    bellman_ford,
    bellman_ford_path,
    NegativeCycleError,
    # Bidirectional Dijkstra
    bidirectional_dijkstra,
)
from .algorithms.traversal import bfs, bfs_path, dfs, dfs_path, detect_cycle

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
    'NegativeCycleError',
    'bidirectional_dijkstra',
    # Traversal
    'bfs',
    'bfs_path',
    'dfs',
    'dfs_path',
    'detect_cycle',
    # Metadata
    '__version__',
    '__author__',
]
