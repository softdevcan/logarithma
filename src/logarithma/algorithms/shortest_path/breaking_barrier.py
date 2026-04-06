"""
Breaking the Sorting Barrier SSSP
==================================

Deterministic O(m log^{2/3} n) single-source shortest path algorithm for
directed graphs with real non-negative edge weights.

Based on:
    Duan, Mao, Mao, Shu, Yin (2025)
    "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths"
    arXiv:2504.17033v2

Algorithm Overview:
    Merges Dijkstra (priority queue, sorts by distance) and Bellman-Ford
    (relaxes all edges for k steps, no sorting) via recursive partitioning.

    The key insight: Dijkstra's frontier S can grow to Θ(n) vertices,
    forcing Ω(n log n) sorting. This algorithm shrinks S to |S|/k "pivots"
    via k-step Bellman-Ford, reducing per-vertex cost from Θ(log n) to
    log n / log^{Ω(1)}(n).

    Three components (Algorithms 1-3 in the paper):
        - FindPivots(B, S)      — reduces S to |S|/k pivots
        - BaseCase(B, S)        — mini Dijkstra (l=0)
        - BMSSP(l, B, S)        — recursive driver

    Parameters:
        k = floor(log^{1/3}(n))
        t = floor(log^{2/3}(n))
        l = ceil(log(n) / t)    at top level, B = inf

Time Complexity: O(m log^{2/3} n)
Space Complexity: O(n + m)

Data structure D (Lemma 3.3):
    Implemented by BlockHeap in block_heap.py — a two-sequence block
    linked list (D0 for BatchPrepend, D1 for Insert) with a SortedList-based
    BST tracking per-block upper bounds in D1.  Supports Insert, BatchPrepend,
    and Pull in amortized O(max{1, log(N/M)}) time.

v0.6.0 optimizations (pure-Python tier):
    - Node ID mapping: all original nodes mapped to contiguous integers 0..n-1.
      This eliminates repr() calls in tiebreaking (was ~11% of runtime).
    - alpha array: pre-allocated list instead of dict, removes .get() overhead.
    - dist_est array: pre-allocated list, O(1) index vs dict lookup.
    - to_constant_degree rewritten with plain dicts — avoids NetworkX add_edge
      overhead during transform (was ~10% of runtime).

v0.6.0 Cython tier (optional):
    If breaking_barrier_core.so/.pyd is present (built via setup_ext.py),
    the hot-path functions (_should_relax, _find_pivots, _base_case, _bmssp)
    run as compiled C code with typed memoryviews.  Falls back to pure Python
    automatically when the extension is not compiled.
"""

import heapq
import math
from typing import Any, Dict, List, Tuple

import networkx as nx

from logarithma.algorithms.exceptions import (
    validate_graph,
    validate_source,
)
from logarithma.algorithms.shortest_path.block_heap import BlockHeap
from logarithma.algorithms.shortest_path.graph_transform import (
    to_constant_degree,
    map_distances_back,
)

# ---------------------------------------------------------------------------
# Optional Cython acceleration
# ---------------------------------------------------------------------------

try:
    from logarithma.algorithms.shortest_path.breaking_barrier_core import (
        bmssp_run as _bmssp_run_cy,
    )
    _CYTHON_AVAILABLE = True
except ImportError:
    _CYTHON_AVAILABLE = False

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Node = Any
Dist = float
DistMap = Dict[Node, Dist]
# Adjacency list: node → list of (neighbour, weight) — built once at entry
AdjList = Dict[Node, List[Tuple[Node, float]]]
PredMap = Dict[Node, Any]   # PRED[v] → predecessor node or None
AlphaMap = Dict[Node, int]  # α[v] → hop count


# ---------------------------------------------------------------------------
# Integer-mapped core — all internal nodes are contiguous ints 0..n-1
# ---------------------------------------------------------------------------

