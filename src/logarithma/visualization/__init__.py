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

from .shortest_path_viz import (
    plot_astar_search,
    plot_bellman_ford_result,
    plot_negative_cycle,
    plot_bidirectional_search,
    plot_shortest_path_comparison,
    plot_breaking_barrier_result,
)

from .traversal_viz import (
    plot_dfs_tree,
)

from .mst_viz import (
    plot_mst,
    plot_mst_comparison,
    plot_kruskal_steps,
)

from .flow_viz import (
    plot_flow_network,
    plot_flow_paths,
)

from .graph_properties_viz import (
    plot_scc,
    plot_topological_order,
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
    # Algorithm-specific shortest path visualization
    'plot_astar_search',
    'plot_bellman_ford_result',
    'plot_negative_cycle',
    'plot_bidirectional_search',
    'plot_shortest_path_comparison',
    'plot_breaking_barrier_result',
    # Traversal-specific visualization
    'plot_dfs_tree',
    # MST visualization
    'plot_mst',
    'plot_mst_comparison',
    'plot_kruskal_steps',
    # Network flow visualization
    'plot_flow_network',
    'plot_flow_paths',
    # Graph properties visualization
    'plot_scc',
    'plot_topological_order',
]
