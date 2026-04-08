"""
Unit tests for Johnson's All-Pairs Shortest Path algorithm.

Test coverage:
    - Basic correctness (directed / undirected)
    - Path reconstruction
    - Negative edge weights (no cycle)
    - Negative-cycle detection
    - Edge cases: single node, two nodes, disconnected graph
    - Default weight (no 'weight' attribute)
    - Integer and string node labels
    - Comparison with Floyd-Warshall and Dijkstra
    - EmptyGraphError
"""

import math
import pytest
import networkx as nx

import logarithma as lg
from logarithma.algorithms.shortest_path.johnson import (
    johnson,
    johnson_path,
    reconstruct_path,
)
from logarithma.algorithms.exceptions import EmptyGraphError, NegativeCycleError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_directed():
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

class TestJohnsonDirected:
    def test_return_keys(self):
        G = make_directed()
        result = johnson(G)
        assert 'distances' in result
        assert 'predecessors' in result

    def test_all_nodes_present(self):
        G = make_directed()
        result = johnson(G)
        nodes = set(G.nodes())
        assert set(result['distances'].keys()) == nodes
        for u in nodes:
            assert set(result['distances'][u].keys()) == nodes

    def test_diagonal_zero(self):
        G = make_directed()
        d = johnson(G)['distances']
        for node in G.nodes():
            assert d[node][node] == pytest.approx(0.0)

    def test_known_distances(self):
        G = make_directed()
        d = johnson(G)['distances']
        # A→D: A→B(3)→C(2)→D(1) = 6
        assert d['A']['D'] == pytest.approx(6.0)
        # A→E: A→B→C→D→E = 3+2+1+2 = 8
        assert d['A']['E'] == pytest.approx(8.0)
        # A→C: direct=8, via B=3+2=5 → 5
        assert d['A']['C'] == pytest.approx(5.0)
        # B→E: B→C→D→E = 2+1+2 = 5
        assert d['B']['E'] == pytest.approx(5.0)

    def test_unreachable_is_inf(self):
        G = make_directed()
        d = johnson(G)['distances']
        assert d['E']['A'] == float('inf')
        assert d['D']['A'] == float('inf')

    def test_top_level_api(self):
        G = make_directed()
        result = lg.johnson(G)
        assert result['distances']['A']['D'] == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# Basic correctness — undirected
# ---------------------------------------------------------------------------

class TestJohnsonUndirected:
    def test_symmetry(self):
        G = make_undirected()
        d = johnson(G)['distances']
        for u in G.nodes():
            for v in G.nodes():
                assert d[u][v] == pytest.approx(d[v][u])

    def test_known_distances(self):
        G = make_undirected()
        d = johnson(G)['distances']
        # A→B: direct=4, via C=2+1=3 → 3
        assert d['A']['B'] == pytest.approx(3.0)
        # A→E: A→C→B→D→E = 2+1+5+2=10, A→C→E=12 → 10
        assert d['A']['E'] == pytest.approx(10.0)

    def test_no_inf_for_connected(self):
        G = make_undirected()
        d = johnson(G)['distances']
        for u in G.nodes():
            for v in G.nodes():
                assert d[u][v] != float('inf')


# ---------------------------------------------------------------------------
# Path reconstruction
# ---------------------------------------------------------------------------

class TestJohnsonPath:
    def test_path_correct(self):
        G = make_directed()
        path = johnson_path(G, 'A', 'D')
        assert path[0] == 'A'
        assert path[-1] == 'D'
        for i in range(len(path) - 1):
            assert G.has_edge(path[i], path[i + 1])

    def test_path_length_matches_distance(self):
        G = make_directed()
        result = johnson(G)
        path = reconstruct_path(result['predecessors'], 'A', 'E')
        total = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        assert total == pytest.approx(result['distances']['A']['E'])

    def test_path_to_self(self):
        G = make_directed()
        path = johnson_path(G, 'A', 'A')
        assert path == ['A']

    def test_path_unreachable(self):
        G = make_directed()
        path = johnson_path(G, 'E', 'A')
        assert path == []

    def test_path_undirected(self):
        G = make_undirected()
        path = johnson_path(G, 'A', 'E')
        assert path[0] == 'A'
        assert path[-1] == 'E'
        total = sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        d = johnson(G)['distances']['A']['E']
        assert total == pytest.approx(d)


# ---------------------------------------------------------------------------
# Negative edge weights (no cycle)
# ---------------------------------------------------------------------------

