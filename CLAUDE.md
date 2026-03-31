# CLAUDE.md — Logarithma Project Guide

## Proje Özeti

**Logarithma**, Duan et al. (2025) makalesindeki "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths" algoritmasını Python kütüphanesi olarak hayata geçirmeyi hedefleyen bir proje. Ana vizyon: Dijkstra'nın O(m + n log n) sorting barrier'ını kıran O(m + n log log n) SSSP implementasyonu.

- **GitHub**: softdevcan/logarithma
- **PyPI**: logarithma
- **Yazar**: Can AKYILDIRIM (akyildirimcan@gmail.com)
- **Lisans**: MIT
- **Python**: 3.8+

---

## Mevcut Durum (Mart 2026)

### Versiyon: 0.4.0

### Implement Edilmiş Özellikler

| Modül | Fonksiyonlar | Durum |
|-------|-------------|-------|
| `dijkstra` | `dijkstra()`, `dijkstra_with_path()` | ✅ v0.2.0 |
| `bfs` | `bfs()`, `bfs_path()` | ✅ v0.2.0 |
| `dfs` | `dfs()`, `dfs_path()`, `detect_cycle()` | ✅ v0.2.0 |
| `utils` | 34 fonksiyon (generators/validators/converters/metrics) | ✅ v0.2.0 |
| `astar` | `astar()`, `astar_with_stats()`, 3 heuristic | ✅ v0.3.0 |
| `bellman_ford` | `bellman_ford()`, `bellman_ford_path()` | ✅ v0.3.0 |
| `bidirectional_dijkstra` | `bidirectional_dijkstra()` | ✅ v0.3.0 |
| `exceptions` | 7 exception sınıfı + 5 validator helper | ✅ v0.4.0 |
| `visualization` | 23 fonksiyon — genel (10) + algoritma-spesifik (13) | ✅ v0.4.0 |
| `mst` | `kruskal_mst()`, `prim_mst()` | ✅ v0.4.0 |
| `network_flow` | `max_flow()` (Edmonds-Karp) | ✅ v0.4.0 |
| `graph_properties` | `tarjan_scc()`, `topological_sort()` | ✅ v0.4.0 |

**Unit test toplamı: 182**

### Henüz Yapılmamışlar (Roadmap)

- ❌ Floyd-Warshall / Johnson's
- 🎯 **Breaking the Sorting Barrier SSSP** (arXiv:2504.17033v2) — ANA HEDEF

---

## Proje Yapısı

```
logarithma/
├── src/logarithma/
│   ├── __init__.py               # public API exports
│   ├── algorithms/
│   │   ├── exceptions.py         # Merkezi hata yönetimi (7 exception + 5 validator)
│   │   ├── shortest_path/
│   │   │   ├── dijkstra.py       # dijkstra + dijkstra_with_path
│   │   │   ├── astar.py          # astar + astar_with_stats + 3 heuristic
│   │   │   ├── bellman_ford.py   # bellman_ford + bellman_ford_path
│   │   │   └── bidirectional_dijkstra.py
│   │   ├── traversal/
│   │   │   ├── bfs.py            # bfs + bfs_path
│   │   │   └── dfs.py            # dfs + dfs_path + detect_cycle
│   │   ├── mst/
│   │   │   ├── kruskal.py        # kruskal_mst (Union-Find, O(E log E))
│   │   │   └── prim.py           # prim_mst (min-heap, O(E + V log V))
│   │   ├── network_flow/
│   │   │   └── max_flow.py       # max_flow — Edmonds-Karp (O(V·E²))
│   │   └── graph_properties/
│   │       ├── tarjan_scc.py     # tarjan_scc — iteratif (O(V+E))
│   │       └── topological_sort.py  # topological_sort — DFS + Kahn (O(V+E))
│   ├── utils/
│   │   ├── graph_generators.py   # 9 generator fonksiyon
│   │   ├── validators.py         # 8 validator fonksiyon
│   │   ├── converters.py         # 8 converter fonksiyon
│   │   └── metrics.py            # 9 metrics fonksiyon
│   └── visualization/
│       ├── graph_plotter.py      # 5 genel fonksiyon + _get_layout() helper
│       ├── algorithm_viz.py      # 5 performans/karşılaştırma fonksiyonu
│       ├── shortest_path_viz.py  # 5 shortest-path algoritma fonksiyonu
│       ├── traversal_viz.py      # 1 traversal fonksiyonu (plot_dfs_tree)
│       ├── mst_viz.py            # 3 MST fonksiyon (plot_mst, comparison, steps)
│       ├── flow_viz.py           # 2 flow fonksiyon (plot_flow_network, plot_flow_paths)
│       └── graph_properties_viz.py  # 2 fonksiyon (plot_scc, plot_topological_order)
├── tests/
│   ├── unit/
│   │   ├── test_dijkstra.py
│   │   ├── test_visualization.py
│   │   ├── test_kruskal.py
│   │   ├── test_prim.py
│   │   ├── test_max_flow.py
│   │   ├── test_tarjan_scc.py
│   │   └── test_topological_sort.py
│   ├── integration/
│   │   └── test_viz_integration.py
│   └── benchmarks/
│       ├── benchmark_shortest_path.py
│       └── framework.py
├── examples/
│   ├── visualization/
│   │   ├── 01_basic_plotting.py
│   │   ├── 02_algorithm_visualization.py
│   │   ├── 03_performance_analysis.py
│   │   └── 04_algorithm_specific_viz.py  # A*, BF, BiDijkstra, DFS tree
│   ├── mst_examples.py
│   ├── network_flow_examples.py
│   └── graph_properties_examples.py
├── docs/
│   ├── ALGORITHM_ROADMAP.md
│   ├── breaking_barrier_research.md
│   └── PROJECT_STRUCTURE.md
├── pyproject.toml
├── CHANGELOG.md
└── CLAUDE.md
```

