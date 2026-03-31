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
    
    def test_directed_graph(self):
        """Test Dijkstra on directed graph"""
        DG = nx.DiGraph()
        DG.add_edge('A', 'B', weight=1)
        DG.add_edge('B', 'C', weight=2)
        DG.add_edge('A', 'C', weight=5)
        
        result = dijkstra(DG, 'A')
        
        assert result['A'] == 0
        assert result['B'] == 1
        assert result['C'] == 3
    
    def test_disconnected_graph(self):
        """Test with disconnected components"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('C', 'D', weight=1)
        
        result = dijkstra(G, 'A')
        
        assert result['A'] == 0
        assert result['B'] == 1
        assert result['C'] == float('inf')
        assert result['D'] == float('inf')
    
    def test_single_node(self):
        """Test with single node graph"""
        G = nx.Graph()
        G.add_node('A')
        
        result = dijkstra(G, 'A')
        
        assert result['A'] == 0
    
    def test_no_weights(self):
        """Test with unweighted graph (default weight=1)"""
        G = nx.Graph()
        G.add_edge('A', 'B')
        G.add_edge('B', 'C')
        G.add_edge('A', 'C')
        
        result = dijkstra(G, 'A')
        
        assert result['A'] == 0
        assert result['B'] == 1
        assert result['C'] == 1
    
    def test_integer_nodes(self):
        """Test with integer node labels"""
        G = nx.Graph()
        G.add_edge(1, 2, weight=5)
        G.add_edge(2, 3, weight=3)
        G.add_edge(1, 3, weight=10)
        
        result = dijkstra(G, 1)
        
        assert result[1] == 0
        assert result[2] == 5
        assert result[3] == 8
    
    def test_source_not_in_graph(self):
        """Test error handling for invalid source"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        
        with pytest.raises(ValueError, match="Source vertex 'Z' not found"):
            dijkstra(G, 'Z')
    
    def test_empty_graph(self):
        """Test error handling for empty graph"""
        G = nx.Graph()
        
        with pytest.raises(ValueError, match="graph is empty"):
            dijkstra(G, 'A')
    
    def test_negative_weight(self):
        """Test error handling for negative weights"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=-1)
        
        with pytest.raises(ValueError, match="Negative edge weight"):
            dijkstra(G, 'A')


class TestDijkstraWithPath:
    """Test cases for Dijkstra with path reconstruction"""
    
    def test_path_to_target(self):
        """Test path reconstruction to specific target"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        G.add_edge('B', 'C', weight=1)
        G.add_edge('A', 'D', weight=5)
        G.add_edge('D', 'C', weight=1)
        
        result = dijkstra_with_path(G, 'A', 'C')
        
        assert result['distances']['C'] == 2
        assert result['paths']['C'] == ['A', 'B', 'C']
    
    def test_unreachable_node(self):
        """Test path to unreachable node"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        G.add_node('C')
        
        result = dijkstra_with_path(G, 'A')
        
        assert result['distances']['C'] == float('inf')
        assert result['paths']['C'] == []
    
    def test_target_not_in_graph(self):
        """Test error handling for invalid target"""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1)
        
        with pytest.raises(ValueError, match="Target vertex 'Z' not found"):
            dijkstra_with_path(G, 'A', 'Z')
    
    def test_directed_graph_path(self):
        """Test path reconstruction in directed graph"""
        DG = nx.DiGraph()
        DG.add_edge('A', 'B', weight=1)
        DG.add_edge('B', 'C', weight=1)
        # No edge from C back to A
        
        result = dijkstra_with_path(DG, 'A', 'C')
        
        assert result['paths']['C'] == ['A', 'B', 'C']
        
    def test_self_loop(self):
        """Test handling of self-loops"""
        G = nx.Graph()
        G.add_edge('A', 'A', weight=1)  # Self-loop
        G.add_edge('A', 'B', weight=2)
        
        result = dijkstra_with_path(G, 'A')
        
        # Should find shortest path without using self-loop
        assert result['distances']['A'] == 0
        assert result['distances']['B'] == 2