class TestJohnsonNegativeWeights:
    def test_negative_edge_no_cycle(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=-3)   # negative, no cycle
        G.add_edge('C', 'D', weight=1)
        d = johnson(G)['distances']
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
        path = johnson_path(G, 'A', 'C')
        assert path == ['A', 'B', 'C']

    def test_all_negative_edges_no_cycle(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=-1)
        G.add_edge('B', 'C', weight=-2)
        # A→C via B = -3; no cycle
        d = johnson(G)['distances']
        assert d['A']['C'] == pytest.approx(-3.0)


# ---------------------------------------------------------------------------
# Negative cycle detection
# ---------------------------------------------------------------------------

class TestJohnsonNegativeCycle:
    def test_raises_negative_cycle_error(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=-3)
        G.add_edge('C', 'A', weight=1)   # cycle total = -1
        with pytest.raises(NegativeCycleError):
            johnson(G)

    def test_two_node_negative_cycle(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=-1)
        G.add_edge('B', 'A', weight=-1)
        with pytest.raises(NegativeCycleError):
            johnson(G)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestJohnsonEdgeCases:
    def test_empty_graph(self):
        G = nx.DiGraph()
        with pytest.raises(EmptyGraphError):
            johnson(G)

    def test_single_node(self):
        G = nx.DiGraph()
        G.add_node('A')
        result = johnson(G)
        assert result['distances']['A']['A'] == pytest.approx(0.0)

    def test_two_nodes_directed(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=5)
        d = johnson(G)['distances']
        assert d['A']['B'] == pytest.approx(5.0)
        assert d['B']['A'] == float('inf')

    def test_two_nodes_undirected(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=5)
        d = johnson(G)['distances']
        assert d['A']['B'] == pytest.approx(5.0)
        assert d['B']['A'] == pytest.approx(5.0)

    def test_disconnected_graph(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('C', 'D', weight=2)
        d = johnson(G)['distances']
        assert d['A']['B'] == pytest.approx(1.0)
        assert d['C']['D'] == pytest.approx(2.0)
        assert d['A']['C'] == float('inf')
        assert d['A']['D'] == float('inf')

    def test_default_weight_one(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B')
        G.add_edge('B', 'C')
        d = johnson(G)['distances']
        assert d['A']['C'] == pytest.approx(2.0)

    def test_integer_node_labels(self):
        G = nx.DiGraph()
        G.add_edge(0, 1, weight=1)
        G.add_edge(1, 2, weight=2)
        G.add_edge(0, 2, weight=10)
        d = johnson(G)['distances']
        assert d[0][2] == pytest.approx(3.0)

    def test_no_edges(self):
        G = nx.DiGraph()
        G.add_nodes_from(['A', 'B', 'C'])
        d = johnson(G)['distances']
        assert d['A']['B'] == float('inf')
        assert d['A']['A'] == pytest.approx(0.0)

    def test_linear_chain(self):
        G = nx.DiGraph()
        for i in range(5):
            G.add_edge(i, i + 1, weight=1)
        d = johnson(G)['distances']
        assert d[0][5] == pytest.approx(5.0)
        assert d[5][0] == float('inf')


# ---------------------------------------------------------------------------
# Comparison with Floyd-Warshall and Dijkstra
# ---------------------------------------------------------------------------

class TestJohnsonVsOtherAlgorithms:
    def _random_positive_graph(self, seed=7):
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

    def test_matches_floyd_warshall(self):
        from logarithma.algorithms.shortest_path.floyd_warshall import floyd_warshall
        G = self._random_positive_graph()
        j = johnson(G)['distances']
        fw = floyd_warshall(G)['distances']
        for u in G.nodes():
            for v in G.nodes():
                j_d = j[u][v]
                fw_d = fw[u][v]
                if math.isinf(j_d):
                    assert math.isinf(fw_d)
                else:
                    assert j_d == pytest.approx(fw_d, rel=1e-9)

    def test_matches_dijkstra(self):
        G = self._random_positive_graph()
        j = johnson(G)['distances']
        for src in G.nodes():
            dijk = lg.dijkstra(G, src)
            for tgt in G.nodes():
                j_d = j[src][tgt]
                dijk_d = dijk[tgt]
                if math.isinf(j_d):
                    assert math.isinf(dijk_d)
                else:
                    assert j_d == pytest.approx(dijk_d, rel=1e-9)

    def test_negative_weights_matches_floyd_warshall(self):
        from logarithma.algorithms.shortest_path.floyd_warshall import floyd_warshall
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=-3)
        G.add_edge('C', 'D', weight=1)
        G.add_edge('D', 'B', weight=2)
        j = johnson(G)['distances']
        fw = floyd_warshall(G)['distances']
        for u in G.nodes():
            for v in G.nodes():
                j_d = j[u][v]
                fw_d = fw[u][v]
                if math.isinf(j_d):
                    assert math.isinf(fw_d)
                else:
                    assert j_d == pytest.approx(fw_d, rel=1e-9)
