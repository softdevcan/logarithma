"""
Performance Analysis and Comparison Examples
============================================

This example demonstrates algorithm performance visualization.
"""

import time
import networkx as nx
from logarithma import dijkstra
from logarithma.visualization import (
    plot_algorithm_comparison,
    plot_complexity_analysis,
    plot_degree_distribution,
    plot_graph_metrics
)
from logarithma.utils import generate_random_graph, graph_summary

print("=" * 60)
print("LOGARITHMA - Performance Analysis Examples")
print("=" * 60)

# Example 1: Algorithm Complexity Analysis
print("\n1. Runtime Complexity Analysis")
print("-" * 60)

sizes = [50, 100, 200, 500, 1000]
times = []

print("Running Dijkstra on graphs of increasing size...")
for n in sizes:
    G = generate_random_graph(n, 0.1, weighted=True, seed=42)
    
    start = time.time()
    dijkstra(G, 0)
    elapsed = time.time() - start
    
    times.append(elapsed)
    print(f"  n={n:4d}: {elapsed:.4f}s")

plot_complexity_analysis(sizes, times, complexity_label="O(E + V log V)",
                        title="Dijkstra Runtime Analysis")

# Example 2: Compare Multiple Algorithms
print("\n2. Algorithm Comparison")
print("-" * 60)

from logarithma import bfs

sizes = [100, 200, 500, 1000]
results = {'Dijkstra': {}, 'BFS': {}}

print("Comparing Dijkstra vs BFS...")
for n in sizes:
    G = generate_random_graph(n, 0.1, weighted=True, seed=42)
    
    # Dijkstra
    start = time.time()
    dijkstra(G, 0)
    results['Dijkstra'][n] = time.time() - start
    
    # BFS
    start = time.time()
    bfs(G, 0)
    results['BFS'][n] = time.time() - start
    
    print(f"  n={n:4d}: Dijkstra={results['Dijkstra'][n]:.4f}s, BFS={results['BFS'][n]:.4f}s")

plot_algorithm_comparison(results, metric="Time (seconds)",
                         title="Dijkstra vs BFS Performance")

# Example 3: Degree Distribution Analysis
print("\n3. Degree Distribution Analysis")
print("-" * 60)

# Random graph (Erdős-Rényi)
G_random = generate_random_graph(100, 0.1, seed=42)
print(f"Random graph: {G_random.number_of_nodes()} nodes, {G_random.number_of_edges()} edges")
plot_degree_distribution(G_random, title="Degree Distribution - Random Graph")

# Scale-free graph (Barabási-Albert)
G_scalefree = nx.barabasi_albert_graph(100, 3, seed=42)
print(f"Scale-free graph: {G_scalefree.number_of_nodes()} nodes, {G_scalefree.number_of_edges()} edges")
plot_degree_distribution(G_scalefree, title="Degree Distribution - Scale-Free Graph")

# Example 4: Graph Metrics Dashboard
print("\n4. Graph Metrics Dashboard")
print("-" * 60)

G = generate_random_graph(50, 0.15, weighted=True, seed=42)
metrics = graph_summary(G)

print("Graph metrics:")
for key, value in metrics.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.4f}")
    else:
        print(f"  {key}: {value}")

plot_graph_metrics(metrics, title="Graph Analysis Dashboard")

# Example 5: Density vs Performance
print("\n5. Graph Density Impact on Performance")
print("-" * 60)

densities = [0.05, 0.1, 0.2, 0.3, 0.5]
results_density = {'Dijkstra': {}}

print("Testing Dijkstra on graphs with different densities...")
for density in densities:
    G = generate_random_graph(500, density, weighted=True, seed=42)
    
    start = time.time()
    dijkstra(G, 0)
    elapsed = time.time() - start
    
    results_density['Dijkstra'][int(density * 100)] = elapsed
    print(f"  Density={density:.2f}: {elapsed:.4f}s ({G.number_of_edges()} edges)")

plot_algorithm_comparison(results_density, metric="Time (seconds)",
                         title="Dijkstra Performance vs Graph Density")

print("\n" + "=" * 60)
print("Performance analysis completed!")
print("=" * 60)
