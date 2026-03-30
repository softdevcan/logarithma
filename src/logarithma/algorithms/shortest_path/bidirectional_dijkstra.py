"""
Bidirectional Dijkstra Shortest Path Algorithm
===============================================

Bidirectional Dijkstra runs two simultaneous Dijkstra searches — a *forward*
search from the source and a *backward* search from the target — and terminates
when the two frontiers meet. For point-to-point queries on large graphs this
typically reduces the number of expanded nodes by roughly 50 % compared with
standard Dijkstra, making it well-suited for long-range routing.

Termination criterion
----------------------
The search stops when a node *u* is extracted from both the forward open set
and the backward open set. At that moment the best path seen so far (tracked
as ``mu``) is optimal. The stopping condition is:

    dist_f[u] + dist_b[u] >= mu

where dist_f / dist_b are the tentative distances from source / target.
This is the standard criterion proved correct in:

    Pohl, I. (1971). "Bi-directional Search." Machine Intelligence, 6, 127–140.

Backward search on directed graphs
------------------------------------
For a directed graph the backward search must follow edges in *reverse*
direction (i.e. it traverses the transposed graph). NetworkX provides
``graph.predecessors(v)`` for DiGraph, which gives exactly the nodes from
which an edge points *to* v, and the weight ``graph[u][v]['weight']``.

Time Complexity:  O((b + E/V) · d/2 log n) in practice — roughly half the
                  node expansions of standard Dijkstra for uniform graphs.
                  Worst-case is still O(E + V log V) but typical speedup
                  is 1.5–2.5× on road networks and random graphs.
Space Complexity: O(V)

Use cases
---------
- Point-to-point shortest path on large road networks
- Social network "degrees of separation"
- Any scenario where both endpoints are known in advance

References
----------
Pohl, I. (1971). "Bi-directional Search."
    Machine Intelligence, 6, 127–140.
Goldberg, A. V., & Harrelson, C. (2005). "Computing the Shortest Path:
    A* Search Meets Graph Theory." SODA 2005.
"""

import heapq
from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx


def bidirectional_dijkstra(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
) -> Dict[str, Any]:
    """
    Find the shortest path between *source* and *target* using bidirectional
    Dijkstra.

    For undirected graphs the backward search is identical to the forward
    search. For directed graphs the backward search follows reversed edges
    (predecessor traversal).

    Args:
        graph:  NetworkX Graph or DiGraph with non-negative edge weights.
                Missing 'weight' attributes default to 1.
        source: Starting vertex.
        target: Destination vertex.

    Returns:
        Dictionary with two keys:
            'distance': float — optimal distance from source to target,
                        or float('inf') if target is unreachable.
            'path':     List[node] — optimal path, or [] if unreachable.

    Raises:
        ValueError: If graph is empty, source/target not in graph, or a
                    negative edge weight is encountered.

    Time Complexity:
        O((V + E) log V) worst case; typically ~2× faster than standard
        Dijkstra for point-to-point queries.

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path.bidirectional_dijkstra import (
        ...     bidirectional_dijkstra
        ... )
        >>>
        >>> G = nx.path_graph(6, create_using=nx.DiGraph())
        >>> for u, v in G.edges():
        ...     G[u][v]['weight'] = 1
        >>>
        >>> result = bidirectional_dijkstra(G, 0, 5)
        >>> print(result['distance'])   # 5
        >>> print(result['path'])       # [0, 1, 2, 3, 4, 5]
    """
    # --- Validation ---
    if len(graph) == 0:
        raise ValueError("Graph is empty.")
    if source not in graph:
        raise ValueError(f"Source vertex '{source}' not found in graph.")
    if target not in graph:
        raise ValueError(f"Target vertex '{target}' not found in graph.")

    # Trivial case: source == target
    if source == target:
        return {'distance': 0.0, 'path': [source]}

    is_directed = isinstance(graph, nx.DiGraph)

    # --- Distance and predecessor tables ---
    # Forward  (from source)
    dist_f: Dict[Any, float] = {source: 0.0}
    pred_f: Dict[Any, Optional[Any]] = {source: None}

    # Backward (from target, following reversed edges)
    dist_b: Dict[Any, float] = {target: 0.0}
    pred_b: Dict[Any, Optional[Any]] = {target: None}

    # --- Priority queues ---
    counter = 0
    pq_f: List[Tuple[float, int, Any]] = [(0.0, counter, source)]
    pq_b: List[Tuple[float, int, Any]] = [(0.0, counter, target)]

    closed_f: set = set()
    closed_b: set = set()

    # mu = best path length found so far; meeting_node = node on that path
    mu: float = float('inf')
    meeting_node: Optional[Any] = None

    # --- Helper: relax one step from an open set ---
    def _relax(
        pq: List,
        dist_mine: Dict[Any, float],
        pred_mine: Dict[Any, Optional[Any]],
        closed_mine: set,
        dist_other: Dict[Any, float],
        reverse: bool,
    ) -> Optional[Any]:
        """
        Pop the best node, relax its neighbours, update mu.
        Returns the popped node (or None if queue is empty).
        """
        nonlocal mu, meeting_node, counter

        if not pq:
            return None

        d, _, u = heapq.heappop(pq)

        if u in closed_mine:
            return u   # stale entry — skip but signal the node

        closed_mine.add(u)

        # Check stopping condition BEFORE expanding
        if d >= mu:
            return u

        # Choose neighbor iterator: forward uses successors/neighbors,
        # backward on DiGraph uses predecessors (reversed edges).
        if reverse and is_directed:
            neighbors = list(graph.predecessors(u))
            def get_weight(nb, node):
                return graph[nb][node].get('weight', 1)
        else:
            neighbors = list(graph.neighbors(u))
            def get_weight(nb, node):
                return graph[node][nb].get('weight', 1)

        for v in neighbors:
            w = get_weight(v, u)
            if w < 0:
                raise ValueError(
                    f"Negative edge weight detected (weight={w}). "
                    "Bidirectional Dijkstra requires non-negative weights."
                )
            new_dist = dist_mine[u] + w
            if new_dist < dist_mine.get(v, float('inf')):
                dist_mine[v] = new_dist
                pred_mine[v] = u
                counter += 1
                heapq.heappush(pq, (new_dist, counter, v))

            # Update mu if v is already settled in the other direction
            if v in dist_other:
                candidate = dist_mine.get(v, float('inf')) + dist_other[v]
                if candidate < mu:
                    mu = candidate
                    meeting_node = v

        return u

    # --- Main loop: alternate forward / backward steps ---
    while pq_f or pq_b:
        # Stopping criterion: the minimum keys in both queues exceed mu
        min_f = pq_f[0][0] if pq_f else float('inf')
        min_b = pq_b[0][0] if pq_b else float('inf')

        if min_f + min_b >= mu:
            break

        # Expand the frontier with the smaller tentative distance
        if min_f <= min_b:
            _relax(pq_f, dist_f, pred_f, closed_f, dist_b, reverse=False)
        else:
            _relax(pq_b, dist_b, pred_b, closed_b, dist_f, reverse=True)

    if meeting_node is None or mu == float('inf'):
        return {'distance': float('inf'), 'path': []}

    path = _reconstruct_path(pred_f, pred_b, source, target, meeting_node)
    return {'distance': mu, 'path': path}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _reconstruct_path(
    pred_f: Dict[Any, Optional[Any]],
    pred_b: Dict[Any, Optional[Any]],
    source: Any,
    target: Any,
    meeting: Any,
) -> List[Any]:
    """
    Stitch together the forward and backward predecessor chains at *meeting*.

    Forward chain:  source → ... → meeting
    Backward chain: target → ... → meeting   (reversed → meeting → ... → target)
    """
    # Forward segment: source → meeting
    path_f: List[Any] = []
    node = meeting
    while node is not None:
        path_f.append(node)
        node = pred_f.get(node)
    path_f.reverse()

    # Backward segment: meeting → target
    path_b: List[Any] = []
    node = pred_b.get(meeting)
    while node is not None:
        path_b.append(node)
        node = pred_b.get(node)

    return path_f + path_b