def _build_int_graph(G_prime: nx.DiGraph):
    """Map G' nodes to integers 0..n-1 and build flat adjacency lists.

    Returns:
        n          : number of nodes
        adj        : list of lists — adj[u] = [(v, weight), ...]
        node_to_id : dict mapping G' node → int id
        id_to_node : list mapping int id → G' node
    """
    nodes = list(G_prime.nodes())
    n = len(nodes)
    node_to_id: Dict[Any, int] = {node: i for i, node in enumerate(nodes)}
    id_to_node: List[Any] = nodes

    # Pre-allocate adjacency as list-of-lists
    adj: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
    nti = node_to_id  # local alias — avoids repeated global lookup
    raw = G_prime._adj
    for u_node in nodes:
        u = nti[u_node]
        nbrs = raw[u_node]
        adj_u = adj[u]
        for v_node, data in nbrs.items():
            adj_u.append((nti[v_node], float(data.get('weight', 1))))

    return n, adj, node_to_id, id_to_node


# ---------------------------------------------------------------------------
# Assumption 2.1 — Lexicographic tiebreaking (§2, p.4)
# Inline version: nodes are ints, alpha/dist_est are lists → no dict overhead
# ---------------------------------------------------------------------------

def _should_relax_int(
    candidate: float,
    v: int,
    u: int,
    dist_est: List[float],
    pred: List[int],
    alpha: List[int],
) -> bool:
    """Assumption 2.1 tiebreaking with integer node IDs (no repr calls).

    Returns True if the path through u to v is "shorter" under the
    lexicographic tuple ordering ⟨distance, hop_count, node_id⟩.
    """
    d_v = dist_est[v]
    if candidate < d_v:
        return True
    if candidate > d_v:
        return False
    # candidate == d_v → tiebreak by hop count, then integer node ID
    new_alpha = alpha[u] + 1
    old_alpha = alpha[v]
    if new_alpha < old_alpha:
        return True
    if new_alpha > old_alpha:
        return False
    # Same distance, same hop count → compare integer IDs (no repr)
    pv = pred[v]
    if pv == -1:
        return True  # v has no predecessor yet → relax
    return u < pv


# ---------------------------------------------------------------------------
# Parameter helpers
# ---------------------------------------------------------------------------

def _compute_params(n: int) -> Tuple[int, int, int]:
    """Return (k, t, l) for a graph with n vertices."""
    if n <= 1:
        return 1, 1, 1
    ln_n = math.log(n)
    k = max(1, int(ln_n ** (1 / 3)))
    t = max(1, int(ln_n ** (2 / 3)))
    l = max(1, math.ceil(math.log2(n) / t))
    return k, t, l


# ---------------------------------------------------------------------------
# Algorithm 1 — FindPivots (integer-node variant)
# ---------------------------------------------------------------------------

def _find_pivots_int(
    B: float,
    S: Dict[int, float],
    dist_est: List[float],
    adj: List[List[Tuple[int, float]]],
    k: int,
    pred: List[int],
    alpha: List[int],
) -> Tuple[Dict[int, float], Dict[int, float]]:
    """Algorithm 1: FindPivots(B, S) → (P, W) — integer node variant."""
    W: Dict[int, float] = dict(S)
    W_prev: Dict[int, float] = dict(S)
    threshold = k * len(S)

    for _ in range(k):
        W_next: Dict[int, float] = {}
        for u in W_prev:
            d_u = dist_est[u]
            for v, w in adj[u]:
                candidate = d_u + w
                if _should_relax_int(candidate, v, u, dist_est, pred, alpha):
                    dist_est[v] = candidate
                    pred[v] = u
                    alpha[v] = alpha[u] + 1
                if candidate < B and v not in W:
                    W_next[v] = dist_est[v]
        W_next = {v: dist_est[v] for v in W_next}
        W.update(W_next)

        if len(W) > threshold:
            return dict(S), W

        W_prev = W_next

    children: Dict[int, list] = {u: [] for u in W}
    for v in W:
        p = pred[v]
        if p != -1 and p in W:
            children[p].append(v)

    subtree_size: Dict[int, int] = {}

    for root in W:
        if root in subtree_size:
            continue
        stack = [(root, False)]
        while stack:
            node, processed = stack.pop()
            if processed:
                size = 1
                for child in children.get(node, []):
                    size += subtree_size.get(child, 0)
                subtree_size[node] = size
            elif node not in subtree_size:
                stack.append((node, True))
                for child in children.get(node, []):
                    if child not in subtree_size:
                        stack.append((child, False))

    P = {u: dist_est[u] for u in S if subtree_size.get(u, 1) >= k}
    if not P:
        P = dict(S)

    return P, W


