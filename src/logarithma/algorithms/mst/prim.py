"""
Prim's Minimum Spanning Tree
=============================

Builds the MST (or MSF for disconnected graphs) by greedily expanding
the current tree using a min-heap of crossing edges.

Time Complexity : O(E + V log V) with binary heap
Space Complexity: O(V + E)
"""

import heapq
from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    validate_graph,
    validate_source,
    validate_undirected,
)


def prim_mst(
    graph: nx.Graph,
    start: Optional[Any] = None,
    weight: str = 'weight',
) -> Dict[str, Any]:
    """Prim's Minimum Spanning Tree (or Forest) algorithm.

    Args:
        graph:  Undirected weighted NetworkX graph (nx.Graph).
                Passing a DiGraph raises UndirectedGraphRequiredError.
        start:  Starting vertex.  If None, the first node in
                graph.nodes() is used.
        weight: Edge attribute name for weights.  Missing attributes
                default to 1.

    Returns:
        Dictionary with keys:
          'mst_edges'      : List[Tuple[Any, Any, float]] — (u, v, weight)
          'total_weight'   : float — sum of MST edge weights
          'num_components' : int   — 1 for a spanning tree, >1 for a forest

    Raises:
        EmptyGraphError:              Graph has no nodes.
        NodeNotFoundError:            start node not in graph.
        UndirectedGraphRequiredError: A DiGraph was supplied.

    Time Complexity: O(E + V log V)
    """
    validate_undirected(graph, 'prim_mst')
    validate_graph(graph, 'prim_mst')

    if start is None:
        start = next(iter(graph.nodes()))
    else:
        validate_source(graph, start)

    mst_edges: List[Tuple[Any, Any, float]] = []
    total_weight: float = 0.0
    visited: set = set()

    def _run_from(source: Any) -> None:
        """Grow the MST from a single source node."""
        visited.add(source)
        # heap entries: (weight, u, v)
        heap: List[Tuple[float, Any, Any]] = []
        for nb, data in graph[source].items():
            heapq.heappush(heap, (data.get(weight, 1), source, nb))

        while heap:
            w, u, v = heapq.heappop(heap)
            if v in visited:
                continue
            visited.add(v)
            mst_edges.append((u, v, w))
            nonlocal total_weight
            total_weight += w
            for nb, data in graph[v].items():
                if nb not in visited:
                    heapq.heappush(heap, (data.get(weight, 1), v, nb))

    # Start from the requested node
    _run_from(start)

    # Handle disconnected graph — process remaining components
    for node in graph.nodes():
        if node not in visited:
            _run_from(node)

    return {
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'num_components': _count_components(graph, mst_edges),
    }


def _count_components(graph: nx.Graph, mst_edges: List[Tuple]) -> int:
    """Count connected components in the MST/MSF."""
    if not mst_edges:
        return graph.number_of_nodes()

    parent: Dict[Any, Any] = {n: n for n in graph.nodes()}

    def find(x: Any) -> Any:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v, _ in mst_edges:
        pu, pv = find(u), find(v)
        if pu != pv:
            parent[pu] = pv

    return len({find(n) for n in graph.nodes()})


