"""
Traversal-Specific Visualizations
===================================

Visualization functions that expose the *internal* behaviour of graph traversal
algorithms — beyond the simple visit-order gradient already provided by
``plot_traversal`` in ``graph_plotter.py``.

Currently provides:
    plot_dfs_tree — DFS tree structure with edge classification and depth info.

Color palette (consistent with shortest_path_viz.py):
    TREE EDGE     solid black arrow
    BACK EDGE     dashed red  arrow  (cycle witness)
    CROSS EDGE    dashed grey arrow  (DiGraph only)
    SOURCE        #2ecc71  green
    CYCLE NODE    #e74c3c  red
    DEPTH TINT    blue gradient by recursion depth
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union

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
# Internal DFS trace helper
# ---------------------------------------------------------------------------

def _dfs_trace(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
) -> Dict[str, Any]:
    """
    Run DFS from *source* and collect detailed edge/node classification data.

    Returns a dict with:
        visited_order   — nodes in discovery (pre-order) order
        discovery       — {node: discovery_time}
        finish          — {node: finish_time}
        depth           — {node: recursion depth from source}
        parent          — {node: parent_node | None}
        tree_edges      — list of (u, v) tree edges
        back_edges      — list of (u, v) back edges  (cycle witnesses)
        cross_edges     — list of (u, v) cross/forward edges (DiGraph only)
        cycle_nodes     — set of nodes that are part of a back-edge cycle
    """
    is_directed = isinstance(graph, nx.DiGraph)
    visited: Set[Any] = set()
    rec_stack: Set[Any] = set()   # active recursion stack (directed)

    visited_order: List[Any] = []
    discovery: Dict[Any, int] = {}
    finish: Dict[Any, int] = {}
    depth: Dict[Any, int] = {}
    parent: Dict[Any, Optional[Any]] = {source: None}

    tree_edges: List[Tuple[Any, Any]] = []
    back_edges: List[Tuple[Any, Any]] = []
    cross_edges: List[Tuple[Any, Any]] = []
    cycle_nodes: Set[Any] = set()

    timer = [0]

    def visit(node: Any, d: int, par: Optional[Any]) -> None:
        visited.add(node)
        rec_stack.add(node)
        depth[node] = d
        discovery[node] = timer[0]
        timer[0] += 1
        visited_order.append(node)

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                parent[neighbor] = node
                tree_edges.append((node, neighbor))
                visit(neighbor, d + 1, node)
            elif is_directed:
                if neighbor in rec_stack:
                    # Back edge — cycle
                    back_edges.append((node, neighbor))
                    cycle_nodes.add(node)
                    cycle_nodes.add(neighbor)
                else:
                    # Cross or forward edge
                    cross_edges.append((node, neighbor))
            else:
                # Undirected: skip edge back to parent, flag anything else as back edge
                if neighbor != par:
                    back_edges.append((node, neighbor))
                    cycle_nodes.add(node)
                    cycle_nodes.add(neighbor)

        rec_stack.discard(node)
        finish[node] = timer[0]
        timer[0] += 1

    visit(source, 0, None)

    # Continue from unvisited nodes (disconnected components)
    for node in graph.nodes():
        if node not in visited:
            parent[node] = None
            visit(node, 0, None)

    return {
        'visited_order': visited_order,
        'discovery': discovery,
        'finish': finish,
        'depth': depth,
        'parent': parent,
        'tree_edges': tree_edges,
        'back_edges': back_edges,
        'cross_edges': cross_edges,
        'cycle_nodes': cycle_nodes,
    }


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def plot_dfs_tree(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    pos: Optional[Dict[Any, Tuple[float, float]]] = None,
    layout: str = "spring",
    show_discovery_finish: bool = True,
    show_depth: bool = False,
    node_size: int = 600,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (11, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize the DFS tree structure with edge classification.

    Edges are drawn in three styles:
    - **Black solid**  : tree edges (edges that DFS actually traversed)
    - **Red dashed**   : back edges (point to an ancestor → cycle witness)
    - **Grey dashed**  : cross/forward edges (DiGraph only, non-tree non-back)

    Nodes are coloured by recursion depth (deeper = darker blue), with the
    source in green and cycle-witness nodes highlighted in red.

    Optional labels above each node show ``d=<discovery> f=<finish>`` times,
    which are useful for understanding DFS interval properties (e.g.
    parenthesis theorem, topological sort, SCC analysis).

    Args:
        graph:                  NetworkX Graph or DiGraph.
        source:                 DFS start node.
        pos:                    Pre-computed layout dict. If None, computed
                                from *layout*.
        layout:                 Layout algorithm name (used if *pos* is None).
        show_discovery_finish:  If True, draw ``d/f`` timestamps above nodes.
        show_depth:             If True, draw recursion depth below nodes.
        node_size:              Matplotlib node size.
        title:                  Figure title.
        figsize:                Figure size (width, height).
        save_path:              If given, save figure to this path.

    Raises:
        ImportError: If matplotlib is not installed.

    Example:
        >>> import networkx as nx
        >>> from logarithma.visualization import plot_dfs_tree
        >>> G = nx.DiGraph()
        >>> G.add_edges_from([('A','B'),('A','C'),('B','D'),('D','B'),('C','D')])
        >>> plot_dfs_tree(G, 'A', layout='spring', show_discovery_finish=True)
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    trace = _dfs_trace(graph, source)
    visited_order = trace['visited_order']
    discovery = trace['discovery']
    finish = trace['finish']
    depth = trace['depth']
    tree_edges = trace['tree_edges']
    back_edges = trace['back_edges']
    cross_edges = trace['cross_edges']
    cycle_nodes = trace['cycle_nodes']

    if pos is None:
        pos = _get_layout(graph, layout)

    # --- Node colours: depth-based blue gradient, overrides for source/cycle ---
    max_depth = max(depth.values()) if depth else 1
    node_colors = []
    for node in graph.nodes():
        if node == source:
            node_colors.append("#2ecc71")           # green — source
        elif node in cycle_nodes:
            node_colors.append("#e74c3c")           # red — cycle participant
        else:
            d = depth.get(node, 0)
            intensity = 0.2 + 0.6 * (d / max(max_depth, 1))
            node_colors.append((0.2, 0.4, intensity + 0.2))  # blue gradient

    fig, ax = plt.subplots(figsize=figsize)

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors,
                           node_size=node_size, ax=ax)
    nx.draw_networkx_labels(graph, pos, font_color="white",
                            font_weight="bold", ax=ax)

    # Draw edge sets separately for styling
    is_directed = isinstance(graph, nx.DiGraph)
    arrow_kw = dict(ax=ax, arrows=is_directed)

    all_edges = set(graph.edges())
    back_set = set(back_edges)
    cross_set = set(cross_edges)
    tree_set = set(tree_edges)

    # Remaining (non-tree, non-back, non-cross) edges — draw faint
    other_edges = [e for e in all_edges
                   if e not in tree_set and e not in back_set and e not in cross_set]

    if other_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=other_edges,
                               edge_color="#dddddd", width=0.8,
                               style="dotted", **arrow_kw)
    if tree_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=tree_edges,
                               edge_color="black", width=2.5,
                               **arrow_kw)
    if back_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=back_edges,
                               edge_color="#e74c3c", width=2.0,
                               style="dashed", **arrow_kw)
    if cross_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=cross_edges,
                               edge_color="#7f8c8d", width=1.5,
                               style="dashed", **arrow_kw)

    # Draw edge weights if present
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                     font_size=7, ax=ax)

    # Optional: discovery/finish labels above nodes
    if show_discovery_finish:
        df_labels = {n: f"d={discovery[n]} f={finish[n]}"
                     for n in graph.nodes() if n in discovery}
        label_pos_up = {k: (v[0], v[1] + 0.10) for k, v in pos.items()}
        nx.draw_networkx_labels(graph, label_pos_up, df_labels,
                                font_size=7, font_color="#2c3e50", ax=ax)

    # Optional: depth labels below nodes
    if show_depth:
        depth_labels = {n: f"depth={depth.get(n, '?')}" for n in graph.nodes()}
        label_pos_down = {k: (v[0], v[1] - 0.10) for k, v in pos.items()}
        nx.draw_networkx_labels(graph, label_pos_down, depth_labels,
                                font_size=7, font_color="#8e44ad", ax=ax)

    # Visit-order annotation in bottom-left
    order_str = "Visit order: " + " → ".join(str(n) for n in visited_order)
    ax.text(0.01, 0.01, order_str, transform=ax.transAxes,
            fontsize=8, color="#555555", verticalalignment="bottom")

    # Legend
    legend_handles = [
        mpatches.Patch(color="#2ecc71", label="Source"),
        mpatches.Patch(color="#e74c3c", label="Cycle node" if cycle_nodes else "Cycle node (none)"),
        mpatches.Patch(color=(0.2, 0.4, 0.8), label="Visited (depth-shaded)"),
        Line2D([0], [0], color="black", linewidth=2.5, label=f"Tree edge ({len(tree_edges)})"),
        Line2D([0], [0], color="#e74c3c", linewidth=2.0, linestyle="dashed",
               label=f"Back edge ({len(back_edges)}) {'← cycle!' if back_edges else ''}"),
    ]
    if cross_edges:
        legend_handles.append(
            Line2D([0], [0], color="#7f8c8d", linewidth=1.5, linestyle="dashed",
                   label=f"Cross/forward edge ({len(cross_edges)})")
        )
    ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    has_cycle = bool(back_edges)
    default_title = (
        f"DFS Tree from '{source}'  —  "
        f"{'Cycle detected' if has_cycle else 'No cycle'}"
    )
    ax.set_title(title or default_title, fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
