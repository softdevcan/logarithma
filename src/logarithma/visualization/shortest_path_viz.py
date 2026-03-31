"""
Algorithm-Specific Shortest Path Visualizations
=================================================

Visualization functions tailored for each shortest-path algorithm introduced in
v0.3.0: A*, Bellman-Ford, and Bidirectional Dijkstra.

Each function runs the underlying algorithm internally (or accepts pre-computed
results) and produces a Matplotlib figure that exposes the algorithm's internal
behaviour — expanded nodes, frontier directions, negative edges, etc.

Color palette (consistent across all functions):
    PATH          #e74c3c  red
    SOURCE        #2ecc71  green
    TARGET        #e67e22  orange
    EXPANDED      #3498db  blue
    UNEXPLORED    #bdc3c7  grey
    NEGATIVE EDGE #c0392b  dark red
    MEETING POINT #f1c40f  yellow

Requirements:
    matplotlib >= 3.5
"""

import heapq
import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

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
_C_PATH = "#e74c3c"
_C_SOURCE = "#2ecc71"
_C_TARGET = "#e67e22"
_C_EXPANDED = "#3498db"
_C_OPEN = "#85c1e9"
_C_UNEXPLORED = "#bdc3c7"
_C_NEG_EDGE = "#c0392b"
_C_MEETING = "#f1c40f"
_C_FWD = "#2980b9"
_C_BWD = "#27ae60"


# ---------------------------------------------------------------------------
# Internal trace helpers
# ---------------------------------------------------------------------------

def _astar_trace(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
    heuristic: Callable[[Any, Any], float],
) -> Tuple[List[Any], Set[Any], Set[Any], Dict[Any, Any], float]:
    """
    Run A* and collect closed_set, open_set_final, and path information.

    Returns:
        path          — list of nodes on the optimal path
        closed_set    — nodes extracted from the open set (expanded)
        open_set_nodes— nodes still in the open set when search ended
        g_score       — best distances found
        distance      — optimal distance (inf if unreachable)
    """
    def zero(n, t):
        return 0.0

    h = heuristic if heuristic is not None else zero

    g_score: Dict[Any, float] = {node: float('inf') for node in graph.nodes()}
    g_score[source] = 0.0
    came_from: Dict[Any, Optional[Any]] = {}

    counter = 0
    open_heap: List[Tuple[float, int, Any]] = [(h(source, target), counter, source)]
    closed_set: Set[Any] = set()
    open_set_nodes: Set[Any] = {source}

    while open_heap:
        f, _, current = heapq.heappop(open_heap)
        open_set_nodes.discard(current)

        if current == target:
            # Reconstruct path
            path: List[Any] = []
            node = target
            while node != source:
                path.append(node)
                node = came_from[node]
            path.append(source)
            path.reverse()
            return path, closed_set, open_set_nodes, g_score, g_score[target]

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor in graph.neighbors(current):
            if neighbor in closed_set:
                continue
            weight = graph[current][neighbor].get('weight', 1)
            tentative_g = g_score[current] + weight
            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_new = tentative_g + h(neighbor, target)
                counter += 1
                heapq.heappush(open_heap, (f_new, counter, neighbor))
                open_set_nodes.add(neighbor)

    return [], closed_set, open_set_nodes, g_score, float('inf')


