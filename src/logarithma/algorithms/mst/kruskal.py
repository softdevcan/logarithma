"""
Kruskal's Minimum Spanning Tree
================================

Builds the MST (or MSF for disconnected graphs) by sorting all edges
by weight and greedily adding non-cycle-forming edges using Union-Find
with path compression and union-by-rank.

Time Complexity : O(E log E)
Space Complexity: O(V + E)
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    validate_graph,
    validate_undirected,
)


# ---------------------------------------------------------------------------
# Union-Find (Disjoint Set Union)
# ---------------------------------------------------------------------------

class _UnionFind:
    """Union-Find with path compression and union-by-rank."""

    def __init__(self, nodes):
        self._parent: Dict[Any, Any] = {n: n for n in nodes}
        self._rank: Dict[Any, int] = {n: 0 for n in nodes}

    def find(self, x: Any) -> Any:
        """Find root with path compression."""
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]  # path halving
            x = self._parent[x]
        return x

    def union(self, x: Any, y: Any) -> bool:
        """Union by rank.  Returns False if x and y are already in the same
        component (i.e., adding this edge would create a cycle)."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx
        self._parent[ry] = rx
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
        return True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def kruskal_mst(
    graph: nx.Graph,
    weight: str = 'weight',
) -> Dict[str, Any]:
    """Kruskal's Minimum Spanning Tree (or Forest) algorithm.

    Args:
        graph:  Undirected weighted NetworkX graph (nx.Graph).
                Passing a DiGraph raises UndirectedGraphRequiredError.
        weight: Edge attribute name for weights.  Missing attributes
                default to 1.

    Returns:
        Dictionary with keys:
          'mst_edges'      : List[Tuple[Any, Any, float]] — (u, v, weight)
          'total_weight'   : float — sum of MST edge weights
          'num_components' : int   — 1 for a spanning tree, >1 for a forest

    Raises:
        EmptyGraphError:              Graph has no nodes.
        UndirectedGraphRequiredError: A DiGraph was supplied.

    Time Complexity: O(E log E)
    """
    validate_undirected(graph, 'kruskal_mst')
    validate_graph(graph, 'kruskal_mst')

    uf = _UnionFind(graph.nodes())

    # Sort edges by weight (ascending)
    sorted_edges: List[Tuple[float, Any, Any]] = sorted(
        (data.get(weight, 1), u, v)
        for u, v, data in graph.edges(data=True)
    )

    mst_edges: List[Tuple[Any, Any, float]] = []
    total_weight: float = 0.0

    for w, u, v in sorted_edges:
        if uf.union(u, v):
            mst_edges.append((u, v, w))
            total_weight += w

    # Count connected components (roots in union-find)
    roots = {uf.find(n) for n in graph.nodes()}
    num_components = len(roots)

    return {
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'num_components': num_components,
    }
