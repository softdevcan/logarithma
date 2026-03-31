"""
Network Flow Examples — Edmonds-Karp Max Flow
=============================================

Demo 1 : Basic max flow on a classic 6-node graph
Demo 2 : Flow conservation check
Demo 3 : Visualization of the flow network
"""

import networkx as nx
import logarithma as lg

# ---------------------------------------------------------------------------
# Demo graph (6-node flow network)
# ---------------------------------------------------------------------------
G = nx.DiGraph()
G.add_edge('s', 'o', capacity=3)
G.add_edge('s', 'p', capacity=3)
G.add_edge('o', 'p', capacity=2)
G.add_edge('o', 'q', capacity=3)
G.add_edge('p', 'r', capacity=2)
G.add_edge('q', 'r', capacity=4)
G.add_edge('q', 't', capacity=2)
G.add_edge('r', 't', capacity=3)

# ---------------------------------------------------------------------------
# Demo 1 — Basic usage
# ---------------------------------------------------------------------------
print("=== Demo 1: Max Flow ===")
result = lg.max_flow(G, source='s', sink='t')
print(f"Max flow value : {result['flow_value']}")
print("Flow per edge  :")
for u, v_dict in result['flow_dict'].items():
    for v, f in v_dict.items():
        if f > 0:
            cap = G[u][v]['capacity']
            print(f"  {u} → {v} : {f:.0f}/{cap}")

# ---------------------------------------------------------------------------
# Demo 2 — Conservation check
# ---------------------------------------------------------------------------
print("\n=== Demo 2: Flow conservation ===")
flow_dict = result['flow_dict']
for node in G.nodes():
    if node in ('s', 't'):
        continue
    inflow = sum(flow_dict.get(pred, {}).get(node, 0) for pred in G.predecessors(node))
    outflow = sum(flow_dict.get(node, {}).get(succ, 0) for succ in G.successors(node))
    ok = abs(inflow - outflow) < 1e-9
    print(f"  {node}: inflow={inflow:.1f}  outflow={outflow:.1f}  conserved={ok}")

# ---------------------------------------------------------------------------
# Demo 3 — Visualization (requires matplotlib)
# ---------------------------------------------------------------------------
try:
    from logarithma.visualization import plot_flow_network, plot_flow_paths
    import matplotlib.pyplot as plt

    fig1 = plot_flow_network(G, flow_result=result, source='s', sink='t')
    fig1.savefig('flow_network.png', dpi=100, bbox_inches='tight')
    print("\nSaved: flow_network.png")

    fig2 = plot_flow_paths(G, flow_result=result, source='s', sink='t')
    fig2.savefig('flow_paths.png', dpi=100, bbox_inches='tight')
    print("Saved: flow_paths.png")

    plt.close('all')
except ImportError:
    print("\n(matplotlib not available — skipping visualization demos)")
