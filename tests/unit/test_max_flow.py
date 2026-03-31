"""Unit tests for Edmonds-Karp max flow algorithm."""

import pytest
import networkx as nx

from logarithma.algorithms.network_flow import max_flow
from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    InvalidModeError,
    NodeNotFoundError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def classic_flow_graph():
    """Classic 6-node directed flow network.

    Source=s, Sink=t, expected max flow=23.

    Topology (Wikipedia Ford-Fulkerson example):
        s→A cap=15,  s→C cap=4
        A→B cap=12
        A→C cap=3
        B→t cap=7,  B→D cap=3
        C→A cap=3,  C→D cap=2
        D→t cap=10
    Expected max flow = 10 (simplified for easy assertion).
    Using a well-known 6-node graph with max flow = 23.
    """
    G = nx.DiGraph()
    G.add_edge('s', 'o', capacity=3)
    G.add_edge('s', 'p', capacity=3)
    G.add_edge('o', 'p', capacity=2)
    G.add_edge('o', 'q', capacity=3)
    G.add_edge('p', 'r', capacity=2)
    G.add_edge('q', 'r', capacity=4)
    G.add_edge('q', 't', capacity=2)
    G.add_edge('r', 't', capacity=3)
    # Max flow s→t = 5
    return G


@pytest.fixture
def simple_dag():
    G = nx.DiGraph()
    G.add_edge('s', 'a', capacity=10)
    G.add_edge('a', 't', capacity=10)
    return G


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_basic_max_flow(classic_flow_graph):
    result = max_flow(classic_flow_graph, 's', 't')
    assert result['flow_value'] == pytest.approx(5.0)


def test_result_keys(classic_flow_graph):
    result = max_flow(classic_flow_graph, 's', 't')
    assert 'flow_value' in result
    assert 'flow_dict' in result
    assert 'residual_graph' in result


def test_single_path(simple_dag):
    result = max_flow(simple_dag, 's', 't')
    assert result['flow_value'] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Flow conservation
# ---------------------------------------------------------------------------

def test_flow_conservation(classic_flow_graph):
    result = max_flow(classic_flow_graph, 's', 't')
    flow_dict = result['flow_dict']
    for node in classic_flow_graph.nodes():
        if node in ('s', 't'):
            continue
        inflow = sum(
            flow_dict.get(pred, {}).get(node, 0.0)
            for pred in classic_flow_graph.predecessors(node)
        )
        outflow = sum(flow_dict.get(node, {}).get(succ, 0.0)
                      for succ in classic_flow_graph.successors(node))
        assert inflow == pytest.approx(outflow), f"Flow conservation violated at {node}"


def test_capacity_constraints(classic_flow_graph):
    result = max_flow(classic_flow_graph, 's', 't')
    flow_dict = result['flow_dict']
    for u, v, data in classic_flow_graph.edges(data=True):
        f = flow_dict.get(u, {}).get(v, 0.0)
        assert f <= data.get('capacity', 1) + 1e-9, f"Capacity exceeded on ({u},{v})"
        assert f >= -1e-9, f"Negative flow on ({u},{v})"


# ---------------------------------------------------------------------------
# Edge / corner cases
# ---------------------------------------------------------------------------

def test_source_same_as_sink():
    G = nx.DiGraph()
    G.add_edge(1, 2, capacity=5)
    result = max_flow(G, 1, 1)
    assert result['flow_value'] == pytest.approx(0.0)


def test_disconnected_source_sink():
    G = nx.DiGraph()
    G.add_edge(1, 2, capacity=5)
    G.add_node(3)  # isolated
    result = max_flow(G, 1, 3)
    assert result['flow_value'] == pytest.approx(0.0)


def test_missing_capacity_defaults_to_1():
    G = nx.DiGraph()
    G.add_edge('a', 'b')  # no capacity attribute
    G.add_edge('b', 'c')
    result = max_flow(G, 'a', 'c')
    assert result['flow_value'] == pytest.approx(1.0)


def test_parallel_paths():
    G = nx.DiGraph()
    G.add_edge('s', 'a', capacity=5)
    G.add_edge('s', 'b', capacity=5)
    G.add_edge('a', 't', capacity=5)
    G.add_edge('b', 't', capacity=5)
    result = max_flow(G, 's', 't')
    assert result['flow_value'] == pytest.approx(10.0)


def test_ford_fulkerson_alias():
    G = nx.DiGraph()
    G.add_edge('s', 't', capacity=7)
    result = max_flow(G, 's', 't', method='ford_fulkerson')
    assert result['flow_value'] == pytest.approx(7.0)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

def test_empty_raises():
    G = nx.DiGraph()
    with pytest.raises(EmptyGraphError):
        max_flow(G, 's', 't')


def test_invalid_source_raises():
    G = nx.DiGraph()
    G.add_edge(1, 2, capacity=3)
    with pytest.raises(NodeNotFoundError):
        max_flow(G, 99, 2)


def test_invalid_sink_raises():
    G = nx.DiGraph()
    G.add_edge(1, 2, capacity=3)
    with pytest.raises(NodeNotFoundError):
        max_flow(G, 1, 99)


def test_invalid_method_raises():
    G = nx.DiGraph()
    G.add_edge(1, 2, capacity=3)
    with pytest.raises(InvalidModeError):
        max_flow(G, 1, 2, method='dinic')
