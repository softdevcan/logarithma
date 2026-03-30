
"""
Integration tests for the visualization module.
Tests all plotting functions to ensure they execute without error.
Uses 'Agg' backend to avoid GUI requirements.
"""

import pytest
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from logarithma.visualization import (
    plot_graph,
    plot_shortest_path,
    plot_traversal,
    plot_distance_heatmap,
    plot_algorithm_comparison,
    plot_complexity_analysis,
    plot_path_comparison,
    plot_degree_distribution,
    plot_graph_metrics,
    plot_graph_interactive
)

# Use non-interactive backend for testing
matplotlib.use('Agg')

@pytest.fixture
def sample_graph():
    """Create a sample graph for testing"""
    return nx.karate_club_graph()

@pytest.fixture
def sample_digraph():
    """Create a sample directed graph"""
    return nx.gnp_random_graph(20, 0.2, directed=True)

def test_plot_graph(sample_graph):
    """Test basic graph plotting"""
    try:
        plot_graph(sample_graph, title="Test Graph")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_graph failed: {e}")

def test_plot_graph_custom_layout(sample_graph):
    """Test graph plotting with custom layout"""
    try:
        plot_graph(sample_graph, layout="circular", node_color="red")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_graph with custom layout failed: {e}")

def test_plot_shortest_path(sample_graph):
    """Test shortest path visualization"""
    path = [0, 1, 2, 8, 33]  # Dummy path
    try:
        plot_shortest_path(sample_graph, path, title="Test Path")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_shortest_path failed: {e}")

def test_plot_traversal(sample_graph):
    """Test traversal visualization"""
    visited = list(range(10))  # Dummy visited order
    try:
        plot_traversal(sample_graph, visited, title="Test Traversal")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_traversal failed: {e}")

def test_plot_distance_heatmap():
    """Test distance heatmap"""
    distances = {i: float(i) for i in range(20)}
    try:
        plot_distance_heatmap(distances, title="Test Heatmap")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_distance_heatmap failed: {e}")

def test_plot_algorithm_comparison():
    """Test algorithm comparison plot"""
    results = {
        'Algo A': {10: 0.1, 20: 0.2, 50: 0.5},
        'Algo B': {10: 0.2, 20: 0.4, 50: 1.0}
    }
    try:
        plot_algorithm_comparison(results, title="Test Comparison")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_algorithm_comparison failed: {e}")

def test_plot_complexity_analysis():
    """Test complexity analysis plot"""
    sizes = [10, 20, 30, 40]
    times = [0.1, 0.2, 0.3, 0.4]
    try:
        plot_complexity_analysis(sizes, times, title="Test Complexity")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_complexity_analysis failed: {e}")

def test_plot_path_comparison(sample_graph):
    """Test path comparison plot"""
    paths = {
        'Algo A': [0, 1, 2, 33],
        'Algo B': [0, 8, 33]
    }
    distances = {'Algo A': 3, 'Algo B': 2}
    try:
        plot_path_comparison(sample_graph, paths, distances)
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_path_comparison failed: {e}")

def test_plot_degree_distribution(sample_graph):
    """Test degree distribution plot"""
    try:
        plot_degree_distribution(sample_graph, title="Test Degree Dist")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_degree_distribution failed: {e}")

def test_plot_graph_metrics():
    """Test graph metrics dashboard"""
    metrics = {
        'param1': 0.5,
        'param2': 100,
        'param3': 12.5,
        'is_connected': True  # Should be ignored
    }
    try:
        plot_graph_metrics(metrics, title="Test Metrics")
        plt.close()
    except Exception as e:
        pytest.fail(f"plot_graph_metrics failed: {e}")

def test_plot_graph_interactive(sample_graph):
    """Test interactive graph plotting (Plotly)"""
    try:
        fig = plot_graph_interactive(sample_graph, title="Test Interactive")
        assert fig is not None
        # Verify it returns a go.Figure (checking type name indirectly to avoid strict dependency if import failed inside module)
        assert "Figure" in str(type(fig))
    except ImportError:
        pytest.skip("Plotly not installed")
    except Exception as e:
        pytest.fail(f"plot_graph_interactive failed: {e}")
