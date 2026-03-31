"""
Topological Sort
================

Topological ordering of a Directed Acyclic Graph (DAG).

Two methods are provided:
  - 'dfs'  : DFS-based post-order reversal (O(V + E))
  - 'kahn' : Kahn's BFS/in-degree algorithm (O(V + E))

Both raise NotDAGError if a cycle is detected.
"""

from collections import deque
from typing import Any, Dict, List, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    InvalidModeError,
    NotDAGError,
    UndirectedGraphRequiredError,
    validate_graph,
)

_VALID_METHODS = ['dfs', 'kahn']


def topological_sort(
    graph: nx.DiGraph,
    method: str = 'dfs',
) -> List[Any]:
    """Return a topological ordering of the nodes in a DAG.

    Args:
        graph:  Directed graph (nx.DiGraph).  Passing an undirected graph
                raises UndirectedGraphRequiredError.
        method: 'dfs' (default) or 'kahn'.  Raises InvalidModeError for any
                other value.

    Returns:
        List of nodes in topological order (earlier nodes have no incoming
        edges from later nodes).

    Raises:
        EmptyGraphError:               Graph has no nodes.
        UndirectedGraphRequiredError:  An nx.Graph was supplied.
        InvalidModeError:              Unknown method string.
        NotDAGError:                   Graph contains a cycle.

    Time Complexity: O(V + E) for both methods.
    """
    if not isinstance(graph, nx.DiGraph):
        raise UndirectedGraphRequiredError('topological_sort')
    validate_graph(graph, 'topological_sort')
    if method not in _VALID_METHODS:
        raise InvalidModeError(method, _VALID_METHODS, 'method')

    if method == 'dfs':
        return _topological_sort_dfs(graph)
    return _topological_sort_kahn(graph)


# ---------------------------------------------------------------------------
# DFS-based implementation (iterative to avoid recursion limit)
# ---------------------------------------------------------------------------

def _topological_sort_dfs(graph: nx.DiGraph) -> List[Any]:
    """Iterative DFS post-order reversal."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[Any, int] = {n: WHITE for n in graph.nodes()}
    result: List[Any] = []

    for start in graph.nodes():
        if color[start] != WHITE:
            continue

        # Each stack frame: (node, iterator_over_successors, entered_gray)
        stack = [(start, iter(graph.successors(start)), False)]
        color[start] = GRAY

        while stack:
            node, neighbors, _ = stack[-1]
            try:
                nb = next(neighbors)
                if color[nb] == WHITE:
                    color[nb] = GRAY
                    stack.append((nb, iter(graph.successors(nb)), False))
                elif color[nb] == GRAY:
                    # Back edge → cycle detected; reconstruct cycle path
                    cycle = [nb]
                    for n, _, __ in reversed(stack):
                        cycle.append(n)
                        if n == nb:
                            break
                    raise NotDAGError('topological_sort', list(reversed(cycle)))
                # BLACK: already fully processed — skip
            except StopIteration:
                # Node fully explored — add to result
                stack.pop()
                color[node] = BLACK
                result.append(node)

    result.reverse()
    return result


# ---------------------------------------------------------------------------
# Kahn's algorithm (BFS / in-degree based)
# ---------------------------------------------------------------------------

def _topological_sort_kahn(graph: nx.DiGraph) -> List[Any]:
    """Kahn's algorithm: repeatedly remove nodes with in-degree 0."""
    in_degree: Dict[Any, int] = dict(graph.in_degree())
    queue: deque = deque(n for n, d in in_degree.items() if d == 0)
    result: List[Any] = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for successor in graph.successors(node):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    if len(result) != graph.number_of_nodes():
        # Some nodes were never reached → cycle exists
        raise NotDAGError('topological_sort')

    return result
