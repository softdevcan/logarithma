#!/usr/bin/env python
"""Quick test for visualization module"""

try:
    from logarithma.visualization import (
        plot_graph,
        plot_shortest_path,
        plot_traversal,
        plot_graph_interactive,
        plot_distance_heatmap,
        plot_algorithm_comparison,
        plot_complexity_analysis,
        plot_path_comparison,
        plot_degree_distribution,
        plot_graph_metrics,
    )
    print("✓ All visualization functions imported successfully!")
    print("  - plot_graph")
    print("  - plot_shortest_path")
    print("  - plot_traversal")
    print("  - plot_graph_interactive")
    print("  - plot_distance_heatmap")
    print("  - plot_algorithm_comparison")
    print("  - plot_complexity_analysis")
    print("  - plot_path_comparison")
    print("  - plot_degree_distribution")
    print("  - plot_graph_metrics")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    import sys
    sys.exit(1)
