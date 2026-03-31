"""
MST Examples — Kruskal & Prim
==============================

Demo 1 : Kruskal basic usage
Demo 2 : Prim basic usage + different start nodes
Demo 3 : Kruskal vs Prim comparison (total weight must match)
Demo 4 : Step-by-step Kruskal visualization
"""

import networkx as nx
import logarithma as lg

# ---------------------------------------------------------------------------
# Demo graph
# ---------------------------------------------------------------------------
G = nx.Graph()
edges = [
    ('A', 'B', 4), ('A', 'C', 2), ('B', 'C', 1),
    ('B', 'D', 5), ('C', 'D', 8), ('C', 'E', 10), ('D', 'E', 2),
]
for u, v, w in edges:
    G.add_edge(u, v, weight=w)

# ---------------------------------------------------------------------------
# Demo 1 — Kruskal
# ---------------------------------------------------------------------------
print("=== Demo 1: Kruskal MST ===")
result = lg.kruskal_mst(G)
print(f"MST edges   : {result['mst_edges']}")
print(f"Total weight: {result['total_weight']}")
print(f"Components  : {result['num_components']}")

# ---------------------------------------------------------------------------
# Demo 2 — Prim
# ---------------------------------------------------------------------------
print("\n=== Demo 2: Prim MST ===")
for start in ['A', 'D']:
    r = lg.prim_mst(G, start=start)
    print(f"  start={start}  weight={r['total_weight']}")

# ---------------------------------------------------------------------------
# Demo 3 — Comparison
# ---------------------------------------------------------------------------
print("\n=== Demo 3: Kruskal == Prim? ===")
k = lg.kruskal_mst(G)
p = lg.prim_mst(G)
print(f"Kruskal weight : {k['total_weight']}")
print(f"Prim weight    : {p['total_weight']}")
print(f"Equal          : {abs(k['total_weight'] - p['total_weight']) < 1e-9}")

# ---------------------------------------------------------------------------
# Demo 4 — Visualization (requires matplotlib)
# ---------------------------------------------------------------------------
try:
    from logarithma.visualization import plot_mst, plot_mst_comparison, plot_kruskal_steps
    import matplotlib.pyplot as plt

    fig1 = plot_mst(G, algorithm='kruskal', show_weights=True)
    fig1.savefig('mst_kruskal.png', dpi=100, bbox_inches='tight')
    print("\nSaved: mst_kruskal.png")

    fig2 = plot_mst_comparison(G)
    fig2.savefig('mst_comparison.png', dpi=100, bbox_inches='tight')
    print("Saved: mst_comparison.png")

    fig3 = plot_kruskal_steps(G)
    fig3.savefig('mst_kruskal_steps.png', dpi=100, bbox_inches='tight')
    print("Saved: mst_kruskal_steps.png")

    plt.close('all')
except ImportError:
    print("\n(matplotlib not available — skipping visualization demos)")
