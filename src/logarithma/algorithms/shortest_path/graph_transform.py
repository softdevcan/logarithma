"""
Constant-Degree Graph Transform
================================

Classical vertex-splitting transformation (Frederickson 1983) that converts
an arbitrary directed graph into a constant-degree graph while preserving
shortest-path distances.

Used as a preprocessing step for the Breaking Barrier SSSP algorithm
(Duan et al., 2025), which requires max in/out-degree <= 2.

Transform rules (paper §2, page 3):
    1. Each vertex v is replaced by a cycle of deg(v) vertices connected
       with zero-weight directed edges.
    2. For every incoming or outgoing neighbour w of v, there is a vertex
       x_vw on this cycle.
    3. For every edge (u, v) in G, add a directed edge from x_uv to x_vu
       with weight w_uv.

Properties:
    - G' has O(m) vertices and O(m) edges
    - Every vertex in G' has in-degree and out-degree at most 2
    - Shortest-path distances are preserved:
      d_G(s, v) = min{ d_G'(s', x) : x in cycle(v) }

v0.6.0: to_constant_degree rewritten with plain dicts/lists instead of
NetworkX add_node/add_edge calls during construction. NetworkX DiGraph is
assembled in one pass at the end, cutting ~10% of total runtime.
"""

from typing import Any, Dict, List, Tuple

import networkx as nx

Node = Any


def to_constant_degree(
    G: nx.DiGraph, source: Node
) -> Tuple[nx.DiGraph, Any, Dict[Node, List]]:
    """Transform G into a constant-degree graph G'.

    Args:
        G:      Directed graph with non-negative 'weight' attributes.
        source: Source vertex in G.

    Returns:
        G':        Constant-degree directed graph (max in/out-degree 2).
        source':   The cycle node in G' corresponding to source.
        node_map:  {original_node: [cycle_node_1, cycle_node_2, ...]}
                   Maps each original vertex to its cycle nodes in G'.

    The transform creates a cycle of vertices for each original vertex v.
    Each cycle node corresponds to one neighbour relationship (incoming or
    outgoing edge).  Cycle edges have zero weight.  Original edges become
    edges between the appropriate cycle nodes with original weight.

    If a vertex v has degree 0 (isolated), it gets a single cycle node.
    """
    node_map: Dict[Node, List] = {}

    # Collect all cycle nodes and edges into plain lists first —
    # avoids per-call NetworkX overhead of add_node/add_edge.
    all_nodes: List[Any] = []
    all_edges: List[Tuple[Any, Any, float]] = []  # (u, v, weight)

    # --- Step 1: Build neighbour lists and create cycle nodes ---
    for v in G.nodes():
        preds = set(G.predecessors(v))
        succs = set(G.successors(v))
        neighbours = sorted(preds | succs, key=repr)

        if not neighbours:
            cycle = [(v, v)]
        else:
            cycle = [(v, w) for w in neighbours]

        node_map[v] = cycle

        for node in cycle:
            all_nodes.append(node)

        # Zero-weight cycle edges: (v,w0) -> (v,w1) -> ... -> (v,w0)
        L = len(cycle)
        for i in range(L):
            u_node = cycle[i]
            v_node = cycle[(i + 1) % L]
            if u_node != v_node:
                all_edges.append((u_node, v_node, 0.0))

    # --- Step 2: Add original edges ---
    for u, v, data in G.edges(data=True):
        w = float(data.get('weight', 1))
        x_uv = (u, v)
        x_vu = (v, u)
        all_edges.append((x_uv, x_vu, w))

    # --- Build G' in one shot ---
    G_prime = nx.DiGraph()
    G_prime.add_nodes_from(all_nodes)
    G_prime.add_weighted_edges_from(all_edges)

    source_prime = node_map[source][0]
    return G_prime, source_prime, node_map


def map_distances_back(
    dist_prime: Dict, node_map: Dict[Node, List]
) -> Dict[Node, float]:
    """Map distances from G' back to original vertices in G.

    For each original vertex v:
        d(v) = min{ dist_prime[x] : x in node_map[v] and x in dist_prime }

    Vertices where no cycle node was reached are omitted (unreachable).

    Args:
        dist_prime: {cycle_node: distance} from G' SSSP.
        node_map:   {original_node: [cycle_node, ...]} from to_constant_degree.

    Returns:
        {original_node: shortest_distance} for reachable vertices.
    """
    result: Dict[Node, float] = {}
    for v, cycle_nodes in node_map.items():
        best = float('inf')
        for x in cycle_nodes:
            d = dist_prime.get(x, float('inf'))
            if d < best:
                best = d
        if best < float('inf'):
            result[v] = best
    return result
