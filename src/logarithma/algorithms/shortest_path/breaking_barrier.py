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
# Assumption 2.1 — Lexicographic tiebreaking (§2, p.4)
# ---------------------------------------------------------------------------

def _should_relax(
    candidate: float,
    v: Node,
    u: Node,
    dist_est: DistMap,
    pred: PredMap,
    alpha: AlphaMap,
) -> bool:
    """Assumption 2.1 tiebreaking: lexicographic path ordering.

    Returns True if the path through u to v is "shorter" than v's current path
    under the lexicographic tuple ordering ⟨distance, hop_count, node_sequence⟩.

    Reference: §2, page 4 — "We treat each path of length l that traverses
    α vertices ... as a tuple ⟨l, α, v_α, ...⟩"
    """
    d_v = dist_est[v]
    if candidate < d_v:
        return True
    if candidate > d_v:
        return False
    # candidate == d_v → tiebreak by hop count, then node ID
    new_alpha = alpha.get(u, 0) + 1
    old_alpha = alpha.get(v, 0)
    if new_alpha < old_alpha:
        return True
    if new_alpha > old_alpha:
        return False
    # Same distance, same hop count → compare node repr for determinism
    return repr(u) < repr(pred.get(v))


# ---------------------------------------------------------------------------
# Parameter helpers
# ---------------------------------------------------------------------------

def _compute_params(n: int) -> Tuple[int, int, int]:
    """Return (k, t, l) for a graph with n vertices.

    For very small n where log(n) < 1 the floor operations yield 0, which
    would make k=0 and cause division-by-zero.  We clamp both k and t to 1
    so the algorithm degenerates gracefully to repeated BaseCase calls.
    """
    if n <= 1:
        return 1, 1, 1
    ln_n = math.log(n)
    k = max(1, int(ln_n ** (1 / 3)))
    t = max(1, int(ln_n ** (2 / 3)))
    # l must satisfy 2^{l*t} >= n so that top-level U_size_limit = k*2^{lt} >= k*n
    # i.e. l >= log2(n) / t
    l = max(1, math.ceil(math.log2(n) / t))
    return k, t, l


# ---------------------------------------------------------------------------
# Algorithm 1 — FindPivots
# ---------------------------------------------------------------------------

def _find_pivots(
    B: Dist,
    S: Dict[Node, Dist],
    dist_est: DistMap,
    adj: AdjList,
    k: int,
    pred: PredMap,
    alpha: AlphaMap,
) -> Tuple[Dict[Node, Dist], Dict[Node, Dist]]:
    """Algorithm 1: FindPivots(B, S) → (P, W).

    Runs k-step Bellman-Ford from S.  Returns pivot set P ⊆ S and
    expanded set W.

    Uses Assumption 2.1 lexicographic tiebreaking (§2, p.4) to guarantee
    the tight-edge structure is a forest (each node has exactly one
    predecessor).

    Args:
        B:        distance upper bound for this BMSSP call
        S:        current frontier {node: dist_est[node]}
        dist_est: global mutable distance-estimate map (d̃)
        adj:      precomputed adjacency list {node: [(neighbour, weight), ...]}
        k:        algorithm parameter
        pred:     global mutable predecessor map (Assumption 2.1)
        alpha:    global mutable hop-count map (Assumption 2.1)

    Returns:
        P: pivot set — subset of S whose shortest-path trees are large
        W: expanded set — all nodes reachable in ≤ k relaxation steps
    """
    W: Dict[Node, Dist] = dict(S)
    W_prev: Dict[Node, Dist] = dict(S)
    threshold = k * len(S)

    for _ in range(k):
        W_next: Dict[Node, Dist] = {}
        for u in W_prev:
            d_u = dist_est[u]
            for v, w in adj[u]:
                candidate = d_u + w
                if _should_relax(candidate, v, u, dist_est, pred, alpha):
                    dist_est[v] = candidate
                    pred[v] = u
                    alpha[v] = alpha.get(u, 0) + 1
                # Only add to W_next if not already in W (prevents re-expansion)
                if candidate < B and v not in W:
                    W_next[v] = dist_est[v]
        W_next = {v: dist_est[v] for v in W_next}
        W.update(W_next)

        if len(W) > threshold:
            # Early exit: P = S (all of S becomes pivots)
            return dict(S), W

        W_prev = W_next

    # Build directed forest F using pred[] (Assumption 2.1 guarantees forest).
    # pred[v] == u means u is the unique tight predecessor of v.
    children: Dict[Node, list] = {u: [] for u in W}
    for v in W:
        p = pred.get(v)
        if p is not None and p in W:
            children[p].append(v)

    # Count subtree sizes rooted at each node in S (iterative to avoid
    # RecursionError on deep graphs)
    subtree_size: Dict[Node, int] = {}

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

    # Pivots: roots in S whose subtree has >= k vertices
    P = {u: dist_est[u] for u in S if subtree_size.get(u, 1) >= k}
    if not P:
        # Fallback: every S node is a pivot (covers k=1 edge case)
        P = dict(S)

    return P, W


