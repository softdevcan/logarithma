"""
A* (A-Star) Algorithm - Usage Examples
=======================================

This example demonstrates the A* shortest path algorithm with various
heuristics and real-world scenarios.

A* extends Dijkstra by using a heuristic function to guide the search
toward the goal, making it significantly faster for point-to-point queries.
"""

import logarithma as lg
import networkx as nx


def example_1_basic_astar():
    """Example 1: Basic A* with Euclidean heuristic"""
    print("=" * 60)
    print("Example 1: Basic A* with Euclidean Heuristic")
    print("=" * 60)

    # Create a graph with 2D coordinates
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=1)
    G.add_edge('A', 'C', weight=2.5)
    G.add_edge('C', 'D', weight=1)
    G.add_edge('B', 'D', weight=3)

    # Node positions for the heuristic
    pos = {
        'A': (0, 0),
        'B': (1, 0),
        'C': (1, 1),
        'D': (2, 1),
    }

    # Create the Euclidean heuristic from positions
    h = lg.euclidean_heuristic(pos)

    # Find shortest path from A to D
    result = lg.astar(G, 'A', 'D', heuristic=h)

    print(f"\nShortest path from A to D:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {' -> '.join(result['path'])}")


def example_2_grid_with_manhattan():
    """Example 2: Grid pathfinding with Manhattan heuristic"""
    print("\n" + "=" * 60)
    print("Example 2: Grid Pathfinding (Manhattan Heuristic)")
    print("=" * 60)

    # Create a 6x6 grid graph
    from logarithma.utils import generate_grid_graph
    grid = generate_grid_graph(6, 6, weighted=False, diagonal=False)

    # Remove edges to create obstacles
    obstacles = [
        ((2, 1), (2, 2)), ((2, 2), (2, 3)), ((2, 3), (2, 4)),
        ((2, 1), (3, 1)), ((2, 2), (3, 2)),
    ]
    for wall in obstacles:
        if grid.has_edge(*wall):
            grid.remove_edge(*wall)

    # Node positions are the grid coordinates themselves
    pos = {node: node for node in grid.nodes()}

    # Manhattan heuristic is ideal for grid movement without diagonals
    h = lg.manhattan_heuristic(pos)

    start = (0, 0)
    end = (5, 5)

    result = lg.astar(grid, start, end, heuristic=h)

    print(f"\nGrid path from {start} to {end}:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path length: {len(result['path'])} nodes")
    print(f"  Path: {result['path']}")


def example_3_astar_vs_dijkstra():
    """Example 3: A* vs Dijkstra efficiency comparison"""
    print("\n" + "=" * 60)
    print("Example 3: A* vs Dijkstra Efficiency")
    print("=" * 60)

    # Create a weighted grid - random weights let A* skip irrelevant nodes
    from logarithma.utils import generate_grid_graph
    grid = generate_grid_graph(20, 20, weighted=True, diagonal=True)

    pos = {node: node for node in grid.nodes()}
    h = lg.euclidean_heuristic(pos)

    source = (0, 0)
    target = (19, 19)

    # A* with stats to measure efficiency
    result_astar = lg.astar_with_stats(grid, source, target, heuristic=h)

    # A* with zero heuristic = Dijkstra behavior
    result_dijkstra = lg.astar_with_stats(grid, source, target,
                                          heuristic=lg.zero_heuristic)

    total_nodes = grid.number_of_nodes()

    print(f"\nGraph: 20x20 weighted grid with diagonals ({total_nodes} nodes)")
    print(f"Query: {source} -> {target}")
    print(f"\n  {'Metric':<25} {'A* (Euclidean)':<18} {'Dijkstra':<18}")
    print(f"  {'-' * 61}")
    print(f"  {'Distance':<25} {result_astar['distance']:<18.2f} "
          f"{result_dijkstra['distance']:<18.2f}")
    print(f"  {'Nodes expanded':<25} {result_astar['nodes_expanded']:<18} "
          f"{result_dijkstra['nodes_expanded']:<18}")
    print(f"  {'Nodes generated':<25} {result_astar['nodes_generated']:<18} "
          f"{result_dijkstra['nodes_generated']:<18}")
    print(f"  {'Expansion ratio':<25} "
          f"{result_astar['nodes_expanded'] / total_nodes:.1%}{'':<12} "
          f"{result_dijkstra['nodes_expanded'] / total_nodes:.1%}")

    saved = result_dijkstra['nodes_expanded'] - result_astar['nodes_expanded']
    print(f"\n  A* expanded {saved} fewer nodes than Dijkstra!")


