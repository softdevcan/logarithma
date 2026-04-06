# Logarithma

> High-performance graph algorithms for Python — from classic Dijkstra to cutting-edge research.

[![PyPI version](https://img.shields.io/pypi/v/logarithma.svg)](https://pypi.org/project/logarithma/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Logarithma is a Python library for graph algorithms built on [NetworkX](https://networkx.org/). It provides clean, well-tested implementations of shortest path and traversal algorithms, including the **Breaking the Sorting Barrier** SSSP algorithm (Duan et al., 2025) — the first Python implementation of an algorithm that surpasses Dijkstra's classical O(n log n) sorting barrier.

## Installation

```bash
pip install logarithma
```

With visualization support:

```bash
pip install logarithma[viz]
```

With optional Cython acceleration for `breaking_barrier_sssp`:

```bash
pip install "logarithma[fast]"
python setup_ext.py build_ext --inplace
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

**Breaking the Sorting Barrier SSSP** — `O(m log²/³ n)`, directed graphs, non-negative weights

The first Python implementation of Duan, Mao, Mao, Shu, Yin (2025) — arXiv:2504.17033v2. Breaks Dijkstra's classical Ω(n log n) sorting barrier for sparse directed graphs. Optional Cython acceleration available in v0.6.0.

```python
import networkx as nx
import logarithma as lg

G = nx.DiGraph()
G.add_edge('s', 'A', weight=2)
G.add_edge('s', 'B', weight=5)
G.add_edge('A', 'C', weight=1)
G.add_edge('B', 'C', weight=2)

distances = lg.breaking_barrier_sssp(G, 's')
# {'s': 0, 'A': 2, 'B': 5, 'C': 3}
```

**Performance (v0.6.0, sparse graphs m ≈ 2n):**

| n | Dijkstra | Breaking Barrier | Ratio |
|---|---|---|---|
| 500 | 0.8ms | 61ms | 75× |
| 1000 | 1.7ms | 47ms | 26× |
| 2000 | 3.4ms | 74ms | 21× |

> The algorithm is asymptotically optimal (O(m log²/³ n) vs Dijkstra's O(m + n log n)) — the practical crossover point requires very large n. Cython acceleration reduces the constant factor ~5–7× vs pure Python.

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

### MST (Minimum Spanning Tree)

**Kruskal** — `O(E log E)`, Union-Find with path compression

```python
result = lg.kruskal_mst(G)
print(result['mst_edges'])     # [(u, v, weight), ...]
print(result['total_weight'])
print(result['num_components'])  # 1 = spanning tree, >1 = spanning forest
```

**Prim** — `O(E + V log V)`, min-heap based

```python
result = lg.prim_mst(G, start='A')
```

### Network Flow

**Edmonds-Karp max flow** — `O(V·E²)`, deterministic

```python
result = lg.max_flow(G, source='s', sink='t')
print(result['flow_value'])   # total max flow
print(result['flow_dict'])    # flow on each edge
```

### Graph Properties

**Tarjan SCC** — `O(V+E)`, iterative, returns SCCs in reverse topological order

```python
sccs = lg.tarjan_scc(G)      # List[List[node]]
for scc in sccs:
    print(scc)
```

**Topological Sort** — `O(V+E)`, DFS or Kahn method

```python
from logarithma import NotDAGError

order = lg.topological_sort(G, method='dfs')    # or 'kahn'

try:
    order = lg.topological_sort(cyclic_graph)
except NotDAGError as e:
    print(e.cycle)   # detected cycle
```

### Visualization

24 visualization functions — requires `pip install logarithma[viz]`.

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
    plot_astar_search,              # expanded nodes, open set, heuristic values
    plot_bellman_ford_result,       # negative edges (dashed red), distance labels
    plot_negative_cycle,            # cycle nodes/edges highlighted in red
    plot_bidirectional_search,      # forward/backward frontiers, meeting point
    plot_shortest_path_comparison,  # Dijkstra vs A* vs BiDijkstra side by side
    plot_breaking_barrier_result,   # distance gradient colouring, path highlight
    plot_dfs_tree,                  # tree/back/cross edges, discovery-finish times
    # MST
    plot_mst,                       # MST edges highlighted on original graph
    plot_mst_comparison,            # Kruskal vs Prim side by side
    plot_kruskal_steps,             # step-by-step Kruskal animation
    # Network Flow
    plot_flow_network,              # flow/capacity labels, saturated/partial/empty
    plot_flow_paths,                # active flow paths (width ∝ flow)
    # Graph Properties
    plot_scc,                       # each SCC a distinct colour + condensation DAG
    plot_topological_order,         # left-to-right layered layout with rank numbers
)

# Breaking Barrier — distance gradient + path to target
distances = lg.breaking_barrier_sssp(G, 's')
plot_breaking_barrier_result(G, 's', distances, highlight_targets=['C'])

# DFS tree — edge classification + discovery/finish timestamps
plot_dfs_tree(G, source='A', show_discovery_finish=True, show_depth=True)

# MST step-by-step
plot_kruskal_steps(G, max_steps=6)

# SCC with condensation DAG
plot_scc(G, show_condensation=True)
```

## Error Handling

All algorithms raise descriptive exceptions from a unified hierarchy:

```python
from logarithma.algorithms.exceptions import (
    GraphError,                    # base class for all logarithma errors
    EmptyGraphError,               # graph has no nodes
    NodeNotFoundError,             # source or target not in graph (.node, .role)
    NegativeWeightError,           # negative edge in Dijkstra/A*/BiDijkstra
    NegativeCycleError,            # Bellman-Ford detected a cycle (.cycle)
    InvalidModeError,              # invalid mode string (.mode, .valid_modes)
    NotDAGError,                   # topological_sort called on cyclic graph (.cycle)
    UndirectedGraphRequiredError,  # DiGraph passed to MST algorithm
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

| Algorithm | Time | Notes |
|-----------|------|-------|
| Dijkstra | `O(E + V log V)` | non-negative weights |
| A\* | `O(b^d)` practical | heuristic-guided |
| Bellman-Ford | `O(V · E)` | negative weights, cycle detection |
| Bidirectional Dijkstra | `O(E + V log V)` ~2× faster | point-to-point |
| **Breaking Barrier SSSP** | **`O(m log²/³ n)`** | **directed, breaks sorting barrier** |
| BFS / DFS | `O(V + E)` | traversal |
| Kruskal MST | `O(E log E)` | undirected, spanning forest |
| Prim MST | `O(E + V log V)` | undirected, spanning forest |
| Max Flow (Edmonds-Karp) | `O(V · E²)` | directed/undirected |
| Tarjan SCC | `O(V + E)` | directed/undirected |
| Topological Sort | `O(V + E)` | DAG only |

## Documentation

Full documentation and examples: **[softdevcan.github.io/logarithma](https://softdevcan.github.io/logarithma/)**

## Research

Logarithma's primary goal is implementing the **Breaking the Sorting Barrier for Directed Single-Source Shortest Paths** (Duan, Mao, Mao, Shu, Yin — arXiv:2504.17033v2, STOC 2025 Best Paper), which surpasses the classical `O(m + n log n)` sorting barrier for directed SSSP. This is the **first Python implementation** of this algorithm.

Key components:
- **BMSSP** (Bounded Multi-Source Shortest Path) — recursive divide-and-conquer framework
- **BlockHeap** (Lemma 3.3) — block-based linked list data structure with Insert / BatchPrepend / Pull
- **Constant-degree transform** (Frederickson 1983) — graph preprocessing for theoretical guarantees
- **Assumption 2.1** — lexicographic tiebreaking for deterministic predecessor forest
- **Cython acceleration** (v0.6.0) — `_should_relax` as `cdef inline nogil`, typed memoryviews for ~5–7× speedup over v0.5.0

## License

MIT — see [LICENSE](LICENSE) for details.

**Author:** Can AKYILDIRIM · [GitHub](https://github.com/softdevcan/logarithma) · [PyPI](https://pypi.org/project/logarithma/)
