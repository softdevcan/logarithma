"""
Bellman-Ford Shortest Path Algorithm
=====================================

Bellman-Ford computes single-source shortest paths in a weighted directed graph
that may contain *negative-weight edges*. It also detects negative-weight cycles
that are reachable from the source — a situation in which no finite shortest-path
solution exists.

Algorithm sketch
----------------
1. Initialise dist[source] = 0, dist[v] = ∞ for all other vertices.
2. Repeat (|V| - 1) times:
       for every edge (u, v, w) in E:
           if dist[u] + w < dist[v]:
               dist[v] = dist[u] + w
               prev[v] = u
3. Negative-cycle check: perform one more relaxation pass.
   If any distance still improves, a negative cycle is reachable from source.

Why |V| - 1 iterations?
   The longest simple path (no repeated vertices) has at most |V| - 1 edges.
   After k passes, dist[v] holds the optimal distance using at most k edges.
   Therefore |V| - 1 passes are sufficient for all simple shortest paths.

Time Complexity:  O(V · E)
Space Complexity: O(V)

Use cases
---------
- Directed graphs with negative edge weights (e.g. financial arbitrage detection)
- Negative-cycle detection (e.g. currency exchange loops, deadlock analysis)
- Distributed routing protocols (e.g. RIP — Routing Information Protocol)
- Preprocessing step in Johnson's all-pairs shortest path algorithm

Important constraint — undirected graphs
-----------------------------------------
Bellman-Ford treats each undirected edge (u, v, w) as two directed edges
u→v and v→u. If w < 0, the pair forms a 2-cycle u→v→u of total weight 2w < 0,
which is by definition a negative cycle. Therefore, Bellman-Ford on an
**undirected** graph with **any** negative-weight edge will always raise
NegativeCycleError. Use directed graphs when negative weights are needed.

References
----------
Bellman, R. (1958). "On a routing problem."
    Quarterly of Applied Mathematics, 16(1), 87–90.
Ford, L. R. (1956). "Network flow theory."
    RAND Corporation Report P-923.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    NegativeCycleError,
    validate_graph,
    validate_source,
    validate_target,
)


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def bellman_ford(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
) -> Dict[str, Any]:
    """
    Compute shortest paths from *source* using the Bellman-Ford algorithm.

    Supports graphs with negative edge weights. Raises :class:`NegativeCycleError`
    if a negative-weight cycle reachable from the source is detected.

    Args:
        graph:  NetworkX Graph or DiGraph. Undirected edges are treated as two
                directed edges (both directions) with the same weight.
                If an edge lacks a 'weight' attribute, weight defaults to 1.
        source: Starting vertex.

    Returns:
        Dictionary with two keys:
            'distances':    Dict[node, float] — shortest distance from source.
                            Unreachable nodes have distance float('inf').
            'predecessors': Dict[node, node|None] — predecessor on the shortest
                            path (for path reconstruction). Source has None.

    Raises:
        ValueError:         If graph is empty or source is not in the graph.
        NegativeCycleError: If a negative-weight cycle reachable from source is
                            detected. The exception carries a `cycle` attribute
                            with the reconstructed cycle nodes.

    Time Complexity:
        O(V · E) where V = |vertices|, E = |edges|.

    Example — graph with negative edge:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path.bellman_ford import bellman_ford
        >>>
        >>> G = nx.DiGraph()
        >>> G.add_edge('A', 'B', weight=4)
        >>> G.add_edge('A', 'C', weight=2)
        >>> G.add_edge('B', 'C', weight=-3)   # negative, but no negative cycle
        >>> G.add_edge('C', 'D', weight=1)
        >>>
        >>> result = bellman_ford(G, 'A')
        >>> print(result['distances'])
        # {'A': 0, 'B': 4, 'C': 1, 'D': 2}   (A→B=4, B→C=4-3=1, C→D=1+1=2)

    Example — negative cycle detection:
        >>> G = nx.DiGraph()
        >>> G.add_edge('A', 'B', weight=1)
        >>> G.add_edge('B', 'C', weight=-3)
        >>> G.add_edge('C', 'A', weight=1)   # cycle A→B→C→A with total weight -1
        >>> bellman_ford(G, 'A')             # raises NegativeCycleError
    """
    # --- Validation ---
    validate_graph(graph, "bellman_ford")
    validate_source(graph, source)

    nodes = list(graph.nodes())
    n = len(nodes)

    # --- Initialisation ---
    dist: Dict[Any, float] = {v: float('inf') for v in nodes}
    dist[source] = 0.0
    pred: Dict[Any, Optional[Any]] = {v: None for v in nodes}

    # Build a flat edge list once — O(E) work, avoids repeated graph traversal.
    # For undirected graphs each edge (u, v) yields two directed entries.
    edges: List[Tuple[Any, Any, float]] = _build_edge_list(graph)

    # --- Relaxation: (|V| - 1) passes ---
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
        # Early termination: if no update occurred, optimum already reached
        if not updated:
            break

    # --- Negative-cycle detection: one additional pass ---
    cycle_entry = None
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            cycle_entry = v
            pred[v] = u          # update predecessor for cycle reconstruction
            break

    if cycle_entry is not None:
        cycle = _reconstruct_negative_cycle(pred, cycle_entry, n)
        raise NegativeCycleError(source, cycle=cycle)

    return {'distances': dist, 'predecessors': pred}


def bellman_ford_path(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
) -> Dict[str, Any]:
    """
    Convenience wrapper: compute the shortest path from *source* to *target*.

    Args:
        graph:  NetworkX Graph or DiGraph (may have negative weights).
        source: Starting vertex.
        target: Destination vertex.

    Returns:
        Dictionary with keys:
            'distance': float — shortest distance (float('inf') if unreachable).
            'path':     List[node] — shortest path, or [] if unreachable.

    Raises:
        ValueError:         On empty graph or missing source/target.
        NegativeCycleError: If a negative-weight cycle reachable from source
                            is detected.

    Example:
        >>> result = bellman_ford_path(G, 'A', 'D')
        >>> print(result['distance'])
        >>> print(result['path'])
    """
    validate_graph(graph, "bellman_ford_path")
    validate_source(graph, source)
    validate_target(graph, target)

    result = bellman_ford(graph, source)
    dist = result['distances']
    pred = result['predecessors']

    if dist[target] == float('inf'):
        return {'distance': float('inf'), 'path': []}

    path = _reconstruct_path(pred, source, target)
    return {'distance': dist[target], 'path': path}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_edge_list(
    graph: Union[nx.Graph, nx.DiGraph],
) -> List[Tuple[Any, Any, float]]:
    """
    Return a flat list of (u, v, weight) for all directed edges.

    For undirected graphs, each edge is expanded into two directed entries
    to correctly handle relaxation in both directions.
    """
    edges = []
    if isinstance(graph, nx.DiGraph):
        for u, v, data in graph.edges(data=True):
            edges.append((u, v, data.get('weight', 1)))
    else:
        for u, v, data in graph.edges(data=True):
            w = data.get('weight', 1)
            edges.append((u, v, w))
            edges.append((v, u, w))
    return edges


def _reconstruct_path(
    pred: Dict[Any, Optional[Any]],
    source: Any,
    target: Any,
) -> List[Any]:
    """Walk the predecessor map from target back to source."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = pred[current]
    else:
        # Predecessor chain did not reach source — graph is disconnected
        return []
    path.reverse()
    return path if path[0] == source else []


def _reconstruct_negative_cycle(
    pred: Dict[Any, Optional[Any]],
    entry: Any,
    n: int,
) -> List[Any]:
    """
    Reconstruct a negative cycle starting from the *entry* node.

    Strategy: follow the predecessor chain for n steps to guarantee we land
    inside the cycle, then trace the cycle.
    """
    # Walk n steps back to ensure we are inside the cycle
    visited = entry
    for _ in range(n):
        visited = pred[visited]

    # Now trace the cycle
    cycle = []
    current = visited
    while True:
        cycle.append(current)
        current = pred[current]
        if current == visited:
            cycle.append(current)
            break
        if len(cycle) > n:          # safeguard against infinite loops
            break

    cycle.reverse()
    return cycle