def example_4_directed_graph():
    """Example 4: A* on a directed graph"""
    print("\n" + "=" * 60)
    print("Example 4: A* on Directed Graph")
    print("=" * 60)

    # Road network with one-way streets
    G = nx.DiGraph()
    G.add_edge('Home', 'Market', weight=3)
    G.add_edge('Home', 'Park', weight=2)
    G.add_edge('Market', 'School', weight=4)
    G.add_edge('Park', 'School', weight=5)
    G.add_edge('Park', 'Library', weight=3)
    G.add_edge('School', 'Library', weight=1)
    G.add_edge('Library', 'Office', weight=2)
    G.add_edge('School', 'Office', weight=6)

    # Positions for heuristic
    pos = {
        'Home': (0, 0),
        'Market': (2, 1),
        'Park': (1, -1),
        'School': (3, 0),
        'Library': (4, -1),
        'Office': (5, 0),
    }

    h = lg.euclidean_heuristic(pos)

    result = lg.astar(G, 'Home', 'Office', heuristic=h)

    print(f"\nShortest route from Home to Office (one-way streets):")
    print(f"  Distance: {result['distance']}")
    print(f"  Route: {' -> '.join(result['path'])}")


def example_5_unreachable_target():
    """Example 5: Handling unreachable targets"""
    print("\n" + "=" * 60)
    print("Example 5: Unreachable Target")
    print("=" * 60)

    # Disconnected directed graph
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=1)
    G.add_edge('B', 'C', weight=2)
    # D is isolated - no path from A to D
    G.add_edge('D', 'E', weight=1)

    result = lg.astar(G, 'A', 'D')

    print(f"\nPath from A to D:")
    print(f"  Distance: {result['distance']}")
    print(f"  Path: {result['path'] if result['path'] else 'No path exists'}")

    # Reachable target for comparison
    result2 = lg.astar(G, 'A', 'C')

    print(f"\nPath from A to C:")
    print(f"  Distance: {result2['distance']}")
    print(f"  Path: {' -> '.join(result2['path'])}")


def example_6_custom_heuristic():
    """Example 6: Writing a custom heuristic"""
    print("\n" + "=" * 60)
    print("Example 6: Custom Heuristic Function")
    print("=" * 60)

    # Weighted graph representing a network with bandwidth costs
    G = nx.Graph()
    G.add_edge('Server1', 'Router1', weight=10)
    G.add_edge('Server1', 'Router2', weight=15)
    G.add_edge('Router1', 'Router2', weight=5)
    G.add_edge('Router1', 'Router3', weight=20)
    G.add_edge('Router2', 'Router3', weight=10)
    G.add_edge('Router3', 'Server2', weight=5)

    # Custom heuristic: assign a "tier" to each node (lower = closer to goal)
    # This is admissible as long as h(n) never overestimates actual distance
    tier = {
        'Server1': 3,
        'Router1': 2,
        'Router2': 2,
        'Router3': 1,
        'Server2': 0,
    }
    TIER_COST = 5  # minimum cost per tier level

    def tier_heuristic(node, target):
        """Estimate based on network tier distance."""
        return abs(tier[node] - tier[target]) * TIER_COST

    result = lg.astar(G, 'Server1', 'Server2', heuristic=tier_heuristic)

    print(f"\nNetwork path from Server1 to Server2:")
    print(f"  Cost: {result['distance']}")
    print(f"  Path: {' -> '.join(result['path'])}")

    # Verify with stats
    stats = lg.astar_with_stats(G, 'Server1', 'Server2',
                                heuristic=tier_heuristic)
    print(f"  Nodes expanded: {stats['nodes_expanded']} / {G.number_of_nodes()}")


def example_7_error_handling():
    """Example 7: Error handling"""
    print("\n" + "=" * 60)
    print("Example 7: Error Handling")
    print("=" * 60)

    G = nx.Graph()
    G.add_edge('A', 'B', weight=5)

    # Source not in graph
    try:
        lg.astar(G, 'Z', 'A')
    except ValueError as e:
        print(f"\n  Error: {e}")

    # Target not in graph
    try:
        lg.astar(G, 'A', 'Z')
    except ValueError as e:
        print(f"  Error: {e}")

    # Negative weight
    G.add_edge('B', 'C', weight=-1)
    try:
        lg.astar(G, 'A', 'C')
    except ValueError as e:
        print(f"  Error: {str(e).encode('ascii', 'replace').decode()}")

    print("\n  A* provides clear error messages for invalid inputs.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LOGARITHMA - A* (A-Star) Algorithm Examples")
    print("=" * 60)

    example_1_basic_astar()
    example_2_grid_with_manhattan()
    example_3_astar_vs_dijkstra()
    example_4_directed_graph()
    example_5_unreachable_target()
    example_6_custom_heuristic()
    example_7_error_handling()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
