"""
Floyd-Warshall All-Pairs Shortest Path Algorithm
=================================================

Dynamic programming algorithm that computes shortest paths between *all pairs*
of vertices in a weighted graph. Works with both positive and negative edge
weights, and detects negative-weight cycles.

Algorithm sketch
----------------
Let dist[i][j][k] = shortest path from i to j using only vertices {1..k}
as intermediate nodes.

Base case (k=0):
    dist[i][j][0] = weight(i,j) if edge exists, 0 if i==j, ∞ otherwise

Recurrence:
    dist[i][j][k] = min(dist[i][j][k-1],
                        dist[i][k][k-1] + dist[k][j][k-1])

In-place update (standard implementation uses a single 2-D matrix):
    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

Negative-cycle detection
------------------------
After running the algorithm, if dist[v][v] < 0 for any vertex v, a
negative-weight cycle exists. No meaningful all-pairs distances can be
returned in that case.

Time Complexity:  O(V³)
Space Complexity: O(V²)

Suitable for
------------
- Dense graphs where O(V²) storage is acceptable
- Graphs with negative edge weights (no negative cycles)
- Computing graph diameter, transitive closure, eccentricity

Not suitable for
----------------
- Very large sparse graphs (prefer Johnson's O(V² log V + VE))
- Graphs with negative-weight cycles

References
----------
Floyd, R. W. (1962). "Algorithm 97: Shortest path."
    Communications of the ACM, 5(6), 345.
Warshall, S. (1962). "A theorem on Boolean matrices."
    Journal of the ACM, 9(1), 11–12.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    NegativeCycleError,
    validate_graph,
)


def floyd_warshall(
    graph: Union[nx.Graph, nx.DiGraph],
) -> Dict[str, Any]:
    """
    Compute all-pairs shortest paths using the Floyd-Warshall algorithm.

    Works with directed and undirected graphs. Supports negative edge weights
    but raises :class:`NegativeCycleError` if a negative-weight cycle exists.

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
            predecessor of v on the shortest path from u to v. Used for
            path reconstruction. ``None`` means no path or u == v.

    Raises:
        EmptyGraphError:    If the graph has no nodes.
        NegativeCycleError: If a negative-weight cycle is detected
                            (dist[v][v] < 0 for some vertex v).

    Time Complexity:
        O(V³) where V = number of vertices.

    Space Complexity:
        O(V²)

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path.floyd_warshall import floyd_warshall
        >>>
        >>> G = nx.DiGraph()
        >>> G.add_edge('A', 'B', weight=3)
        >>> G.add_edge('A', 'C', weight=8)
        >>> G.add_edge('B', 'C', weight=2)
        >>> G.add_edge('C', 'D', weight=1)
        >>> G.add_edge('B', 'D', weight=7)
        >>>
        >>> result = floyd_warshall(G)
        >>> print(result['distances']['A']['D'])   # 6  (A→B→C→D)
        >>> path = floyd_warshall_path(G, 'A', 'D')
        >>> print(path)  # ['A', 'B', 'C', 'D']
    """
    validate_graph(graph, "floyd_warshall")

    nodes = list(graph.nodes())
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}

    INF = float('inf')

    # Initialise distance and predecessor matrices
    dist = [[INF] * n for _ in range(n)]
    pred = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0.0

    # Fill in edge weights
    if isinstance(graph, nx.DiGraph):
        for u, v, data in graph.edges(data=True):
            i, j = idx[u], idx[v]
            w = float(data.get('weight', 1))
            if w < dist[i][j]:          # keep minimum if parallel edges
                dist[i][j] = w
                pred[i][j] = i
    else:
        for u, v, data in graph.edges(data=True):
            i, j = idx[u], idx[v]
            w = float(data.get('weight', 1))
            if w < dist[i][j]:
                dist[i][j] = w
                pred[i][j] = i
            if w < dist[j][i]:
                dist[j][i] = w
                pred[j][i] = j

    # Main DP loop
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                through_k = dist[i][k] + dist[k][j]
                if through_k < dist[i][j]:
                    dist[i][j] = through_k
                    pred[i][j] = pred[k][j]

    # Negative-cycle detection: dist[v][v] < 0 for any v
    for i in range(n):
        if dist[i][i] < 0:
            raise NegativeCycleError(
                source=nodes[i],
                cycle=None,
            )

    # Convert back to node-keyed dicts
    distances: Dict[Any, Dict[Any, float]] = {}
    predecessors: Dict[Any, Dict[Any, Optional[Any]]] = {}

    for i, u in enumerate(nodes):
        distances[u] = {}
        predecessors[u] = {}
        for j, v in enumerate(nodes):
            distances[u][v] = dist[i][j]
            p = pred[i][j]
            predecessors[u][v] = nodes[p] if p is not None else None

    return {'distances': distances, 'predecessors': predecessors}


def floyd_warshall_path(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
) -> List[Any]:
    """
    Return the shortest path from *source* to *target* using Floyd-Warshall.

    Runs the full all-pairs computation internally. If you need paths for
    many pairs, call :func:`floyd_warshall` once and use
    :func:`reconstruct_path` directly.

    Args:
        graph:  NetworkX Graph or DiGraph.
        source: Starting vertex.
        target: Destination vertex.

    Returns:
        List of nodes forming the shortest path from source to target,
        or an empty list if target is unreachable from source.

    Raises:
        EmptyGraphError:    If the graph has no nodes.
        NegativeCycleError: If a negative-weight cycle is detected.

    Example:
        >>> path = floyd_warshall_path(G, 'A', 'D')
        >>> print(path)   # ['A', 'B', 'C', 'D']
    """
    result = floyd_warshall(graph)
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
    predecessor matrix returned by :func:`floyd_warshall`.

    Args:
        predecessors: The ``'predecessors'`` dict from :func:`floyd_warshall`.
        source:       Starting vertex.
        target:       Destination vertex.

    Returns:
        List of nodes on the shortest path, or ``[]`` if unreachable.

    Example:
        >>> result = floyd_warshall(G)
        >>> path = reconstruct_path(result['predecessors'], 'A', 'D')
    """
    if predecessors[source][target] is None:
        return [] if source != target else [source]

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
