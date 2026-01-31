"""
Shortest Path Algorithms Benchmark
==================================

Compare performance of different shortest path algorithms.
"""

import logarithma as lg
from logarithma.utils import generate_random_graph
from framework import AlgorithmBenchmark, compare_algorithms


def benchmark_dijkstra():
    """Benchmark Dijkstra algorithm"""
    print("\n" + "🔷" * 35)
    print("Benchmarking Dijkstra Algorithm")
    print("🔷" * 35)
    
    benchmark = AlgorithmBenchmark(lg.dijkstra, "Dijkstra")
    
    # Test on different graph sizes
    graph_sizes = [10, 50, 100, 500, 1000]
    results = benchmark.run_multiple(
        graph_sizes,
        edge_probability=0.1,
        weighted=True,
        runs_per_size=3
    )
    
    benchmark.print_results()
    return results


def benchmark_bfs():
    """Benchmark BFS algorithm"""
    print("\n" + "🔷" * 35)
    print("Benchmarking BFS Algorithm")
    print("🔷" * 35)
    
    benchmark = AlgorithmBenchmark(lg.bfs, "BFS")
    
    graph_sizes = [10, 50, 100, 500, 1000]
    results = benchmark.run_multiple(
        graph_sizes,
        edge_probability=0.1,
        weighted=False,
        runs_per_size=3
    )
    
    benchmark.print_results()
    return results


def compare_shortest_path_algorithms():
    """Compare Dijkstra vs BFS on unweighted graphs"""
    print("\n" + "🔷" * 35)
    print("Comparing Shortest Path Algorithms")
    print("🔷" * 35)
    
    algorithms = [
        (lg.dijkstra, "Dijkstra"),
        (lg.bfs, "BFS")
    ]
    
    graph_sizes = [50, 100, 200, 500]
    
    results = compare_algorithms(
        algorithms,
        graph_sizes,
        edge_probability=0.1,
        weighted=False,
        runs_per_size=3
    )
    
    # Analysis
    print("\n📊 Analysis:")
    print("=" * 70)
    for size in graph_sizes:
        dijkstra_time = next(r['avg_time'] for r in results['Dijkstra'] if r['size'] == size)
        bfs_time = next(r['avg_time'] for r in results['BFS'] if r['size'] == size)
        speedup = dijkstra_time / bfs_time
        print(f"Size {size}: BFS is {speedup:.2f}x faster than Dijkstra")
    print("=" * 70)
    print("\n✓ For unweighted graphs, BFS is more efficient!")
    
    return results


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("LOGARITHMA - Shortest Path Algorithms Benchmark")
    print("=" * 70)
    
    # Individual benchmarks
    dijkstra_results = benchmark_dijkstra()
    bfs_results = benchmark_bfs()
    
    # Comparison
    comparison = compare_shortest_path_algorithms()
    
    print("\n" + "=" * 70)
    print("✅ Benchmark completed!")
    print("=" * 70 + "\n")
