"""
Dijkstra's Shortest Path Algorithm
=================================

Classic O(E + V log V) implementation of Dijkstra's algorithm
for finding shortest paths in weighted graphs using binary heap.

Time Complexity: O(E + V log V) where E = edges, V = vertices
Space Complexity: O(V)
"""

import heapq
from typing import Dict, List, Optional, Union, Any
import networkx as nx

from logarithma.algorithms.exceptions import (
    validate_graph,
    validate_source,
    validate_target,
    validate_weight,
)


def dijkstra(
    graph: Union[nx.Graph, nx.DiGraph], 
    source: Union[int, str]
) -> Dict[Union[int, str], float]:
    """
    Find shortest paths from source to all other vertices using Dijkstra's algorithm.
    
    Supports both directed and undirected graphs. Works with non-negative edge weights.

    Args:
        graph: NetworkX Graph or DiGraph with non-negative edge weights
        source: Starting vertex

    Returns:
        Dictionary mapping each vertex to its shortest distance from source.
        Unreachable vertices have distance infinity.

    Raises:
        ValueError: If source vertex not in graph or graph is empty
        ValueError: If negative edge weights are detected

    Time Complexity:
        O(E + V log V) where E = number of edges, V = number of vertices

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path import dijkstra
        >>>
        >>> # Undirected graph
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=4)
        >>> G.add_edge('A', 'C', weight=2)
        >>> G.add_edge('B', 'C', weight=1)
        >>>
        >>> distances = dijkstra(G, 'A')
        >>> print(distances)
        {'A': 0, 'C': 2, 'B': 3}
        
        >>> # Directed graph
        >>> DG = nx.DiGraph()
        >>> DG.add_edge('A', 'B', weight=1)
        >>> distances = dijkstra(DG, 'A')
    """
    # Validate input
    validate_graph(graph, "dijkstra")
    validate_source(graph, source)

    # Initialize distances
    distances = {node: float('inf') for node in graph.nodes()}
    distances[source] = 0

    # Priority queue: (distance, vertex)
    pq = [(0, source)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        # Skip if already processed
        if current in visited:
            continue

        visited.add(current)

        # Check all neighbors
        for neighbor in graph.neighbors(current):
            # Get edge weight (default to 1 if not specified)
            weight = graph[current][neighbor].get('weight', 1)
            validate_weight(current, neighbor, weight, "dijkstra")

            new_distance = current_dist + weight

            # Update if shorter path found
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(pq, (new_distance, neighbor))

    return distances


def dijkstra_with_path(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Union[int, str],
    target: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """
    Dijkstra algorithm that also returns the shortest paths.
    
    Supports both directed and undirected graphs with path reconstruction.

    Args:
        graph: NetworkX Graph or DiGraph with non-negative edge weights
        source: Starting vertex
        target: Optional target vertex. If specified, returns only path to target
                and may terminate early. If None, finds paths to all reachable vertices.

    Returns:
        Dictionary with two keys:
            - 'distances': Dict mapping vertices to shortest distances
            - 'paths': Dict mapping vertices to shortest paths (list of vertices)
                      Empty list for unreachable vertices

    Raises:
        ValueError: If source or target vertex not in graph
        ValueError: If graph is empty or has negative weights

    Time Complexity:
        O(E + V log V) for all paths, may be faster with target specified

    Example:
        >>> result = dijkstra_with_path(G, 'A', 'B')
        >>> print(result['distances']['B'])  # Distance to B
        >>> print(result['paths']['B'])      # Path to B: ['A', 'C', 'B']
        
        >>> # All paths from source
        >>> result = dijkstra_with_path(G, 'A')
        >>> for node, path in result['paths'].items():
        ...     print(f"{node}: {path}")
    """
    # Validate input
    validate_graph(graph, "dijkstra_with_path")
    validate_source(graph, source)
    if target is not None:
        validate_target(graph, target)

    # Initialize
    distances = {node: float('inf') for node in graph.nodes()}
    distances[source] = 0
    previous = {node: None for node in graph.nodes()}

    # Priority queue
    pq = [(0, source)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        # Early termination if target found
        if target and current == target:
            break

        if current in visited:
            continue

        visited.add(current)

        # Process neighbors
        for neighbor in graph.neighbors(current):
            weight = graph[current][neighbor].get('weight', 1)
            validate_weight(current, neighbor, weight, "dijkstra_with_path")

            new_distance = current_dist + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current
                heapq.heappush(pq, (new_distance, neighbor))

    # Reconstruct paths
    def get_path(target_node):
        if distances[target_node] == float('inf'):
            return []

        path = []
        current = target_node
        while current is not None:
            path.append(current)
            current = previous[current]
        return path[::-1]

    # Build paths dictionary — all nodes included; unreachable nodes get []
    if target:
        paths = {target: get_path(target)}
    else:
        paths = {node: get_path(node) for node in graph.nodes()}

    return {
        'distances': distances,
        'paths': paths
    }