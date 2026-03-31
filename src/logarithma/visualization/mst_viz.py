"""
MST Visualizations
==================

Visualization functions for Minimum Spanning Tree algorithms (Kruskal, Prim).

Color palette (consistent with the rest of the library):
    MST EDGE      #2ecc71  green  (selected MST edges)
    NON-MST EDGE  #bdc3c7  grey   (other edges)
    SOURCE        #2ecc71  green  (start node for Prim)
    NODE          #3498db  blue   (default nodes)
    STEP ADDED    #e74c3c  red    (newly added edge in step view)

Requirements:
    matplotlib >= 3.5
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .graph_plotter import _get_layout

# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------
_C_MST = "#2ecc71"
_C_NON_MST = "#bdc3c7"
_C_NODE = "#3498db"
_C_STEP_ADDED = "#e74c3c"
_C_TEXT = "#2c3e50"


def _check_matplotlib(fn_name: str) -> None:
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            f"matplotlib is required for {fn_name}(). "
            "Install it with: pip install matplotlib"
        )


# ---------------------------------------------------------------------------
# plot_mst
# ---------------------------------------------------------------------------

def plot_mst(
    graph: nx.Graph,
    mst_result: Optional[Dict[str, Any]] = None,
    algorithm: str = 'kruskal',
    layout: str = 'spring',
    show_weights: bool = True,
    title: Optional[str] = None,
    ax: Optional[Any] = None,
) -> Any:
    """Visualise an MST overlaid on the original graph.

    MST edges are drawn in green and thick; non-MST edges in grey and thin.

    Args:
        graph:       Undirected weighted NetworkX graph.
        mst_result:  Output of kruskal_mst() or prim_mst().  If None the
                     function runs kruskal_mst() internally.
        algorithm:   Label used in the title ('kruskal' or 'prim').
        layout:      NetworkX layout name ('spring', 'circular', …).
        show_weights: Draw edge weight labels.
        title:       Override the auto-generated title.
        ax:          Existing Matplotlib Axes to draw on.  A new figure is
                     created when None.

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_mst')
    from logarithma.algorithms.mst import kruskal_mst

    if mst_result is None:
        mst_result = kruskal_mst(graph)

    mst_edge_set = {
        (min(u, v), max(u, v)) for u, v, _ in mst_result['mst_edges']
    }

    pos = _get_layout(graph, layout)
    created_fig = ax is None
    if created_fig:
        fig, ax = plt.subplots(figsize=(10, 7))
    else:
        fig = ax.get_figure()

    # Split edges
    mst_edges = [
        (u, v) for u, v in graph.edges()
        if (min(u, v), max(u, v)) in mst_edge_set
    ]
    other_edges = [
        (u, v) for u, v in graph.edges()
        if (min(u, v), max(u, v)) not in mst_edge_set
    ]

    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=_C_NODE, node_size=600)
    nx.draw_networkx_labels(graph, pos, ax=ax, font_color='white', font_weight='bold')
    nx.draw_networkx_edges(graph, pos, edgelist=other_edges, ax=ax,
                           edge_color=_C_NON_MST, width=1.5, alpha=0.6)
    nx.draw_networkx_edges(graph, pos, edgelist=mst_edges, ax=ax,
                           edge_color=_C_MST, width=3.5)

    if show_weights:
        edge_labels = {(u, v): graph[u][v].get('weight', 1) for u, v in graph.edges()}
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                     ax=ax, font_size=8, label_pos=0.35)

    alg_label = algorithm.capitalize()
    default_title = (
        f"{alg_label} MST  |  "
        f"Total weight: {mst_result['total_weight']:.2g}  |  "
        f"Components: {mst_result['num_components']}"
    )
    ax.set_title(title or default_title, fontsize=13, fontweight='bold', pad=12)

    legend = [
        Line2D([0], [0], color=_C_MST, lw=3, label='MST edge'),
        Line2D([0], [0], color=_C_NON_MST, lw=1.5, alpha=0.6, label='Non-MST edge'),
    ]
    ax.legend(handles=legend, loc='upper left', fontsize=9)
    ax.axis('off')

    if created_fig:
        plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# plot_mst_comparison
# ---------------------------------------------------------------------------

