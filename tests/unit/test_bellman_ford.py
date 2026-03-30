"""
Unit tests for the Bellman-Ford shortest path algorithm.

Test philosophy
---------------
1. Correctness  — results on non-negative-weight graphs must match Dijkstra.
2. Negative edges — must produce correct distances where Dijkstra would fail.
3. Negative cycles — NegativeCycleError must be raised with cycle info.
4. Undirected graphs — both edge directions must be relaxed.
5. Edge cases — empty graph, single node, disconnected graph, self-loops.
6. Path reconstruction — bellman_ford_path must return a valid walk.
"""

import networkx as nx
import pytest

from logarithma.algorithms.shortest_path.bellman_ford import (
    NegativeCycleError,
    bellman_ford,
    bellman_ford_path,
)
from logarithma.algorithms.shortest_path.dijkstra import dijkstra


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_digraph():
    """Directed graph without negative weights — Dijkstra is the reference."""
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('B', 'D', weight=5)
    G.add_edge('C', 'D', weight=8)
    G.add_edge('C', 'E', weight=10)
    G.add_edge('D', 'E', weight=2)
    return G


@pytest.fixture
def negative_edge_digraph():
    """
    Directed graph WITH a negative edge, but NO negative cycle.
    Known shortest distances from A:
        A→A = 0
        A→B = 4
        A→C = 4 + (-3) = 1
        A→D = 1 + 1 = 2
    """
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('B', 'C', weight=-3)
    G.add_edge('A', 'C', weight=5)   # longer path; C should still be 1
    G.add_edge('C', 'D', weight=1)
    return G


@pytest.fixture
def negative_cycle_digraph():
    """Directed graph with a negative cycle: A→B→C→A (total weight = -1)."""
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=-3)
    G.add_edge('C', 'A', weight=1)
    G.add_edge('A', 'D', weight=10)
    return G


# ---------------------------------------------------------------------------
# 1. Correctness on non-negative graphs (Dijkstra as oracle)
# ---------------------------------------------------------------------------

