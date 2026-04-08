"""
Unit tests for Floyd-Warshall All-Pairs Shortest Path algorithm.

Test coverage:
    - Basic correctness (directed / undirected)
    - Path reconstruction
    - Negative edge weights (no cycle)
    - Negative-cycle detection
    - Edge cases: single node, two nodes, disconnected graph
    - Self-loops, parallel edges
    - Unreachable pairs
    - Comparison with Dijkstra (positive weights)
    - EmptyGraphError
"""

import math
import pytest
import networkx as nx

import logarithma as lg
from logarithma.algorithms.shortest_path.floyd_warshall import (
    floyd_warshall,
    floyd_warshall_path,
    reconstruct_path,
)
from logarithma.algorithms.exceptions import EmptyGraphError, NegativeCycleError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_directed():
    """Simple directed graph used in multiple tests."""
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=3)
    G.add_edge('A', 'C', weight=8)
    G.add_edge('B', 'C', weight=2)
    G.add_edge('B', 'D', weight=7)
    G.add_edge('C', 'D', weight=1)
    G.add_edge('D', 'E', weight=2)
    return G


def make_undirected():
    G = nx.Graph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('B', 'D', weight=5)
    G.add_edge('C', 'D', weight=8)
    G.add_edge('C', 'E', weight=10)
    G.add_edge('D', 'E', weight=2)
    return G


# ---------------------------------------------------------------------------
# Basic correctness — directed
# ---------------------------------------------------------------------------

class TestFloydWarshallDirected:
    def test_return_keys(self):
        G = make_directed()
        result = floyd_warshall(G)
        assert 'distances' in result
        assert 'predecessors' in result

    def test_all_nodes_present(self):
        G = make_directed()
        result = floyd_warshall(G)
        nodes = set(G.nodes())
        assert set(result['distances'].keys()) == nodes
        for u in nodes:
            assert set(result['distances'][u].keys()) == nodes

    def test_diagonal_zero(self):
        G = make_directed()
        result = floyd_warshall(G)
        for node in G.nodes():
            assert result['distances'][node][node] == 0.0

    def test_known_distances(self):
        G = make_directed()
        d = floyd_warshall(G)['distances']
        # A→D: A→B(3)→C(2)→D(1) = 6
        assert d['A']['D'] == pytest.approx(6.0)
        # A→E: A→B→C→D→E = 3+2+1+2 = 8
        assert d['A']['E'] == pytest.approx(8.0)
        # Direct A→C vs A→B→C: 8 vs 5 → 5
        assert d['A']['C'] == pytest.approx(5.0)
        # B→E: B→C→D→E = 2+1+2 = 5
        assert d['B']['E'] == pytest.approx(5.0)

    def test_unreachable_is_inf(self):
        G = make_directed()
        # No back-edges → E cannot reach A
        result = floyd_warshall(G)
        assert result['distances']['E']['A'] == float('inf')
        assert result['distances']['D']['A'] == float('inf')

    def test_top_level_api(self):
        G = make_directed()
        result = lg.floyd_warshall(G)
        assert result['distances']['A']['D'] == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# Basic correctness — undirected
# ---------------------------------------------------------------------------

class TestFloydWarshallUndirected:
    def test_symmetry(self):
        G = make_undirected()
        d = floyd_warshall(G)['distances']
        for u in G.nodes():
            for v in G.nodes():
                assert d[u][v] == pytest.approx(d[v][u])

    def test_known_distances(self):
        G = make_undirected()
        d = floyd_warshall(G)['distances']
        # A→B: direct=4, via C=2+1=3 → 3
        assert d['A']['B'] == pytest.approx(3.0)
        # A→E: A→C→B→D→E = 2+1+5+2=10, A→C→E=2+10=12 → 10
        assert d['A']['E'] == pytest.approx(10.0)

    def test_no_inf_for_connected(self):
        G = make_undirected()
        d = floyd_warshall(G)['distances']
        for u in G.nodes():
            for v in G.nodes():
                assert d[u][v] != float('inf')


# ---------------------------------------------------------------------------
# Path reconstruction
# ---------------------------------------------------------------------------

