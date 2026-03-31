"""Unit tests for Prim's MST algorithm."""

import pytest
import networkx as nx

from logarithma.algorithms.mst import prim_mst
from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    NodeNotFoundError,
    UndirectedGraphRequiredError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_graph():
    G = nx.Graph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('B', 'D', weight=5)
    G.add_edge('C', 'D', weight=8)
    G.add_edge('C', 'E', weight=10)
    G.add_edge('D', 'E', weight=2)
    return G


@pytest.fixture
def disconnected_graph():
    G = nx.Graph()
    G.add_edge(1, 2, weight=3)
    G.add_edge(2, 3, weight=1)
    G.add_edge(4, 5, weight=2)
    return G


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_basic_prim(simple_graph):
    result = prim_mst(simple_graph)
    assert result['total_weight'] == pytest.approx(10.0)


def test_prim_edge_count(simple_graph):
    result = prim_mst(simple_graph)
    assert len(result['mst_edges']) == simple_graph.number_of_nodes() - 1


def test_prim_no_cycles(simple_graph):
    result = prim_mst(simple_graph)
    mst = nx.Graph()
    mst.add_nodes_from(simple_graph.nodes())
    for u, v, _ in result['mst_edges']:
        mst.add_edge(u, v)
    assert nx.is_forest(mst)


def test_prim_result_keys(simple_graph):
    result = prim_mst(simple_graph)
    assert 'mst_edges' in result
    assert 'total_weight' in result
    assert 'num_components' in result


def test_prim_single_component(simple_graph):
    result = prim_mst(simple_graph)
    assert result['num_components'] == 1


# ---------------------------------------------------------------------------
# Start node variants
# ---------------------------------------------------------------------------

def test_prim_different_start_same_weight(simple_graph):
    r1 = prim_mst(simple_graph, start='A')
    r2 = prim_mst(simple_graph, start='D')
    assert r1['total_weight'] == pytest.approx(r2['total_weight'])


def test_prim_start_none_uses_first_node(simple_graph):
    result = prim_mst(simple_graph, start=None)
    assert result['total_weight'] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Disconnected graph
# ---------------------------------------------------------------------------

def test_prim_disconnected(disconnected_graph):
    result = prim_mst(disconnected_graph)
    assert result['num_components'] == 2
    expected = disconnected_graph.number_of_nodes() - 2
    assert len(result['mst_edges']) == expected


def test_prim_disconnected_weight(disconnected_graph):
    result = prim_mst(disconnected_graph)
    assert result['total_weight'] == pytest.approx(6.0)  # 3+1+2 spanning forest


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_prim_single_node():
    G = nx.Graph()
    G.add_node('Z')
    result = prim_mst(G, start='Z')
    assert result['mst_edges'] == []
    assert result['total_weight'] == 0.0
    assert result['num_components'] == 1


def test_prim_no_weight_attribute():
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4)])
    result = prim_mst(G)
    assert result['total_weight'] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_prim_invalid_start():
    G = nx.Graph()
    G.add_edge(1, 2, weight=1)
    with pytest.raises(NodeNotFoundError):
        prim_mst(G, start=99)


def test_prim_directed_raises():
    G = nx.DiGraph()
    G.add_edge(1, 2)
    with pytest.raises(UndirectedGraphRequiredError):
        prim_mst(G)


def test_prim_empty_raises():
    G = nx.Graph()
    with pytest.raises(EmptyGraphError):
        prim_mst(G)


# ---------------------------------------------------------------------------
# Parity with Kruskal
# ---------------------------------------------------------------------------

def test_prim_matches_kruskal(simple_graph):
    from logarithma.algorithms.mst import kruskal_mst
    p = prim_mst(simple_graph)
    k = kruskal_mst(simple_graph)
    assert p['total_weight'] == pytest.approx(k['total_weight'])
    assert p['num_components'] == k['num_components']
