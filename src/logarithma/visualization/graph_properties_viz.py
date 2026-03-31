"""
Graph Properties Visualizations
================================

Visualization functions for structural graph properties:
  - Strongly Connected Components (Tarjan SCC)
  - Topological ordering

Color semantics:
    SCC colours     — matplotlib color cycle (each SCC a distinct colour)
    INTER-SCC edges — dashed grey
    INTRA-SCC edges — solid, same as SCC colour
    TOPO ORDER      — gradient blue (darker = earlier in order)

Requirements:
    matplotlib >= 3.5
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import networkx as nx

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    from matplotlib.colors import to_hex
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .graph_plotter import _get_layout

_SCC_PALETTE = [
    "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#e91e63", "#00bcd4",
]


def _check_matplotlib(fn_name: str) -> None:
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            f"matplotlib is required for {fn_name}(). "
            "Install it with: pip install matplotlib"
        )


# ---------------------------------------------------------------------------
# plot_scc
# ---------------------------------------------------------------------------

def plot_scc(
    graph: Union[nx.DiGraph, nx.Graph],
    scc_result: Optional[List[List[Any]]] = None,
    layout: str = 'spring',
    show_condensation: bool = False,
    title: Optional[str] = None,
    ax: Optional[Any] = None,
) -> Any:
    """Visualise Strongly Connected Components.

    Each SCC is drawn with a distinct node colour.  Intra-SCC edges are solid;
    inter-SCC edges are dashed grey.  Optionally shows the condensation DAG as
    a second subplot.

    Args:
        graph:            Directed (or undirected) NetworkX graph.
        scc_result:       Output of tarjan_scc().  Computed internally if None.
        layout:           NetworkX layout name.
        show_condensation: If True, append a condensation DAG subplot.
        title:            Override auto title.
        ax:               Existing Axes (ignored if show_condensation=True).

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_scc')
    from logarithma.algorithms.graph_properties import tarjan_scc

    if scc_result is None:
        scc_result = tarjan_scc(graph)

    # Map each node → SCC index
    node_to_scc: Dict[Any, int] = {}
    for idx, scc in enumerate(scc_result):
        for node in scc:
            node_to_scc[node] = idx

    pos = _get_layout(graph, layout)

    if show_condensation:
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))
        ax_main = axes[0]
    else:
        created_fig = ax is None
        if created_fig:
            fig, ax_main = plt.subplots(figsize=(11, 7))
        else:
            fig = ax.get_figure()
            ax_main = ax

    # Node colours
    node_colors = [
        _SCC_PALETTE[node_to_scc.get(n, 0) % len(_SCC_PALETTE)]
        for n in graph.nodes()
    ]

    # Split edges
    intra_edges = [
        (u, v) for u, v in graph.edges()
        if node_to_scc.get(u) == node_to_scc.get(v)
    ]
    inter_edges = [
        (u, v) for u, v in graph.edges()
        if node_to_scc.get(u) != node_to_scc.get(v)
    ]

    nx.draw_networkx_nodes(graph, pos, ax=ax_main,
                           node_color=node_colors, node_size=650)
    nx.draw_networkx_labels(graph, pos, ax=ax_main,
                            font_color='white', font_weight='bold')
    nx.draw_networkx_edges(graph, pos, edgelist=intra_edges, ax=ax_main,
                           edge_color=[
                               _SCC_PALETTE[node_to_scc.get(u, 0) % len(_SCC_PALETTE)]
                               for u, v in intra_edges
                           ],
                           width=2.5, arrows=graph.is_directed(), arrowsize=18)
    nx.draw_networkx_edges(graph, pos, edgelist=inter_edges, ax=ax_main,
                           edge_color='#7f8c8d', style='dashed', width=1.5,
                           arrows=graph.is_directed(), arrowsize=18, alpha=0.7)

    legend_handles = [
        mpatches.Patch(color=_SCC_PALETTE[i % len(_SCC_PALETTE)],
                       label=f"SCC {i + 1} ({len(scc)} nodes)")
        for i, scc in enumerate(scc_result)
    ]
    ax_main.legend(handles=legend_handles, loc='upper left', fontsize=8,
                   title='SCCs', title_fontsize=9)
    ax_main.set_title(
        title or f"Strongly Connected Components — {len(scc_result)} SCC(s)",
        fontsize=13, fontweight='bold', pad=12
    )
    ax_main.axis('off')

    if show_condensation:
        _draw_condensation(graph, scc_result, node_to_scc, axes[1])
        fig.suptitle(
            title or f"SCC Analysis — {len(scc_result)} SCC(s)",
            fontsize=14, fontweight='bold'
        )
        axes[0].set_title("Original Graph — SCCs coloured", fontsize=11)

    plt.tight_layout()
    return fig


