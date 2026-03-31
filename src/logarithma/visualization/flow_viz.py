"""
Network Flow Visualizations
============================

Visualization functions for maximum flow networks.

Color semantics:
    SOURCE        #2ecc71  green
    SINK          #e67e22  orange
    OTHER NODES   #3498db  blue
    SATURATED     #e74c3c  red    (flow == capacity)
    PARTIAL FLOW  #3498db  blue   (0 < flow < capacity)
    EMPTY EDGE    #bdc3c7  grey   (flow == 0)

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
_C_SOURCE = "#2ecc71"
_C_SINK = "#e67e22"
_C_NODE = "#3498db"
_C_SATURATED = "#e74c3c"
_C_PARTIAL = "#3498db"
_C_EMPTY = "#bdc3c7"


def _check_matplotlib(fn_name: str) -> None:
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            f"matplotlib is required for {fn_name}(). "
            "Install it with: pip install matplotlib"
        )


# ---------------------------------------------------------------------------
# plot_flow_network
# ---------------------------------------------------------------------------

def plot_flow_network(
    graph: Union[nx.DiGraph, nx.Graph],
    flow_result: Optional[Dict[str, Any]] = None,
    source: Optional[Any] = None,
    sink: Optional[Any] = None,
    capacity: str = 'capacity',
    layout: str = 'spring',
    title: Optional[str] = None,
    ax: Optional[Any] = None,
) -> Any:
    """Visualise a flow network with flow/capacity labels on every edge.

    Edge colours:
        Red   — saturated (flow == capacity)
        Blue  — partial flow (0 < flow < capacity)
        Grey  — unused (flow == 0 or no flow computed)

    Args:
        graph:       Directed or undirected NetworkX graph.
        flow_result: Output of max_flow().  If None and both source/sink are
                     supplied, max_flow() is run internally.
        source:      Flow source node (used for node colouring and auto-run).
        sink:        Flow sink node.
        capacity:    Edge attribute name for capacity.
        layout:      NetworkX layout name.
        title:       Override auto-generated title.
        ax:          Existing Axes; a new figure is created when None.

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_flow_network')

    if flow_result is None and source is not None and sink is not None:
        from logarithma.algorithms.network_flow import max_flow as _max_flow
        flow_result = _max_flow(graph, source, sink, capacity=capacity)

    pos = _get_layout(graph, layout)
    created_fig = ax is None
    if created_fig:
        fig, ax = plt.subplots(figsize=(12, 8))
    else:
        fig = ax.get_figure()

    # Node colours
    node_colors = []
    for n in graph.nodes():
        if n == source:
            node_colors.append(_C_SOURCE)
        elif n == sink:
            node_colors.append(_C_SINK)
        else:
            node_colors.append(_C_NODE)

    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=node_colors, node_size=700)
    nx.draw_networkx_labels(graph, pos, ax=ax, font_color='white', font_weight='bold')

    # Build per-edge colour and label
    flow_dict = flow_result['flow_dict'] if flow_result else {}
    edge_colors = []
    edge_labels: Dict[Tuple, str] = {}

    for u, v, data in graph.edges(data=True):
        cap = data.get(capacity, 1)
        f = 0.0
        if flow_dict and u in flow_dict and v in flow_dict[u]:
            f = flow_dict[u][v]

        if cap > 0 and f >= cap:
            edge_colors.append(_C_SATURATED)
        elif f > 0:
            edge_colors.append(_C_PARTIAL)
        else:
            edge_colors.append(_C_EMPTY)

        edge_labels[(u, v)] = f"{f:.4g}/{cap}"

    nx.draw_networkx_edges(
        graph, pos, ax=ax,
        edge_color=edge_colors, width=2.5,
        arrows=True, arrowsize=20,
        connectionstyle='arc3,rad=0.1' if graph.is_directed() else 'arc3,rad=0.0',
    )
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                 ax=ax, font_size=8, label_pos=0.4)

    flow_val = flow_result['flow_value'] if flow_result else 'N/A'
    default_title = (
        f"Flow Network  |  Max flow: {flow_val}"
        + (f"  ({source} → {sink})" if source is not None else "")
    )
    ax.set_title(title or default_title, fontsize=13, fontweight='bold', pad=12)

    legend_elements = [
        mpatches.Patch(color=_C_SOURCE, label='Source'),
        mpatches.Patch(color=_C_SINK, label='Sink'),
        Line2D([0], [0], color=_C_SATURATED, lw=2.5, label='Saturated'),
        Line2D([0], [0], color=_C_PARTIAL, lw=2.5, label='Partial flow'),
        Line2D([0], [0], color=_C_EMPTY, lw=2.5, alpha=0.6, label='Unused'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
    ax.axis('off')

    if created_fig:
        plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# plot_flow_paths
# ---------------------------------------------------------------------------

def plot_flow_paths(
    graph: Union[nx.DiGraph, nx.Graph],
    flow_result: Dict[str, Any],
    source: Any,
    sink: Any,
    capacity: str = 'capacity',
    layout: str = 'spring',
) -> Any:
    """Visualise only the edges that carry positive flow.

    Edge thickness is proportional to the flow magnitude.

    Args:
        graph:       Original graph.
        flow_result: Output of max_flow().
        source:      Flow source (for node colouring).
        sink:        Flow sink (for node colouring).
        capacity:    Edge attribute for capacity labels.
        layout:      NetworkX layout name.

    Returns:
        matplotlib.figure.Figure
    """
    _check_matplotlib('plot_flow_paths')

    pos = _get_layout(graph, layout)
    fig, ax = plt.subplots(figsize=(12, 8))

    node_colors = [
        _C_SOURCE if n == source else (_C_SINK if n == sink else _C_NODE)
        for n in graph.nodes()
    ]
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=node_colors, node_size=700)
    nx.draw_networkx_labels(graph, pos, ax=ax, font_color='white', font_weight='bold')

    flow_dict = flow_result['flow_dict']
    max_f = max(
        (f for u_dict in flow_dict.values() for f in u_dict.values()),
        default=1.0,
    ) or 1.0

    active_edges = []
    widths = []
    labels: Dict[Tuple, str] = {}

    for u, v, data in graph.edges(data=True):
        f = flow_dict.get(u, {}).get(v, 0.0)
        if f > 0:
            active_edges.append((u, v))
            widths.append(1.5 + 6 * (f / max_f))
            cap = data.get(capacity, 1)
            labels[(u, v)] = f"{f:.4g}/{cap}"

    inactive = [(u, v) for u, v in graph.edges() if (u, v) not in active_edges]
    nx.draw_networkx_edges(graph, pos, edgelist=inactive, ax=ax,
                           edge_color=_C_EMPTY, width=1, alpha=0.3,
                           arrows=graph.is_directed(), arrowsize=15)
    if active_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=active_edges, ax=ax,
                               edge_color=_C_PARTIAL, width=widths,
                               arrows=graph.is_directed(), arrowsize=20,
                               connectionstyle='arc3,rad=0.1')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels,
                                     ax=ax, font_size=8, label_pos=0.4)

    ax.set_title(
        f"Flow Paths  |  Total flow: {flow_result['flow_value']:.4g}  "
        f"({source} → {sink})",
        fontsize=13, fontweight='bold', pad=12
    )
    ax.legend(
        handles=[
            Line2D([0], [0], color=_C_PARTIAL, lw=3, label='Active flow (width ∝ flow)'),
            Line2D([0], [0], color=_C_EMPTY, lw=1, alpha=0.3, label='Unused edge'),
        ],
        loc='upper left', fontsize=9
    )
    ax.axis('off')
    plt.tight_layout()
    return fig
