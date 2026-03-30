"""
Unit tests for the A* shortest path algorithm.

Test philosophy
---------------
1. Correctness — every result is cross-validated against Dijkstra, which is
   the reference implementation for non-negative weighted graphs.
2. Heuristic quality — zero heuristic must degenerate to Dijkstra; a well-
   informed heuristic must expand ≤ as many nodes as zero heuristic.
3. Edge cases — empty graph, single node, disconnected graph, self-loops,
   directed graphs, equal-weight edges.
4. Error handling — negative weights and invalid nodes raise ValueError.
"""

import math

import networkx as nx
import pytest

from logarithma.algorithms.shortest_path.astar import (
    astar,
    astar_with_stats,
    euclidean_heuristic,
    haversine_heuristic,
    manhattan_heuristic,
    zero_heuristic,
)
from logarithma.algorithms.shortest_path.dijkstra import dijkstra


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_graph():
    """5-node undirected graph with known shortest paths."""
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
def grid_graph_with_pos():
    """3×3 grid graph with (row, col) coordinates."""
    G = nx.grid_2d_graph(3, 3)
    for u, v in G.edges():
        G[u][v]['weight'] = 1
    pos = {node: (node[1], node[0]) for node in G.nodes()}  # (x=col, y=row)
    return G, pos


@pytest.fixture
def directed_graph():
    """Directed graph — asymmetric shortest paths."""
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=2)
    G.add_edge('A', 'C', weight=10)
    G.add_edge('C', 'D', weight=1)
    G.add_edge('D', 'A', weight=1)  # cycle back
    return G


# ---------------------------------------------------------------------------
# 1. Basic correctness
# ---------------------------------------------------------------------------

class TestAstarCorrectness:

    def test_simple_path(self, simple_graph):
        # A→C=2, C→B=1, B→D=5  → total 8  (optimal path)
        # A→B=4, B→D=5          → total 9
        result = astar(simple_graph, 'A', 'D')
        assert result['distance'] == 8
        dijk = dijkstra(simple_graph, 'A')
        assert result['distance'] == dijk['D']

    def test_result_matches_dijkstra_all_pairs(self, simple_graph):
        """A* (zero heuristic) must match Dijkstra for every pair."""
        nodes = list(simple_graph.nodes())
        for source in nodes:
            dijk = dijkstra(simple_graph, source)
            for target in nodes:
                result = astar(simple_graph, source, target)
                assert result['distance'] == pytest.approx(dijk[target]), (
                    f"Mismatch for {source}→{target}: "
                    f"astar={result['distance']}, dijkstra={dijk[target]}"
                )

    def test_path_is_valid(self, simple_graph):
        """The returned path must be a valid walk in the graph."""
        result = astar(simple_graph, 'A', 'E')
        path = result['path']
        assert path[0] == 'A'
        assert path[-1] == 'E'
        for i in range(len(path) - 1):
            assert simple_graph.has_edge(path[i], path[i + 1]), (
                f"Edge {path[i]}–{path[i+1]} not in graph"
            )

    def test_path_cost_matches_distance(self, simple_graph):
        """Sum of edge weights along the returned path == reported distance."""
        result = astar(simple_graph, 'A', 'E')
        path = result['path']
        cost = sum(
            simple_graph[path[i]][path[i + 1]]['weight']
            for i in range(len(path) - 1)
        )
        assert cost == pytest.approx(result['distance'])

    def test_source_equals_target(self, simple_graph):
        result = astar(simple_graph, 'A', 'A')
        assert result['distance'] == 0
        assert result['path'] == ['A']

    def test_unreachable_target(self):
        G = nx.Graph()
        G.add_nodes_from(['X', 'Y'])
        result = astar(G, 'X', 'Y')
        assert result['distance'] == float('inf')
        assert result['path'] == []

    def test_single_edge_graph(self):
        G = nx.Graph()
        G.add_edge('U', 'V', weight=7)
        result = astar(G, 'U', 'V')
        assert result['distance'] == 7
        assert result['path'] == ['U', 'V']


# ---------------------------------------------------------------------------
# 2. Directed graph
# ---------------------------------------------------------------------------

