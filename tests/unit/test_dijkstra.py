"""
Unit tests for Dijkstra algorithm
"""

import pytest
import networkx as nx
from logarithma.algorithms.shortest_path import dijkstra, dijkstra_with_path


class TestDijkstra:
    """Test cases for Dijkstra algorithm"""

    def test_basic_dijkstra(self):
        """Test basic Dijkstra functionality"""
        # Create simple graph
        G = nx.Graph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=1)

        # Run Dijkstra
        result = dijkstra(G, 'A')

        # Verify results
        assert result['A'] == 0
        assert result['C'] == 2
        assert result['B'] == 3

    def test_dijkstra_with_path(self):
        """Test Dijkstra with path reconstruction"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=4)
        G.add_edge('A', 'C', weight=2)
        G.add_edge('B', 'C', weight=1)

        result = dijkstra_with_path(G, 'A')

        # Check distances
        assert result['distances']['A'] == 0
        assert result['distances']['C'] == 2
        assert result['distances']['B'] == 3

        # Check paths
        assert result['paths']['A'] == ['A']
        assert result['paths']['C'] == ['A', 'C']
        assert result['paths']['B'] == ['A', 'C', 'B']