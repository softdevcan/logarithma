"""
Tests for breaking_barrier_sssp
================================

Correctness is validated by comparing against Dijkstra on random graphs.
"""

import math
import random

import networkx as nx
import pytest

from logarithma import breaking_barrier_sssp, dijkstra
from logarithma.algorithms.exceptions import (
    EmptyGraphError,
    NodeNotFoundError,
    NegativeWeightError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assert_distances_equal(result: dict, expected: dict, tol: float = 1e-9):
    """Both dicts must have the same keys and values within tol."""
    assert set(result.keys()) == set(expected.keys()), (
        f"Key mismatch: got {set(result.keys())}, expected {set(expected.keys())}"
    )
    for node in expected:
        assert abs(result[node] - expected[node]) < tol, (
            f"d[{node}]: got {result[node]}, expected {expected[node]}"
        )


def _dijkstra_reachable(G, source):
    """Return Dijkstra distances for reachable nodes only."""
    all_dist = dijkstra(G, source)
    return {n: d for n, d in all_dist.items() if d < float('inf')}


# ---------------------------------------------------------------------------
# Walkthrough graph (hand-verified)
# ---------------------------------------------------------------------------

@pytest.fixture
def walkthrough_graph():
    G = nx.DiGraph()
    G.add_edge('s', 'A', weight=2)
    G.add_edge('s', 'B', weight=5)
    G.add_edge('A', 'C', weight=1)
    G.add_edge('A', 'D', weight=4)
    G.add_edge('B', 'D', weight=1)
    G.add_edge('B', 'E', weight=3)
    G.add_edge('C', 'F', weight=3)
    G.add_edge('D', 'F', weight=1)
    G.add_edge('D', 'G', weight=2)
    G.add_edge('E', 'G', weight=1)
    G.add_edge('F', 'G', weight=2)
    return G


def test_walkthrough_graph(walkthrough_graph):
    result = breaking_barrier_sssp(walkthrough_graph, 's')
    expected = {'s': 0, 'A': 2, 'B': 5, 'C': 3, 'D': 6, 'E': 8, 'F': 6, 'G': 8}
    _assert_distances_equal(result, expected)


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_single_node():
    G = nx.DiGraph()
    G.add_node('x')
    result = breaking_barrier_sssp(G, 'x')
    assert result == {'x': 0}


def test_two_nodes_connected():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=3)
    result = breaking_barrier_sssp(G, 'A')
    assert result == {'A': 0, 'B': 3}


def test_two_nodes_no_path():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=3)
    result = breaking_barrier_sssp(G, 'B')
    assert result == {'B': 0}


def test_linear_chain():
    G = nx.DiGraph()
    for i in range(5):
        G.add_edge(i, i + 1, weight=1)
    result = breaking_barrier_sssp(G, 0)
    expected = {i: float(i) for i in range(6)}
    _assert_distances_equal(result, expected)


def test_zero_weight_edges():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=0)
    G.add_edge('B', 'C', weight=0)
    G.add_edge('A', 'C', weight=1)
    result = breaking_barrier_sssp(G, 'A')
    assert result['C'] == 0.0


def test_all_same_weight():
    G = nx.DiGraph()
    edges = [('s', 'a'), ('s', 'b'), ('a', 'c'), ('b', 'c'), ('c', 'd')]
    for u, v in edges:
        G.add_edge(u, v, weight=2)
    result = breaking_barrier_sssp(G, 's')
    expected = {'s': 0, 'a': 2, 'b': 2, 'c': 4, 'd': 6}
    _assert_distances_equal(result, expected)


def test_disconnected_graph():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_node('C')  # isolated
    result = breaking_barrier_sssp(G, 'A')
    assert 'C' not in result
    assert result == {'A': 0, 'B': 1}


def test_float_weights():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1.5)
    G.add_edge('B', 'C', weight=2.5)
    G.add_edge('A', 'C', weight=5.0)
    result = breaking_barrier_sssp(G, 'A')
    assert abs(result['C'] - 4.0) < 1e-9