class TestAstarDirected:

    def test_directed_path_found(self, directed_graph):
        result = astar(directed_graph, 'A', 'D')
        assert result['distance'] == pytest.approx(4.0)   # A→B=1, B→C=2, C→D=1
        assert result['path'] == ['A', 'B', 'C', 'D']

    def test_directed_asymmetry(self, directed_graph):
        """A→D has a path but D→B does not (no outgoing edge from D to B)."""
        result = astar(directed_graph, 'D', 'B')
        # D→A=1, A→B=1 → distance 2
        assert result['distance'] == pytest.approx(2.0)

    def test_directed_matches_dijkstra(self, directed_graph):
        dijk = dijkstra(directed_graph, 'A')
        for target in directed_graph.nodes():
            result = astar(directed_graph, 'A', target)
            assert result['distance'] == pytest.approx(dijk[target])


# ---------------------------------------------------------------------------
# 3. Heuristic tests
# ---------------------------------------------------------------------------

class TestAstarHeuristics:

    def test_zero_heuristic_matches_dijkstra(self, simple_graph):
        dijk = dijkstra(simple_graph, 'A')
        result = astar(simple_graph, 'A', 'E', heuristic=zero_heuristic)
        assert result['distance'] == pytest.approx(dijk['E'])

    def test_euclidean_heuristic_correct_result(self, grid_graph_with_pos):
        G, pos = grid_graph_with_pos
        h = euclidean_heuristic(pos)
        source, target = (0, 0), (2, 2)
        result = astar(G, source, target, heuristic=h)
        dijk = dijkstra(G, source)
        assert result['distance'] == pytest.approx(dijk[target])

    def test_euclidean_heuristic_fewer_expansions(self, grid_graph_with_pos):
        """Informed heuristic should expand ≤ nodes compared to zero heuristic."""
        G, pos = grid_graph_with_pos
        source, target = (0, 0), (2, 2)

        h_zero = zero_heuristic
        h_euc = euclidean_heuristic(pos)

        stats_zero = astar_with_stats(G, source, target, heuristic=h_zero)
        stats_euc = astar_with_stats(G, source, target, heuristic=h_euc)

        assert stats_euc['nodes_expanded'] <= stats_zero['nodes_expanded']

    def test_manhattan_heuristic_grid(self, grid_graph_with_pos):
        G, pos = grid_graph_with_pos
        h = manhattan_heuristic(pos)
        source, target = (0, 0), (2, 2)
        result = astar(G, source, target, heuristic=h)
        dijk = dijkstra(G, source)
        assert result['distance'] == pytest.approx(dijk[target])

    def test_haversine_heuristic_geographic(self):
        """Simple geographic graph: Istanbul → Ankara → Izmir."""
        G = nx.Graph()
        # Approximate lat/lon coordinates
        cities = {
            'Istanbul': (41.0082, 28.9784),
            'Ankara':   (39.9334, 32.8597),
            'Izmir':    (38.4192, 27.1287),
        }
        G.add_node('Istanbul')
        G.add_node('Ankara')
        G.add_node('Izmir')

        # Haversine distances (approximate km) as edge weights
        def hav_dist(c1, c2):
            lat1, lon1 = map(math.radians, cities[c1])
            lat2, lon2 = map(math.radians, cities[c2])
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            return 2 * 6371 * math.asin(math.sqrt(a))

        G.add_edge('Istanbul', 'Ankara', weight=hav_dist('Istanbul', 'Ankara'))
        G.add_edge('Ankara', 'Izmir',   weight=hav_dist('Ankara', 'Izmir'))
        G.add_edge('Istanbul', 'Izmir', weight=hav_dist('Istanbul', 'Izmir'))

        h = haversine_heuristic(cities)
        result = astar(G, 'Istanbul', 'Izmir', heuristic=h)
        dijk = dijkstra(G, 'Istanbul')

        assert result['distance'] == pytest.approx(dijk['Izmir'], rel=1e-6)


# ---------------------------------------------------------------------------
# 4. Weighted graphs — various topologies
# ---------------------------------------------------------------------------