# ---------------------------------------------------------------------------
# Algorithm 2 — BaseCase (l = 0)
# ---------------------------------------------------------------------------

def _base_case(
    B: Dist,
    S: Dict[Node, Dist],
    dist_est: DistMap,
    adj: AdjList,
    k: int,
    pred: PredMap,
    alpha: AlphaMap,
) -> Tuple[Dist, Dict[Node, Dist]]:
    """Algorithm 2: BaseCase(B, S) → (B', U).

    Mini Dijkstra starting from all nodes in S.  Stops after finding
    k+1 vertices or exhausting the heap (whichever comes first).

    Uses Assumption 2.1 lexicographic tiebreaking for heap ordering
    and relaxation (§2, p.4).

    Returns:
        B': new boundary (<= B)
        U:  set of complete vertices found
    """
    # Heap entries: (dist, alpha, repr(node), node) — A2.1 tiebreaking
    heap: list = []

    for node, d in S.items():
        heapq.heappush(heap, (d, alpha.get(node, 0), repr(node), node))

    U0: Dict[Node, Dist] = {}

    while heap and len(U0) <= k:
        d, _a, _r, u = heapq.heappop(heap)
        if u in U0 or d > dist_est[u]:
            continue  # already processed or stale entry
        U0[u] = dist_est[u]

        d_u = dist_est[u]
        for v, w in adj[u]:
            candidate = d_u + w
            if candidate < B and _should_relax(candidate, v, u, dist_est, pred, alpha):
                dist_est[v] = candidate
                pred[v] = u
                alpha[v] = alpha.get(u, 0) + 1
                heapq.heappush(heap, (candidate, alpha[v], repr(v), v))

    if len(U0) <= k:
        # Fewer than k+1 vertices found — successful, return B
        return B, U0

    # k+1 vertices found — partial execution.
    # Paper Algorithm 2, lines 16-17:
    #   B' = max_{v in U0} d̂[v];  U = {v in U0 : d̂[v] < B'}
    #
    # Under Assumption 2.1 all distances are unique, so exactly one node
    # has the maximum and U contains k nodes.  We use sorted selection
    # which is equivalent and handles any residual ties correctly.
    sorted_nodes = sorted(U0.keys(), key=lambda u: (dist_est[u], alpha.get(u, 0), repr(u)))
    keep = sorted_nodes[:k]
    B_prime = dist_est[sorted_nodes[k]]
    U = {u: dist_est[u] for u in keep}
    return B_prime, U


# ---------------------------------------------------------------------------
# Algorithm 3 — BMSSP (recursive driver)
# ---------------------------------------------------------------------------

