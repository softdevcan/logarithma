"""
Dijkstra Algorithm - Basic Introduction
========================================

This example demonstrates basic usage of Dijkstra's shortest path algorithm.
"""

import logarithma as lg
import networkx as nx


def example_1_basic_dijkstra():
    """Example 1: Basic shortest path calculation"""
    print("=" * 60)
    print("Example 1: Basic Dijkstra")
    print("=" * 60)
    
    # Create a simple weighted graph
    G = nx.Graph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('B', 'D', weight=5)
    G.add_edge('C', 'D', weight=8)
    G.add_edge('C', 'E', weight=10)
    G.add_edge('D', 'E', weight=2)
    
    # Find shortest distances from A
    distances = lg.dijkstra(G, 'A')
    
    print(f"\nShortest distances from 'A':")
    for node, dist in sorted(distances.items()):
        print(f"  {node}: {dist}")
    
    print("\n[+] A to E: A -> C (2) -> B (3) -> D (8) -> E (10)")


def example_2_with_path():
    """Example 2: Get shortest path, not just distance"""
    print("\n" + "=" * 60)
    print("Example 2: Dijkstra with Path Reconstruction")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edge('A', 'B', weight=4)
    G.add_edge('A', 'C', weight=2)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('B', 'D', weight=5)
    G.add_edge('C', 'D', weight=8)
    
    # Get both distance and path
    result = lg.dijkstra_with_path(G, 'A', 'D')
    
    distance = result['distances']['D']
    path = result['paths']['D']
    
    print(f"\nShortest path from A to D:")
    print(f"  Distance: {distance}")
    print(f"  Path: {' -> '.join(path)}")


def example_3_directed_graph():
    """Example 3: Dijkstra on directed graphs"""
    print("\n" + "=" * 60)
    print("Example 3: Directed Graph")
    print("=" * 60)
    
    # Create directed graph
    DG = nx.DiGraph()
    DG.add_edge('A', 'B', weight=1)
    DG.add_edge('B', 'C', weight=2)
    DG.add_edge('A', 'C', weight=5)
    DG.add_edge('C', 'D', weight=1)
    # Note: No edge from D back to A
    
    distances = lg.dijkstra(DG, 'A')
    
    print(f"\nDirected graph - distances from 'A':")
    for node, dist in sorted(distances.items()):
        print(f"  {node}: {dist}")
    
    print("\n[+] In directed graphs, edges only work one way!")


def example_4_real_world_scenario():
    """Example 4: Real-world scenario - City routing"""
    print("\n" + "=" * 60)
    print("Example 4: City Routing Scenario")
    print("=" * 60)
    
    # City road network
    cities = nx.Graph()
    cities.add_edge('Istanbul', 'Ankara', weight=450)
    cities.add_edge('Istanbul', 'Izmir', weight=340)
    cities.add_edge('Ankara', 'Izmir', weight=580)
    cities.add_edge('Ankara', 'Antalya', weight=480)
    cities.add_edge('Izmir', 'Antalya', weight=420)
    
    # Find shortest route from Istanbul to Antalya
    result = lg.dijkstra_with_path(cities, 'Istanbul', 'Antalya')
    
    distance = result['distances']['Antalya']
    path = result['paths']['Antalya']
    
    print(f"\nBest route from Istanbul to Antalya:")
    print(f"  Route: {' -> '.join(path)}")
    print(f"  Total distance: {distance} km")


def example_5_error_handling():
    """Example 5: Error handling"""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edge('A', 'B', weight=5)
    
    # Try invalid source
    try:
        lg.dijkstra(G, 'Z')
    except ValueError as e:
        print(f"\n[-] Error caught: {e}")
    
    # Try negative weight
    G.add_edge('B', 'C', weight=-1)
    try:
        lg.dijkstra(G, 'A')
    except ValueError as e:
        print(f"[-] Error caught: {e}")
    
    print("\n[+] Logarithma provides helpful error messages!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LOGARITHMA - Dijkstra Algorithm Examples")
    print("=" * 60)
    
    example_1_basic_dijkstra()
    example_2_with_path()
    example_3_directed_graph()
    example_4_real_world_scenario()
    example_5_error_handling()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
