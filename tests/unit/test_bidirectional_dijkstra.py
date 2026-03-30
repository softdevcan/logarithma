"""
Unit tests for Bidirectional Dijkstra.

Test philosophy
---------------
1. Correctness — every result cross-validated against standard Dijkstra.
2. Directed graphs — backward search must follow reversed edges.
3. Edge cases — source == target, disconnected graph, single edge, self-loops.
4. Path validity — returned path must be a valid walk with matching cost.
5. Error handling — negative weights, missing nodes, empty graph.
"""

import networkx as nx
import pytest

from logarithma.algorithms.shortest_path.bidirectional_dijkstra import (
    bidirectional_dijkstra,
)
from logarithma.algorithms.shortest_path.dijkstra import dijkstra


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_undirected():
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
def simple_directed():
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=2)
    G.add_edge('A', 'C', weight=10)
    G.add_edge('C', 'D', weight=1)
    G.add_edge('D', 'E', weight=3)
    return G


# ---------------------------------------------------------------------------
# 1. Correctness — match standard Dijkstra
# ---------------------------------------------------------------------------

class TestBidirectionalDijkstraCorrectness:

    def test_undirected_matches_dijkstra_all_pairs(self, simple_undirected):
        nodes = list(simple_undirected.nodes())
        for source in nodes:
            dijk = dijkstra(simple_undirected, source)
            for target in nodes:
                result = bidirectional_dijkstra(simple_undirected, source, target)
                assert result['distance'] == pytest.approx(dijk[target]), (
                    f"{source}→{target}: bidir={result['distance']}, dijk={dijk[target]}"
                )

    def test_directed_matches_dijkstra(self, simple_directed):
        dijk = dijkstra(simple_directed, 'A')
        for target in simple_directed.nodes():
            result = bidirectional_dijkstra(simple_directed, 'A', target)
            assert result['distance'] == pytest.approx(dijk[target])

    def test_path_cost_equals_distance(self, simple_undirected):
        result = bidirectional_dijkstra(simple_undirected, 'A', 'E')
        path = result['path']
        cost = sum(
            simple_undirected[path[i]][path[i + 1]]['weight']
            for i in range(len(path) - 1)
        )
        assert cost == pytest.approx(result['distance'])

    def test_path_is_valid_walk_undirected(self, simple_undirected):
        result = bidirectional_dijkstra(simple_undirected, 'A', 'E')
        path = result['path']
        assert path[0] == 'A'
        assert path[-1] == 'E'
        for i in range(len(path) - 1):
            assert simple_undirected.has_edge(path[i], path[i + 1])

    def test_path_is_valid_walk_directed(self, simple_directed):
        result = bidirectional_dijkstra(simple_directed, 'A', 'E')
        path = result['path']
        assert path[0] == 'A'
        assert path[-1] == 'E'
        for i in range(len(path) - 1):
            assert simple_directed.has_edge(path[i], path[i + 1])

    def test_large_random_undirected_matches_dijkstra(self):
        import random
        random.seed(2024)
        G = nx.gnm_random_graph(60, 200, seed=2024)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(0.5, 20.0)

        for source, target in [(0, 30), (5, 55), (10, 40)]:
            dijk = dijkstra(G, source)
            result = bidirectional_dijkstra(G, source, target)
            assert result['distance'] == pytest.approx(dijk[target], rel=1e-9)

    def test_large_random_directed_matches_dijkstra(self):
        import random
        random.seed(99)
        G = nx.gnm_random_graph(50, 180, seed=99, directed=True)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1.0, 15.0)

        for source, target in [(0, 25), (3, 40)]:
            dijk = dijkstra(G, source)
            result = bidirectional_dijkstra(G, source, target)
            assert result['distance'] == pytest.approx(dijk[target], rel=1e-9)


# ---------------------------------------------------------------------------
# 2. Directed graph — asymmetric paths
# ---------------------------------------------------------------------------

