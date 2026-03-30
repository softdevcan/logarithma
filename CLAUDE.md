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

### Versiyon: 0.2.0

**⚠️ Dikkat**: README.md hâlâ "Current Version: 0.1.0" yazıyor — güncel değil. Gerçek versiyon `src/logarithma/__init__.py` ve `pyproject.toml`'da 0.2.0.

### Implement Edilmiş Özellikler

| Modül | Fonksiyonlar | Durum |
|-------|-------------|-------|
| `dijkstra` | `dijkstra()`, `dijkstra_with_path()` | ✅ Tamamlandı |
| `bfs` | `bfs()`, `bfs_path()` | ✅ Tamamlandı |
| `dfs` | `dfs()`, `dfs_path()`, `detect_cycle()` | ✅ Tamamlandı |
| `utils.generators` | 9 fonksiyon (random, grid, complete, tree...) | ✅ Tamamlandı |
| `utils.validators` | 8 fonksiyon (connected, DAG, negative weights...) | ✅ Tamamlandı |
| `utils.converters` | 8 fonksiyon (adj matrix, edge list, graphml...) | ✅ Tamamlandı |
| `utils.metrics` | 9 fonksiyon (density, diameter, centrality...) | ✅ Tamamlandı |
| `visualization` | 10 fonksiyon (plot_graph, plot_shortest_path...) | ⚠️ Dosyalar var, git'e eklenmemiş |

### Henüz Yapılmamışlar (Roadmap)

- ❌ A* algoritması
- ❌ Bellman-Ford
- ❌ Bidirectional Dijkstra
- ❌ Floyd-Warshall / Johnson's
- ❌ Kruskal / Prim MST
- ❌ Tarjan SCC
- ❌ Topological Sort
- ❌ Ford-Fulkerson / Edmonds-Karp
- 🎯 **Breaking the Sorting Barrier SSSP** (arXiv:2504.17033v2) — ANA HEDEF

---

## Proje Yapısı

```
logarithma/
├── src/logarithma/
│   ├── __init__.py               # v0.2.0, public API exports
│   ├── algorithms/
│   │   ├── shortest_path/
│   │   │   └── dijkstra.py       # Dijkstra + dijkstra_with_path
│   │   └── traversal/
│   │       ├── bfs.py            # bfs + bfs_path
│   │       └── dfs.py            # dfs + dfs_path + detect_cycle
│   ├── utils/
│   │   ├── graph_generators.py   # 9 generator fonksiyon
│   │   ├── validators.py         # 8 validator fonksiyon
│   │   ├── converters.py         # 8 converter fonksiyon
│   │   └── metrics.py            # 9 metrics fonksiyon
│   └── visualization/            # Git'e eklenmemiş (untracked)
│       ├── graph_plotter.py      # Statik görselleştirme
│       └── algorithm_viz.py      # Algoritma karşılaştırma grafikleri
├── tests/
│   ├── unit/
│   │   ├── test_dijkstra.py      # 17+ test case
│   │   └── test_visualization.py # Untracked
│   ├── integration/
│   │   └── test_viz_integration.py # Untracked
│   └── benchmarks/
│       ├── benchmark_shortest_path.py
│       └── framework.py
├── docs/
│   ├── ALGORITHM_ROADMAP.md      # Detaylı algoritma planı
│   ├── breaking_barrier_research.md  # Makale analiz planı
│   └── PROJECT_STRUCTURE.md
├── pyproject.toml                # Build config, dependencies
├── CHANGELOG.md
└── CLAUDE.md                     # Bu dosya
```

---

## Public API

```python
import logarithma as lg

# Shortest Path
lg.dijkstra(G, source)
lg.dijkstra_with_path(G, source, target=None)

# Traversal
lg.bfs(G, source)
lg.bfs_path(G, source, target=None)
lg.dfs(G, source)
lg.dfs_path(G, source, target)
lg.detect_cycle(G)

# Utils (ayrı import gerekir)
from logarithma.utils import generate_random_graph, graph_summary, ...
from logarithma.visualization import plot_graph, plot_shortest_path, ...
```

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
| Faz 1 | v0.2.0 | BFS/DFS, Utils, Visualization | ✅ Büyük ölçüde tamamlandı |
| Faz 2 | v0.3.0 | A*, Bellman-Ford, Bidirectional Dijkstra | ⏳ Sıradaki |
| Faz 3 | v0.4.0 | MST (Kruskal/Prim), Network Flow, SCC | 📋 Planlandı |
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

1. **README.md güncel değil** — "v0.1.0" yazıyor, visualization ve utils "Coming Soon" olarak listeleniyor.
2. **Visualization modülü git'e eklenmemiş** — `git status` untracked gösteriyor.
3. **test_visualization.py ve test_viz_integration.py** untracked — test coverage eksik.
4. `examples/visualization/` dizini untracked.
5. Dijkstra'da `graph.neighbors()` kullanımı — DiGraph'ta sadece out-edges döner, bu beklenen davranış.

---

## Bu Dosya Hakkında

CLAUDE.md proje süresince güncel tutulmalıdır. Her önemli değişiklikten sonra:
- Tamamlanan özellikler "Mevcut Durum" tablosuna işlenir
- Yeni bilinen sorunlar eklenir
- Roadmap durumu güncellenir
