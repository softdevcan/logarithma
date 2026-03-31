"""Unit tests for topological_sort (DFS and Kahn methods)."""

import pytest
import networkx as nx

from logarithma.algorithms.graph_properties import topological_sort
from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    InvalidModeError,
    NotDAGError,
    UndirectedGraphRequiredError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_valid_topo_order(graph: nx.DiGraph, order) -> bool:
    """Return True if 'order' is a valid topological ordering of 'graph'."""
    rank = {node: i for i, node in enumerate(order)}
    for u, v in graph.edges():
        if rank[u] >= rank[v]:
            return False
    return True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_dag():
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)])
    return G


@pytest.fixture
def linear_chain():
    G = nx.DiGraph()
    for i in range(1, 6):
        G.add_edge(i, i + 1)
    return G


@pytest.fixture
def cyclic_graph():
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1)])
    return G


# ---------------------------------------------------------------------------
# DFS method — basic correctness
# ---------------------------------------------------------------------------

def test_dfs_basic_valid(simple_dag):
    order = topological_sort(simple_dag, method='dfs')
    assert set(order) == set(simple_dag.nodes())
    assert _is_valid_topo_order(simple_dag, order)


def test_dfs_linear_chain(linear_chain):
    order = topological_sort(linear_chain, method='dfs')
    assert order == list(range(1, 7))


def test_dfs_single_node():
    G = nx.DiGraph()
    G.add_node(42)
    assert topological_sort(G, method='dfs') == [42]


# ---------------------------------------------------------------------------
# Kahn method — basic correctness
# ---------------------------------------------------------------------------

def test_kahn_basic_valid(simple_dag):
    order = topological_sort(simple_dag, method='kahn')
    assert set(order) == set(simple_dag.nodes())
    assert _is_valid_topo_order(simple_dag, order)


def test_kahn_linear_chain(linear_chain):
    order = topological_sort(linear_chain, method='kahn')
    assert order == list(range(1, 7))


def test_kahn_single_node():
    G = nx.DiGraph()
    G.add_node(7)
    assert topological_sort(G, method='kahn') == [7]


# ---------------------------------------------------------------------------
# Both methods agree on validity
# ---------------------------------------------------------------------------

def test_both_methods_valid_on_same_graph(simple_dag):
    order_dfs = topological_sort(simple_dag, method='dfs')
    order_kahn = topological_sort(simple_dag, method='kahn')
    assert _is_valid_topo_order(simple_dag, order_dfs)
    assert _is_valid_topo_order(simple_dag, order_kahn)


def test_multiple_sources_dag():
    G = nx.DiGraph()
    G.add_edges_from([(1, 3), (2, 3), (3, 4)])
    for method in ('dfs', 'kahn'):
        order = topological_sort(G, method=method)
        assert _is_valid_topo_order(G, order)
        assert set(order) == {1, 2, 3, 4}


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------

def test_dfs_cyclic_raises_not_dag(cyclic_graph):
    with pytest.raises(NotDAGError) as exc_info:
        topological_sort(cyclic_graph, method='dfs')
    assert exc_info.value.algorithm == 'topological_sort'


def test_kahn_cyclic_raises_not_dag(cyclic_graph):
    with pytest.raises(NotDAGError):
        topological_sort(cyclic_graph, method='kahn')


def test_dfs_cycle_attribute_set(cyclic_graph):
    with pytest.raises(NotDAGError) as exc_info:
        topological_sort(cyclic_graph, method='dfs')
    # cycle attribute should be populated by DFS method
    err = exc_info.value
    if err.cycle is not None:
        assert len(err.cycle) >= 2


def test_self_loop_raises():
    G = nx.DiGraph()
    G.add_edge(1, 1)
    for method in ('dfs', 'kahn'):
        with pytest.raises(NotDAGError):
            topological_sort(G, method=method)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_undirected_raises():
    G = nx.Graph()
    G.add_edge(1, 2)
    with pytest.raises(UndirectedGraphRequiredError):
        topological_sort(G)


def test_empty_raises():
    G = nx.DiGraph()
    with pytest.raises(EmptyGraphError):
        topological_sort(G)


def test_invalid_method_raises():
    G = nx.DiGraph()
    G.add_edge(1, 2)
    with pytest.raises(InvalidModeError):
        topological_sort(G, method='tarjan')