def _draw_condensation(
    graph: Union[nx.DiGraph, nx.Graph],
    scc_result: List[List[Any]],
    node_to_scc: Dict[Any, int],
    ax: Any,
) -> None:
    """Draw the condensation DAG on the given axes."""
    cond = nx.DiGraph()
    for i in range(len(scc_result)):
        cond.add_node(i, label=f"SCC{i + 1}\n({len(scc_result[i])})")
    for u, v in graph.edges():
        su, sv = node_to_scc.get(u), node_to_scc.get(v)
        if su is not None and sv is not None and su != sv:
            cond.add_edge(su, sv)

    cond_pos = nx.spring_layout(cond, seed=42)
    node_colors = [_SCC_PALETTE[i % len(_SCC_PALETTE)] for i in cond.nodes()]
    labels = {i: f"SCC{i + 1}\n({len(scc_result[i])})" for i in cond.nodes()}

    nx.draw_networkx_nodes(cond, cond_pos, ax=ax,
                           node_color=node_colors, node_size=1200)
    nx.draw_networkx_labels(cond, cond_pos, labels=labels, ax=ax,
                            font_color='white', font_weight='bold', font_size=8)
    nx.draw_networkx_edges(cond, cond_pos, ax=ax,
                           edge_color='#34495e', width=2,
                           arrows=True, arrowsize=20)
    ax.set_title("Condensation DAG", fontsize=11)
    ax.axis('off')


# ---------------------------------------------------------------------------
# plot_topological_order
# ---------------------------------------------------------------------------

def plot_topological_order(
    graph: nx.DiGraph,
    order: Optional[List[Any]] = None,
    layout: str = 'layered',
    title: Optional[str] = None,
) -> Any:
    """Visualise a topological ordering of a DAG.

    Nodes are arranged left-to-right according to their position in the
    topological order.  Node colour transitions from dark blue (first) to
    light blue (last).  Each node displays its rank number.

    Args:
        graph:  Directed acyclic graph.
        order:  Output of topological_sort().  Computed internally if None.
        layout: 'layered' (left-to-right by rank) or any NetworkX layout name.
        title:  Override auto-generated title.

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_topological_order')
    from logarithma.algorithms.graph_properties import topological_sort

    if order is None:
        order = topological_sort(graph)

    rank: Dict[Any, int] = {n: i for i, n in enumerate(order)}
    n = len(order)

    if layout == 'layered':
        pos = _layered_pos(graph, order)
    else:
        pos = _get_layout(graph, layout)

    # Colour gradient: dark → light blue
    try:
        import matplotlib.cm as cm
        cmap = cm.get_cmap('Blues')
        node_colors = [to_hex(cmap(0.4 + 0.55 * rank[nd] / max(n - 1, 1)))
                       for nd in graph.nodes()]
    except Exception:
        node_colors = ['#3498db'] * graph.number_of_nodes()

    fig, ax = plt.subplots(figsize=(max(12, n * 1.4), 7))

    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=node_colors, node_size=700)

    # Labels: node name + rank
    labels = {nd: f"{nd}\n(#{rank[nd] + 1})" for nd in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels=labels, ax=ax,
                            font_color='white', font_weight='bold', font_size=8)

    nx.draw_networkx_edges(graph, pos, ax=ax,
                           edge_color='#34495e', width=2,
                           arrows=True, arrowsize=20,
                           connectionstyle='arc3,rad=0.1')

    ax.set_title(
        title or f"Topological Order — {n} nodes",
        fontsize=13, fontweight='bold', pad=12
    )
    ax.axis('off')
    plt.tight_layout()
    return fig


def _layered_pos(graph: nx.DiGraph, order: List[Any]) -> Dict[Any, Tuple[float, float]]:
    """Position nodes left-to-right by topological rank, spreading vertically."""
    rank: Dict[Any, int] = {n: i for i, n in enumerate(order)}
    n = len(order)

    # Group nodes by rank for vertical distribution
    from collections import defaultdict
    columns: Dict[int, List[Any]] = defaultdict(list)
    for node in graph.nodes():
        columns[rank[node]].append(node)

    pos: Dict[Any, Tuple[float, float]] = {}
    for col_idx, nodes_in_col in columns.items():
        x = col_idx / max(n - 1, 1)
        for row_idx, node in enumerate(nodes_in_col):
            y = 0.5 if len(nodes_in_col) == 1 else row_idx / (len(nodes_in_col) - 1)
            pos[node] = (x, y)
    return pos
