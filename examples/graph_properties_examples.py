"""
Graph Properties Examples — Tarjan SCC & Topological Sort
==========================================================

Demo 1 : Tarjan SCC on a directed graph
Demo 2 : Topological sort (DFS and Kahn methods)
Demo 3 : NotDAGError on a cyclic graph
Demo 4 : Visualizations
"""

import networkx as nx
import logarithma as lg
from logarithma.algorithms.exceptions import NotDAGError

# ---------------------------------------------------------------------------
# Demo 1 — Tarjan SCC
# ---------------------------------------------------------------------------
print("=== Demo 1: Tarjan SCC ===")
G = nx.DiGraph()
G.add_edges_from([
    (0, 1), (1, 2), (2, 0),   # SCC {0,1,2}
    (1, 3),                    # bridge
    (3, 4), (4, 5), (5, 4),   # SCC {4,5}
])
sccs = lg.tarjan_scc(G)
for i, scc in enumerate(sccs):
    print(f"  SCC {i+1}: {sorted(scc)}")

# ---------------------------------------------------------------------------
# Demo 2 — Topological sort
# ---------------------------------------------------------------------------
print("\n=== Demo 2: Topological Sort ===")
DAG = nx.DiGraph()
DAG.add_edges_from([
    ('read_data', 'clean_data'),
    ('read_data', 'validate'),
    ('clean_data', 'train_model'),
    ('validate', 'train_model'),
    ('train_model', 'evaluate'),
])

order_dfs = lg.topological_sort(DAG, method='dfs')
order_kahn = lg.topological_sort(DAG, method='kahn')
print(f"DFS  order : {order_dfs}")
print(f"Kahn order : {order_kahn}")

# ---------------------------------------------------------------------------
# Demo 3 — Cycle detection
# ---------------------------------------------------------------------------
print("\n=== Demo 3: Cyclic graph raises NotDAGError ===")
CG = nx.DiGraph()
CG.add_edges_from([(1, 2), (2, 3), (3, 1)])
try:
    lg.topological_sort(CG)
except NotDAGError as e:
    print(f"Caught NotDAGError: {e}")
    if e.cycle:
        print(f"  Cycle path: {e.cycle}")

# ---------------------------------------------------------------------------
# Demo 4 — Visualizations
# ---------------------------------------------------------------------------
try:
    from logarithma.visualization import plot_scc, plot_topological_order
    import matplotlib.pyplot as plt

    fig1 = plot_scc(G, show_condensation=True)
    fig1.savefig('scc_graph.png', dpi=100, bbox_inches='tight')
    print("\nSaved: scc_graph.png")

    fig2 = plot_topological_order(DAG)
    fig2.savefig('topological_order.png', dpi=100, bbox_inches='tight')
    print("Saved: topological_order.png")

    plt.close('all')
except ImportError:
    print("\n(matplotlib not available — skipping visualization demos)")
