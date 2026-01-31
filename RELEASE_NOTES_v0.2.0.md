# 🚀 logarithma v0.2.0 Release Notes

We're excited to announce the release of logarithma v0.2.0! This major update brings significant enhancements to the library with new algorithms, comprehensive utilities, and improved code quality.

## 🎯 What's New

### 📊 Graph Traversal Algorithms
- **BFS (Breadth-First Search)**: Complete implementation with path finding capabilities
- **DFS (Depth-First Search)**: Both recursive and iterative versions
- **Cycle Detection**: Detect cycles in directed and undirected graphs

### 🛠️ Comprehensive Utils Module
The new utils module provides 34 essential functions across 4 categories:

1. **Graph Generators** (9 functions)
   - Create random graphs, grids, complete graphs, trees, and more
   - Perfect for testing and experimentation

2. **Validators** (8 functions)
   - Check connectivity, DAG properties, negative weights
   - Validate graph properties before running algorithms

3. **Converters** (8 functions)
   - Convert between adjacency matrices, edge lists, and NetworkX graphs
   - Seamless integration with other graph libraries

4. **Metrics** (9 functions)
   - Calculate density, degree statistics, diameter, clustering coefficients
   - Comprehensive graph analysis tools

### ⚡ Enhanced Dijkstra Algorithm
- Added support for directed graphs (nx.DiGraph)
- Negative weight validation with clear error messages
- Improved documentation and examples
- Better error handling for edge cases

### 📚 Documentation & Examples
- New example scripts demonstrating all features
- Benchmark framework for performance testing
- Comprehensive API documentation

## 💻 Installation

```bash
pip install --upgrade logarithma
```

## 🔧 Quick Start

```python
import logarithma as lg
from logarithma.utils import generate_random_graph, graph_summary

# Create a random graph
G = generate_random_graph(100, 0.1, weighted=True)

# Analyze the graph
summary = graph_summary(G)
print(f"Nodes: {summary['nodes']}, Edges: {summary['edges']}")
print(f"Density: {summary['density']:.4f}")

# Find shortest paths
distances = lg.dijkstra(G, source=0)

# Perform graph traversal
visited = lg.bfs(G, source=0)
path = lg.dfs_path(G, source=0, target=50)

# Detect cycles
has_cycle = lg.detect_cycle(G)
```

## 📈 Performance

All algorithms are optimized for performance with comprehensive test coverage. The new benchmark framework allows you to measure performance on your specific use cases.

## 🔮 What's Next (v0.3.0+)

- Visualization module with Matplotlib and Plotly support
- Additional algorithms: A*, Bellman-Ford, Floyd-Warshall
- Performance optimizations with Cython/Numba
- Advanced shortest path algorithm from "Breaking the Sorting Barrier" (2025)

## 🙏 Acknowledgments

Thank you to all users who provided feedback on v0.1.0. Your input has been invaluable in shaping this release.

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

**GitHub**: https://github.com/softdevcan/logarithma  
**PyPI**: https://pypi.org/project/logarithma/  
**Issues**: https://github.com/softdevcan/logarithma/issues