def plot_mst_comparison(
    graph: nx.Graph,
    layout: str = 'spring',
    show_weights: bool = True,
) -> Any:
    """Compare Kruskal and Prim MSTs side-by-side.

    Args:
        graph:       Undirected weighted NetworkX graph.
        layout:      NetworkX layout name.
        show_weights: Draw edge weight labels.

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_mst_comparison')
    from logarithma.algorithms.mst import kruskal_mst, prim_mst

    kruskal_result = kruskal_mst(graph)
    prim_result = prim_mst(graph)

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle("MST Comparison: Kruskal vs Prim", fontsize=15, fontweight='bold')

    for ax, result, alg in zip(axes, [kruskal_result, prim_result], ['kruskal', 'prim']):
        plot_mst(graph, mst_result=result, algorithm=alg,
                 layout=layout, show_weights=show_weights, ax=ax)

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# plot_kruskal_steps
# ---------------------------------------------------------------------------

def plot_kruskal_steps(
    graph: nx.Graph,
    max_steps: int = 6,
    layout: str = 'spring',
) -> Any:
    """Animate Kruskal's algorithm step-by-step (static multi-subplot).

    Each subplot shows the MST built so far with the most recently added
    edge highlighted in red.

    Args:
        graph:     Undirected weighted NetworkX graph.
        max_steps: Maximum number of steps to show (grid: 2 rows × 3 cols).
        layout:    NetworkX layout name.

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_kruskal_steps')
    from logarithma.algorithms.mst.kruskal import _UnionFind

    pos = _get_layout(graph, layout)

    # Compute step-by-step Kruskal edges
    uf = _UnionFind(graph.nodes())
    sorted_edges = sorted(
        (data.get('weight', 1), u, v)
        for u, v, data in graph.edges(data=True)
    )

    steps: List[Tuple[List, Tuple, float]] = []  # (mst_so_far, last_edge, weight)
    mst_so_far: List[Tuple] = []
    for w, u, v in sorted_edges:
        if uf.union(u, v):
            mst_so_far = mst_so_far + [(u, v)]
            steps.append((list(mst_so_far), (u, v), w))
            if len(steps) >= max_steps:
                break

    cols = 3
    rows = (len(steps) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
    axes_flat = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    fig.suptitle("Kruskal's Algorithm — Step-by-Step", fontsize=14, fontweight='bold')

    for i, (mst_edges_so_far, last_edge, last_w) in enumerate(steps):
        ax = axes_flat[i]
        mst_set = {(min(u, v), max(u, v)) for u, v in mst_edges_so_far}
        last_norm = (min(last_edge[0], last_edge[1]), max(last_edge[0], last_edge[1]))

        other = [(u, v) for u, v in graph.edges()
                 if (min(u, v), max(u, v)) not in mst_set]
        prev_mst = [(u, v) for u, v in mst_edges_so_far
                    if (min(u, v), max(u, v)) != last_norm]
        new_edge = [(u, v) for u, v in mst_edges_so_far
                    if (min(u, v), max(u, v)) == last_norm]

        nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=_C_NODE, node_size=500)
        nx.draw_networkx_labels(graph, pos, ax=ax, font_color='white', font_weight='bold', font_size=8)
        nx.draw_networkx_edges(graph, pos, edgelist=other, ax=ax,
                               edge_color=_C_NON_MST, width=1, alpha=0.5)
        nx.draw_networkx_edges(graph, pos, edgelist=prev_mst, ax=ax,
                               edge_color=_C_MST, width=2.5)
        nx.draw_networkx_edges(graph, pos, edgelist=new_edge, ax=ax,
                               edge_color=_C_STEP_ADDED, width=4)

        edge_labels = {(u, v): graph[u][v].get('weight', 1) for u, v in graph.edges()}
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                     ax=ax, font_size=7, label_pos=0.35)

        last_u, last_v = last_edge
        ax.set_title(
            f"Step {i + 1}: Add ({last_u}–{last_v}, w={last_w:.2g})",
            fontsize=10, fontweight='bold'
        )
        ax.axis('off')

    # Hide unused axes
    for j in range(len(steps), len(axes_flat)):
        axes_flat[j].set_visible(False)

    plt.tight_layout()
    return fig