# ---------------------------------------------------------------------------
# Algorithm 2 — BaseCase (integer-node variant)
# ---------------------------------------------------------------------------

def _base_case_int(
    B: float,
    S: Dict[int, float],
    dist_est: List[float],
    adj: List[List[Tuple[int, float]]],
    k: int,
    pred: List[int],
    alpha: List[int],
) -> Tuple[float, Dict[int, float]]:
    """Algorithm 2: BaseCase(B, S) — integer node variant."""
    heap: list = []

    for node, d in S.items():
        heapq.heappush(heap, (d, alpha[node], node, node))

    U0: Dict[int, float] = {}

    while heap and len(U0) <= k:
        d, _a, _r, u = heapq.heappop(heap)
        if u in U0 or d > dist_est[u]:
            continue
        U0[u] = dist_est[u]

        d_u = dist_est[u]
        for v, w in adj[u]:
            candidate = d_u + w
            if candidate < B and _should_relax_int(candidate, v, u, dist_est, pred, alpha):
                dist_est[v] = candidate
                pred[v] = u
                alpha[v] = alpha[u] + 1
                heapq.heappush(heap, (candidate, alpha[v], v, v))

    if len(U0) <= k:
        return B, U0

    sorted_nodes = sorted(U0.keys(), key=lambda u: (dist_est[u], alpha[u], u))
    keep = sorted_nodes[:k]
    B_prime = dist_est[sorted_nodes[k]]
    U = {u: dist_est[u] for u in keep}
    return B_prime, U


# ---------------------------------------------------------------------------
# Algorithm 3 — BMSSP (integer-node variant)
# ---------------------------------------------------------------------------

