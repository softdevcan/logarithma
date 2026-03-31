"""
BFS & DFS - Graph Traversal Examples
====================================

This example demonstrates BFS and DFS algorithms.
"""

import logarithma as lg
import networkx as nx


def example_1_bfs_basics():
    """Example 1: Basic BFS traversal"""
    print("=" * 60)
    print("Example 1: BFS - Breadth-First Search")
    print("=" * 60)
    
    # Create a simple graph
    G = nx.Graph()
    G.add_edges_from([
        ('A', 'B'), ('A', 'C'),
        ('B', 'D'), ('B', 'E'),
        ('C', 'F'), ('C', 'G')
    ])
    
    # BFS from A
    distances = lg.bfs(G, 'A')
    
    print("\nBFS distances from 'A' (level-by-level):")
    for level in range(max(distances.values()) + 1):
        nodes = [n for n, d in distances.items() if d == level]
        print(f"  Level {level}: {nodes}")


def example_2_bfs_shortest_path():
    """Example 2: BFS for shortest path in unweighted graph"""
    print("\n" + "=" * 60)
    print("Example 2: BFS Shortest Path (Unweighted)")
    print("=" * 60)
    
    # Social network
    network = nx.Graph()
    network.add_edges_from([
        ('Alice', 'Bob'), ('Alice', 'Carol'),
        ('Bob', 'David'), ('Carol', 'David'),
        ('David', 'Eve'), ('Eve', 'Frank')
    ])
    
    # Find shortest path from Alice to Frank
    result = lg.bfs_path(network, 'Alice', 'Frank')
    
    path = result['paths']['Frank']
    distance = result['distances']['Frank']
    
    print(f"\nShortest connection from Alice to Frank:")
    print(f"  Path: {' -> '.join(path)}")
    print(f"  Degrees of separation: {distance}")


def example_3_dfs_basics():
    """Example 3: Basic DFS traversal"""
    print("\n" + "=" * 60)
    print("Example 3: DFS - Depth-First Search")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edges_from([
        ('A', 'B'), ('A', 'C'),
        ('B', 'D'), ('B', 'E'),
        ('C', 'F')
    ])
    
    # DFS recursive
    visited_recursive = lg.dfs(G, 'A', mode='recursive')
    print(f"\nDFS (recursive) from 'A': {visited_recursive}")
    
    # DFS iterative
    visited_iterative = lg.dfs(G, 'A', mode='iterative')
    print(f"DFS (iterative) from 'A': {visited_iterative}")
    
    print("\n[+] Both methods explore depth-first!")


def example_4_cycle_detection():
    """Example 4: Detect cycles in graphs"""
    print("\n" + "=" * 60)
    print("Example 4: Cycle Detection")
    print("=" * 60)
    
    # Graph without cycle (tree)
    tree = nx.Graph()
    tree.add_edges_from([('A', 'B'), ('B', 'C'), ('B', 'D')])
    
    has_cycle, cycle = lg.detect_cycle(tree)
    print(f"\nTree graph:")
    print(f"  Has cycle: {has_cycle}")
    
    # Graph with cycle
    cyclic = nx.Graph()
    cyclic.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'A')])
    
    has_cycle, cycle = lg.detect_cycle(cyclic)
    print(f"\nCyclic graph:")
    print(f"  Has cycle: {has_cycle}")
    print(f"  Cycle: {cycle}")


def example_5_maze_solving():
    """Example 5: Maze solving with BFS"""
    print("\n" + "=" * 60)
    print("Example 5: Maze Solving with BFS")
    print("=" * 60)
    
    # Simple maze as grid
    from logarithma.utils import generate_grid_graph
    
    maze = generate_grid_graph(5, 5, weighted=False, diagonal=False)
    
    # Remove some edges to create walls
    walls = [((1, 1), (1, 2)), ((2, 1), (2, 2)), ((3, 1), (3, 2))]
    for wall in walls:
        if maze.has_edge(*wall):
            maze.remove_edge(*wall)
    
    # Find path from start to end
    start = (0, 0)
    end = (4, 4)
    
    result = lg.bfs_path(maze, start, end)
    
    if result['paths'][end]:
        print(f"\nMaze solved!")
        print(f"  Start: {start}")
        print(f"  End: {end}")
        print(f"  Steps: {result['distances'][end]}")
        print(f"  Path length: {len(result['paths'][end])}")
    else:
        print("\nNo path found!")


def example_6_comparison():
    """Example 6: BFS vs DFS comparison"""
    print("\n" + "=" * 60)
    print("Example 6: BFS vs DFS Comparison")
    print("=" * 60)
    
    G = nx.Graph()
    G.add_edges_from([
        (1, 2), (1, 3),
        (2, 4), (2, 5),
        (3, 6), (3, 7)
    ])
    
    # BFS - finds shortest path
    bfs_result = lg.bfs_path(G, 1, 7)
    bfs_path = bfs_result['paths'][7]
    
    # DFS - finds a path (not necessarily shortest)
    dfs_path = lg.dfs_path(G, 1, 7)
    
    print(f"\nFinding path from 1 to 7:")
    print(f"  BFS path: {bfs_path} (length: {len(bfs_path)})")
    print(f"  DFS path: {dfs_path} (length: {len(dfs_path)})")
    print(f"\n[+] BFS guarantees shortest path!")
    print(f"[+] DFS is faster for deep searches!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LOGARITHMA - BFS & DFS Examples")
    print("=" * 60)
    
    example_1_bfs_basics()
    example_2_bfs_shortest_path()
    example_3_dfs_basics()
    example_4_cycle_detection()
    example_5_maze_solving()
    example_6_comparison()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60 + "\n")
