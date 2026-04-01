"""
A* (A-Star) Shortest Path Algorithm
====================================

A* is an informed search algorithm that extends Dijkstra's approach by using
a heuristic function h(n) to guide the search toward the goal. It is optimal
and complete when the heuristic is *admissible* (never overestimates the true
cost to the goal).

Evaluation function:  f(n) = g(n) + h(n)
    g(n) — exact cost from source to node n (known)
    h(n) — estimated cost from n to target (heuristic)

Time Complexity:  O(b^d) worst case, where b = branching factor, d = solution depth.
                  In practice, with a good admissible heuristic, A* visits far fewer
                  nodes than Dijkstra.
Space Complexity: O(V) — open set can hold all vertices in the worst case.

Optimality conditions:
    - Admissibility:  h(n) ≤ true_cost(n, target)  → guarantees optimal solution
    - Consistency:    h(n) ≤ w(n,m) + h(m)          → no reopening of nodes needed

References:
    Hart, P. E., Nilsson, N. J., & Raphael, B. (1968).
    "A Formal Basis for the Heuristic Determination of Minimum Cost Paths."
    IEEE Transactions on Systems Science and Cybernetics, 4(2), 100–107.
"""

import heapq
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    validate_graph,
    validate_source,
    validate_target,
    validate_weight,
)


# ---------------------------------------------------------------------------
# Built-in admissible heuristics
# ---------------------------------------------------------------------------

def euclidean_heuristic(pos: Dict[Any, Tuple[float, float]]) -> Callable:
    """
    Euclidean distance heuristic for 2-D coordinate graphs.

    Admissible when edge weights represent actual Euclidean distances.

    Args:
        pos: Dictionary mapping node → (x, y) coordinates.

    Returns:
        Callable h(node, target) → float
    """
    def h(node: Any, target: Any) -> float:
        x1, y1 = pos[node]
        x2, y2 = pos[target]
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return h


def manhattan_heuristic(pos: Dict[Any, Tuple[float, float]]) -> Callable:
    """
    Manhattan distance heuristic for grid-based graphs.

    Admissible when movement is axis-aligned and edge weights are unit distances.

    Args:
        pos: Dictionary mapping node → (x, y) coordinates.

    Returns:
        Callable h(node, target) → float
    """
    def h(node: Any, target: Any) -> float:
        x1, y1 = pos[node]
        x2, y2 = pos[target]
        return abs(x1 - x2) + abs(y1 - y2)
    return h


def haversine_heuristic(pos: Dict[Any, Tuple[float, float]]) -> Callable:
    """
    Haversine distance heuristic for geographic (lat/lon) graphs.

    Returns the great-circle distance in kilometres. Admissible when edge
    weights are geographic distances (km).

    Args:
        pos: Dictionary mapping node → (latitude, longitude) in degrees.

    Returns:
        Callable h(node, target) → float
    """
    EARTH_RADIUS_KM = 6371.0

    def h(node: Any, target: Any) -> float:
        lat1, lon1 = map(math.radians, pos[node])
        lat2, lon2 = map(math.radians, pos[target])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))
    return h