def test_default_weight_is_one():
    G = nx.DiGraph()
    G.add_edge('X', 'Y')  # no weight attribute
    result = breaking_barrier_sssp(G, 'X')
    assert result == {'X': 0, 'Y': 1}


def test_parallel_paths_picks_shorter():
    # Two paths A→C: direct (w=10) vs A→B→C (w=1+1=2)
    G = nx.DiGraph()
    G.add_edge('A', 'C', weight=10)
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=1)
    result = breaking_barrier_sssp(G, 'A')
    assert result['C'] == 2


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_empty_graph_raises():
    G = nx.DiGraph()
    with pytest.raises(EmptyGraphError):
        breaking_barrier_sssp(G, 'x')


def test_source_not_found_raises():
    G = nx.DiGraph()
    G.add_node('A')
    with pytest.raises(NodeNotFoundError):
        breaking_barrier_sssp(G, 'Z')


def test_negative_weight_raises():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=-1)
    with pytest.raises(NegativeWeightError):
        breaking_barrier_sssp(G, 'A')


# ---------------------------------------------------------------------------
# Comparison against Dijkstra — random graphs
# ---------------------------------------------------------------------------

def _random_directed_graph(n: int, edge_prob: float, seed: int) -> nx.DiGraph:
    rng = random.Random(seed)
    G = nx.DiGraph()
    nodes = list(range(n))
    G.add_nodes_from(nodes)
    for u in nodes:
        for v in nodes:
            if u != v and rng.random() < edge_prob:
                G.add_edge(u, v, weight=round(rng.uniform(0.1, 10.0), 2))
    return G


@pytest.mark.parametrize("seed", range(30))
def test_matches_dijkstra_random_small(seed):
    G = _random_directed_graph(n=10, edge_prob=0.4, seed=seed)
    if G.number_of_nodes() == 0:
        return
    source = 0
    result = breaking_barrier_sssp(G, source)
    expected = _dijkstra_reachable(G, source)
    _assert_distances_equal(result, expected)


@pytest.mark.parametrize("seed", range(10))
def test_matches_dijkstra_random_medium(seed):
    G = _random_directed_graph(n=50, edge_prob=0.15, seed=seed + 100)
    source = 0
    result = breaking_barrier_sssp(G, source)
    expected = _dijkstra_reachable(G, source)
    _assert_distances_equal(result, expected)


@pytest.mark.parametrize("seed", range(5))
def test_matches_dijkstra_random_larger(seed):
    G = _random_directed_graph(n=200, edge_prob=0.05, seed=seed + 200)
    source = 0
    result = breaking_barrier_sssp(G, source)
    expected = _dijkstra_reachable(G, source)
    _assert_distances_equal(result, expected)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_source_is_sink():
    """Source has no outgoing edges."""
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('C', 'B', weight=1)
    result = breaking_barrier_sssp(G, 'B')
    assert result == {'B': 0}


def test_complete_directed_graph():
    n = 6
    G = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if i != j:
                G.add_edge(i, j, weight=float(abs(i - j)))
    source = 0
    result = breaking_barrier_sssp(G, source)
    expected = _dijkstra_reachable(G, source)
    _assert_distances_equal(result, expected)


def test_star_graph():
    G = nx.DiGraph()
    for i in range(1, 8):
        G.add_edge(0, i, weight=float(i))
    result = breaking_barrier_sssp(G, 0)
    for i in range(1, 8):
        assert result[i] == float(i)


def test_dag_with_multiple_paths():
    G = nx.DiGraph()
    G.add_edge('s', 'a', weight=1)
    G.add_edge('s', 'b', weight=4)
    G.add_edge('a', 'b', weight=2)
    G.add_edge('a', 'c', weight=5)
    G.add_edge('b', 'c', weight=1)
    result = breaking_barrier_sssp(G, 's')
    expected = {'s': 0, 'a': 1, 'b': 3, 'c': 4}
    _assert_distances_equal(result, expected)