class TestFloydWarshallPath:
    def test_path_correct(self):
        G = make_directed()
        path = floyd_warshall_path(G, 'A', 'D')
        assert path[0] == 'A'
        assert path[-1] == 'D'
        # Verify every step is a real edge
        for i in range(len(path) - 1):
            assert G.has_edge(path[i], path[i + 1])

    def test_path_length_matches_distance(self):
        G = make_directed()
        result = floyd_warshall(G)
        path = reconstruct_path(result['predecessors'], 'A', 'E')
        total = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        assert total == pytest.approx(result['distances']['A']['E'])

    def test_path_to_self(self):
        G = make_directed()
        path = floyd_warshall_path(G, 'A', 'A')
        assert path == ['A']

    def test_path_unreachable(self):
        G = make_directed()
        path = floyd_warshall_path(G, 'E', 'A')
        assert path == []

    def test_path_undirected(self):
        G = make_undirected()
        path = floyd_warshall_path(G, 'A', 'E')
        assert path[0] == 'A'
        assert path[-1] == 'E'
        total = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        d = floyd_warshall(G)['distances']['A']['E']
        assert total == pytest.approx(d)


# ---------------------------------------------------------------------------
# Negative edge weights (no cycle)
# ---------------------------------------------------------------------------

class TestFloydWarshallNegativeWeights:
    def test_negative_edge_no_cycle(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=-3)   # negative but no cycle
        G.add_edge('C', 'D', weight=1)
        d = floyd_warshall(G)['distances']
        # A→C: direct=2, via B=4-3=1 → 1
        assert d['A']['C'] == pytest.approx(1.0)
        # A→D: 1+1=2
        assert d['A']['D'] == pytest.approx(2.0)

    def test_negative_edge_path(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=-3)
        G.add_edge('C', 'D', weight=1)
        path = floyd_warshall_path(G, 'A', 'C')
        assert path == ['A', 'B', 'C']


# ---------------------------------------------------------------------------
# Negative cycle detection
# ---------------------------------------------------------------------------

class TestFloydWarshallNegativeCycle:
    def test_raises_negative_cycle_error(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=-3)
        G.add_edge('C', 'A', weight=1)   # total cycle weight = -1
        with pytest.raises(NegativeCycleError):
            floyd_warshall(G)

    def test_self_loop_negative(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('A', 'A', weight=-1)   # negative self-loop
        with pytest.raises(NegativeCycleError):
            floyd_warshall(G)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestFloydWarshallEdgeCases:
    def test_empty_graph(self):
        G = nx.DiGraph()
        with pytest.raises(EmptyGraphError):
            floyd_warshall(G)

    def test_single_node(self):
        G = nx.DiGraph()
        G.add_node('A')
        result = floyd_warshall(G)
        assert result['distances']['A']['A'] == 0.0

    def test_two_nodes_directed(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=5)
        d = floyd_warshall(G)['distances']
        assert d['A']['B'] == pytest.approx(5.0)
        assert d['B']['A'] == float('inf')

    def test_two_nodes_undirected(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=5)
        d = floyd_warshall(G)['distances']
        assert d['A']['B'] == pytest.approx(5.0)
        assert d['B']['A'] == pytest.approx(5.0)

    def test_disconnected_graph(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('C', 'D', weight=2)
        d = floyd_warshall(G)['distances']
        assert d['A']['B'] == pytest.approx(1.0)
        assert d['C']['D'] == pytest.approx(2.0)
        assert d['A']['C'] == float('inf')
        assert d['A']['D'] == float('inf')

    def test_default_weight_one(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B')   # no weight attr
        G.add_edge('B', 'C')
        d = floyd_warshall(G)['distances']
        assert d['A']['C'] == pytest.approx(2.0)

    def test_integer_node_labels(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=1)
        G.add_edge(1, 2, weight=2)
        G.add_edge(0, 2, weight=10)
        d = floyd_warshall(G)['distances']
        assert d[0][2] == pytest.approx(3.0)

    def test_no_edges(self):
        G = nx.DiGraph()
        G.add_nodes_from(['A', 'B', 'C'])
        d = floyd_warshall(G)['distances']
        assert d['A']['B'] == float('inf')
        assert d['A']['A'] == 0.0


# ---------------------------------------------------------------------------
# Comparison with Dijkstra (positive weights)
# ---------------------------------------------------------------------------

class TestFloydWarshallVsDijkstra:
    def _random_graph(self, seed=42):
        import random
        rng = random.Random(seed)
        G = nx.DiGraph()
        nodes = list(range(10))
        G.add_nodes_from(nodes)
        for u in nodes:
            for v in nodes:
                if u != v and rng.random() < 0.4:
                    G.add_edge(u, v, weight=rng.randint(1, 20))
        return G

    def test_matches_dijkstra_all_pairs(self):
        G = self._random_graph()
        fw = floyd_warshall(G)['distances']
        for src in G.nodes():
            dijk = lg.dijkstra(G, src)
            for tgt in G.nodes():
                fw_d = fw[src][tgt]
                dijk_d = dijk[tgt]
                if math.isinf(fw_d):
                    assert math.isinf(dijk_d)
                else:
                    assert fw_d == pytest.approx(dijk_d, rel=1e-9)