def _bidirectional_trace(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
) -> Tuple[List[Any], Set[Any], Set[Any], Any, float]:
    """
    Run Bidirectional Dijkstra and collect frontier membership for each node.

    Returns:
        path          — optimal path
        fwd_visited   — nodes settled by the forward search
        bwd_visited   — nodes settled by the backward search
        meeting_node  — node where the two frontiers met
        distance      — optimal distance
    """
    is_directed = isinstance(graph, nx.DiGraph)

    dist_f: Dict[Any, float] = {source: 0.0}
    pred_f: Dict[Any, Optional[Any]] = {source: None}
    dist_b: Dict[Any, float] = {target: 0.0}
    pred_b: Dict[Any, Optional[Any]] = {target: None}

    counter = 0
    pq_f = [(0.0, counter, source)]
    pq_b = [(0.0, counter, target)]
    closed_f: Set[Any] = set()
    closed_b: Set[Any] = set()

    mu: float = float('inf')
    meeting_node: Optional[Any] = None

    def _relax(pq, dist_mine, pred_mine, closed_mine, dist_other, reverse):
        nonlocal mu, meeting_node, counter
        if not pq:
            return
        d, _, u = heapq.heappop(pq)
        if u in closed_mine:
            return
        closed_mine.add(u)
        if d >= mu:
            return
        if reverse and is_directed:
            neighbors = list(graph.predecessors(u))
            def gw(nb, node): return graph[nb][node].get('weight', 1)
        else:
            neighbors = list(graph.neighbors(u))
            def gw(nb, node): return graph[node][nb].get('weight', 1)
        for v in neighbors:
            w = gw(v, u)
            new_dist = dist_mine[u] + w
            if new_dist < dist_mine.get(v, float('inf')):
                dist_mine[v] = new_dist
                pred_mine[v] = u
                counter += 1
                heapq.heappush(pq, (new_dist, counter, v))
            if v in dist_other:
                candidate = dist_mine.get(v, float('inf')) + dist_other[v]
                if candidate < mu:
                    mu = candidate
                    meeting_node = v

    while pq_f or pq_b:
        min_f = pq_f[0][0] if pq_f else float('inf')
        min_b = pq_b[0][0] if pq_b else float('inf')
        if min_f + min_b >= mu:
            break
        if min_f <= min_b:
            _relax(pq_f, dist_f, pred_f, closed_f, dist_b, False)
        else:
            _relax(pq_b, dist_b, pred_b, closed_b, dist_f, True)

    if meeting_node is None or mu == float('inf'):
        return [], closed_f, closed_b, None, float('inf')

    # Reconstruct path
    path_f: List[Any] = []
    node = meeting_node
    while node is not None:
        path_f.append(node)
        node = pred_f.get(node)
    path_f.reverse()

    path_b: List[Any] = []
    node = pred_b.get(meeting_node)
    while node is not None:
        path_b.append(node)
        node = pred_b.get(node)

    return path_f + path_b, closed_f, closed_b, meeting_node, mu


# ---------------------------------------------------------------------------
# Public visualisation functions
# ---------------------------------------------------------------------------

