# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""
Breaking Barrier SSSP — Core (Cython)
======================================

Cython port of the hot-path functions from breaking_barrier.py.

All internal node IDs are Py_ssize_t (contiguous integers 0..n-1).
dist_est, pred, alpha are typed memoryviews over pre-allocated arrays,
giving O(1) C-level access with no Python overhead.

Public entry point:
    bmssp_run(n, adj, source_id, k, t, l) -> list of n doubles
"""

import heapq
import array as _array

from libc.math cimport HUGE_VAL

try:
    from logarithma.algorithms.shortest_path.block_heap import BlockHeap as _BlockHeap
except Exception:
    from logarithma.algorithms.shortest_path.block_heap import BlockHeap as _BlockHeap

cdef double _INF = HUGE_VAL


# ---------------------------------------------------------------------------
# _should_relax — cdef inline, no Python overhead
# ---------------------------------------------------------------------------

cdef inline bint _should_relax(
    double candidate,
    Py_ssize_t v,
    Py_ssize_t u,
    double[::1] dist_est,
    Py_ssize_t[::1] pred,
    Py_ssize_t[::1] alpha,
) nogil:
    cdef double d_v = dist_est[v]
    if candidate < d_v:
        return True
    if candidate > d_v:
        return False
    cdef Py_ssize_t new_a = alpha[u] + 1
    cdef Py_ssize_t old_a = alpha[v]
    if new_a < old_a:
        return True
    if new_a > old_a:
        return False
    cdef Py_ssize_t pv = pred[v]
    if pv == -1:
        return True
    return u < pv


# ---------------------------------------------------------------------------
# FindPivots
# ---------------------------------------------------------------------------

def _find_pivots(
    double B,
    dict S,
    double[::1] dist_est,
    list adj,
    Py_ssize_t k,
    Py_ssize_t[::1] pred,
    Py_ssize_t[::1] alpha,
):
    cdef dict W = dict(S)
    cdef dict W_prev = dict(S)
    cdef Py_ssize_t threshold = k * len(S)
    cdef Py_ssize_t u, v
    cdef double d_u, w, candidate
    cdef object edge
    cdef Py_ssize_t p, root, node, size
    cdef bint processed

    for _ in range(k):
        W_next = {}
        for u in W_prev:
            d_u = dist_est[u]
            for edge in adj[u]:
                v = <Py_ssize_t>edge[0]
                w = <double>edge[1]
                candidate = d_u + w
                if _should_relax(candidate, v, u, dist_est, pred, alpha):
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

    # Build forest
    children = {u: [] for u in W}
    for v in W:
        p = pred[v]
        if p != -1 and p in W:
            children[p].append(v)

    subtree_size = {}
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
# BaseCase
# ---------------------------------------------------------------------------

def _base_case(
    double B,
    dict S,
    double[::1] dist_est,
    list adj,
    Py_ssize_t k,
    Py_ssize_t[::1] pred,
    Py_ssize_t[::1] alpha,
):
    cdef list heap = []
    cdef Py_ssize_t u, v
    cdef double d, w, candidate, d_u
    cdef object edge

    for node, d in S.items():
        u = <Py_ssize_t>node
        heapq.heappush(heap, (d, alpha[u], u, u))

    cdef dict U0 = {}

    while heap and len(U0) <= k:
        entry = heapq.heappop(heap)
        d = <double>entry[0]
        u = <Py_ssize_t>entry[3]
        if u in U0 or d > dist_est[u]:
            continue
        U0[u] = dist_est[u]

        d_u = dist_est[u]
        for edge in adj[u]:
            v = <Py_ssize_t>edge[0]
            w = <double>edge[1]
            candidate = d_u + w
            if candidate < B and _should_relax(candidate, v, u, dist_est, pred, alpha):
                dist_est[v] = candidate
                pred[v] = u
                alpha[v] = alpha[u] + 1
                heapq.heappush(heap, (candidate, alpha[v], v, v))

    if len(U0) <= k:
        return B, U0

    sorted_nodes = sorted(U0.keys(), key=lambda x: (dist_est[x], alpha[x], x))
    keep = sorted_nodes[:k]
    B_prime = dist_est[sorted_nodes[k]]
    U = {u: dist_est[u] for u in keep}
    return B_prime, U


# ---------------------------------------------------------------------------
# BMSSP — recursive driver
# ---------------------------------------------------------------------------

def _bmssp(
    Py_ssize_t l,
    double B,
    dict S,
    double[::1] dist_est,
    list adj,
    Py_ssize_t k,
    Py_ssize_t t,
    Py_ssize_t[::1] pred,
    Py_ssize_t[::1] alpha,
):
    cdef Py_ssize_t u, v, M_sz
    cdef double d_u, w, candidate, B_i, B_i_prime, B0_prime, B_final, d_node
    cdef bint successful
    cdef object edge, node
    cdef dict U, U_i, S_i

    if l == 0:
        return _base_case(B, S, dist_est, adj, k, pred, alpha)

    P, W = _find_pivots(B, S, dist_est, adj, k, pred, alpha)

    M_sz = <Py_ssize_t>max(1, 2 ** (<int>(l - 1) * <int>t))
    D = _BlockHeap(M=M_sz, B=B)
    for node, d_node in P.items():
        D.insert(node, d_node)

    if not P:
        B0_prime = B
    else:
        B0_prime = min(dist_est[nd] for nd in P)

    U = {}
    U_size_limit = <Py_ssize_t>(k * (2 ** (<int>l * <int>t)))
    B_i_prime = B0_prime
    successful = False

    while len(U) < U_size_limit and not D.is_empty():
        S_i, B_i = D.pull(M_sz)

        B_i_prime, U_i = _bmssp(l - 1, B_i, S_i, dist_est, adj, k, t, pred, alpha)
        U.update(U_i)

        K = []

        for u in U_i:
            d_u = dist_est[u]
            for edge in adj[u]:
                v = <Py_ssize_t>edge[0]
                w = <double>edge[1]
                candidate = d_u + w
                if _should_relax(candidate, v, u, dist_est, pred, alpha):
                    dist_est[v] = candidate
                    pred[v] = u
                    alpha[v] = alpha[u] + 1
                    if v in U and candidate < <double>U[v]:
                        del U[v]
                if candidate <= dist_est[v] and v not in U and candidate < B:
                    if candidate >= B_i:
                        D.insert(v, candidate)
                    elif candidate >= B_i_prime:
                        K.append((v, candidate))
                    else:
                        D.insert(v, candidate)

        if B_i < B:
            for node in S_i:
                d_node = <double>S_i[node]
                if node not in U and d_node >= B_i_prime and d_node < B_i:
                    K.append((node, d_node))

        D.batch_prepend(K)

        if len(U) >= U_size_limit:
            break
    else:
        successful = True

    B_final = B if successful else min(B_i_prime, B)

    prop_heap = []
    for node in W:
        v = <Py_ssize_t>node
        if v not in U and dist_est[v] < B_final:
            U[v] = dist_est[v]
            heapq.heappush(prop_heap, (dist_est[v], v))

    while prop_heap:
        entry = heapq.heappop(prop_heap)
        d_u = <double>entry[0]
        u = <Py_ssize_t>entry[1]
        if d_u > dist_est[u]:
            continue
        for edge in adj[u]:
            v = <Py_ssize_t>edge[0]
            w = <double>edge[1]
            candidate = d_u + w
            if candidate >= B_final:
                continue
            if _should_relax(candidate, v, u, dist_est, pred, alpha):
                dist_est[v] = candidate
                pred[v] = u
                alpha[v] = alpha[u] + 1
                if v in U and candidate < <double>U[v]:
                    del U[v]
                if v not in U:
                    U[v] = candidate
                    heapq.heappush(prop_heap, (candidate, v))
            elif v not in U and dist_est[v] < B_final and dist_est[v] < _INF:
                U[v] = dist_est[v]
                heapq.heappush(prop_heap, (dist_est[v], v))

    return B_final, U


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def bmssp_run(
    Py_ssize_t n,
    list adj,
    Py_ssize_t source_id,
    Py_ssize_t k,
    Py_ssize_t t,
    Py_ssize_t l,
):
    """Run BMSSP from source_id.  Returns list of n doubles."""
    cdef double[::1] dist_est
    cdef Py_ssize_t[::1] pred
    cdef Py_ssize_t[::1] alpha

    # 'q' = signed long long (8 bytes) = Py_ssize_t on 64-bit platforms
    dist_arr = _array.array('d', [_INF] * n)
    pred_arr = _array.array('q', [-1] * n)
    alpha_arr = _array.array('q', [0] * n)

    dist_est = dist_arr
    pred = pred_arr
    alpha = alpha_arr

    dist_est[source_id] = 0.0

    S_init = {source_id: 0.0}
    _bmssp(l, _INF, S_init, dist_est, adj, k, t, pred, alpha)

    return list(dist_arr)
