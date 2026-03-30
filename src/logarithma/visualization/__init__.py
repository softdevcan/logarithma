"""
Visualization Module
===================

Graph and algorithm visualization tools using Matplotlib and Plotly.

This module provides functions for:
- Static graph plotting with Matplotlib
- Interactive graph visualization with Plotly
- Shortest path highlighting
- Traversal order visualization
- Algorithm performance comparison
- Graph metrics dashboards

Basic Usage:
    >>> from logarithma.visualization import plot_graph, plot_shortest_path
    >>> import networkx as nx
    >>> 
    >>> G = nx.karate_club_graph()
    >>> plot_graph(G, title="Karate Club Network")
    >>> 
    >>> # Visualize shortest path
    >>> from logarithma import dijkstra_with_path
    >>> distance, path = dijkstra_with_path(G, 0, 33)
    >>> plot_shortest_path(G, path, title=f"Shortest Path (d={distance})")

Requirements:
    - matplotlib: For static visualizations (pip install matplotlib)
    - plotly: For interactive visualizations (pip install plotly)
"""

from .graph_plotter import (
    plot_graph,
    plot_shortest_path,
    plot_traversal,
    plot_graph_interactive,
    plot_distance_heatmap,
)

from .algorithm_viz import (
    plot_algorithm_comparison,
    plot_complexity_analysis,
    plot_path_comparison,
    plot_degree_distribution,
    plot_graph_metrics,
)

__all__ = [
    # Graph plotting
    'plot_graph',
    'plot_shortest_path',
    'plot_traversal',
    'plot_graph_interactive',
    'plot_distance_heatmap',
    # Algorithm visualization
    'plot_algorithm_comparison',
    'plot_complexity_analysis',
    'plot_path_comparison',
    'plot_degree_distribution',
    'plot_graph_metrics',
]
