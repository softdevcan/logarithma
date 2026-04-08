"""
Johnson's All-Pairs Shortest Path Algorithm
============================================

Johnson's algorithm computes all-pairs shortest paths efficiently for
*sparse* graphs. It combines Bellman-Ford and Dijkstra:

1. Add a virtual source vertex *q* connected to every node with weight 0.
2. Run Bellman-Ford from *q* to compute potentials h[v].
   If a negative cycle exists, abort.
3. Reweight every edge (u, v, w) → w' = w + h[u] - h[v].
   The reweighted graph has non-negative edge weights, so Dijkstra applies.
4. Run Dijkstra from every vertex in the reweighted graph.
5. Convert back: dist[u][v] = dijkstra_dist[u][v] - h[u] + h[v].

Why does reweighting work?
--------------------------
For any path u → ... → v the telescoping sum of (h[u_i] - h[u_{i+1}]) terms
reduces to h[u] - h[v]. So all paths between the same (u, v) pair shift by the
same constant, and the *relative* ordering (hence the shortest path) is preserved.

Time Complexity:  O(V² log V + VE)
                  (V Dijkstra runs, each O(E + V log V) with binary heap)
Space Complexity: O(V²)  for the output distance matrix

Comparison with Floyd-Warshall
-------------------------------
- Floyd-Warshall: O(V³) — better when graph is dense (E ≈ V²)
- Johnson's:      O(V² log V + VE) — better for sparse graphs (E ≪ V²)

References
----------
Johnson, D. B. (1977). "Efficient algorithms for shortest paths in sparse
    networks." Journal of the ACM, 24(1), 1–13.
"""

from typing import Any, Dict, List, Optional, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    NegativeCycleError,
    validate_graph,
)


def johnson(
    graph: Union[nx.Graph, nx.DiGraph],
) -> Dict[str, Any]:
    """
    Compute all-pairs shortest paths using Johnson's algorithm.

    Handles graphs with negative edge weights (no negative cycles). For
    undirected graphs with any negative edge, a 2-cycle always forms a negative
    cycle, so :class:`NegativeCycleError` will be raised.

    Args:
        graph: NetworkX Graph or DiGraph. Edge weights are read from the
               'weight' attribute (defaults to 1 if missing).

    Returns:
        Dictionary with two keys:

        ``'distances'``
            Dict[node, Dict[node, float]] — dist[u][v] is the shortest
            distance from u to v. Unreachable pairs have distance
            ``float('inf')``.

        ``'predecessors'``
            Dict[node, Dict[node, node | None]] — pred[u][v] is the
            predecessor of v on the shortest path from u to v.

    Raises:
        EmptyGraphError:    If the graph has no nodes.
        NegativeCycleError: If a negative-weight cycle is detected during
                            the Bellman-Ford potential computation.

    Time Complexity:
        O(V² log V + VE) where V = vertices, E = edges.

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path.johnson import johnson
        >>>
        >>> G = nx.DiGraph()
        >>> G.add_edge('A', 'B', weight=3)
        >>> G.add_edge('A', 'C', weight=8)
        >>> G.add_edge('B', 'C', weight=2)
        >>> G.add_edge('C', 'D', weight=1)
        >>>
        >>> result = johnson(G)
        >>> print(result['distances']['A']['D'])   # 6  (A→B→C→D)
    """
    validate_graph(graph, "johnson")

    nodes = list(graph.nodes())

    # --- Step 1: add virtual source q ---
    # Use an object guaranteed not to clash with existing nodes.
    q = object()
    augmented = nx.DiGraph()
    augmented.add_nodes_from(nodes)
    augmented.add_node(q)

    # Copy existing edges (directed; undirected → both directions)
    if isinstance(graph, nx.DiGraph):
        for u, v, data in graph.edges(data=True):
            augmented.add_edge(u, v, weight=float(data.get('weight', 1)))
    else:
        for u, v, data in graph.edges(data=True):
            w = float(data.get('weight', 1))
            augmented.add_edge(u, v, weight=w)
            augmented.add_edge(v, u, weight=w)

    # Virtual source → every original node, weight 0
    for v in nodes:
        augmented.add_edge(q, v, weight=0.0)

    # --- Step 2: Bellman-Ford from q to get potentials h ---
    h = _bellman_ford_potentials(augmented, q, nodes)

    # --- Step 3 + 4 + 5: Dijkstra from each source in reweighted graph ---
    distances: Dict[Any, Dict[Any, float]] = {}
    predecessors: Dict[Any, Dict[Any, Optional[Any]]] = {}

    for src in nodes:
        d, pred = _dijkstra_reweighted(graph, src, h, nodes)
        distances[src] = d
        predecessors[src] = pred

    return {'distances': distances, 'predecessors': predecessors}


