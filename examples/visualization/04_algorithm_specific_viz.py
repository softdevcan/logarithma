"""
04_algorithm_specific_viz.py
============================

Demonstrates the algorithm-specific visualization functions added in v0.3.x:
  - plot_astar_search              — A* expanded-node map
  - plot_bellman_ford_result       — Bellman-Ford distances + negative edges
  - plot_negative_cycle            — Negative cycle highlight
  - plot_bidirectional_search      — Two-frontier Bidirectional Dijkstra
  - plot_shortest_path_comparison  — Side-by-side algorithm comparison
  - plot_dfs_tree                  — DFS tree with edge classification

Run:
    python examples/visualization/04_algorithm_specific_viz.py

Requirements:
    pip install logarithma[viz]   # or: pip install matplotlib
"""

import networkx as nx

from logarithma.algorithms.shortest_path.bellman_ford import bellman_ford
from logarithma.algorithms.exceptions import NegativeCycleError
from logarithma.algorithms.shortest_path.astar import manhattan_heuristic
from logarithma.visualization import (
    plot_astar_search,
    plot_bellman_ford_result,
    plot_negative_cycle,
    plot_bidirectional_search,
    plot_shortest_path_comparison,
    plot_dfs_tree,
)


# ---------------------------------------------------------------------------
# Helper: build a small grid graph with positions
# ---------------------------------------------------------------------------

def _grid_graph(rows: int, cols: int) -> tuple:
    """Return a weighted grid DiGraph and a pos dict keyed by (row, col)."""
    G = nx.grid_2d_graph(rows, cols, create_using=nx.Graph())
    for u, v in G.edges():
        G[u][v]['weight'] = 1
    pos = {(r, c): (c, -r) for r in range(rows) for c in range(cols)}
    return G, pos


# ---------------------------------------------------------------------------
# 1. A* search visualization on a 5×5 grid
# ---------------------------------------------------------------------------

def demo_astar():
    print("1/6  A* search visualization …")
    G, pos = _grid_graph(5, 5)
    source, target = (0, 0), (4, 4)
    h = manhattan_heuristic(pos)
    plot_astar_search(
        G, source, target,
        heuristic=h,
        pos=pos,
        show_heuristic=True,
        title="A* Search on 5×5 Grid (Manhattan heuristic)",
    )


# ---------------------------------------------------------------------------
# 2. Bellman-Ford result with a negative edge
# ---------------------------------------------------------------------------

def demo_bellman_ford():
    print("2/6  Bellman-Ford result visualization …")
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=-3)
    G.add_edge('C', 'D', weight=1)
    G.add_edge('B', 'D', weight=5)

    result = bellman_ford(G, 'A')
    plot_bellman_ford_result(
        G, 'A',
        distances=result['distances'],
        predecessors=result['predecessors'],
        highlight_targets=['D'],
        layout='spring',
        title="Bellman-Ford: graph with a negative edge",
    )


# ---------------------------------------------------------------------------
# 3. Negative cycle visualization
# ---------------------------------------------------------------------------

def demo_negative_cycle():
    print("3/6  Negative cycle visualization …")
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=-3)
    G.add_edge('C', 'A', weight=1)   # total cycle weight = -1
    G.add_edge('A', 'D', weight=2)
    G.add_edge('C', 'D', weight=2)

    try:
        bellman_ford(G, 'A')
    except NegativeCycleError as exc:
        plot_negative_cycle(
            G, exc.cycle,
            layout='circular',
            title="Negative Cycle Detected by Bellman-Ford",
        )


# ---------------------------------------------------------------------------
# 4. Bidirectional Dijkstra search visualization
# ---------------------------------------------------------------------------

def demo_bidirectional():
    print("4/6  Bidirectional Dijkstra visualization …")
    G = nx.path_graph(8, create_using=nx.Graph())
    # Add a few shortcuts
    G.add_edge(0, 4, weight=3)
    G.add_edge(2, 6, weight=2)
    for u, v in G.edges():
        if 'weight' not in G[u][v]:
            G[u][v]['weight'] = 1

    plot_bidirectional_search(
        G, source=0, target=7,
        layout='spring',
        title="Bidirectional Dijkstra: node 0 → node 7",
    )


# ---------------------------------------------------------------------------
# 5. Side-by-side comparison: Dijkstra vs A* vs Bidirectional Dijkstra
# ---------------------------------------------------------------------------

def demo_comparison():
    print("5/6  Shortest path comparison (all three algorithms) …")
    G = nx.karate_club_graph()
    for u, v in G.edges():
        G[u][v]['weight'] = 1

    plot_shortest_path_comparison(
        G, source=0, target=33,
        algorithms=['dijkstra', 'astar', 'bidirectional'],
        layout='spring',
    )


# ---------------------------------------------------------------------------
# 6. DFS tree visualization — directed graph with a back edge (cycle)
# ---------------------------------------------------------------------------

def demo_dfs_tree():
    print("6/6  DFS tree visualization …")
    G = nx.DiGraph()
    G.add_edges_from([
        ('A', 'B'), ('A', 'C'),
        ('B', 'D'), ('D', 'B'),   # back edge D→B (cycle)
        ('C', 'D'), ('C', 'E'),
        ('E', 'A'),               # back edge E→A (cycle)
    ])
    plot_dfs_tree(
        G, source='A',
        layout='spring',
        show_discovery_finish=True,
        show_depth=True,
        title="DFS Tree — directed graph with back edges",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_astar()
    demo_bellman_ford()
    demo_negative_cycle()
    demo_bidirectional()
    demo_comparison()
    demo_dfs_tree()
    print("All demos completed.")
