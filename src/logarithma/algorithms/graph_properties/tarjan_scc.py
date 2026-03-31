"""
Tarjan's Strongly Connected Components
=======================================

Iterative implementation of Tarjan's SCC algorithm.
Returns SCCs in reverse topological order of the condensation DAG
(sink SCC appears first).

Time Complexity : O(V + E)
Space Complexity: O(V)
"""

from typing import Any, Dict, List, Optional, Union

import networkx as nx

from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    validate_graph,
)


def tarjan_scc(graph: Union[nx.DiGraph, nx.Graph]) -> List[List[Any]]:
    """Find all Strongly Connected Components using Tarjan's algorithm.

    Works on both directed and undirected graphs.  For undirected graphs
    every connected component is trivially an SCC, so the result equals
    the connected components.

    Args:
        graph: A NetworkX graph (directed or undirected).

    Returns:
        List of SCCs, each SCC being a list of nodes.  Returned in
        *reverse topological order* of the condensation DAG — the sink
        SCC (no outgoing edges in the condensation) comes first.
        Single-node SCCs without self-loops are included.

    Raises:
        EmptyGraphError: Graph has no nodes.

    Time Complexity: O(V + E)
    """
    validate_graph(graph, 'tarjan_scc')

    index_counter = [0]
    stack: List[Any] = []
    on_stack: Dict[Any, bool] = {}
    index: Dict[Any, int] = {}
    lowlink: Dict[Any, int] = {}
    sccs: List[List[Any]] = []

    # Use successors() for DiGraph, neighbors() for undirected Graph
    def _adj(node: Any):
        if graph.is_directed():
            return graph.successors(node)
        return graph.neighbors(node)

    # Iterative Tarjan using explicit call stack.
    # Each frame: (node, iterator_of_successors)
    for start in graph.nodes():
        if start in index:
            continue

        call_stack = [(start, iter(_adj(start)))]
        index[start] = lowlink[start] = index_counter[0]
        index_counter[0] += 1
        stack.append(start)
        on_stack[start] = True

        while call_stack:
            node, neighbors = call_stack[-1]
            advanced = False
            for nb in neighbors:
                if nb not in index:
                    # Tree edge — recurse
                    index[nb] = lowlink[nb] = index_counter[0]
                    index_counter[0] += 1
                    stack.append(nb)
                    on_stack[nb] = True
                    call_stack.append((nb, iter(_adj(nb))))
                    advanced = True
                    break
                elif on_stack.get(nb, False):
                    # Back edge — update lowlink
                    if lowlink[node] > index[nb]:
                        lowlink[node] = index[nb]

            if not advanced:
                # All successors processed — pop this frame
                call_stack.pop()
                if call_stack:
                    parent = call_stack[-1][0]
                    if lowlink[parent] > lowlink[node]:
                        lowlink[parent] = lowlink[node]

                # If this node is a root of an SCC
                if lowlink[node] == index[node]:
                    scc: List[Any] = []
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        scc.append(w)
                        if w == node:
                            break
                    sccs.append(scc)

    return sccs
