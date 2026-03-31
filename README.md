# Logarithma

> High-performance graph algorithms for Python — from classic Dijkstra to cutting-edge research.

[![PyPI version](https://img.shields.io/pypi/v/logarithma.svg)](https://pypi.org/project/logarithma/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Logarithma is a Python library for graph algorithms built on [NetworkX](https://networkx.org/). It provides clean, well-tested implementations of shortest path and traversal algorithms, with the primary research goal of implementing the **Breaking the Sorting Barrier** SSSP algorithm (Duan et al., 2025).

## Installation

```bash
pip install logarithma
```

With visualization support:

```bash
pip install logarithma[viz]
```

**Requirements:** Python 3.8+, NumPy ≥ 1.20, NetworkX ≥ 2.6

## Quick Start

```python
import logarithma as lg
import networkx as nx

G = nx.Graph()
G.add_edge('A', 'B', weight=4)
G.add_edge('A', 'C', weight=2)
G.add_edge('B', 'C', weight=1)
G.add_edge('C', 'D', weight=8)

# Shortest distances from A
distances = lg.dijkstra(G, 'A')
# {'A': 0, 'C': 2, 'B': 3, 'D': 10}

# Shortest path to D
result = lg.dijkstra_with_path(G, 'A', 'D')
print(result['path'])    # ['A', 'C', 'D']
print(result['distance']) # 10
```

## Algorithms

### Shortest Path

**Dijkstra** — `O(E + V log V)`, non-negative weights, directed & undirected

```python
distances = lg.dijkstra(G, source='A')
result = lg.dijkstra_with_path(G, source='A', target='D')
```

**A\* (A-Star)** — heuristic-guided, optimal with admissible heuristic

```python
from logarithma import astar, euclidean_heuristic, manhattan_heuristic, haversine_heuristic

pos = {'A': (0, 0), 'B': (3, 0), 'C': (3, 4)}
result = astar(G, 'A', 'C', heuristic=euclidean_heuristic(pos))
print(result['distance'])  # 5
print(result['path'])      # ['A', 'B', 'C']
```

**Bellman-Ford** — `O(V·E)`, supports negative-weight edges and cycle detection

```python
from logarithma import bellman_ford, bellman_ford_path, NegativeCycleError

DG = nx.DiGraph()
DG.add_edge('A', 'B', weight=4)
DG.add_edge('B', 'C', weight=-3)

result = bellman_ford(DG, 'A')
# distances: {'A': 0, 'B': 4, 'C': 1}

try:
    bellman_ford(graph_with_cycle, 'A')
except NegativeCycleError as e:
    print(e.cycle)  # reconstructed cycle nodes
```

**Bidirectional Dijkstra** — simultaneous forward/backward search, ~2× faster for point-to-point

```python
result = lg.bidirectional_dijkstra(G, source='A', target='D')
print(result['distance'])
print(result['path'])
```

### Graph Traversal

**BFS** and **DFS** with path reconstruction and cycle detection:

```python
# BFS — shortest path by edge count
distances = lg.bfs(G, source='A')
result = lg.bfs_path(G, source='A', target='D')

# DFS — traversal order, path finding, cycle detection
visited = lg.dfs(G, source='A')                    # recursive (default)
visited = lg.dfs(G, source='A', mode='iterative')
path = lg.dfs_path(G, source='A', target='D')

has_cycle, cycle = lg.detect_cycle(G)
```

### Utils

34 utility functions across 4 categories:

```python
from logarithma.utils import (
    # Generators
    generate_random_graph, generate_grid_graph, generate_scale_free_graph,
    # Validators
    is_connected, is_dag, has_negative_weights, validate_graph,
    # Converters
    to_adjacency_matrix, from_edge_list, to_graphml,
    # Metrics
    graph_density, diameter, graph_summary,
)

G = generate_random_graph(n=100, edge_prob=0.1, weighted=True, seed=42)
print(graph_summary(G))
# {'nodes': 100, 'edges': 491, 'density': 0.099, 'avg_degree': 9.82, ...}
```

### Visualization

16 visualization functions — requires `pip install logarithma[viz]`.

**General graph plotting:**
```python
from logarithma.visualization import plot_graph, plot_shortest_path, plot_traversal

plot_graph(G, layout='spring', title='My Graph')
plot_shortest_path(G, path, title='Shortest Path')
plot_traversal(G, visited_order, title='BFS Traversal')
```

**Algorithm-specific visualizations:**
```python
from logarithma.visualization import (
    plot_astar_search,             # expanded nodes, open set, heuristic values
    plot_bellman_ford_result,      # negative edges (dashed red), distance labels
    plot_negative_cycle,           # cycle nodes/edges highlighted in red
    plot_bidirectional_search,     # forward/backward frontiers, meeting point
    plot_shortest_path_comparison, # Dijkstra vs A* vs BiDijkstra side by side
    plot_dfs_tree,                 # tree/back/cross edges, discovery-finish times
)

# A* — show which nodes were expanded vs skipped
from logarithma.algorithms.shortest_path.astar import manhattan_heuristic
pos = {node: node for node in G.nodes()}   # grid graph positions
plot_astar_search(G, source=(0,0), target=(4,4),
                  heuristic=manhattan_heuristic(pos), show_heuristic=True)

# DFS tree — edge classification + discovery/finish timestamps
plot_dfs_tree(G, source='A', show_discovery_finish=True, show_depth=True)

# Side-by-side comparison
plot_shortest_path_comparison(G, source=0, target=33)
```

## Error Handling

All algorithms raise descriptive exceptions from a unified hierarchy:

```python
from logarithma.algorithms.exceptions import (
    GraphError,          # base class for all logarithma errors
    EmptyGraphError,     # graph has no nodes
    NodeNotFoundError,   # source or target not in graph (.node, .role attributes)
    NegativeWeightError, # negative edge in Dijkstra/A*/BiDijkstra (.u, .v, .weight)
    NegativeCycleError,  # Bellman-Ford detected a cycle (.cycle = list of nodes)
    InvalidModeError,    # invalid mode string (e.g. dfs mode) (.mode, .valid_modes)
)

try:
    result = bellman_ford(G, source='A')
except NegativeCycleError as e:
    print(e.cycle)        # ['A', 'B', 'C', 'A']
except NodeNotFoundError as e:
    print(e.node, e.role) # 'Z', 'source'
```

All exceptions are subclasses of both `GraphError` and `ValueError`, so existing `except ValueError` blocks remain compatible.

## Complexity Reference

| Algorithm | Time | Negative Weights |
|-----------|------|-----------------|
| Dijkstra | `O(E + V log V)` | ✗ |
| A\* | `O(b^d)` practical | ✗ |
| Bellman-Ford | `O(V · E)` | ✓ |
| Bidirectional Dijkstra | `O(E + V log V)` ~2× faster | ✗ |
| BFS / DFS | `O(V + E)` | — |

## Documentation

Full documentation and examples: **[softdevcan.github.io/logarithma](https://softdevcan.github.io/logarithma/)**

## Research

Logarithma's primary goal is implementing the **Breaking the Sorting Barrier for Directed Single-Source Shortest Paths** (Duan, Mao, Mao, Shu, Yin — arXiv:2504.17033v2, 2025), which surpasses the classical `O(m + n log n)` sorting barrier for directed SSSP.

## License

MIT — see [LICENSE](LICENSE) for details.

**Author:** Can AKYILDIRIM · [GitHub](https://github.com/softdevcan/logarithma) · [PyPI](https://pypi.org/project/logarithma/)