def johnson_path(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
) -> List[Any]:
    """
    Return the shortest path from *source* to *target* using Johnson's algorithm.

    Runs the full all-pairs computation internally. For many pair queries on
    the same graph, call :func:`johnson` once and use
    :func:`reconstruct_path` directly.

    Args:
        graph:  NetworkX Graph or DiGraph.
        source: Starting vertex.
        target: Destination vertex.

    Returns:
        List of nodes forming the shortest path, or ``[]`` if unreachable.

    Raises:
        EmptyGraphError:    If the graph has no nodes.
        NegativeCycleError: If a negative-weight cycle is detected.

    Example:
        >>> path = johnson_path(G, 'A', 'D')
        >>> print(path)   # ['A', 'B', 'C', 'D']
    """
    result = johnson(graph)
    pred = result['predecessors']
    dist = result['distances']

    if source not in dist or target not in dist[source]:
        return []
    if dist[source][target] == float('inf'):
        return []

    return reconstruct_path(pred, source, target)


def reconstruct_path(
    predecessors: Dict[Any, Dict[Any, Optional[Any]]],
    source: Any,
    target: Any,
) -> List[Any]:
    """
    Reconstruct the shortest path from *source* to *target* using the
    predecessor matrix returned by :func:`johnson`.

    Args:
        predecessors: The ``'predecessors'`` dict from :func:`johnson`.
        source:       Starting vertex.
        target:       Destination vertex.

    Returns:
        List of nodes on the shortest path, or ``[]`` if unreachable.
    """
    if source == target:
        return [source]
    if predecessors[source][target] is None:
        return []

    path = []
    current = target
    while current != source:
        path.append(current)
        current = predecessors[source][current]
        if current is None:
            return []
    path.append(source)
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _bellman_ford_potentials(
    augmented: nx.DiGraph,
    q: object,
    nodes: list,
) -> Dict[Any, float]:
    """
    Run Bellman-Ford from the virtual source *q* on the augmented graph.

    Returns h[v] = shortest distance from q to v (the Johnson potential).
    Raises NegativeCycleError if a negative cycle is detected.
    """
    INF = float('inf')
    dist: Dict[Any, float] = {v: INF for v in augmented.nodes()}
    dist[q] = 0.0
    pred: Dict[Any, Any] = {v: None for v in augmented.nodes()}

    n = augmented.number_of_nodes()
    edges = [(u, v, d.get('weight', 1)) for u, v, d in augmented.edges(data=True)]

    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
        if not updated:
            break

    # Negative-cycle check
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            # Reconstruct cycle for the error message
            cycle = _trace_cycle(pred, v, n)
            raise NegativeCycleError(source=v, cycle=cycle)

    return {v: dist[v] for v in nodes}


def _dijkstra_reweighted(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    h: Dict[Any, float],
    nodes: list,
) -> tuple:
    """
    Run Dijkstra on the h-reweighted graph from *source*.

    Edge weight reweighting: w'(u,v) = w(u,v) + h[u] - h[v] ≥ 0.
    After Dijkstra, convert back: dist[u][v] = d'[v] - h[source] + h[v].

    Returns (distances_dict, predecessors_dict) with original-weight distances.
    """
    import heapq

    INF = float('inf')
    d_prime: Dict[Any, float] = {v: INF for v in nodes}
    d_prime[source] = 0.0
    pred: Dict[Any, Optional[Any]] = {v: None for v in nodes}

    pq = [(0.0, source)]
    visited: set = set()

    # Build adjacency for efficiency
    if isinstance(graph, nx.DiGraph):
        def neighbors(u):
            for v, data in graph[u].items():
                yield v, float(data.get('weight', 1))
    else:
        def neighbors(u):
            for v, data in graph[u].items():
                yield v, float(data.get('weight', 1))

    while pq:
        cur_d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        for v, w in neighbors(u):
            w_prime = w + h[u] - h[v]
            new_d = cur_d + w_prime
            if new_d < d_prime[v]:
                d_prime[v] = new_d
                pred[v] = u
                heapq.heappush(pq, (new_d, v))

    # Convert back to true distances
    h_src = h[source]
    distances: Dict[Any, float] = {}
    for v in nodes:
        if d_prime[v] == INF:
            distances[v] = INF
        else:
            distances[v] = d_prime[v] - h_src + h[v]

    return distances, pred


def _trace_cycle(pred: Dict, entry: Any, n: int) -> List[Any]:
    """Walk n steps back to land inside the cycle, then trace it."""
    v = entry
    for _ in range(n):
        if pred[v] is None:
            return []
        v = pred[v]
    start = v
    cycle = []
    current = start
    while True:
        cycle.append(current)
        current = pred[current]
        if current == start or current is None:
            if current == start:
                cycle.append(current)
            break
        if len(cycle) > n:
            break
    cycle.reverse()
    return cycle