---

## Public API

```python
import logarithma as lg

# Shortest Path
lg.dijkstra(G, source)
lg.dijkstra_with_path(G, source, target=None)
lg.astar(G, source, target, heuristic=None)
lg.astar_with_stats(G, source, target, heuristic=None)
lg.bellman_ford(G, source)
lg.bellman_ford_path(G, source, target)
lg.bidirectional_dijkstra(G, source, target)

# Traversal
lg.bfs(G, source)
lg.bfs_path(G, source, target=None)
lg.dfs(G, source, mode='recursive')
lg.dfs_path(G, source, target)
lg.detect_cycle(G)

# MST
lg.kruskal_mst(G)
lg.prim_mst(G, start=None)

# Network Flow
lg.max_flow(G, source, sink, capacity='capacity', method='edmonds_karp')

# Graph Properties
lg.tarjan_scc(G)
lg.topological_sort(G, method='dfs')

# Exceptions (import gerekir)
from logarithma import NegativeCycleError, NotDAGError, UndirectedGraphRequiredError
from logarithma.algorithms.exceptions import (
    GraphError, EmptyGraphError, NodeNotFoundError,
    NegativeWeightError, NegativeCycleError, InvalidModeError,
    NotDAGError, UndirectedGraphRequiredError,
)

# Utils (ayrı import gerekir)
from logarithma.utils import generate_random_graph, graph_summary, ...

# Visualization (ayrı import gerekir)
from logarithma.visualization import (
    # Genel
    plot_graph, plot_shortest_path, plot_traversal,
    plot_graph_interactive, plot_distance_heatmap,
    # Performans / karşılaştırma
    plot_algorithm_comparison, plot_complexity_analysis,
    plot_path_comparison, plot_degree_distribution, plot_graph_metrics,
    # Algoritma-spesifik shortest path
    plot_astar_search, plot_bellman_ford_result, plot_negative_cycle,
    plot_bidirectional_search, plot_shortest_path_comparison,
    # Traversal
    plot_dfs_tree,
    # MST
    plot_mst, plot_mst_comparison, plot_kruskal_steps,
    # Network Flow
    plot_flow_network, plot_flow_paths,
    # Graph Properties
    plot_scc, plot_topological_order,
)
```

---

## Error Handling Yapısı

Tüm hata yönetimi `src/logarithma/algorithms/exceptions.py` içinde merkezileştirilmiştir.

### Exception Hiyerarşisi

