"""
Maximum Flow — Edmonds-Karp Algorithm
======================================

Edmonds-Karp is Ford-Fulkerson with BFS for augmenting path selection,
giving a deterministic O(V * E^2) worst-case complexity independent of
edge capacities.

Supports both directed and undirected graphs.  For undirected graphs
each edge is treated as having capacity in both directions.

Time Complexity : O(V * E^2)
Space Complexity: O(V + E)
"""

from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    InvalidModeError,
    validate_graph,
    validate_source,
    validate_target,
)

_VALID_METHODS = ['edmonds_karp', 'ford_fulkerson']


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def max_flow(
    graph: Union[nx.DiGraph, nx.Graph],
    source: Any,
    sink: Any,
    capacity: str = 'capacity',
    method: str = 'edmonds_karp',
) -> Dict[str, Any]:
    """Compute the maximum flow from source to sink.

    Args:
        graph:    Directed or undirected NetworkX graph with edge capacity
                  attributes.  Missing capacity defaults to 1.
        source:   Flow source node.
        sink:     Flow sink node.
        capacity: Edge attribute name for capacity.  Default: 'capacity'.
        method:   Algorithm variant.  'edmonds_karp' (default) or
                  'ford_fulkerson' (alias for the same implementation).

    Returns:
        Dictionary with keys:
          'flow_value'    : float — total maximum flow from source to sink
          'flow_dict'     : Dict[Any, Dict[Any, float]] — flow on each edge
          'residual_graph': nx.DiGraph — residual network after max flow

    Raises:
        EmptyGraphError:   Graph has no nodes.
        NodeNotFoundError: source or sink not in graph.
        InvalidModeError:  Unknown method string.

    Time Complexity: O(V * E^2)
    """
    validate_graph(graph, 'max_flow')
    validate_source(graph, source)
    validate_target(graph, sink)
    if method not in _VALID_METHODS:
        raise InvalidModeError(method, _VALID_METHODS, 'method')

    # Trivial case
    if source == sink:
        flow_dict = {n: {nb: 0.0 for nb in graph.neighbors(n)} for n in graph.nodes()}
        return {
            'flow_value': 0.0,
            'flow_dict': flow_dict,
            'residual_graph': _build_residual(graph, capacity),
        }

    residual = _build_residual(graph, capacity)
    flow_value = _edmonds_karp(residual, source, sink)

    # Build flow_dict from residual (original capacity - residual capacity)
    flow_dict = _extract_flow_dict(graph, residual, capacity)

    return {
        'flow_value': flow_value,
        'flow_dict': flow_dict,
        'residual_graph': residual,
    }


# ---------------------------------------------------------------------------
# Residual graph construction
# ---------------------------------------------------------------------------

def _build_residual(
    graph: Union[nx.DiGraph, nx.Graph],
    capacity_attr: str,
) -> nx.DiGraph:
    """Build directed residual graph from the original graph."""
    R = nx.DiGraph()
    R.add_nodes_from(graph.nodes())

    if graph.is_directed():
        for u, v, data in graph.edges(data=True):
            cap = data.get(capacity_attr, 1)
            if R.has_edge(u, v):
                R[u][v]['capacity'] += cap
            else:
                R.add_edge(u, v, capacity=cap, flow=0.0)
            # Backward edge
            if not R.has_edge(v, u):
                R.add_edge(v, u, capacity=0.0, flow=0.0)
    else:
        # Undirected: each edge has capacity in both directions
        for u, v, data in graph.edges(data=True):
            cap = data.get(capacity_attr, 1)
            if R.has_edge(u, v):
                R[u][v]['capacity'] += cap
            else:
                R.add_edge(u, v, capacity=cap, flow=0.0)
            if R.has_edge(v, u):
                R[v][u]['capacity'] += cap
            else:
                R.add_edge(v, u, capacity=cap, flow=0.0)

    return R


# ---------------------------------------------------------------------------
# BFS augmenting path (Edmonds-Karp)
# ---------------------------------------------------------------------------

def _bfs_find_path(
    residual: nx.DiGraph,
    source: Any,
    sink: Any,
) -> Optional[List[Any]]:
    """BFS over residual graph to find an augmenting path.

    Returns list of nodes from source to sink, or None if unreachable.
    Only traverses edges with residual capacity > 0.
    """
    parent: Dict[Any, Any] = {source: None}
    queue: deque = deque([source])

    while queue:
        node = queue.popleft()
        if node == sink:
            # Reconstruct path
            path = []
            cur = sink
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path

        for nb in residual.successors(node):
            if nb not in parent and residual[node][nb]['capacity'] > 0:
                parent[nb] = node
                queue.append(nb)

    return None


# ---------------------------------------------------------------------------
# Edmonds-Karp main loop
# ---------------------------------------------------------------------------

def _edmonds_karp(residual: nx.DiGraph, source: Any, sink: Any) -> float:
    """Augment along BFS paths until no augmenting path exists."""
    total_flow = 0.0

    while True:
        path = _bfs_find_path(residual, source, sink)
        if path is None:
            break

        # Find bottleneck (minimum residual capacity along path)
        bottleneck = min(
            residual[path[i]][path[i + 1]]['capacity']
            for i in range(len(path) - 1)
        )

        # Update residual capacities
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v]['capacity'] -= bottleneck
            residual[u][v]['flow'] = residual[u][v].get('flow', 0.0) + bottleneck
            residual[v][u]['capacity'] += bottleneck

        total_flow += bottleneck

    return total_flow


# ---------------------------------------------------------------------------
# Extract flow_dict from residual
# ---------------------------------------------------------------------------

def _extract_flow_dict(
    graph: Union[nx.DiGraph, nx.Graph],
    residual: nx.DiGraph,
    capacity_attr: str,
) -> Dict[Any, Dict[Any, float]]:
    """Build a flow_dict matching the original graph's edge structure."""
    flow_dict: Dict[Any, Dict[Any, float]] = {n: {} for n in graph.nodes()}

    if graph.is_directed():
        for u, v, data in graph.edges(data=True):
            cap = data.get(capacity_attr, 1)
            if residual.has_edge(u, v):
                used = cap - residual[u][v]['capacity']
                flow_dict[u][v] = max(0.0, used)
            else:
                flow_dict[u][v] = 0.0
    else:
        for u, v, data in graph.edges(data=True):
            cap = data.get(capacity_attr, 1)
            if residual.has_edge(u, v):
                used = cap - residual[u][v]['capacity']
                flow_dict[u][v] = max(0.0, used)
                flow_dict.setdefault(v, {})[u] = max(0.0, used)
            else:
                flow_dict[u][v] = 0.0
                flow_dict.setdefault(v, {})[u] = 0.0

    return flow_dict
