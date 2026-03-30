# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-30

### Added
- **A\* Algorithm** (`astar`, `astar_with_stats`)
  - Heuristic-guided shortest path — optimal with admissible heuristic
  - Three built-in heuristics: `euclidean_heuristic`, `manhattan_heuristic`, `haversine_heuristic`
  - `zero_heuristic` degenerates A* to Dijkstra (baseline comparison)
  - `astar_with_stats` returns diagnostic node-expansion counts
  - Supports directed and undirected graphs
  - 31 unit tests

- **Bellman-Ford Algorithm** (`bellman_ford`, `bellman_ford_path`)
  - Supports directed graphs with negative-weight edges
  - `NegativeCycleError` (ValueError subclass) raised with reconstructed cycle
  - Early-termination optimisation when no relaxation occurs in a pass
  - `bellman_ford_path` convenience wrapper with path reconstruction
  - Documents the undirected + negative-weight → always 2-cycle constraint
  - 32 unit tests

- **Bidirectional Dijkstra** (`bidirectional_dijkstra`)
  - Simultaneous forward/backward search for point-to-point queries
  - Backward search on DiGraph follows reversed edges (predecessors)
  - ~2× fewer node expansions vs standard Dijkstra (Pohl 1971 criterion)
  - Supports directed and undirected graphs, non-negative weights
  - 23 unit tests

### Fixed
- `dijkstra_with_path`: unreachable nodes now included in `paths` dict with
  value `[]` instead of being silently omitted

### Updated
- Public API (`__init__.py`): all new algorithms exported at top level
- Version bumped to `0.3.0`
- `ALGORITHM_ROADMAP.md`, `DEVELOPMENT.md`, `CLAUDE.md` updated to reflect
  v0.3.0 completions

## [0.2.0] - 2026-01-31

### Added
- **Graph Traversal Algorithms**
  - BFS (Breadth-First Search) with path finding
  - DFS (Depth-First Search) with recursive and iterative implementations
  - Cycle detection for directed and undirected graphs

- **Comprehensive Utils Module**
  - **Graph Generators**: 9 functions for creating various graph types
    - Random graphs, grid graphs, complete graphs, trees, etc.
  - **Validators**: 8 functions for graph property validation
    - Connectivity checks, DAG validation, negative weight detection, etc.
  - **Converters**: 8 functions for graph format conversion
    - Adjacency matrix, edge list, adjacency list conversions
  - **Metrics**: 9 functions for graph analysis
    - Density, degree statistics, diameter, clustering coefficient, etc.

- **Examples and Documentation**
  - Example scripts for Dijkstra, BFS/DFS, and utils module
  - Benchmark framework for performance testing
  - Comprehensive documentation updates

### Improved
- **Dijkstra Algorithm Enhancements**
  - Added support for directed graphs (nx.DiGraph)
  - Negative weight validation with proper error handling
  - Enhanced error messages for missing nodes
  - Improved docstrings with detailed examples
  - Better time complexity documentation (O(E + V log V))

- **Test Coverage**
  - Expanded Dijkstra tests from 2 to 17+ test cases
  - Added edge case testing (disconnected graphs, single nodes, etc.)
  - Comprehensive error handling tests

- **Code Quality**
  - Removed debug print statements for production readiness
  - Added type hints throughout the codebase
  - Improved module organization and imports
  - Better docstring coverage

### Documentation
- Updated README with v0.2.0 features
- Created comprehensive development guides
- Added algorithm roadmap for future implementations
- Documented the Breaking the Sorting Barrier SSSP (2025) as primary goal

## [0.1.0] - 2024-06-XX

### Added
- Initial release
- Basic Dijkstra's shortest path algorithm
- NetworkX integration
- PyPI package setup