class TestBidirectionalDijkstraDirected:

    def test_directed_forward_path(self):
        G = nx.DiGraph()
        G.add_edge('S', 'A', weight=1)
        G.add_edge('A', 'T', weight=1)
        G.add_edge('T', 'S', weight=100)  # no useful shortcut
        result = bidirectional_dijkstra(G, 'S', 'T')
        assert result['distance'] == pytest.approx(2.0)
        assert result['path'] == ['S', 'A', 'T']

    def test_directed_no_reverse_path(self):
        """S→T exists but T→S does not: backward search has no forward edges."""
        G = nx.DiGraph()
        G.add_edge('S', 'M', weight=3)
        G.add_edge('M', 'T', weight=3)
        result = bidirectional_dijkstra(G, 'S', 'T')
        assert result['distance'] == pytest.approx(6.0)

    def test_directed_asymmetric_weight(self):
        """Two one-way paths; only the cheaper one counts."""
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=1)
        G.add_edge('A', 'C', weight=100)
        result = bidirectional_dijkstra(G, 'A', 'C')
        assert result['distance'] == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# 3. Edge cases
# ---------------------------------------------------------------------------

class TestBidirectionalDijkstraEdgeCases:

    def test_source_equals_target(self, simple_undirected):
        result = bidirectional_dijkstra(simple_undirected, 'B', 'B')
        assert result['distance'] == 0.0
        assert result['path'] == ['B']

    def test_single_edge_graph(self):
        G = nx.Graph()
        G.add_edge('X', 'Y', weight=7)
        result = bidirectional_dijkstra(G, 'X', 'Y')
        assert result['distance'] == pytest.approx(7.0)
        assert result['path'] == ['X', 'Y']

    def test_disconnected_graph(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        G.add_node('Z')
        result = bidirectional_dijkstra(G, 'A', 'Z')
        assert result['distance'] == float('inf')
        assert result['path'] == []

    def test_disconnected_directed_graph(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('C', 'D', weight=1)   # separate component
        result = bidirectional_dijkstra(G, 'A', 'D')
        assert result['distance'] == float('inf')

    def test_self_loop_ignored(self):
        G = nx.Graph()
        G.add_edge('A', 'A', weight=999)
        G.add_edge('A', 'B', weight=2)
        result = bidirectional_dijkstra(G, 'A', 'B')
        assert result['distance'] == pytest.approx(2.0)

    def test_unweighted_graph(self):
        """No weight attribute — defaults to 1 per edge."""
        G = nx.grid_2d_graph(4, 4)
        result = bidirectional_dijkstra(G, (0, 0), (3, 3))
        dijk = dijkstra(G, (0, 0))
        assert result['distance'] == pytest.approx(dijk[(3, 3)])

    def test_path_graph_chain(self):
        G = nx.path_graph(10)
        for u, v in G.edges():
            G[u][v]['weight'] = 1
        result = bidirectional_dijkstra(G, 0, 9)
        assert result['distance'] == pytest.approx(9.0)
        assert result['path'] == list(range(10))

    def test_complete_graph(self):
        """In a complete graph the shortest path should be the direct edge."""
        G = nx.complete_graph(5)
        for u, v in G.edges():
            G[u][v]['weight'] = 10
        G[0][4]['weight'] = 1   # shortcut
        result = bidirectional_dijkstra(G, 0, 4)
        assert result['distance'] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 4. Error handling
# ---------------------------------------------------------------------------

class TestBidirectionalDijkstraErrors:

    def test_empty_graph_raises(self):
        with pytest.raises(ValueError, match="empty"):
            bidirectional_dijkstra(nx.Graph(), 'A', 'B')

    def test_source_missing_raises(self):
        G = nx.path_graph(3)
        with pytest.raises(ValueError, match="Source"):
            bidirectional_dijkstra(G, 99, 1)

    def test_target_missing_raises(self):
        G = nx.path_graph(3)
        with pytest.raises(ValueError, match="Target"):
            bidirectional_dijkstra(G, 0, 99)

    def test_negative_weight_raises(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=-3)
        with pytest.raises(ValueError, match="Negative"):
            bidirectional_dijkstra(G, 'A', 'B')

    def test_negative_weight_directed_raises(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=-2)
        with pytest.raises(ValueError, match="Negative"):
            bidirectional_dijkstra(G, 'A', 'C')
