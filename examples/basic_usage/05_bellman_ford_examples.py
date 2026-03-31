"""
Bellman-Ford Algorithm - Usage Examples
========================================

This example demonstrates the Bellman-Ford shortest path algorithm,
which supports negative edge weights and detects negative cycles.

Unlike Dijkstra, Bellman-Ford can handle graphs with negative-weight
edges, making it essential for financial modeling, network routing,
and arbitrage detection.
"""

import logarithma as lg
import networkx as nx
from logarithma import NegativeCycleError


def example_1_basic_bellman_ford():
    """Example 1: Basic shortest path with positive weights"""
    print("=" * 60)
    print("Example 1: Basic Bellman-Ford")
    print("=" * 60)

    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'D', weight=3)
    G.add_edge('C', 'B', weight=1)
    G.add_edge('C', 'D', weight=7)
    G.add_edge('D', 'E', weight=1)

    result = lg.bellman_ford(G, 'A')

    print(f"\nShortest distances from 'A':")
    for node, dist in sorted(result['distances'].items()):
        print(f"  {node}: {dist}")


def example_2_negative_weights():
    """Example 2: Negative edge weights (no cycle)"""
    print("\n" + "=" * 60)
    print("Example 2: Negative Edge Weights")
    print("=" * 60)

    # Financial model: costs can be negative (representing gains)
    G = nx.DiGraph()
    G.add_edge('Start', 'A', weight=5)
    G.add_edge('Start', 'B', weight=8)
    G.add_edge('A', 'B', weight=-3)     # shortcut with a "gain"
    G.add_edge('A', 'C', weight=6)
    G.add_edge('B', 'C', weight=2)
    G.add_edge('C', 'End', weight=1)

    result = lg.bellman_ford(G, 'Start')

    print(f"\nShortest distances from 'Start':")
    for node, dist in sorted(result['distances'].items()):
        print(f"  {node}: {dist}")

    # Note: Start -> A (5) -> B (5-3=2) is cheaper than Start -> B (8)
    print(f"\n  Direct Start->B costs 8")
    print(f"  But Start->A->B costs only {result['distances']['B']}")
    print(f"  Negative edge A->B creates a shortcut!")


def example_3_path_reconstruction():
    """Example 3: Path reconstruction with bellman_ford_path"""
    print("\n" + "=" * 60)
    print("Example 3: Path Reconstruction")
    print("=" * 60)

    G = nx.DiGraph()
    G.add_edge('S', 'A', weight=10)
    G.add_edge('S', 'B', weight=6)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'A', weight=-4)    # negative edge
    G.add_edge('B', 'C', weight=5)
    G.add_edge('C', 'D', weight=1)

    result = lg.bellman_ford_path(G, 'S', 'D')

    print(f"\nShortest path from S to D:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {' -> '.join(result['path'])}")
    print(f"\n  S->B (6) -> B->A (-4=2) -> A->C (2=4) -> C->D (1=5)")


def example_4_negative_cycle_detection():
    """Example 4: Detecting negative cycles"""
    print("\n" + "=" * 60)
    print("Example 4: Negative Cycle Detection")
    print("=" * 60)

    # Currency exchange: a negative cycle means arbitrage opportunity
    G = nx.DiGraph()

    # Simulated exchange rates as log-costs (negative = profitable)
    G.add_edge('USD', 'EUR', weight=1)
    G.add_edge('EUR', 'GBP', weight=-3)
    G.add_edge('GBP', 'USD', weight=1)   # cycle: 1 + (-3) + 1 = -1 (profit!)

    print("\n  Currency exchange graph:")
    print("  USD --(1)--> EUR --(-3)--> GBP --(1)--> USD")
    print("  Cycle total weight: 1 + (-3) + 1 = -1 (negative!)")

    try:
        lg.bellman_ford(G, 'USD')
    except NegativeCycleError as e:
        print(f"\n  Detected: {e}")
        print(f"  Cycle nodes: {e.cycle}")
        print(f"\n  This means infinite profit is possible (arbitrage)!")