class TestBellmanFordCorrectness:

    def test_matches_dijkstra_undirected(self):
        G = nx.Graph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=1)
        G.add_edge('B', 'D', weight=5)
        G.add_edge('C', 'D', weight=8)

        dijk = dijkstra(G, 'A')
        bf = bellman_ford(G, 'A')

        for node, expected in dijk.items():
            assert bf['distances'][node] == pytest.approx(expected), (
                f"Node {node}: bellman_ford={bf['distances'][node]}, dijkstra={expected}"
            )

    def test_matches_dijkstra_directed(self, simple_digraph):
        dijk = dijkstra(simple_digraph, 'A')
        bf = bellman_ford(simple_digraph, 'A')
        for node in simple_digraph.nodes():
            assert bf['distances'][node] == pytest.approx(dijk[node])

    def test_source_distance_is_zero(self, simple_digraph):
        result = bellman_ford(simple_digraph, 'A')
        assert result['distances']['A'] == 0

    def test_unreachable_node_is_inf(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_node('C')   # isolated
        result = bellman_ford(G, 'A')
        assert result['distances']['C'] == float('inf')

    def test_predecessors_reconstruct_valid_path(self, simple_digraph):
        """Walking the predecessor chain must yield a valid path."""
        result = bellman_ford(simple_digraph, 'A')
        pred = result['predecessors']

        # Walk from 'E' back to 'A'
        path = []
        current = 'E'
        while current is not None:
            path.append(current)
            current = pred[current]
        path.reverse()

        assert path[0] == 'A'
        assert path[-1] == 'E'
        for i in range(len(path) - 1):
            assert simple_digraph.has_edge(path[i], path[i + 1])

    def test_single_node_no_edges(self):
        G = nx.DiGraph()
        G.add_node('X')
        result = bellman_ford(G, 'X')
        assert result['distances']['X'] == 0

    def test_unweighted_default_weight_1(self):
        G = nx.path_graph(4, create_using=nx.DiGraph())
        result = bellman_ford(G, 0)
        assert result['distances'][3] == 3


# ---------------------------------------------------------------------------
# 2. Negative-weight edges (valid — no negative cycle)
# ---------------------------------------------------------------------------

class TestBellmanFordNegativeEdges:

    def test_negative_edge_correct_distance(self, negative_edge_digraph):
        result = bellman_ford(negative_edge_digraph, 'A')
        assert result['distances']['B'] == pytest.approx(4.0)
        assert result['distances']['C'] == pytest.approx(1.0)   # via A→B→C
        assert result['distances']['D'] == pytest.approx(2.0)

    def test_negative_edge_predecessor_correct(self, negative_edge_digraph):
        result = bellman_ford(negative_edge_digraph, 'A')
        # C is reached via B (A→B→C is cheaper than A→C)
        assert result['predecessors']['C'] == 'B'

    def test_all_negative_weights_no_cycle(self):
        """DAG with all negative weights — no cycle, solution exists."""
        G = nx.DiGraph()
        G.add_edge('S', 'A', weight=-1)
        G.add_edge('S', 'B', weight=-2)
        G.add_edge('A', 'T', weight=-3)
        G.add_edge('B', 'T', weight=-1)
        result = bellman_ford(G, 'S')
        # S→A→T = -4, S→B→T = -3  → optimal is S→A→T
        assert result['distances']['T'] == pytest.approx(-4.0)

    def test_negative_edge_undirected_raises(self):
        """
        Undirected graph with a negative edge always produces a negative cycle.

        An undirected edge (u, v, w < 0) is expanded to two directed edges
        u→v and v→u, both with weight w. This creates a 2-cycle u→v→u of
        total weight 2w < 0, which is a valid negative cycle by definition.
        Bellman-Ford must detect and raise NegativeCycleError.
        """
        G = nx.Graph()
        G.add_edge('A', 'B', weight=5)
        G.add_edge('B', 'C', weight=-2)   # creates B→C→B cycle with weight -4
        G.add_edge('A', 'C', weight=10)
        with pytest.raises(NegativeCycleError):
            bellman_ford(G, 'A')

    def test_large_negative_weight(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=100)
        G.add_edge('A', 'C', weight=1)
        G.add_edge('C', 'B', weight=-200)   # makes A→C→B = -199
        result = bellman_ford(G, 'A')
        assert result['distances']['B'] == pytest.approx(-199.0)


# ---------------------------------------------------------------------------
# 3. Negative cycle detection
# ---------------------------------------------------------------------------

class TestBellmanFordNegativeCycles:

    def test_negative_cycle_raises(self, negative_cycle_digraph):
        with pytest.raises(NegativeCycleError):
            bellman_ford(negative_cycle_digraph, 'A')

    def test_negative_cycle_error_carries_cycle(self, negative_cycle_digraph):
        with pytest.raises(NegativeCycleError) as exc_info:
            bellman_ford(negative_cycle_digraph, 'A')
        error = exc_info.value
        assert error.cycle is not None
        assert len(error.cycle) >= 2

    def test_negative_cycle_unreachable_from_source_no_raise(self):
        """A negative cycle NOT reachable from source must not raise."""
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)      # source component
        G.add_edge('X', 'Y', weight=1)      # isolated negative cycle
        G.add_edge('Y', 'X', weight=-3)
        result = bellman_ford(G, 'A')
        assert result['distances']['B'] == pytest.approx(1.0)

    def test_self_loop_negative_raises(self):
        """A self-loop with negative weight is a trivial negative cycle."""
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'B', weight=-1)   # self-loop
        with pytest.raises(NegativeCycleError):
            bellman_ford(G, 'A')

    def test_negative_cycle_of_length_three(self):
        G = nx.DiGraph()
        G.add_edge('P', 'Q', weight=2)
        G.add_edge('Q', 'R', weight=-5)
        G.add_edge('R', 'P', weight=1)   # total: 2 - 5 + 1 = -2 < 0
        with pytest.raises(NegativeCycleError):
            bellman_ford(G, 'P')

    def test_negative_cycle_error_is_value_error_subclass(self, negative_cycle_digraph):
        """NegativeCycleError must be a subclass of ValueError for easy catching."""
        with pytest.raises(ValueError):
            bellman_ford(negative_cycle_digraph, 'A')


