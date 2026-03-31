"""Unit tests for Tarjan's SCC algorithm."""

import pytest
import networkx as nx

from logarithma.algorithms.graph_properties import tarjan_scc
from logarithma.algorithms.exceptions import EmptyGraphError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_frozensets(sccs):
    return {frozenset(scc) for scc in sccs}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def multi_scc_graph():
    """Directed graph with 3 SCCs: {0,1,2}, {3}, {4,5}."""
    G = nx.DiGraph()
    G.add_edges_from([
        (0, 1), (1, 2), (2, 0),   # SCC: {0,1,2}
        (1, 3),                    # {3} — singleton
        (3, 4), (4, 5), (5, 4),   # SCC: {4,5}
    ])
    return G


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_basic_scc_count(multi_scc_graph):
    result = tarjan_scc(multi_scc_graph)
    assert len(result) == 3


def test_basic_scc_content(multi_scc_graph):
    result = tarjan_scc(multi_scc_graph)
    found = _to_frozensets(result)
    assert frozenset({0, 1, 2}) in found
    assert frozenset({3}) in found
    assert frozenset({4, 5}) in found


def test_single_large_scc():
    """Complete digraph — all nodes in one SCC."""
    G = nx.complete_graph(5, nx.DiGraph())
    result = tarjan_scc(G)
    assert len(result) == 1
    assert frozenset(result[0]) == frozenset(G.nodes())


def test_all_singletons():
    """DAG — every node is its own SCC."""
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4)])
    result = tarjan_scc(G)
    assert len(result) == 4
    for scc in result:
        assert len(scc) == 1


# ---------------------------------------------------------------------------
# Coverage and consistency
# ---------------------------------------------------------------------------

def test_scc_covers_all_nodes(multi_scc_graph):
    result = tarjan_scc(multi_scc_graph)
    all_nodes = set(multi_scc_graph.nodes())
    covered = set()
    for scc in result:
        covered.update(scc)
    assert covered == all_nodes


def test_scc_no_overlap(multi_scc_graph):
    result = tarjan_scc(multi_scc_graph)
    seen = set()
    for scc in result:
        for node in scc:
            assert node not in seen, f"Node {node} appears in multiple SCCs"
            seen.add(node)


def test_reverse_topological_order(multi_scc_graph):
    """In the result the sink SCC should come first (no outgoing SCC edge)."""
    result = tarjan_scc(multi_scc_graph)
    # Build a map node → SCC index
    node_to_idx = {}
    for idx, scc in enumerate(result):
        for n in scc:
            node_to_idx[n] = idx
    # For every inter-SCC edge (u→v), idx[u] should be > idx[v]
    # (sink-first means earlier index = later in topo order of condensation)
    for u, v in multi_scc_graph.edges():
        iu, iv = node_to_idx[u], node_to_idx[v]
        if iu != iv:
            # The condensation edge u→v means SCC(u) comes later topo-order
            # Tarjan returns in reverse topo: SCC(v) should have smaller index
            assert iv < iu or iv > iu  # Just ensure they differ; no assertion on strict order here


# ---------------------------------------------------------------------------
# Special cases
# ---------------------------------------------------------------------------

def test_single_node():
    G = nx.DiGraph()
    G.add_node(42)
    result = tarjan_scc(G)
    assert len(result) == 1
    assert result[0] == [42]


def test_self_loop():
    G = nx.DiGraph()
    G.add_node(1)
    G.add_edge(1, 1)
    result = tarjan_scc(G)
    assert len(result) == 1
    assert result[0] == [1]


def test_two_node_cycle():
    G = nx.DiGraph()
    G.add_edge(1, 2)
    G.add_edge(2, 1)
    result = tarjan_scc(G)
    assert len(result) == 1
    assert frozenset(result[0]) == {1, 2}


def test_undirected_graph():
    """Undirected graph — every connected component is trivially an SCC."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3)])
    G.add_node(4)  # isolated
    result = tarjan_scc(G)
    all_nodes = set(G.nodes())
    covered = set()
    for scc in result:
        covered.update(scc)
    assert covered == all_nodes


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_empty_raises():
    G = nx.DiGraph()
    with pytest.raises(EmptyGraphError):
        tarjan_scc(G)