```
Exception
└── GraphError  (base — logarithma'ya özgü tüm hatalar)
    ├── EmptyGraphError(GraphError, ValueError)
    │       Boş grafa algoritma uygulandığında.
    ├── NodeNotFoundError(GraphError, ValueError)
    │       source veya target node grafta yokken.
    ├── NegativeWeightError(GraphError, ValueError)
    │       Negatif ağırlık kabul etmeyen algoritmada (Dijkstra, A*, BiDijkstra).
    ├── NegativeCycleError(GraphError, ValueError)
    │       Bellman-Ford negatif döngü tespit ettiğinde. `.cycle` attribute ile
    │       döngü node listesi taşır.
    ├── InvalidModeError(GraphError, ValueError)
    │       Geçersiz mod string'i verildiğinde (örn. dfs mode parametresi).
    ├── NotDAGError(GraphError, ValueError)
    │       topological_sort() döngülü grafa uygulandığında. `.cycle` attribute
    │       ile tespit edilen döngü node listesi taşır.
    └── UndirectedGraphRequiredError(GraphError, TypeError)
            kruskal_mst(), prim_mst() gibi undirected-only algoritmalara
            DiGraph verildiğinde.
```

### Validator Helper'lar

```python
from logarithma.algorithms.exceptions import (
    validate_graph,       # EmptyGraphError fırlatır
    validate_source,      # NodeNotFoundError fırlatır
    validate_target,      # NodeNotFoundError fırlatır
    validate_weight,      # NegativeWeightError fırlatır
    validate_undirected,  # UndirectedGraphRequiredError fırlatır
)
```

Tüm algoritmalar bu helper'ları kullanır. Yeni bir algoritma eklenirken bunlar kullanılmalı, özel ValueError yazılmamalıdır.

### Tipik Kullanım Örneği

```python
from logarithma import bellman_ford
from logarithma.algorithms.exceptions import NegativeCycleError, NodeNotFoundError

try:
    result = bellman_ford(G, source='A')
except NegativeCycleError as e:
    print(e.cycle)   # döngüyü oluşturan node listesi
except NodeNotFoundError as e:
    print(e.node, e.role)   # hangi node, 'source' mu 'target' mı
```

---

## Visualization Modülü Detayı

### Dosya Organizasyonu

| Dosya | İçerik | Fonksiyon Sayısı |
|-------|--------|-----------------|
| `graph_plotter.py` | Genel graf çizimi (statik + interaktif) | 5 + `_get_layout()` |
| `algorithm_viz.py` | Performans karşılaştırma, metrik dashboard | 5 |
| `shortest_path_viz.py` | A*, Bellman-Ford, BiDijkstra özel görseller | 5 |
| `traversal_viz.py` | DFS ağacı, kenar sınıflandırması | 1 |
| `mst_viz.py` | Kruskal/Prim MST görselleştirme | 3 |
| `flow_viz.py` | Max flow network görselleştirme | 2 |
| `graph_properties_viz.py` | SCC, condensation DAG, topological order | 2 |

### Algoritma-Spesifik Fonksiyonlar (shortest_path_viz.py)

| Fonksiyon | Gösterdiği |
|-----------|-----------|
| `plot_astar_search` | Expanded (closed set) / open set node'lar, heuristic değerler |
| `plot_bellman_ford_result` | Negatif kenarlar (kesik kırmızı), mesafe etiketleri, path highlight |
| `plot_negative_cycle` | Döngü node/kenarları kalın kırmızı, toplam döngü ağırlığı |
| `plot_bidirectional_search` | Forward (mavi) / backward (yeşil) frontier, buluşma noktası (sarı) |
| `plot_shortest_path_comparison` | Dijkstra / A* / BiDijkstra yan yana subplot karşılaştırma |

### DFS Tree Fonksiyonu (traversal_viz.py)