def plot_astar_search(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
    heuristic: Optional[Callable[[Any, Any], float]] = None,
    pos: Optional[Dict[Any, Tuple[float, float]]] = None,
    layout: str = "spring",
    show_heuristic: bool = False,
    node_size: int = 500,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize the A* search process on a graph.

    Nodes are colour-coded by their role in the search:
    - **Green**  : source
    - **Orange** : target
    - **Blue**   : expanded (closed set)
    - **Light blue**: generated but not yet expanded (open set at termination)
    - **Grey**   : never reached
    - **Red path**: optimal path found

    Args:
        graph:          NetworkX Graph or DiGraph with non-negative weights.
        source:         Source node.
        target:         Target node.
        heuristic:      Admissible heuristic callable h(node, target) → float.
                        Defaults to zero heuristic (equivalent to Dijkstra).
        pos:            Pre-computed layout dict {node: (x, y)}.
                        If None, computed from *layout*.
        layout:         Layout algorithm name (used if *pos* is None).
        show_heuristic: If True, draw the heuristic value h(n, target) above
                        each node (requires *heuristic* to be provided).
        node_size:      Matplotlib node size.
        title:          Figure title.
        figsize:        Figure size (width, height).
        save_path:      If given, save figure to this path (PNG/SVG etc.).

    Raises:
        ImportError: If matplotlib is not installed.

    Example:
        >>> import networkx as nx
        >>> from logarithma.visualization import plot_astar_search
        >>> G = nx.grid_2d_graph(5, 5)
        >>> for u, v in G.edges():
        ...     G[u][v]['weight'] = 1
        >>> plot_astar_search(G, (0, 0), (4, 4), title="A* on 5×5 Grid")
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    path, closed_set, open_set_nodes, g_score, distance = _astar_trace(
        graph, source, target, heuristic
    )

    if pos is None:
        pos = _get_layout(graph, layout)

    # Assign node colours
    node_colors = []
    for node in graph.nodes():
        if node == source:
            node_colors.append(_C_SOURCE)
        elif node == target:
            node_colors.append(_C_TARGET)
        elif node in closed_set:
            node_colors.append(_C_EXPANDED)
        elif node in open_set_nodes:
            node_colors.append(_C_OPEN)
        else:
            node_colors.append(_C_UNEXPLORED)

    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if path else []

    fig, ax = plt.subplots(figsize=figsize)

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_size, ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)
    nx.draw_networkx_edges(graph, pos, edge_color="lightgray", width=1.0, ax=ax,
                           arrows=isinstance(graph, nx.DiGraph))

    if path_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges,
                               edge_color=_C_PATH, width=3.0, ax=ax,
                               arrows=isinstance(graph, nx.DiGraph))

    edge_labels = nx.get_edge_attributes(graph, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

    if show_heuristic and heuristic is not None:
        h_labels = {n: f"h={heuristic(n, target):.1f}" for n in graph.nodes()}
        label_pos = {k: (v[0], v[1] + 0.07) for k, v in pos.items()}
        nx.draw_networkx_labels(graph, label_pos, h_labels,
                                font_size=7, font_color="darkblue", ax=ax)

    legend_handles = [
        mpatches.Patch(color=_C_SOURCE, label="Source"),
        mpatches.Patch(color=_C_TARGET, label="Target"),
        mpatches.Patch(color=_C_EXPANDED, label=f"Expanded ({len(closed_set)})"),
        mpatches.Patch(color=_C_OPEN, label=f"Open set ({len(open_set_nodes)})"),
        mpatches.Patch(color=_C_UNEXPLORED, label="Unexplored"),
        mpatches.Patch(color=_C_PATH, label=f"Path (d={distance:.2g})"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    ax.set_title(title or f"A* Search: {source} → {target}", fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def plot_bellman_ford_result(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    distances: Dict[Any, float],
    predecessors: Dict[Any, Optional[Any]],
    highlight_targets: Optional[List[Any]] = None,
    pos: Optional[Dict[Any, Tuple[float, float]]] = None,
    layout: str = "spring",
    node_size: int = 500,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize the result of a Bellman-Ford computation.

    Highlights negative-weight edges in dark red and shows the shortest-path
    distances inside each node label.  If *highlight_targets* is provided,
    the shortest path from source to each target is drawn in red.

    Args:
        graph:              NetworkX Graph or DiGraph.
        source:             Source node used when running bellman_ford().
        distances:          ``result['distances']`` from :func:`bellman_ford`.
        predecessors:       ``result['predecessors']`` from :func:`bellman_ford`.
        highlight_targets:  List of target nodes whose paths to draw.
                            If None, no paths are highlighted.
        pos:                Pre-computed layout dict.
        layout:             Layout algorithm name (used if *pos* is None).
        node_size:          Matplotlib node size.
        title:              Figure title.
        figsize:            Figure size.
        save_path:          Save path for the figure.

    Raises:
        ImportError: If matplotlib is not installed.

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path.bellman_ford import bellman_ford
        >>> from logarithma.visualization import plot_bellman_ford_result
        >>> G = nx.DiGraph()
        >>> G.add_edge('A', 'B', weight=4)
        >>> G.add_edge('A', 'C', weight=2)
        >>> G.add_edge('B', 'C', weight=-3)
        >>> G.add_edge('C', 'D', weight=1)
        >>> result = bellman_ford(G, 'A')
        >>> plot_bellman_ford_result(G, 'A', result['distances'],
        ...                         result['predecessors'],
        ...                         highlight_targets=['D'])
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    if pos is None:
        pos = _get_layout(graph, layout)

    # Separate edges into negative and non-negative
    neg_edges = [(u, v) for u, v, d in graph.edges(data=True)
                 if d.get('weight', 1) < 0]
    pos_edges = [(u, v) for u, v in graph.edges()
                 if (u, v) not in neg_edges]

    # Build node colours
    node_colors = [_C_SOURCE if n == source else _C_UNEXPLORED
                   for n in graph.nodes()]

    fig, ax = plt.subplots(figsize=figsize)

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_size, ax=ax)

    # Node labels include distance
    dist_labels = {
        n: f"{n}\n(d={distances[n]:.4g})" if distances[n] != float('inf')
        else f"{n}\n(∞)"
        for n in graph.nodes()
    }
    nx.draw_networkx_labels(graph, pos, dist_labels, font_size=8, ax=ax)

    # Draw positive edges
    nx.draw_networkx_edges(graph, pos, edgelist=pos_edges,
                           edge_color="gray", width=1.5, ax=ax,
                           arrows=isinstance(graph, nx.DiGraph))
    # Draw negative edges
    if neg_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=neg_edges,
                               edge_color=_C_NEG_EDGE, width=2.5, ax=ax,
                               arrows=isinstance(graph, nx.DiGraph),
                               style="dashed")

    # Draw edge weight labels
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

    # Highlight paths to requested targets
    if highlight_targets:
        for tgt in highlight_targets:
            if distances.get(tgt, float('inf')) == float('inf'):
                continue
            path = _trace_path(predecessors, source, tgt)
            path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            nx.draw_networkx_edges(graph, pos, edgelist=path_edges,
                                   edge_color=_C_PATH, width=3.0, ax=ax,
                                   arrows=isinstance(graph, nx.DiGraph))
            nx.draw_networkx_nodes(graph, pos, nodelist=[tgt],
                                   node_color=_C_TARGET, node_size=node_size, ax=ax)

    legend_handles = [
        mpatches.Patch(color=_C_SOURCE, label="Source"),
        mpatches.Patch(color=_C_TARGET, label="Target(s)"),
        Line2D([0], [0], color="gray", linewidth=1.5, label="Positive edge"),
        Line2D([0], [0], color=_C_NEG_EDGE, linewidth=2.5,
               linestyle="dashed", label=f"Negative edge ({len(neg_edges)})"),
        Line2D([0], [0], color=_C_PATH, linewidth=3.0, label="Shortest path"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    ax.set_title(title or f"Bellman-Ford result from '{source}'",
                 fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def plot_negative_cycle(
    graph: Union[nx.Graph, nx.DiGraph],
    cycle: List[Any],
    pos: Optional[Dict[Any, Tuple[float, float]]] = None,
    layout: str = "spring",
    node_size: int = 500,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize a negative-weight cycle detected by Bellman-Ford.

    Cycle nodes are coloured red, cycle edges are drawn as thick dark-red
    arrows, and the total cycle weight is shown in the title.

    Args:
        graph:      NetworkX Graph or DiGraph.
        cycle:      List of nodes forming the cycle (as returned in
                    ``NegativeCycleError.cycle``).
        pos:        Pre-computed layout dict.
        layout:     Layout algorithm name (used if *pos* is None).
        node_size:  Matplotlib node size.
        title:      Figure title.
        figsize:    Figure size.
        save_path:  Save path for the figure.

    Raises:
        ImportError: If matplotlib is not installed.

    Example:
        >>> from logarithma.algorithms.exceptions import NegativeCycleError
        >>> try:
        ...     bellman_ford(G, source)
        ... except NegativeCycleError as e:
        ...     plot_negative_cycle(G, e.cycle)
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    if pos is None:
        pos = _get_layout(graph, layout)

    cycle_set = set(cycle)
    # Build cycle edge list (consecutive pairs in cycle list)
    cycle_edges = [(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)]

    # Compute total cycle weight
    total_weight = sum(
        graph[u][v].get('weight', 1) for u, v in cycle_edges
        if graph.has_edge(u, v)
    )

    node_colors = [_C_PATH if n in cycle_set else _C_UNEXPLORED
                   for n in graph.nodes()]

    fig, ax = plt.subplots(figsize=figsize)

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_size, ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)

    non_cycle_edges = [(u, v) for u, v in graph.edges() if (u, v) not in cycle_edges]
    nx.draw_networkx_edges(graph, pos, edgelist=non_cycle_edges,
                           edge_color="lightgray", width=1.0, ax=ax,
                           arrows=isinstance(graph, nx.DiGraph))
    nx.draw_networkx_edges(graph, pos, edgelist=cycle_edges,
                           edge_color=_C_NEG_EDGE, width=4.0, ax=ax,
                           arrows=isinstance(graph, nx.DiGraph))

    edge_labels = nx.get_edge_attributes(graph, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

    legend_handles = [
        mpatches.Patch(color=_C_PATH, label="Cycle node"),
        mpatches.Patch(color=_C_UNEXPLORED, label="Other node"),
        Line2D([0], [0], color=_C_NEG_EDGE, linewidth=4.0,
               label=f"Cycle edge (total w={total_weight:.4g})"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    default_title = (
        f"Negative Cycle Detected  (total weight = {total_weight:.4g})\n"
        f"Cycle: {' → '.join(str(n) for n in cycle)}"
    )
    ax.set_title(title or default_title, fontsize=13, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def plot_bidirectional_search(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
    pos: Optional[Dict[Any, Tuple[float, float]]] = None,
    layout: str = "spring",
    node_size: int = 500,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
) -> None:
    """
    Visualize the two-frontier search of Bidirectional Dijkstra.

    Nodes are colour-coded by which frontier settled them:
    - **Green**   : source
    - **Orange**  : target
    - **Blue**    : settled by forward search only
    - **Teal**    : settled by backward search only
    - **Purple**  : settled by both frontiers
    - **Yellow**  : meeting point
    - **Red path**: optimal path

    Args:
        graph:      NetworkX Graph or DiGraph with non-negative weights.
        source:     Source node.
        target:     Target node.
        pos:        Pre-computed layout dict.
        layout:     Layout algorithm name (used if *pos* is None).
        node_size:  Matplotlib node size.
        title:      Figure title.
        figsize:    Figure size.
        save_path:  Save path for the figure.

    Raises:
        ImportError: If matplotlib is not installed.

    Example:
        >>> from logarithma.visualization import plot_bidirectional_search
        >>> import networkx as nx
        >>> G = nx.path_graph(8)
        >>> for u, v in G.edges():
        ...     G[u][v]['weight'] = 1
        >>> plot_bidirectional_search(G, 0, 7)
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    path, fwd_visited, bwd_visited, meeting_node, distance = _bidirectional_trace(
        graph, source, target
    )

    if pos is None:
        pos = _get_layout(graph, layout)

    both = fwd_visited & bwd_visited

    node_colors = []
    for node in graph.nodes():
        if node == source:
            node_colors.append(_C_SOURCE)
        elif node == target:
            node_colors.append(_C_TARGET)
        elif node == meeting_node:
            node_colors.append(_C_MEETING)
        elif node in both:
            node_colors.append("#8e44ad")   # purple — both frontiers
        elif node in fwd_visited:
            node_colors.append(_C_FWD)
        elif node in bwd_visited:
            node_colors.append(_C_BWD)
        else:
            node_colors.append(_C_UNEXPLORED)

    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if path else []

    fig, ax = plt.subplots(figsize=figsize)

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_size, ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)
    nx.draw_networkx_edges(graph, pos, edge_color="lightgray", width=1.0, ax=ax,
                           arrows=isinstance(graph, nx.DiGraph))

    if path_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges,
                               edge_color=_C_PATH, width=3.0, ax=ax,
                               arrows=isinstance(graph, nx.DiGraph))

    edge_labels = nx.get_edge_attributes(graph, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

    legend_handles = [
        mpatches.Patch(color=_C_SOURCE, label="Source"),
        mpatches.Patch(color=_C_TARGET, label="Target"),
        mpatches.Patch(color=_C_MEETING, label="Meeting point"),
        mpatches.Patch(color=_C_FWD, label=f"Forward only ({len(fwd_visited - both)})"),
        mpatches.Patch(color=_C_BWD, label=f"Backward only ({len(bwd_visited - both)})"),
        mpatches.Patch(color="#8e44ad", label=f"Both frontiers ({len(both)})"),
        mpatches.Patch(color=_C_UNEXPLORED, label="Unexplored"),
        mpatches.Patch(color=_C_PATH, label=f"Path (d={distance:.2g})"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    ax.set_title(title or f"Bidirectional Dijkstra: {source} → {target}",
                 fontsize=14, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def plot_shortest_path_comparison(
    graph: Union[nx.Graph, nx.DiGraph],
    source: Any,
    target: Any,
    algorithms: Optional[List[str]] = None,
    heuristic: Optional[Callable[[Any, Any], float]] = None,
    pos: Optional[Dict[Any, Tuple[float, float]]] = None,
    layout: str = "spring",
    node_size: int = 400,
    figsize: Optional[Tuple[int, int]] = None,
    save_path: Optional[str] = None,
) -> None:
    """
    Compare multiple shortest-path algorithms on the same graph side by side.

    Each algorithm is run automatically and a subplot is drawn showing the
    resulting path, distance, and number of expanded nodes.

    Args:
        graph:      NetworkX Graph or DiGraph with non-negative edge weights.
        source:     Source node.
        target:     Target node.
        algorithms: List of algorithm names to include.
                    Supported: ``'dijkstra'``, ``'astar'``, ``'bidirectional'``.
                    Defaults to all three.
        heuristic:  Heuristic callable passed to A*. Defaults to zero heuristic.
        pos:        Pre-computed layout dict (shared across all subplots).
        layout:     Layout algorithm name (used if *pos* is None).
        node_size:  Matplotlib node size.
        figsize:    Figure size. Auto-computed if None.
        save_path:  Save path for the figure.

    Raises:
        ImportError: If matplotlib is not installed.
        ValueError:  If an unrecognised algorithm name is provided.

    Example:
        >>> from logarithma.visualization import plot_shortest_path_comparison
        >>> import networkx as nx
        >>> G = nx.karate_club_graph()
        >>> plot_shortest_path_comparison(G, 0, 33)
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib is required. Install with: pip install matplotlib")

    # Lazy imports — kept here to avoid circular imports at module level
    from logarithma.algorithms.shortest_path.dijkstra import dijkstra_with_path
    from logarithma.algorithms.shortest_path.astar import astar_with_stats
    from logarithma.algorithms.shortest_path.bidirectional_dijkstra import bidirectional_dijkstra

    supported = {"dijkstra", "astar", "bidirectional"}
    if algorithms is None:
        algorithms = ["dijkstra", "astar", "bidirectional"]

    for alg in algorithms:
        if alg not in supported:
            raise ValueError(f"Unknown algorithm '{alg}'. Choose from {supported}")

    if pos is None:
        pos = _get_layout(graph, layout)

    # Run each algorithm and collect results
    results: Dict[str, Dict] = {}

    if "dijkstra" in algorithms:
        dist, path = dijkstra_with_path(graph, source, target)
        results["dijkstra"] = {
            "label": "Dijkstra",
            "distance": dist,
            "path": path,
            "expanded": None,
        }

    if "astar" in algorithms:
        res = astar_with_stats(graph, source, target, heuristic=heuristic)
        results["astar"] = {
            "label": "A*",
            "distance": res['distance'],
            "path": res['path'],
            "expanded": res['nodes_expanded'],
        }

    if "bidirectional" in algorithms:
        res = bidirectional_dijkstra(graph, source, target)
        results["bidirectional"] = {
            "label": "Bidirectional Dijkstra",
            "distance": res['distance'],
            "path": res['path'],
            "expanded": None,
        }

    n_plots = len(results)
    if figsize is None:
        figsize = (7 * n_plots, 7)

    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    if n_plots == 1:
        axes = [axes]

    default_node_color = "#aed6f1"

    for ax, (alg_key, info) in zip(axes, results.items()):
        path = info["path"]
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if path else []
        path_set = set(path)

        node_colors = []
        for node in graph.nodes():
            if node == source:
                node_colors.append(_C_SOURCE)
            elif node == target:
                node_colors.append(_C_TARGET)
            elif node in path_set:
                node_colors.append(_C_PATH)
            else:
                node_colors.append(default_node_color)

        nx.draw_networkx_nodes(graph, pos, node_color=node_colors,
                               node_size=node_size, ax=ax)
        nx.draw_networkx_labels(graph, pos, ax=ax, font_size=8)
        nx.draw_networkx_edges(graph, pos, edge_color="lightgray", width=1.0, ax=ax,
                               arrows=isinstance(graph, nx.DiGraph))
        if path_edges:
            nx.draw_networkx_edges(graph, pos, edgelist=path_edges,
                                   edge_color=_C_PATH, width=3.0, ax=ax,
                                   arrows=isinstance(graph, nx.DiGraph))

        edge_labels = nx.get_edge_attributes(graph, 'weight')
        if edge_labels:
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax,
                                         font_size=7)

        subtitle = f"d = {info['distance']:.4g}"
        if info["expanded"] is not None:
            subtitle += f"  |  expanded: {info['expanded']}"
        ax.set_title(f"{info['label']}\n{subtitle}", fontsize=12, fontweight="bold")
        ax.axis("off")

    fig.suptitle(
        f"Shortest Path Comparison: {source} → {target}",
        fontsize=15, fontweight="bold", y=1.02
    )
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _trace_path(
    predecessors: Dict[Any, Optional[Any]],
    source: Any,
    target: Any,
) -> List[Any]:
    """Reconstruct a path from a Bellman-Ford predecessor map."""
    path: List[Any] = []
    current: Optional[Any] = target
    visited: Set[Any] = set()
    while current is not None and current not in visited:
        path.append(current)
        visited.add(current)
        if current == source:
            break
        current = predecessors.get(current)
    path.reverse()
    return path if path and path[0] == source else []
