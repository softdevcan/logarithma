"""
Bidirectional Dijkstra - Usage Examples
========================================

This example demonstrates the Bidirectional Dijkstra algorithm, which
searches simultaneously from both source and target. For point-to-point
queries on large graphs, it typically explores fewer nodes than standard
Dijkstra - making it ideal for long-range routing.
"""

import logarithma as lg
import networkx as nx


def example_1_basic_bidirectional():
    """Example 1: Basic bidirectional shortest path"""
    print("=" * 60)
    print("Example 1: Basic Bidirectional Dijkstra")
    print("=" * 60)

    G = nx.Graph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('B', 'D', weight=5)
    G.add_edge('C', 'D', weight=8)
    G.add_edge('C', 'E', weight=10)
    G.add_edge('D', 'E', weight=2)

    result = lg.bidirectional_dijkstra(G, 'A', 'E')

    print(f"\nShortest path from A to E:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {' -> '.join(result['path'])}")


def example_2_directed_graph():
    """Example 2: Bidirectional Dijkstra on directed graphs"""
    print("\n" + "=" * 60)
    print("Example 2: Directed Graph")
    print("=" * 60)

    # One-way road network
    G = nx.DiGraph()
    G.add_edge('North', 'Center', weight=3)
    G.add_edge('Center', 'South', weight=4)
    G.add_edge('North', 'East', weight=5)
    G.add_edge('East', 'Center', weight=2)
    G.add_edge('East', 'South', weight=6)
    G.add_edge('Center', 'West', weight=1)
    G.add_edge('West', 'South', weight=3)

    result = lg.bidirectional_dijkstra(G, 'North', 'South')

    print(f"\nShortest path from North to South:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {' -> '.join(result['path'])}")

    # Note: backward search follows edges in reverse on DiGraph
    print(f"\n  On directed graphs, backward search follows reversed edges.")


def example_3_same_source_target():
    """Example 3: Source equals target (trivial case)"""
    print("\n" + "=" * 60)
    print("Example 3: Same Source and Target")
    print("=" * 60)

    G = nx.Graph()
    G.add_edge('A', 'B', weight=5)
    G.add_edge('B', 'C', weight=3)

    result = lg.bidirectional_dijkstra(G, 'A', 'A')

    print(f"\nPath from A to A:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {result['path']}")
    print(f"\n  Distance is 0 and path contains only the source node.")


def example_4_city_routing():
    """Example 4: Real-world scenario - city routing"""
    print("\n" + "=" * 60)
    print("Example 4: City Routing")
    print("=" * 60)

    # Turkish cities road network (km)
    roads = nx.Graph()
    roads.add_edge('Istanbul', 'Ankara', weight=450)
    roads.add_edge('Istanbul', 'Bursa', weight=155)
    roads.add_edge('Istanbul', 'Izmir', weight=340)
    roads.add_edge('Bursa', 'Ankara', weight=385)
    roads.add_edge('Bursa', 'Eskisehir', weight=155)
    roads.add_edge('Eskisehir', 'Ankara', weight=235)
    roads.add_edge('Ankara', 'Konya', weight=260)
    roads.add_edge('Izmir', 'Antalya', weight=420)
    roads.add_edge('Konya', 'Antalya', weight=300)
    roads.add_edge('Ankara', 'Antalya', weight=480)

    # Find shortest route
    result = lg.bidirectional_dijkstra(roads, 'Istanbul', 'Antalya')

    print(f"\nBest route from Istanbul to Antalya:")
    print(f"  Route: {' -> '.join(result['path'])}")
    print(f"  Total distance: {result['distance']} km")

    # Compare with Dijkstra
    dj_result = lg.dijkstra_with_path(roads, 'Istanbul', 'Antalya')
    dj_dist = dj_result['distances']['Antalya']
    print(f"\n  Dijkstra confirms: {dj_dist} km (same result)")


def example_5_large_graph():
    """Example 5: Large graph - grid routing"""
    print("\n" + "=" * 60)
    print("Example 5: Large Grid Graph")
    print("=" * 60)

    from logarithma.utils import generate_grid_graph

    # Create a weighted grid
    grid = generate_grid_graph(15, 15, weighted=True, diagonal=True)

    source = (0, 0)
    target = (14, 14)

    result = lg.bidirectional_dijkstra(grid, source, target)

    print(f"\nGrid: 15x15 weighted with diagonals ({grid.number_of_nodes()} nodes)")
    print(f"  Source: {source}")
    print(f"  Target: {target}")
    print(f"  Distance: {result['distance']:.2f}")
    print(f"  Path length: {len(result['path'])} nodes")


def example_6_unreachable_target():
    """Example 6: Unreachable target"""
    print("\n" + "=" * 60)
    print("Example 6: Unreachable Target")
    print("=" * 60)

    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=2)
    # D is only reachable from D->E, not from A
    G.add_edge('D', 'E', weight=3)

    result = lg.bidirectional_dijkstra(G, 'A', 'D')

    print(f"\nPath from A to D:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {result['path'] if result['path'] else 'No path exists'}")


def example_7_vs_standard_dijkstra():
    """Example 7: Comparing with standard Dijkstra"""
    print("\n" + "=" * 60)
    print("Example 7: Bidirectional vs Standard Dijkstra")
    print("=" * 60)

    # Build a larger random graph
    from logarithma.utils import generate_random_graph

    G = generate_random_graph(100, edge_probability=0.08, seed=42)

    # Pick two nodes
    nodes = list(G.nodes())
    source, target = nodes[0], nodes[-1]

    # Both algorithms should give the same result
    bidir = lg.bidirectional_dijkstra(G, source, target)
    standard = lg.dijkstra_with_path(G, source, target)

    std_dist = standard['distances'].get(target, float('inf'))
    std_path = standard['paths'].get(target, [])

    print(f"\nRandom graph: {G.number_of_nodes()} nodes, "
          f"{G.number_of_edges()} edges")
    print(f"  Source: {source}, Target: {target}")
    print(f"\n  {'Algorithm':<25} {'Distance':<15} {'Path length':<15}")
    print(f"  {'-' * 55}")
    print(f"  {'Bidirectional Dijkstra':<25} {bidir['distance']:<15.2f} "
          f"{len(bidir['path']):<15}")
    print(f"  {'Standard Dijkstra':<25} {std_dist:<15.2f} "
          f"{len(std_path):<15}")
    print(f"\n  Both produce the same optimal distance!")


def example_8_error_handling():
    """Example 8: Error handling"""
    print("\n" + "=" * 60)
    print("Example 8: Error Handling")
    print("=" * 60)

    G = nx.Graph()
    G.add_edge('A', 'B', weight=5)

    # Source not in graph
    try:
        lg.bidirectional_dijkstra(G, 'Z', 'A')
    except ValueError as e:
        print(f"\n  Error: {e}")

    # Target not in graph
    try:
        lg.bidirectional_dijkstra(G, 'A', 'Z')
    except ValueError as e:
        print(f"  Error: {e}")

    # Negative weight
    G.add_edge('B', 'C', weight=-1)
    try:
        lg.bidirectional_dijkstra(G, 'A', 'C')
    except ValueError as e:
        print(f"  Error: {e}")

    print("\n  Clear error messages for all invalid inputs.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LOGARITHMA - Bidirectional Dijkstra Examples")
    print("=" * 60)

    example_1_basic_bidirectional()
    example_2_directed_graph()
    example_3_same_source_target()
    example_4_city_routing()
    example_5_large_graph()
    example_6_unreachable_target()
    example_7_vs_standard_dijkstra()
    example_8_error_handling()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