`plot_dfs_tree(graph, source, show_discovery_finish, show_depth)`:
- **Tree edge** — siyah kalın (DFS'in geçtiği kenarlar)
- **Back edge** — kesik kırmızı (ataya işaret eder → döngü kanıtı)
- **Cross/forward edge** — kesik gri (yalnızca DiGraph)
- Node rengi: source=yeşil, döngü node'u=kırmızı, diğerleri derinliğe göre mavi gradyan
- `show_discovery_finish=True`: her node üzerinde `d=X f=Y` zaman damgaları
- `show_depth=True`: recursion derinliği etiketi

### MST Visualization (mst_viz.py)

| Fonksiyon | Gösterdiği |
|-----------|-----------|
| `plot_mst` | MST kenarları yeşil/kalın, non-MST gri; total weight başlıkta |
| `plot_mst_comparison` | Kruskal ve Prim yan yana subplot |
| `plot_kruskal_steps` | Adım adım Kruskal (max 6 subplot), yeni kenar kırmızı |

### Flow Visualization (flow_viz.py)

| Fonksiyon | Gösterdiği |
|-----------|-----------|
| `plot_flow_network` | `flow/capacity` kenar etiketleri; doymuş=kırmızı, kısmi=mavi, boş=gri |
| `plot_flow_paths` | Aktif flow kenarlar (kalınlık ∝ flow); kaynak=yeşil, havuz=turuncu |

### Graph Properties Visualization (graph_properties_viz.py)

| Fonksiyon | Gösterdiği |
|-----------|-----------|
| `plot_scc` | Her SCC farklı renk; intra-SCC kenarlar solid, inter-SCC dashed; `show_condensation=True` ile condensation DAG |
| `plot_topological_order` | Soldan sağa hizalama (`layout='layered'`); node rank numaraları; koyu→açık mavi gradyan |

### Renk Paleti (tüm fonksiyonlarda tutarlı)

| Anlam | Renk |
|-------|------|
| Path / MST edge | `#2ecc71` yeşil |
| Source | `#2ecc71` yeşil |
| Target / Sink | `#e67e22` turuncu |
| Expanded/visited | `#3498db` mavi |
| Unexplored / Non-MST | `#bdc3c7` gri |
| Saturated / Negative / Cycle | `#e74c3c` kırmızı |
| Negative edge (dark) | `#c0392b` koyu kırmızı |
| Meeting point | `#f1c40f` sarı |

---

## Geliştirme Ortamı

```bash
# Kurulum
pip install -e ".[dev,viz]"

# Test
pytest tests/

# Linting
black src/
isort src/
flake8 src/
```

**Bağımlılıklar**: `numpy>=1.20`, `networkx>=2.6`
**Opsiyonel**: `matplotlib>=3.5`, `plotly>=5.0` (viz için)

---

## Roadmap Özeti

| Faz | Versiyon | Hedef | Durum |
|-----|---------|-------|-------|
| Faz 1 | v0.2.0 | BFS/DFS, Utils, Visualization | ✅ Tamamlandı |
| Faz 2 | v0.3.0 | A*, Bellman-Ford, Bidirectional Dijkstra | ✅ Tamamlandı |
| Faz 2.x | v0.3.x | Algoritma-spesifik visualization, DFS tree viz, error handling | ✅ Tamamlandı |
| Faz 3 | v0.4.0 | MST (Kruskal/Prim), Network Flow, SCC, Topological Sort | ✅ Tamamlandı |
| Faz 4 | v0.5.0 | **Breaking the Sorting Barrier SSSP** | 🎯 ANA HEDEF |
| Faz 5 | v0.6.0 | Cython optimizasyonu, paralel işleme | 📋 Planlandı |
| Faz 6 | v1.0.0 | Domain modülleri, production release | 📋 Planlandı |

**Hedef v1.0.0**: Eylül 2026

---

## Breaking the Sorting Barrier — Ana Hedef

**Makale**: Duan, Mao, Mao, Shu, Yin (2025) — arXiv:2504.17033v2
**Kompleksite hedefi**: Dijkstra'nın O(m + n log n) sınırını kırmak
**Kapsam**: Directed graphs, non-negative integer weights

Makale henüz detaylı incelenmedi. Implementasyon planı `docs/breaking_barrier_research.md` içinde.
Makale PDF'i: `docs/Breaking the Sorting Barrier for Directed Single-Source Shortest.pdf`

---

## Bilinen Sorunlar / Dikkat Edilecekler

1. **test_viz_integration.py** — `matplotlib` yüklü olmayan ortamlarda import hatası verir; integration testler `pytest tests/unit/` ile ayrı çalıştırılmalı.
2. Dijkstra'da `graph.neighbors()` kullanımı — DiGraph'ta sadece out-edges döner, bu beklenen davranış.
3. Yeni visualization fonksiyonları (`mst_viz.py`, `flow_viz.py`, `graph_properties_viz.py`) için unit test henüz yazılmadı.
4. `prim.py` içindeki `_find_component` fonksiyonu dead code — bir sonraki cleanup'ta silinebilir.

---

## Bu Dosya Hakkında

CLAUDE.md proje süresince güncel tutulmalıdır. Her önemli değişiklikten sonra:
- Tamamlanan özellikler "Mevcut Durum" tablosuna işlenir
- Yeni bilinen sorunlar eklenir
- Roadmap durumu güncellenir