def example_5_no_negative_cycle():
    """Example 5: Negative weights without forming a cycle"""
    print("\n" + "=" * 60)
    print("Example 5: Safe Negative Weights (No Cycle)")
    print("=" * 60)

    # DAG with negative weights - no cycles possible
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=3)
    G.add_edge('A', 'C', weight=5)
    G.add_edge('B', 'C', weight=-2)
    G.add_edge('B', 'D', weight=6)
    G.add_edge('C', 'D', weight=-1)

    result = lg.bellman_ford(G, 'A')

    print(f"\nDAG with negative weights (safe):")
    for node, dist in sorted(result['distances'].items()):
        print(f"  {node}: {dist}")

    path_result = lg.bellman_ford_path(G, 'A', 'D')
    print(f"\n  Path A to D: {' -> '.join(path_result['path'])}")
    print(f"  Distance: {path_result['distance']}")


def example_6_unreachable_nodes():
    """Example 6: Handling unreachable nodes"""
    print("\n" + "=" * 60)
    print("Example 6: Unreachable Nodes")
    print("=" * 60)

    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=2)
    # D and E form a separate component
    G.add_edge('D', 'E', weight=3)

    result = lg.bellman_ford(G, 'A')

    print(f"\nDistances from 'A':")
    for node, dist in sorted(result['distances'].items()):
        status = f"{dist}" if dist != float('inf') else "unreachable"
        print(f"  {node}: {status}")

    # bellman_ford_path returns empty path for unreachable targets
    path_result = lg.bellman_ford_path(G, 'A', 'D')
    print(f"\n  Path A to D: {path_result['path'] if path_result['path'] else 'No path exists'}")
    print(f"  Distance: {path_result['distance']}")


def example_7_dijkstra_vs_bellman_ford():
    """Example 7: When to use Bellman-Ford vs Dijkstra"""
    print("\n" + "=" * 60)
    print("Example 7: Bellman-Ford vs Dijkstra")
    print("=" * 60)

    # Graph with only positive weights - both algorithms work
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'D', weight=3)
    G.add_edge('C', 'B', weight=1)
    G.add_edge('C', 'D', weight=5)

    bf_result = lg.bellman_ford(G, 'A')
    dj_result = lg.dijkstra(G, 'A')

    print(f"\nPositive-weight graph - both produce the same result:")
    print(f"\n  {'Node':<8} {'Bellman-Ford':<15} {'Dijkstra':<15}")
    print(f"  {'-' * 38}")
    for node in sorted(bf_result['distances'].keys()):
        print(f"  {node:<8} {bf_result['distances'][node]:<15} {dj_result[node]:<15}")

    print(f"\n  Use Dijkstra for:     non-negative weights (faster)")
    print(f"  Use Bellman-Ford for: negative weights or cycle detection")


def example_8_error_handling():
    """Example 8: Error handling"""
    print("\n" + "=" * 60)
    print("Example 8: Error Handling")
    print("=" * 60)

    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)

    # Source not in graph
    try:
        lg.bellman_ford(G, 'Z')
    except ValueError as e:
        print(f"\n  Error: {e}")

    # Target not in graph (bellman_ford_path)
    try:
        lg.bellman_ford_path(G, 'A', 'Z')
    except ValueError as e:
        print(f"  Error: {e}")

    # Negative cycle
    G.add_edge('B', 'C', weight=-5)
    G.add_edge('C', 'A', weight=1)
    try:
        lg.bellman_ford(G, 'A')
    except NegativeCycleError as e:
        print(f"  Error: {e}")

    print("\n  Bellman-Ford provides clear error messages!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LOGARITHMA - Bellman-Ford Algorithm Examples")
    print("=" * 60)

    example_1_basic_bellman_ford()
    example_2_negative_weights()
    example_3_path_reconstruction()
    example_4_negative_cycle_detection()
    example_5_no_negative_cycle()
    example_6_unreachable_nodes()
    example_7_dijkstra_vs_bellman_ford()
    example_8_error_handling()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