def zero_heuristic(_node: Any, _target: Any) -> float:
    """
    Zero heuristic — degenerates A* to Dijkstra's algorithm.

    Useful for correctness verification: astar(..., heuristic=zero_heuristic)
    must produce the same result as dijkstra().
    """
    return 0.0


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def astar(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
    heuristic: Optional[Callable[[Any, Any], float]] = None,
) -> Dict[str, Any]:
    """
    Find the shortest path from *source* to *target* using the A* algorithm.

    Unlike Dijkstra, A* is a *single-pair* algorithm — it terminates as soon
    as *target* is extracted from the open set, making it highly efficient for
    point-to-point queries when a good heuristic is available.

    Args:
        graph:     NetworkX Graph or DiGraph with non-negative edge weights.
                   If an edge lacks a 'weight' attribute, weight defaults to 1.
        source:    Starting vertex.
        target:    Goal vertex.
        heuristic: Callable h(node, target) → estimated cost to goal.
                   Must be admissible (never overestimates) to guarantee
                   optimality. Defaults to zero_heuristic (equivalent to
                   Dijkstra).

    Returns:
        Dictionary with two keys:
            'distance': float — optimal distance from source to target,
                        or float('inf') if target is unreachable.
            'path':     List[node] — optimal path as a list of vertices,
                        or [] if target is unreachable.

    Raises:
        EmptyGraphError:     If the graph has no nodes.
        NodeNotFoundError:   If source or target is not in the graph.
        NegativeWeightError: If any edge weight is negative.

    Time Complexity:
        O(b^d) worst case. With an admissible and consistent heuristic the
        effective branching factor drops significantly; in the best case (near-
        perfect heuristic) approaches O(m) like Dijkstra.

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path.astar import (
        ...     astar, euclidean_heuristic
        ... )
        >>>
        >>> G = nx.Graph()
        >>> pos = {'A': (0, 0), 'B': (1, 0), 'C': (1, 1), 'D': (2, 1)}
        >>> G.add_edge('A', 'B', weight=1)
        >>> G.add_edge('B', 'C', weight=1)
        >>> G.add_edge('A', 'C', weight=2)
        >>> G.add_edge('C', 'D', weight=1)
        >>>
        >>> h = euclidean_heuristic(pos)
        >>> result = astar(G, 'A', 'D', heuristic=h)
        >>> print(result['distance'])   # 3
        >>> print(result['path'])       # ['A', 'B', 'C', 'D']
    """
    # --- Input validation ---
    validate_graph(graph, "astar")
    validate_source(graph, source)
    validate_target(graph, target)

    if heuristic is None:
        heuristic = zero_heuristic

    # --- Data structures ---
    # g_score[n]  : best known cost from source to n
    # f_score[n]  : g_score[n] + h(n, target)  (priority key)
    # came_from[n]: predecessor of n on the optimal path
    g_score: Dict[Any, float] = {node: float('inf') for node in graph.nodes()}
    g_score[source] = 0.0

    came_from: Dict[Any, Optional[Any]] = {}

    # Open set: (f_score, tie-break counter, node)
    # The counter ensures a consistent ordering when f-scores are equal,
    # avoiding comparison of heterogeneous node types.
    counter = 0
    open_set: List[Tuple[float, int, Any]] = [
        (heuristic(source, target), counter, source)
    ]
    closed_set: set = set()

    # --- Main loop ---
    while open_set:
        f, _, current = heapq.heappop(open_set)

        # Goal test on extraction (guarantees optimality for admissible h)
        if current == target:
            return {
                'distance': g_score[target],
                'path': _reconstruct_path(came_from, source, target),
            }

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue

            weight = graph[current][neighbor].get('weight', 1)
            validate_weight(current, neighbor, weight, "astar")

            tentative_g = g_score[current] + weight

            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_new = tentative_g + heuristic(neighbor, target)
                counter += 1
                heapq.heappush(open_set, (f_new, counter, neighbor))

    # Target unreachable
    return {'distance': float('inf'), 'path': []}


def astar_with_stats(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
    heuristic: Optional[Callable[[Any, Any], float]] = None,
) -> Dict[str, Any]:
    """
    A* with diagnostic statistics — useful for benchmarking and heuristic
    quality analysis.

    Returns the same result as :func:`astar` plus:
        'nodes_expanded': int — number of nodes extracted from the open set.
        'nodes_generated': int — total nodes pushed onto the open set.

    The ratio ``nodes_expanded / |V|`` measures heuristic effectiveness:
    closer to 0 means the heuristic guides search more precisely.

    Args:
        graph:     NetworkX Graph or DiGraph.
        source:    Starting vertex.
        target:    Goal vertex.
        heuristic: Admissible heuristic callable h(node, target) → float.

    Returns:
        Dict with keys: 'distance', 'path', 'nodes_expanded', 'nodes_generated'.

    Raises:
        EmptyGraphError:     If the graph has no nodes.
        NodeNotFoundError:   If source or target is not in the graph.
        NegativeWeightError: If any edge weight is negative.

    Example:
        >>> result = astar_with_stats(G, 'A', 'D', heuristic=h)
        >>> print(result['nodes_expanded'])
        >>> print(result['nodes_generated'])
    """
    validate_graph(graph, "astar_with_stats")
    validate_source(graph, source)
    validate_target(graph, target)

    if heuristic is None:
        heuristic = zero_heuristic

    g_score: Dict[Any, float] = {node: float('inf') for node in graph.nodes()}
    g_score[source] = 0.0
    came_from: Dict[Any, Optional[Any]] = {}

    counter = 0
    nodes_generated = 1
    nodes_expanded = 0
    open_set: List[Tuple[float, int, Any]] = [
        (heuristic(source, target), counter, source)
    ]
    closed_set: set = set()

    while open_set:
        f, _, current = heapq.heappop(open_set)

        if current == target:
            return {
                'distance': g_score[target],
                'path': _reconstruct_path(came_from, source, target),
                'nodes_expanded': nodes_expanded,
                'nodes_generated': nodes_generated,
            }

        if current in closed_set:
            continue
        closed_set.add(current)
        nodes_expanded += 1

        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue

            weight = graph[current][neighbor].get('weight', 1)
            validate_weight(current, neighbor, weight, "astar_with_stats")

            tentative_g = g_score[current] + weight
            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_new = tentative_g + heuristic(neighbor, target)
                counter += 1
                nodes_generated += 1
                heapq.heappush(open_set, (f_new, counter, neighbor))

    return {
        'distance': float('inf'),
        'path': [],
        'nodes_expanded': nodes_expanded,
        'nodes_generated': nodes_generated,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _reconstruct_path(
    came_from: Dict[Any, Any],
    source: Any,
    target: Any,
) -> List[Any]:
    """Walk the came_from map backwards to reconstruct the optimal path."""
    path = []
    current = target
    while current != source:
        path.append(current)
        current = came_from[current]
    path.append(source)
    path.reverse()
    return path