def _bmssp_int(
    l: int,
    B: float,
    S: Dict[int, float],
    dist_est: List[float],
    adj: List[List[Tuple[int, float]]],
    k: int,
    t: int,
    pred: List[int],
    alpha: List[int],
) -> Tuple[float, Dict[int, float]]:
    """Algorithm 3: BMSSP(l, B, S) — integer node variant."""
    if l == 0:
        return _base_case_int(B, S, dist_est, adj, k, pred, alpha)

    P, W = _find_pivots_int(B, S, dist_est, adj, k, pred, alpha)

    M = max(1, 2 ** ((l - 1) * t))
    D = BlockHeap(M=M, B=B)
    for node, d in P.items():
        D.insert(node, d)

    if not P:
        B0_prime = B
    else:
        B0_prime = min(dist_est[node] for node in P)

    U: Dict[int, float] = {}
    U_size_limit = k * (2 ** (l * t))
    B_i_prime = B0_prime
    successful = False

    while len(U) < U_size_limit and not D.is_empty():
        S_i, B_i = D.pull(M)

        B_i_prime, U_i = _bmssp_int(l - 1, B_i, S_i, dist_est, adj, k, t, pred, alpha)

        U.update(U_i)

        K: list = []

        for u in U_i:
            d_u = dist_est[u]
            for v, w in adj[u]:
                candidate = d_u + w
                if _should_relax_int(candidate, v, u, dist_est, pred, alpha):
                    dist_est[v] = candidate
                    pred[v] = u
                    alpha[v] = alpha[u] + 1
                    if v in U and candidate < U[v]:
                        del U[v]
                if candidate <= dist_est[v] and v not in U and candidate < B:
                    if candidate >= B_i:
                        D.insert(v, candidate)
                    elif candidate >= B_i_prime:
                        K.append((v, candidate))
                    else:
                        D.insert(v, candidate)

        if B_i < B:
            for node, d in S_i.items():
                if node not in U and d >= B_i_prime and d < B_i:
                    K.append((node, d))

        D.batch_prepend(K)

        if len(U) >= U_size_limit:
            break

    else:
        successful = True

    B_final = B if successful else min(B_i_prime, B)

    prop_heap: list = []
    for node in W:
        if node not in U and dist_est[node] < B_final:
            U[node] = dist_est[node]
            heapq.heappush(prop_heap, (dist_est[node], node))

    while prop_heap:
        d_u, u = heapq.heappop(prop_heap)
        if d_u > dist_est[u]:
            continue
        for v, w in adj[u]:
            candidate = d_u + w
            if candidate >= B_final:
                continue
            if _should_relax_int(candidate, v, u, dist_est, pred, alpha):
                dist_est[v] = candidate
                pred[v] = u
                alpha[v] = alpha[u] + 1
                if v in U and candidate < U[v]:
                    del U[v]
                if v not in U:
                    U[v] = candidate
                    heapq.heappush(prop_heap, (candidate, v))
            elif v not in U and dist_est[v] < B_final and dist_est[v] < float('inf'):
                U[v] = dist_est[v]
                heapq.heappush(prop_heap, (dist_est[v], v))

    return B_final, U


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def breaking_barrier_sssp(
    graph: nx.DiGraph,
    source: Node,
) -> Dict[Node, float]:
    """Find shortest paths from source using the O(m log^{2/3} n) algorithm.

    Deterministic SSSP on directed graphs with real non-negative edge weights.
    Asymptotically faster than Dijkstra for sparse graphs (m = O(n)) as
    n → ∞, breaking the classical Ω(n log n) sorting barrier.

    Args:
        graph:  Directed graph (nx.DiGraph) with non-negative edge weights.
                Edge weights are read from the 'weight' attribute (default 1).
        source: Source vertex.

    Returns:
        Dictionary {node: shortest_distance} for every vertex reachable from
        source.  Unreachable vertices are not included.

    Raises:
        EmptyGraphError:     If the graph has no nodes.
        NodeNotFoundError:   If source is not in the graph.
        NegativeWeightError: If any edge weight is negative.

    Time Complexity:
        O(m log^{2/3} n) where m = |E|, n = |V|

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path import breaking_barrier_sssp
        >>>
        >>> G = nx.DiGraph()
        >>> G.add_edge('s', 'A', weight=2)
        >>> G.add_edge('s', 'B', weight=5)
        >>> G.add_edge('A', 'C', weight=1)
        >>> G.add_edge('B', 'C', weight=2)
        >>>
        >>> breaking_barrier_sssp(G, 's')
        {'s': 0, 'A': 2, 'B': 5, 'C': 3}
    """
    validate_graph(graph, "breaking_barrier_sssp")
    validate_source(graph, source)

    from logarithma.algorithms.exceptions import NegativeWeightError
    for u, v, data in graph.edges(data=True):
        w = data.get('weight', 1)
        if w < 0:
            raise NegativeWeightError(u, v, w, "breaking_barrier_sssp")

    # --- Constant-degree transform (§2, p.3) ---
    G_prime, source_prime, node_map = to_constant_degree(graph, source)

    # --- Map G' nodes to integers 0..n-1 ---
    n, adj, node_to_id, id_to_node = _build_int_graph(G_prime)

    source_id = node_to_id[source_prime]
    k, t, l = _compute_params(n)

    INF = float('inf')

    if _CYTHON_AVAILABLE:
        # --- Cython path: typed memoryviews, compiled C hot-path ---
        dist_list = _bmssp_run_cy(n, adj, source_id, k, t, l)
    else:
        # --- Pure Python path ---
        dist_est: List[float] = [INF] * n
        dist_est[source_id] = 0.0
        pred: List[int] = [-1] * n
        alpha: List[int] = [0] * n
        S_init = {source_id: 0.0}
        _bmssp_int(l, INF, S_init, dist_est, adj, k, t, pred, alpha)
        dist_list = dist_est

    # --- Map distances back: int id → G' node → original node ---
    dist_prime: Dict[Any, float] = {}
    for i, d in enumerate(dist_list):
        if d < INF:
            dist_prime[id_to_node[i]] = d

    return map_distances_back(dist_prime, node_map)