# ---------------------------------------------------------------------------
# 4. bellman_ford_path — path reconstruction convenience wrapper
# ---------------------------------------------------------------------------

class TestBellmanFordPath:

    def test_path_found(self, negative_edge_digraph):
        result = bellman_ford_path(negative_edge_digraph, 'A', 'D')
        assert result['distance'] == pytest.approx(2.0)
        assert result['path'][0] == 'A'
        assert result['path'][-1] == 'D'

    def test_path_is_valid_walk(self, simple_digraph):
        result = bellman_ford_path(simple_digraph, 'A', 'E')
        path = result['path']
        for i in range(len(path) - 1):
            assert simple_digraph.has_edge(path[i], path[i + 1])

    def test_path_cost_matches_distance(self, simple_digraph):
        result = bellman_ford_path(simple_digraph, 'A', 'E')
        path = result['path']
        cost = sum(
            simple_digraph[path[i]][path[i + 1]].get('weight', 1)
            for i in range(len(path) - 1)
        )
        assert cost == pytest.approx(result['distance'])

    def test_unreachable_returns_inf_empty_path(self):
        G = nx.DiGraph()
        G.add_edge('A', 'B', weight=1)
        G.add_node('C')
        result = bellman_ford_path(G, 'A', 'C')
        assert result['distance'] == float('inf')
        assert result['path'] == []

    def test_source_equals_target(self, simple_digraph):
        result = bellman_ford_path(simple_digraph, 'A', 'A')
        assert result['distance'] == 0
        assert result['path'] == ['A']

    def test_negative_edge_path(self, negative_edge_digraph):
        result = bellman_ford_path(negative_edge_digraph, 'A', 'C')
        # optimal: A→B→C with distance 1.0
        assert result['distance'] == pytest.approx(1.0)
        assert result['path'] == ['A', 'B', 'C']

    def test_path_raises_on_negative_cycle(self, negative_cycle_digraph):
        with pytest.raises(NegativeCycleError):
            bellman_ford_path(negative_cycle_digraph, 'A', 'D')


# ---------------------------------------------------------------------------
# 5. Error handling
# ---------------------------------------------------------------------------

class TestBellmanFordErrors:

    def test_empty_graph_raises(self):
        with pytest.raises(ValueError, match="empty"):
            bellman_ford(nx.DiGraph(), 'A')

    def test_source_not_in_graph_raises(self):
        G = nx.path_graph(3, create_using=nx.DiGraph())
        with pytest.raises(ValueError, match="Source"):
            bellman_ford(G, 99)

    def test_path_empty_graph_raises(self):
        with pytest.raises(ValueError, match="empty"):
            bellman_ford_path(nx.DiGraph(), 'A', 'B')

    def test_path_source_not_in_graph_raises(self):
        G = nx.path_graph(3, create_using=nx.DiGraph())
        with pytest.raises(ValueError, match="Source"):
            bellman_ford_path(G, 99, 1)

    def test_path_target_not_in_graph_raises(self):
        G = nx.path_graph(3, create_using=nx.DiGraph())
        with pytest.raises(ValueError, match="Target"):
            bellman_ford_path(G, 0, 99)


# ---------------------------------------------------------------------------
# 6. Performance / stress
# ---------------------------------------------------------------------------

class TestBellmanFordStress:

    def test_long_chain_graph(self):
        """Linear chain of 500 nodes — result should equal hop count."""
        n = 500
        G = nx.path_graph(n, create_using=nx.DiGraph())
        for u, v in G.edges():
            G[u][v]['weight'] = 1
        result = bellman_ford(G, 0)
        assert result['distances'][n - 1] == pytest.approx(float(n - 1))

    def test_matches_dijkstra_random_graph(self):
        """Statistical correctness against Dijkstra on a random positive graph."""
        import random
        random.seed(7)
        G = nx.gnm_random_graph(40, 150, seed=7, directed=True)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(0.5, 10.0)

        for source in [0, 10, 20]:
            dijk = dijkstra(G, source)
            bf = bellman_ford(G, source)
            for node in G.nodes():
                assert bf['distances'][node] == pytest.approx(dijk[node], rel=1e-9)
