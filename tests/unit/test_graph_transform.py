"""
Tests for constant-degree graph transform
==========================================

Validates that the Frederickson 1983 vertex-splitting transform:
1. Produces a graph with max in/out-degree <= 2
2. Preserves shortest-path distances
3. Handles edge cases (single node, disconnected, zero-weight, etc.)
"""

import networkx as nx
import pytest

from logarithma.algorithms.shortest_path.graph_transform import (
    to_constant_degree,
    map_distances_back,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _max_degree(G: nx.DiGraph) -> int:
    """Return max of in-degree and out-degree across all nodes."""
    max_in = max((G.in_degree(v) for v in G.nodes()), default=0)
    max_out = max((G.out_degree(v) for v in G.nodes()), default=0)
    return max(max_in, max_out)


def _dijkstra_reachable(G, source):
    """Dijkstra distances for reachable nodes only."""
    lengths = dict(nx.single_source_dijkstra_path_length(G, source))
    return {n: d for n, d in lengths.items() if d < float('inf')}


def _assert_distances_equal(result, expected, tol=1e-9):
    assert set(result.keys()) == set(expected.keys()), (
        f"Key mismatch: got {sorted(result.keys(), key=repr)}, "
        f"expected {sorted(expected.keys(), key=repr)}"
    )
    for node in expected:
        assert abs(result[node] - expected[node]) < tol, (
            f"d[{node}]: got {result[node]}, expected {expected[node]}"
        )


# ---------------------------------------------------------------------------
# Degree constraint tests
# ---------------------------------------------------------------------------

class TestDegreeConstraint:

    def test_simple_graph_max_degree_2(self):
        G = nx.DiGraph()
        G.add_edge('s', 'A', weight=2)
        G.add_edge('s', 'B', weight=5)
        G.add_edge('A', 'C', weight=1)
        G.add_edge('B', 'C', weight=2)
        G_prime, _, _ = to_constant_degree(G, 's')
        assert _max_degree(G_prime) <= 2

    def test_high_degree_node(self):
        """A node with degree 10 should still produce max degree 2."""
        G = nx.DiGraph()
        for i in range(10):
            G.add_edge('hub', i, weight=float(i + 1))
        G_prime, _, _ = to_constant_degree(G, 'hub')
        assert _max_degree(G_prime) <= 2

    def test_complete_graph_degree_2(self):
        n = 6
        G = nx.DiGraph()
        for i in range(n):
            for j in range(n):
                if i != j:
                    G.add_edge(i, j, weight=float(abs(i - j)))
        G_prime, _, _ = to_constant_degree(G, 0)
        assert _max_degree(G_prime) <= 2

    def test_bidirectional_edges_degree_2(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=3)
        G.add_edge('B', 'A', weight=4)
        G_prime, _, _ = to_constant_degree(G, 'A')
        assert _max_degree(G_prime) <= 2


# ---------------------------------------------------------------------------
# Distance preservation tests
# ---------------------------------------------------------------------------

class TestDistancePreservation:

    def test_walkthrough_graph(self):
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

        expected = {'s': 0, 'A': 2, 'B': 5, 'C': 3, 'D': 6, 'E': 8, 'F': 6, 'G': 8}
        G_prime, source_prime, node_map = to_constant_degree(G, 's')

        dist_prime = _dijkstra_reachable(G_prime, source_prime)
        result = map_distances_back(dist_prime, node_map)
        _assert_distances_equal(result, expected)

    def test_linear_chain(self):
        G = nx.DiGraph()
        for i in range(5):
            G.add_edge(i, i + 1, weight=1)
        expected = {i: float(i) for i in range(6)}

        G_prime, sp, nm = to_constant_degree(G, 0)
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        _assert_distances_equal(result, expected)

    def test_zero_weight_edges(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=0)
        G.add_edge('B', 'C', weight=0)
        G.add_edge('A', 'C', weight=1)

        G_prime, sp, nm = to_constant_degree(G, 'A')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert result['C'] == 0.0

    def test_float_weights(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1.5)
        G.add_edge('B', 'C', weight=2.5)
        G.add_edge('A', 'C', weight=5.0)

        G_prime, sp, nm = to_constant_degree(G, 'A')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert abs(result['C'] - 4.0) < 1e-9

    def test_default_weight_is_one(self):
        G = nx.DiGraph()
        G.add_edge('X', 'Y')
        G_prime, sp, nm = to_constant_degree(G, 'X')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert result == {'X': 0, 'Y': 1}

    def test_parallel_paths(self):
        G = nx.DiGraph()
        G.add_edge('A', 'C', weight=10)
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=1)

        G_prime, sp, nm = to_constant_degree(G, 'A')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert result['C'] == 2


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_single_node(self):
        G = nx.DiGraph()
        G.add_node('x')
        G_prime, sp, nm = to_constant_degree(G, 'x')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert result == {'x': 0}

    def test_two_nodes_no_path(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=3)
        G_prime, sp, nm = to_constant_degree(G, 'B')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert result == {'B': 0}

    def test_disconnected_graph(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_node('C')
        G_prime, sp, nm = to_constant_degree(G, 'A')
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert 'C' not in result
        assert result == {'A': 0, 'B': 1}

    def test_self_loop(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=2)
        G.add_edge('A', 'A', weight=5)  # self-loop
        G_prime, sp, nm = to_constant_degree(G, 'A')
        assert _max_degree(G_prime) <= 2
        dist_prime = _dijkstra_reachable(G_prime, sp)
        result = map_distances_back(dist_prime, nm)
        assert result['A'] == 0
        assert result['B'] == 2


# ---------------------------------------------------------------------------
# Graph size tests
# ---------------------------------------------------------------------------

class TestGraphSize:

    def test_vertex_count_is_O_m(self):
        """G' should have at most 2m + n vertices (each edge creates 2 cycle nodes)."""
        G = nx.DiGraph()
        for i in range(10):
            G.add_edge(i, (i + 1) % 10, weight=1)
            G.add_edge(i, (i + 3) % 10, weight=2)
        m = G.number_of_edges()
        n = G.number_of_nodes()
        G_prime, _, _ = to_constant_degree(G, 0)
        # Upper bound: each edge contributes at most 2 cycle nodes
        # but neighbours are deduplicated, so actual count <= 2m
        assert G_prime.number_of_nodes() <= 2 * m + n

    def test_edge_count_is_O_m(self):
        """G' should have O(m) edges: m original + cycle edges."""
        G = nx.DiGraph()
        for i in range(10):
            G.add_edge(i, (i + 1) % 10, weight=1)
        m = G.number_of_edges()
        G_prime, _, _ = to_constant_degree(G, 0)
        # Cycle edges + original edges: at most 2 * (cycle_nodes) + m
        # Loose bound: 4m is safe
        assert G_prime.number_of_edges() <= 4 * m + G.number_of_nodes()


# ---------------------------------------------------------------------------
# Random graph comparison with Dijkstra
# ---------------------------------------------------------------------------

import random

def _random_directed_graph(n, edge_prob, seed):
    rng = random.Random(seed)
    G = nx.DiGraph()
    nodes = list(range(n))
    G.add_nodes_from(nodes)
    for u in nodes:
        for v in nodes:
            if u != v and rng.random() < edge_prob:
                G.add_edge(u, v, weight=round(rng.uniform(0.1, 10.0), 2))
    return G


@pytest.mark.parametrize("seed", range(20))
def test_random_graph_distances_preserved(seed):
    G = _random_directed_graph(n=15, edge_prob=0.3, seed=seed)
    if G.number_of_nodes() == 0:
        return
    source = 0
    expected = _dijkstra_reachable(G, source)

    G_prime, sp, nm = to_constant_degree(G, source)
    assert _max_degree(G_prime) <= 2

    dist_prime = _dijkstra_reachable(G_prime, sp)
    result = map_distances_back(dist_prime, nm)
    _assert_distances_equal(result, expected)
