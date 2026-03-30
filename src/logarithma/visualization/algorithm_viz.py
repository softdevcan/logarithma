"""
Algorithm Visualization Module
==============================

Visualize algorithm performance, comparisons, and analysis.
"""

from typing import Dict, List, Optional, Tuple, Any
import time

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def plot_algorithm_comparison(
    results: Dict[str, Dict[str, float]],
    metric: str = "time",
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None,
) -> None:
    """
    Compare multiple algorithms across different graph sizes.
    
    Args:
        results: Nested dict {algorithm_name: {graph_size: metric_value}}
        metric: Metric to plot (e.g., 'time', 'memory', 'operations')
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> results = {
        ...     'Dijkstra': {100: 0.01, 500: 0.05, 1000: 0.15},
        ...     'BFS': {100: 0.005, 500: 0.02, 1000: 0.08}
        ... }
        >>> plot_algorithm_comparison(results, metric='time (s)')
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    plt.figure(figsize=figsize)
    
    for algo_name, data in results.items():
        sizes = sorted(data.keys())
        values = [data[s] for s in sizes]
        plt.plot(sizes, values, marker='o', label=algo_name, linewidth=2)
    
    plt.xlabel('Graph Size (nodes)', fontsize=12)
    plt.ylabel(metric.capitalize(), fontsize=12)
    plt.title(title or f'Algorithm Comparison - {metric}', fontsize=16, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_complexity_analysis(
    sizes: List[int],
    times: List[float],
    complexity_label: str = "O(n log n)",
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> None:
    """
    Plot algorithm runtime vs theoretical complexity.
    
    Args:
        sizes: List of input sizes
        times: List of execution times
        complexity_label: Theoretical complexity (for label)
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> from logarithma.utils import generate_random_graph
        >>> from logarithma import dijkstra
        >>> import time
        >>> sizes, times = [], []
        >>> for n in [100, 200, 500, 1000]:
        ...     G = generate_random_graph(n, 0.1, weighted=True)
        ...     start = time.time()
        ...     dijkstra(G, 0)
        ...     times.append(time.time() - start)
        ...     sizes.append(n)
        >>> plot_complexity_analysis(sizes, times, "O(E + V log V)")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    plt.figure(figsize=figsize)
    
    plt.plot(sizes, times, 'o-', linewidth=2, markersize=8, label='Actual Runtime')
    
    plt.xlabel('Input Size', fontsize=12)
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.title(title or f'Runtime Analysis ({complexity_label})', 
             fontsize=16, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_path_comparison(
    G,
    paths: Dict[str, List],
    distances: Dict[str, float],
    layout: str = "spring",
    figsize: Tuple[int, int] = (15, 5),
    save_path: Optional[str] = None,
) -> None:
    """
    Compare multiple paths side by side.
    
    Args:
        G: NetworkX graph
        paths: Dictionary mapping algorithm names to paths
        distances: Dictionary mapping algorithm names to path distances
        layout: Layout algorithm
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> # Compare Dijkstra and BFS paths
        >>> from logarithma import dijkstra_with_path, bfs_path
        >>> dist1, path1 = dijkstra_with_path(G, 0, 10)
        >>> path2 = bfs_path(G, 0, 10)
        >>> paths = {'Dijkstra': path1, 'BFS': path2}
        >>> distances = {'Dijkstra': dist1, 'BFS': len(path2)-1}
        >>> plot_path_comparison(G, paths, distances)
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    import networkx as nx
    
    n_paths = len(paths)
    fig, axes = plt.subplots(1, n_paths, figsize=figsize)
    
    if n_paths == 1:
        axes = [axes]
    
    layouts = {
        'spring': nx.spring_layout,
        'circular': nx.circular_layout,
        'kamada_kawai': nx.kamada_kawai_layout,
    }
    pos = layouts.get(layout, nx.spring_layout)(G)
    
    for idx, (algo_name, path) in enumerate(paths.items()):
        ax = axes[idx]
        
        # Draw graph
        nx.draw_networkx_nodes(G, pos, node_size=300, node_color='lightblue', ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1.0, ax=ax)
        nx.draw_networkx_labels(G, pos, ax=ax)
        
        # Highlight path
        if path:
            nx.draw_networkx_nodes(G, pos, nodelist=path, node_size=300, 
                                  node_color='red', alpha=0.8, ax=ax)
            path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                                  edge_color='red', width=3.0, ax=ax)
        
        dist = distances.get(algo_name, 'N/A')
        ax.set_title(f'{algo_name}\nDistance: {dist}', fontsize=12, fontweight='bold')
        ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_degree_distribution(
    G,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> None:
    """
    Plot the degree distribution of a graph.
    
    Args:
        G: NetworkX graph
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> import networkx as nx
        >>> from logarithma.visualization import plot_degree_distribution
        >>> G = nx.barabasi_albert_graph(100, 3)
        >>> plot_degree_distribution(G, title="Degree Distribution")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    import networkx as nx
    
    degrees = [d for n, d in G.degree()]
    
    plt.figure(figsize=figsize)
    plt.hist(degrees, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    plt.xlabel('Degree', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(title or 'Degree Distribution', fontsize=16, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_graph_metrics(
    metrics: Dict[str, Any],
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize multiple graph metrics in a dashboard.
    
    Args:
        metrics: Dictionary of metric names and values
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> from logarithma.utils import graph_summary
        >>> metrics = graph_summary(G)
        >>> plot_graph_metrics(metrics, title="Graph Analysis Dashboard")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    # Filter numeric metrics
    numeric_metrics = {k: v for k, v in metrics.items() 
                      if isinstance(v, (int, float)) and not isinstance(v, bool)}
    
    if not numeric_metrics:
        print("No numeric metrics to plot")
        return
    
    fig, ax = plt.subplots(figsize=figsize)
    
    metric_names = list(numeric_metrics.keys())
    metric_values = list(numeric_metrics.values())
    
    # Create horizontal bar chart
    y_pos = range(len(metric_names))
    ax.barh(y_pos, metric_values, color='steelblue', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(metric_names)
    ax.set_xlabel('Value', fontsize=12)
    ax.set_title(title or 'Graph Metrics', fontsize=16, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(metric_values):
        ax.text(v, i, f' {v:.4f}' if isinstance(v, float) else f' {v}',
               va='center', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
