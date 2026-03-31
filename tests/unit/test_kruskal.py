"""Unit tests for Kruskal's MST algorithm."""

import pytest
import networkx as nx

from logarithma.algorithms.mst import kruskal_mst
from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    UndirectedGraphRequiredError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_graph():
    """Simple 5-node undirected weighted graph (known MST weight = 11)."""
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
    G.add_edge(4, 5, weight=2)  # separate component
    return G


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_basic_kruskal(simple_graph):
    result = kruskal_mst(simple_graph)
    assert result['total_weight'] == pytest.approx(10.0)


def test_kruskal_edge_count(simple_graph):
    result = kruskal_mst(simple_graph)
    expected_edges = simple_graph.number_of_nodes() - 1
    assert len(result['mst_edges']) == expected_edges


def test_kruskal_no_cycles(simple_graph):
    result = kruskal_mst(simple_graph)
    mst = nx.Graph()
    mst.add_nodes_from(simple_graph.nodes())
    for u, v, w in result['mst_edges']:
        mst.add_edge(u, v)
    assert nx.is_forest(mst)


def test_kruskal_result_keys(simple_graph):
    result = kruskal_mst(simple_graph)
    assert 'mst_edges' in result
    assert 'total_weight' in result
    assert 'num_components' in result


def test_kruskal_single_component(simple_graph):
    result = kruskal_mst(simple_graph)
    assert result['num_components'] == 1


# ---------------------------------------------------------------------------
# Disconnected graph → spanning forest
# ---------------------------------------------------------------------------

def test_kruskal_disconnected(disconnected_graph):
    result = kruskal_mst(disconnected_graph)
    assert result['num_components'] == 2
    # Forest has V - components edges
    expected = disconnected_graph.number_of_nodes() - 2
    assert len(result['mst_edges']) == expected


def test_kruskal_disconnected_weight(disconnected_graph):
    result = kruskal_mst(disconnected_graph)
    assert result['total_weight'] == pytest.approx(6.0)  # 3+1+2 = all edges (spanning forest)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_kruskal_single_node():
    G = nx.Graph()
    G.add_node('X')
    result = kruskal_mst(G)
    assert result['mst_edges'] == []
    assert result['total_weight'] == 0.0
    assert result['num_components'] == 1


def test_kruskal_two_nodes():
    G = nx.Graph()
    G.add_edge('A', 'B', weight=7)
    result = kruskal_mst(G)
    assert len(result['mst_edges']) == 1
    assert result['total_weight'] == pytest.approx(7.0)


def test_kruskal_no_weight_attribute():
    """Edges without 'weight' attribute should default to 1."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4)])
    result = kruskal_mst(G)
    assert result['total_weight'] == pytest.approx(3.0)


def test_kruskal_uniform_weights():
    G = nx.Graph()
    G.add_edge(1, 2, weight=5)
    G.add_edge(2, 3, weight=5)
    G.add_edge(3, 4, weight=5)
    G.add_edge(1, 4, weight=5)
    result = kruskal_mst(G)
    assert len(result['mst_edges']) == 3
    assert result['total_weight'] == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_kruskal_directed_raises():
    G = nx.DiGraph()
    G.add_edge(1, 2)
    with pytest.raises(UndirectedGraphRequiredError):
        kruskal_mst(G)


def test_kruskal_empty_raises():
    G = nx.Graph()
    with pytest.raises(EmptyGraphError):
        kruskal_mst(G)


# ---------------------------------------------------------------------------
# Parity with Prim
# ---------------------------------------------------------------------------

def test_kruskal_matches_prim(simple_graph):
    from logarithma.algorithms.mst import prim_mst
    k = kruskal_mst(simple_graph)
    p = prim_mst(simple_graph)
    assert k['total_weight'] == pytest.approx(p['total_weight'])
    assert k['num_components'] == p['num_components']
