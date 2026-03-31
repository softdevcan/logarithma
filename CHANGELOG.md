# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-03-31

### Added
- **Algorithm-specific visualization module** (`src/logarithma/visualization/shortest_path_viz.py`)
  - `plot_astar_search` — expanded (closed set) / open set node renk kodlaması, opsiyonel heuristic değer etiketleri
  - `plot_bellman_ford_result` — negatif kenarlar kesik kırmızı, her node'da mesafe etiketi, hedef path highlight
  - `plot_negative_cycle` — döngü node/kenarları kalın kırmızı, toplam döngü ağırlığı başlıkta
  - `plot_bidirectional_search` — forward (mavi) / backward (yeşil) frontier, buluşma noktası (sarı), overlap (mor)
  - `plot_shortest_path_comparison` — Dijkstra / A\* / Bidirectional Dijkstra yan yana subplot karşılaştırma
  - Dahili `_astar_trace`, `_bidirectional_trace` helper'ları (public API'ye dokunulmadan step-by-step veri toplar)

- **DFS tree visualization** (`src/logarithma/visualization/traversal_viz.py`)
  - `plot_dfs_tree` — tree edges (siyah), back edges (kesik kırmızı), cross/forward edges (kesik gri, DiGraph)
  - Node rengi: source=yeşil, döngü node'u=kırmızı, diğerleri derinliğe göre mavi gradyan
  - `show_discovery_finish=True`: discovery/finish zaman damgaları (parenthesis teoremi)
  - `show_depth=True`: recursion derinliği etiketi
  - Ziyaret sırası altta metin olarak gösterilir

- **`_get_layout()` helper** (`graph_plotter.py`)
  - Tüm visualization dosyaları ortak layout dict'i bu helper üzerinden kullanır (DRY)

- **Yeni örnek dosyası** (`examples/visualization/04_algorithm_specific_viz.py`)
  - 6 demo: A\* search, Bellman-Ford, negatif döngü, BiDijkstra, karşılaştırma, DFS tree

### Updated
- `graph_plotter.py` — `plot_graph`, `plot_shortest_path`, `plot_traversal`, `plot_graph_interactive` fonksiyonlarındaki tekrar eden layout dict'leri kaldırıldı, `_get_layout()` kullanılıyor
- `visualization/__init__.py` — 6 yeni fonksiyon export'a eklendi (toplam 16 fonksiyon)
- `CLAUDE.md`, `README.md`, `docs/ALGORITHM_ROADMAP.md` — visualization ve error handling dokümantasyonu güncellendi

## [0.3.2] - 2026-03-30

### Added
- **Centralized error handling** (`src/logarithma/algorithms/exceptions.py`)
  - Exception hiyerarşisi: `GraphError` (base) → `EmptyGraphError`, `NodeNotFoundError`, `NegativeWeightError`, `NegativeCycleError`, `InvalidModeError`
  - Tüm exception'lar hem `GraphError` hem `ValueError` subclass'ı — geriye dönük uyumluluk korundu
  - `NegativeCycleError.cycle` attribute ile döngü node listesi taşınıyor
  - 4 validator helper: `validate_graph`, `validate_source`, `validate_target`, `validate_weight`
  - Tüm algoritmalar (Dijkstra, A\*, Bellman-Ford, BiDijkstra, BFS, DFS) bu yapıya taşındı

- **Yeni örnek dosyaları** (`examples/basic_usage/`)
  - `04_astar_examples.py` — A\* heuristic karşılaştırması, grid pathfinding, stats
  - `05_bellman_ford_examples.py` — negatif ağırlıklar, NegativeCycleError kullanımı
  - `06_bidirectional_dijkstra_examples.py` — büyük graf benchmark, BiDijkstra vs Dijkstra

### Updated
- Tüm algoritma modülleri exception import'ları `exceptions.py`'ye taşındı
- `__init__.py` — tüm exception sınıfları top-level'da export ediliyor
- `index.html` versiyon güncellendi

## [0.3.1] - 2026-03-30

### Fixed
- PyPI badge URL README.md'de güncellendi
- GitHub Pages `index.html` versiyon etiketi v0.3.1'e güncellendi

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