def _bmssp(
    l: int,
    B: Dist,
    S: Dict[Node, Dist],
    dist_est: DistMap,
    adj: AdjList,
    k: int,
    t: int,
    pred: PredMap,
    alpha: AlphaMap,
) -> Tuple[Dist, Dict[Node, Dist]]:
    """Algorithm 3: BMSSP(l, B, S) → (B', U).

    Bounded Multi-Source Shortest Path.

    Args:
        l:        recursion level (top level = ceil(log n / t))
        B:        distance upper bound
        S:        set of pivot vertices {node: dist_est[node]}
        dist_est: global mutable distance-estimate map
        adj:      precomputed adjacency list {node: [(neighbour, weight), ...]}
        k, t:     algorithm parameters
        pred:     global mutable predecessor map (Assumption 2.1)
        alpha:    global mutable hop-count map (Assumption 2.1)

    Returns:
        B': updated boundary
        U:  set of complete vertices with d(v) < B'
    """
    # --- Base case ---
    if l == 0:
        return _base_case(B, S, dist_est, adj, k, pred, alpha)

    # --- FindPivots ---
    P, W = _find_pivots(B, S, dist_est, adj, k, pred, alpha)

    # --- Initialise data structure D ---
    M = max(1, 2 ** ((l - 1) * t))
    D = BlockHeap(M=M, B=B)
    for node, d in P.items():
        D.insert(node, d)

    if not P:
        B0_prime = B
    else:
        B0_prime = min(dist_est[node] for node in P)

    U: Dict[Node, Dist] = {}
    U_size_limit = k * (2 ** (l * t))
    B_i_prime = B0_prime
    successful = False

    # --- Main iteration ---
    while len(U) < U_size_limit and not D.is_empty():
        # Pull next batch of pivots
        S_i, B_i = D.pull(M)

        # Recursive call on level l-1
        B_i_prime, U_i = _bmssp(l - 1, B_i, S_i, dist_est, adj, k, t, pred, alpha)

        U.update(U_i)

        K: list = []

        # Relax outgoing edges from newly completed vertices.
        for u in U_i:
            d_u = dist_est[u]
            for v, w in adj[u]:
                candidate = d_u + w
                if _should_relax(candidate, v, u, dist_est, pred, alpha):
                    dist_est[v] = candidate
                    pred[v] = u
                    alpha[v] = alpha.get(u, 0) + 1
                    # If v was already finalized with a worse distance,
                    # remove from U and re-queue for reprocessing.
                    if v in U and candidate < U[v]:
                        del U[v]
                if candidate <= dist_est[v] and v not in U and candidate < B:
                    if candidate >= B_i:
                        D.insert(v, candidate)
                    elif candidate >= B_i_prime:
                        K.append((v, candidate))
                    else:
                        D.insert(v, candidate)

        # Batch-prepend S_i nodes in [B_i_prime, B_i) that aren't done yet.
        # Skip when B_i == B: the sub-call saw B as its upper bound and
        # already handled everything up to B, so re-queuing would loop forever.
        if B_i < B:
            for node, d in S_i.items():
                if node not in U and d >= B_i_prime and d < B_i:
                    K.append((node, d))

        D.batch_prepend(K)

        # Partial execution: too many vertices found
        if len(U) >= U_size_limit:
            break

    else:
        # Loop exited because D is empty — successful execution
        successful = True

    # Successful: return B (all vertices within B are complete)
    # Partial:    return B_i_prime (tighter boundary found)
    B_final = B if successful else min(B_i_prime, B)

    # Add W nodes within the final boundary to U (Algorithm 3, line 22)
    # and propagate their edges.  W nodes were relaxed by FindPivots but
    # never entered D/BaseCase, so their outgoing edges need processing.
    # We use a heap-driven sweep to propagate in distance order, ensuring
    # downstream nodes also receive correct distances.
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
            if _should_relax(candidate, v, u, dist_est, pred, alpha):
                dist_est[v] = candidate
                pred[v] = u
                alpha[v] = alpha.get(u, 0) + 1
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

    # --- Weight validation on original graph ---
    from logarithma.algorithms.exceptions import NegativeWeightError
    for u, v, data in graph.edges(data=True):
        w = data.get('weight', 1)
        if w < 0:
            raise NegativeWeightError(u, v, w, "breaking_barrier_sssp")

    # --- Constant-degree transform (§2, p.3) ---
    #
    # The paper assumes a graph with constant in/out-degrees (≤ 2).
    # We apply the classical Frederickson 1983 vertex-splitting transform:
    # each vertex v is replaced by a cycle of deg(v) nodes connected with
    # zero-weight edges.  This preserves shortest-path distances while
    # ensuring the algorithm's theoretical guarantees hold.
    G_prime, source_prime, node_map = to_constant_degree(graph, source)

    # --- Build adjacency list on transformed graph ---
    raw_adj = G_prime._adj
    adj: AdjList = {}
    for u, nbrs in raw_adj.items():
        neighbours = []
        for v, data in nbrs.items():
            neighbours.append((v, float(data.get('weight', 1))))
        adj[u] = neighbours

    n = G_prime.number_of_nodes()
    k, t, l = _compute_params(n)

    # Global mutable distance estimates (d̃ in the paper)
    dist_est: DistMap = {node: float('inf') for node in G_prime.nodes()}
    dist_est[source_prime] = 0.0

    # Assumption 2.1 — predecessor and hop-count maps for tiebreaking
    pred: PredMap = {source_prime: None}
    alpha_map: AlphaMap = {source_prime: 0}

    # Top-level call: BMSSP(l, B=inf, S={source'})
    S_init = {source_prime: 0.0}
    _bmssp(l, float('inf'), S_init, dist_est, adj, k, t, pred, alpha_map)

    # --- Map distances back to original vertices ---
    dist_prime = {node: d for node, d in dist_est.items() if d < float('inf')}
    return map_distances_back(dist_prime, node_map)
