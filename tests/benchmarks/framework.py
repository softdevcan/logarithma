"""
Benchmark Framework
==================

Framework for benchmarking graph algorithms.
"""

import time
import psutil
import os
from typing import Callable, Dict, List, Any, Union
import networkx as nx
from logarithma.utils import generate_random_graph


class AlgorithmBenchmark:
    """Benchmark framework for graph algorithms"""
    
    def __init__(self, algorithm: Callable, name: str):
        """
        Initialize benchmark.
        
        Args:
            algorithm: Function to benchmark
            name: Name of the algorithm
        """
        self.algorithm = algorithm
        self.name = name
        self.results = []
    
    def run_single(
        self,
        graph: Union[nx.Graph, nx.DiGraph],
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run single benchmark.
        
        Returns:
            Dictionary with timing and memory info
        """
        # Get initial memory
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run algorithm
        start_time = time.perf_counter()
        result = self.algorithm(graph, *args, **kwargs)
        end_time = time.perf_counter()
        
        # Get final memory
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'time': end_time - start_time,
            'memory_delta': mem_after - mem_before,
            'result': result
        }
    
    def run_multiple(
        self,
        graph_sizes: List[int],
        graph_generator: Callable = None,
        runs_per_size: int = 3,
        **gen_kwargs
    ) -> List[Dict[str, Any]]:
        """
        Run benchmark on multiple graph sizes.
        
        Args:
            graph_sizes: List of graph sizes to test
            graph_generator: Function to generate graphs
            runs_per_size: Number of runs per size
            **gen_kwargs: Arguments for graph generator
        
        Returns:
            List of benchmark results
        """
        if graph_generator is None:
            graph_generator = generate_random_graph
        
        results = []
        
        for size in graph_sizes:
            print(f"Benchmarking {self.name} on graph size {size}...")
            
            size_results = []
            for run in range(runs_per_size):
                # Generate graph
                graph = graph_generator(size, **gen_kwargs)
                
                # Run benchmark
                result = self.run_single(graph, 0)  # Use node 0 as source
                size_results.append(result)
            
            # Calculate averages
            avg_time = sum(r['time'] for r in size_results) / runs_per_size
            avg_memory = sum(r['memory_delta'] for r in size_results) / runs_per_size
            
            results.append({
                'size': size,
                'avg_time': avg_time,
                'avg_memory': avg_memory,
                'runs': size_results
            })
        
        self.results = results
        return results
    
    def print_results(self):
        """Print benchmark results in table format"""
        if not self.results:
            print("No results to display")
            return
        
        print(f"\n{'='*70}")
        print(f"Benchmark Results: {self.name}")
        print(f"{'='*70}")
        print(f"{'Size':<10} {'Avg Time (s)':<15} {'Avg Memory (MB)':<20}")
        print(f"{'-'*70}")
        
        for result in self.results:
            print(f"{result['size']:<10} "
                  f"{result['avg_time']:<15.6f} "
                  f"{result['avg_memory']:<20.2f}")
        
        print(f"{'='*70}\n")


def compare_algorithms(
    algorithms: List[tuple],  # [(func, name), ...]
    graph_sizes: List[int],
    **kwargs
) -> Dict[str, List[Dict]]:
    """
    Compare multiple algorithms.
    
    Args:
        algorithms: List of (function, name) tuples
        graph_sizes: List of graph sizes to test
        **kwargs: Arguments for graph generation
    
    Returns:
        Dictionary mapping algorithm names to results
    """
    all_results = {}
    
    for algo_func, algo_name in algorithms:
        benchmark = AlgorithmBenchmark(algo_func, algo_name)
        results = benchmark.run_multiple(graph_sizes, **kwargs)
        benchmark.print_results()
        all_results[algo_name] = results
    
    # Print comparison
    print(f"\n{'='*70}")
    print("Algorithm Comparison")
    print(f"{'='*70}")
    print(f"{'Size':<10} ", end='')
    for _, name in algorithms:
        print(f"{name:<20}", end='')
    print()
    print(f"{'-'*70}")
    
    for i, size in enumerate(graph_sizes):
        print(f"{size:<10} ", end='')
        for _, name in algorithms:
            time_val = all_results[name][i]['avg_time']
            print(f"{time_val:<20.6f}", end='')
        print()
    
    print(f"{'='*70}\n")
    
    return all_results
