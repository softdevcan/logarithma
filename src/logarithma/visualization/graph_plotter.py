"""
Graph Plotting Module
=====================

Static and interactive graph visualization using Matplotlib and Plotly.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import networkx as nx

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def plot_graph(
    G: Union[nx.Graph, nx.DiGraph],
    layout: str = "spring",
    node_size: int = 500,
    node_color: str = "lightblue",
    edge_color: str = "gray",
    with_labels: bool = True,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
    **kwargs
) -> None:
    """
    Plot a graph using Matplotlib.
    
    Args:
        G: NetworkX graph
        layout: Layout algorithm ('spring', 'circular', 'kamada_kawai', 'random', 'shell')
        node_size: Size of nodes
        node_color: Color of nodes
        edge_color: Color of edges
        with_labels: Whether to show node labels
        title: Plot title
        figsize: Figure size (width, height)
        save_path: Path to save the figure (optional)
        **kwargs: Additional arguments for nx.draw()
        
    Raises:
        ImportError: If matplotlib is not installed
        
    Example:
        >>> import networkx as nx
        >>> from logarithma.visualization import plot_graph
        >>> G = nx.karate_club_graph()
        >>> plot_graph(G, title="Karate Club Network")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required for plotting. Install with: pip install matplotlib")
    
    # Get layout
    layouts = {
        'spring': nx.spring_layout,
        'circular': nx.circular_layout,
        'kamada_kawai': nx.kamada_kawai_layout,
        'random': nx.random_layout,
        'shell': nx.shell_layout,
    }
    
    if layout not in layouts:
        raise ValueError(f"Unknown layout: {layout}. Choose from {list(layouts.keys())}")
    
    pos = layouts[layout](G)
    
    # Create figure
    plt.figure(figsize=figsize)
    
    # Draw graph
    nx.draw(
        G, pos,
        node_size=node_size,
        node_color=node_color,
        edge_color=edge_color,
        with_labels=with_labels,
        **kwargs
    )
    
    # Draw edge weights if available
    edge_labels = nx.get_edge_attributes(G, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    if title:
        plt.title(title, fontsize=16, fontweight='bold')
    
    plt.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_shortest_path(
    G: Union[nx.Graph, nx.DiGraph],
    path: List,
    layout: str = "spring",
    node_size: int = 500,
    path_color: str = "red",
    path_width: float = 3.0,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize a path in a graph with highlighting.
    
    Args:
        G: NetworkX graph
        path: List of nodes representing the path
        layout: Layout algorithm
        node_size: Size of nodes
        path_color: Color for path nodes and edges
        path_width: Width of path edges
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> import networkx as nx
        >>> from logarithma import dijkstra_with_path
        >>> from logarithma.visualization import plot_shortest_path
        >>> G = nx.karate_club_graph()
        >>> distance, path = dijkstra_with_path(G, 0, 33)
        >>> plot_shortest_path(G, path, title=f"Shortest Path (distance={distance})")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    # Get layout
    layouts = {
        'spring': nx.spring_layout,
        'circular': nx.circular_layout,
        'kamada_kawai': nx.kamada_kawai_layout,
        'random': nx.random_layout,
        'shell': nx.shell_layout,
    }
    pos = layouts.get(layout, nx.spring_layout)(G)
    
    plt.figure(figsize=figsize)
    
    # Draw all nodes and edges in default colors
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1.0)
    nx.draw_networkx_labels(G, pos)
    
    # Highlight path nodes
    if path:
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_size=node_size, 
                              node_color=path_color, alpha=0.8)
        
        # Highlight path edges
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                              edge_color=path_color, width=path_width)
    
    # Draw edge weights
    edge_labels = nx.get_edge_attributes(G, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    if title:
        plt.title(title, fontsize=16, fontweight='bold')
    
    # Add legend
    path_patch = mpatches.Patch(color=path_color, label='Shortest Path')
    default_patch = mpatches.Patch(color='lightblue', label='Other Nodes')
    plt.legend(handles=[path_patch, default_patch], loc='upper right')
    
    plt.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_traversal(
    G: Union[nx.Graph, nx.DiGraph],
    visited_order: List,
    layout: str = "spring",
    node_size: int = 500,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize graph traversal order (BFS/DFS).
    
    Args:
        G: NetworkX graph
        visited_order: List of nodes in visit order
        layout: Layout algorithm
        node_size: Size of nodes
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> import networkx as nx
        >>> from logarithma import bfs
        >>> from logarithma.visualization import plot_traversal
        >>> G = nx.karate_club_graph()
        >>> visited = bfs(G, 0)
        >>> plot_traversal(G, visited, title="BFS Traversal Order")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    layouts = {
        'spring': nx.spring_layout,
        'circular': nx.circular_layout,
        'kamada_kawai': nx.kamada_kawai_layout,
        'random': nx.random_layout,
        'shell': nx.shell_layout,
    }
    pos = layouts.get(layout, nx.spring_layout)(G)
    
    plt.figure(figsize=figsize)
    
    # Create color map based on visit order
    node_colors = []
    for node in G.nodes():
        if node in visited_order:
            # Color based on visit order (earlier = darker)
            idx = visited_order.index(node)
            intensity = 1 - (idx / len(visited_order))
            node_colors.append((1-intensity, 0.5, intensity))  # Blue gradient
        else:
            node_colors.append('lightgray')
    
    # Draw graph
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=node_colors)
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1.0)
    nx.draw_networkx_labels(G, pos)
    
    # Add visit order as labels
    visit_labels = {node: str(visited_order.index(node) + 1) 
                   for node in visited_order}
    label_pos = {k: (v[0], v[1] + 0.08) for k, v in pos.items() if k in visit_labels}
    nx.draw_networkx_labels(G, label_pos, visit_labels, 
                           font_size=8, font_color='red', font_weight='bold')
    
    if title:
        plt.title(title, fontsize=16, fontweight='bold')
    
    plt.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_graph_interactive(
    G: Union[nx.Graph, nx.DiGraph],
    layout: str = "spring",
    title: Optional[str] = None,
    node_size: int = 20,
    save_path: Optional[str] = None,
) -> go.Figure:
    """
    Create an interactive graph visualization using Plotly.
    
    Args:
        G: NetworkX graph
        layout: Layout algorithm
        title: Plot title
        node_size: Size of nodes
        save_path: Path to save HTML file
        
    Returns:
        Plotly Figure object
        
    Raises:
        ImportError: If plotly is not installed
        
    Example:
        >>> import networkx as nx
        >>> from logarithma.visualization import plot_graph_interactive
        >>> G = nx.karate_club_graph()
        >>> fig = plot_graph_interactive(G, title="Interactive Karate Club")
        >>> fig.show()
    """
    if not PLOTLY_AVAILABLE:
        raise ImportError("plotly is required. Install with: pip install plotly")
    
    # Get layout
    layouts = {
        'spring': nx.spring_layout,
        'circular': nx.circular_layout,
        'kamada_kawai': nx.kamada_kawai_layout,
        'random': nx.random_layout,
        'shell': nx.shell_layout,
    }
    pos = layouts.get(layout, nx.spring_layout)(G)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Node: {node}<br>Degree: {G.degree(node)}")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[str(node) for node in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=node_size,
            color=[G.degree(node) for node in G.nodes()],
            colorbar=dict(
                thickness=15,
                title='Node Degree',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=title or 'Interactive Graph',
                       titlefont_size=16,
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0, l=0, r=0, t=40),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       plot_bgcolor='white'
                   ))
    
    if save_path:
        fig.write_html(save_path)
    
    return fig


def plot_distance_heatmap(
    distances: Dict[Any, float],
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> None:
    """
    Plot a heatmap of distances from a source node.
    
    Args:
        distances: Dictionary mapping nodes to distances
        title: Plot title
        figsize: Figure size
        save_path: Path to save the figure
        
    Example:
        >>> from logarithma import dijkstra
        >>> from logarithma.visualization import plot_distance_heatmap
        >>> distances = dijkstra(G, source=0)
        >>> plot_distance_heatmap(distances, title="Distances from Node 0")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")
    
    nodes = sorted(distances.keys())
    dists = [distances[n] for n in nodes]
    
    plt.figure(figsize=figsize)
    plt.bar(range(len(nodes)), dists, color='steelblue', alpha=0.7)
    plt.xlabel('Node', fontsize=12)
    plt.ylabel('Distance', fontsize=12)
    plt.xticks(range(len(nodes)), nodes, rotation=45 if len(nodes) > 20 else 0)
    
    if title:
        plt.title(title, fontsize=16, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
