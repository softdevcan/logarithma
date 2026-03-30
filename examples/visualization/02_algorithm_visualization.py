"""
Algorithm Visualization Examples
=================================

This example demonstrates how to visualize algorithm results.
"""

import networkx as nx
from logarithma import dijkstra, dijkstra_with_path, bfs, dfs
from logarithma.visualization import (
    plot_shortest_path,
    plot_traversal,
    plot_distance_heatmap,
    plot_path_comparison
)
from logarithma.utils import generate_random_graph

print("=" * 60)
print("LOGARITHMA - Algorithm Visualization Examples")
print("=" * 60)

# Create a test graph
G = generate_random_graph(30, 0.15, weighted=True, seed=42)
print(f"\nCreated graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Example 1: Visualize Shortest Path
print("\n1. Shortest Path Visualization (Dijkstra)")
print("-" * 60)

source, target = 0, 20
distance, path = dijkstra_with_path(G, source, target)
print(f"Shortest path from {source} to {target}:")
print(f"Distance: {distance:.2f}")
print(f"Path: {' -> '.join(map(str, path))}")

plot_shortest_path(G, path, layout="spring", 
                  title=f"Shortest Path: {source} → {target} (distance={distance:.2f})")

# Example 2: Visualize BFS Traversal
print("\n2. BFS Traversal Visualization")
print("-" * 60)

visited_bfs = bfs(G, source=0)
print(f"BFS from node 0 visited {len(visited_bfs)} nodes")
print(f"Visit order: {visited_bfs[:10]}..." if len(visited_bfs) > 10 else f"Visit order: {visited_bfs}")

plot_traversal(G, visited_bfs, layout="spring", title="BFS Traversal from Node 0")

# Example 3: Visualize DFS Traversal
print("\n3. DFS Traversal Visualization")
print("-" * 60)

visited_dfs = dfs(G, source=0)
print(f"DFS from node 0 visited {len(visited_dfs)} nodes")
print(f"Visit order: {visited_dfs[:10]}..." if len(visited_dfs) > 10 else f"Visit order: {visited_dfs}")

plot_traversal(G, visited_dfs, layout="spring", title="DFS Traversal from Node 0")

# Example 4: Distance Heatmap
print("\n4. Distance Heatmap")
print("-" * 60)

distances = dijkstra(G, source=0)
print(f"Computed distances from node 0 to all reachable nodes")
print(f"Number of reachable nodes: {len(distances)}")

plot_distance_heatmap(distances, title="Distances from Node 0")

# Example 5: Compare Different Paths
print("\n5. Path Comparison (Dijkstra vs BFS)")
print("-" * 60)

# Create a simpler graph for comparison
G_simple = nx.Graph()
edges = [
    (0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 5),
    (2, 3, 8), (2, 4, 10), (3, 4, 2), (3, 5, 6), (4, 5, 3)
]
G_simple.add_weighted_edges_from(edges)

source, target = 0, 5

# Dijkstra path (shortest by weight)
dist_dijkstra, path_dijkstra = dijkstra_with_path(G_simple, source, target)

# BFS path (shortest by hops)
from logarithma import bfs_path
path_bfs = bfs_path(G_simple, source, target)
dist_bfs = sum(G_simple[path_bfs[i]][path_bfs[i+1]]['weight'] 
              for i in range(len(path_bfs)-1))

print(f"\nDijkstra path: {' -> '.join(map(str, path_dijkstra))}")
print(f"Dijkstra distance: {dist_dijkstra:.2f}")
print(f"\nBFS path: {' -> '.join(map(str, path_bfs))}")
print(f"BFS distance: {dist_bfs:.2f}")

paths = {
    'Dijkstra (weighted)': path_dijkstra,
    'BFS (unweighted)': path_bfs
}
distances = {
    'Dijkstra (weighted)': dist_dijkstra,
    'BFS (unweighted)': dist_bfs
}

plot_path_comparison(G_simple, paths, distances, layout="spring")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
