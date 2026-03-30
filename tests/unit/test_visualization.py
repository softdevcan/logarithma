"""
Unit tests for visualization module
"""

import pytest
import networkx as nx
from logarithma.utils import generate_random_graph


class TestGraphPlotter:
    """Test graph plotting functions"""
    
    def test_plot_graph_import(self):
        """Test that plot_graph can be imported"""
        try:
            from logarithma.visualization import plot_graph
            assert plot_graph is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_shortest_path_import(self):
        """Test that plot_shortest_path can be imported"""
        try:
            from logarithma.visualization import plot_shortest_path
            assert plot_shortest_path is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_traversal_import(self):
        """Test that plot_traversal can be imported"""
        try:
            from logarithma.visualization import plot_traversal
            assert plot_traversal is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_graph_interactive_import(self):
        """Test that plot_graph_interactive can be imported"""
        try:
            from logarithma.visualization import plot_graph_interactive
            assert plot_graph_interactive is not None
        except ImportError:
            pytest.skip("plotly not installed")
    
    def test_invalid_layout(self):
        """Test that invalid layout raises ValueError"""
        try:
            from logarithma.visualization import plot_graph
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            G = nx.karate_club_graph()
            with pytest.raises(ValueError, match="Unknown layout"):
                plot_graph(G, layout="invalid_layout")
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestAlgorithmViz:
    """Test algorithm visualization functions"""
    
    def test_plot_algorithm_comparison_import(self):
        """Test that plot_algorithm_comparison can be imported"""
        try:
            from logarithma.visualization import plot_algorithm_comparison
            assert plot_algorithm_comparison is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_complexity_analysis_import(self):
        """Test that plot_complexity_analysis can be imported"""
        try:
            from logarithma.visualization import plot_complexity_analysis
            assert plot_complexity_analysis is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_path_comparison_import(self):
        """Test that plot_path_comparison can be imported"""
        try:
            from logarithma.visualization import plot_path_comparison
            assert plot_path_comparison is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_degree_distribution_import(self):
        """Test that plot_degree_distribution can be imported"""
        try:
            from logarithma.visualization import plot_degree_distribution
            assert plot_degree_distribution is not None
        except ImportError:
            pytest.skip("matplotlib not installed")
    
    def test_plot_graph_metrics_import(self):
        """Test that plot_graph_metrics can be imported"""
        try:
            from logarithma.visualization import plot_graph_metrics
            assert plot_graph_metrics is not None
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestVisualizationModule:
    """Test visualization module structure"""
    
    def test_module_import(self):
        """Test that visualization module can be imported"""
        import logarithma.visualization
        assert logarithma.visualization is not None
    
    def test_all_exports(self):
        """Test that expected functions can be imported"""
        import logarithma.visualization as viz
        
        expected_functions = [
            'plot_graph',
            'plot_shortest_path',
            'plot_traversal',
            'plot_graph_interactive',
            'plot_distance_heatmap',
            'plot_algorithm_comparison',
            'plot_complexity_analysis',
            'plot_path_comparison',
            'plot_degree_distribution',
            'plot_graph_metrics',
        ]
        
        for func in expected_functions:
            assert hasattr(viz, func), f"{func} not available in visualization module"