class TestAstarWeightedGraphs:

    def test_unweighted_edges_default_weight_1(self):
        G = nx.path_graph(5)  # 0-1-2-3-4, no weight attribute
        result = astar(G, 0, 4)
        assert result['distance'] == 4
        assert result['path'] == [0, 1, 2, 3, 4]

    def test_non_integer_weights(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1.5)
        G.add_edge('B', 'C', weight=2.3)
        G.add_edge('A', 'C', weight=5.0)
        result = astar(G, 'A', 'C')
        assert result['distance'] == pytest.approx(3.8)

    def test_parallel_path_chooses_shortest(self):
        """Two paths of length 3: one via high-weight edges, one via low."""
        G = nx.Graph()
        G.add_edge('S', 'M1', weight=1)
        G.add_edge('M1', 'T', weight=1)
        G.add_edge('S', 'M2', weight=10)
        G.add_edge('M2', 'T', weight=10)
        result = astar(G, 'S', 'T')
        assert result['distance'] == pytest.approx(2.0)
        assert 'M1' in result['path']

    def test_large_random_graph_matches_dijkstra(self):
        """Statistical correctness check on a random weighted graph."""
        import random
        random.seed(42)
        G = nx.gnm_random_graph(50, 200, seed=42)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(0.1, 10.0)

        for source in [0, 5, 10]:
            dijk = dijkstra(G, source)
            for target in [1, 20, 49]:
                if target in G:
                    result = astar(G, source, target)
                    assert result['distance'] == pytest.approx(dijk[target], rel=1e-9)


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

class TestAstarEdgeCases:

    def test_single_node_graph(self):
        G = nx.Graph()
        G.add_node('alone')
        result = astar(G, 'alone', 'alone')
        assert result['distance'] == 0
        assert result['path'] == ['alone']

    def test_self_loop_ignored(self):
        """Self-loops must not affect shortest path correctness."""
        G = nx.Graph()
        G.add_edge('A', 'A', weight=100)
        G.add_edge('A', 'B', weight=3)
        result = astar(G, 'A', 'B')
        assert result['distance'] == 3

    def test_disconnected_component(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('C', 'D', weight=1)  # isolated component
        result = astar(G, 'A', 'D')
        assert result['distance'] == float('inf')
        assert result['path'] == []

    def test_star_graph(self):
        """Star topology: all shortest paths go through the center."""
        G = nx.star_graph(5)
        for u, v in G.edges():
            G[u][v]['weight'] = 2
        result = astar(G, 1, 3)
        assert result['distance'] == 4      # 1→0→3
        assert result['path'] == [1, 0, 3]


# ---------------------------------------------------------------------------
# 6. Error handling
# ---------------------------------------------------------------------------

class TestAstarErrors:

    def test_empty_graph_raises(self):
        G = nx.Graph()
        with pytest.raises(ValueError, match="empty"):
            astar(G, 'A', 'B')

    def test_source_not_in_graph_raises(self):
        G = nx.path_graph(3)
        with pytest.raises(ValueError, match="Source"):
            astar(G, 99, 1)

    def test_target_not_in_graph_raises(self):
        G = nx.path_graph(3)
        with pytest.raises(ValueError, match="Target"):
            astar(G, 0, 99)

    def test_negative_weight_raises(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=-1)
        with pytest.raises(ValueError, match="Negative"):
            astar(G, 'A', 'B')


# ---------------------------------------------------------------------------
# 7. astar_with_stats
# ---------------------------------------------------------------------------

class TestAstarWithStats:

    def test_stats_keys_present(self, simple_graph):
        result = astar_with_stats(simple_graph, 'A', 'E')
        assert 'distance' in result
        assert 'path' in result
        assert 'nodes_expanded' in result
        assert 'nodes_generated' in result

    def test_stats_distance_matches_astar(self, simple_graph):
        r1 = astar(simple_graph, 'A', 'E')
        r2 = astar_with_stats(simple_graph, 'A', 'E')
        assert r1['distance'] == pytest.approx(r2['distance'])
        assert r1['path'] == r2['path']

    def test_nodes_expanded_positive(self, simple_graph):
        result = astar_with_stats(simple_graph, 'A', 'E')
        assert result['nodes_expanded'] >= 1
        assert result['nodes_generated'] >= result['nodes_expanded']

    def test_unreachable_stats(self):
        G = nx.Graph()
        G.add_nodes_from(['X', 'Y'])
        result = astar_with_stats(G, 'X', 'Y')
        assert result['distance'] == float('inf')
        assert result['nodes_expanded'] == 1  # only source expanded
