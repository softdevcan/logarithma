"""
Basic Graph Plotting Examples
==============================

This example demonstrates basic graph visualization using the logarithma library.
"""

import networkx as nx
from logarithma.visualization import plot_graph, plot_graph_interactive
from logarithma.utils import generate_random_graph

print("=" * 60)
print("LOGARITHMA - Basic Graph Plotting Examples")
print("=" * 60)

# Example 1: Plot a simple graph
print("\n1. Simple Graph Visualization")
print("-" * 60)

G = nx.karate_club_graph()
print(f"Created Karate Club graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Plot with different layouts
print("\nPlotting with spring layout...")
plot_graph(G, layout="spring", title="Karate Club - Spring Layout", node_size=300)

print("\nPlotting with circular layout...")
plot_graph(G, layout="circular", title="Karate Club - Circular Layout", node_size=300)

# Example 2: Plot a weighted random graph
print("\n2. Weighted Random Graph")
print("-" * 60)

G_random = generate_random_graph(20, 0.2, weighted=True, seed=42)
print(f"Created random graph: {G_random.number_of_nodes()} nodes, {G_random.number_of_edges()} edges")

plot_graph(G_random, layout="kamada_kawai", title="Random Weighted Graph", 
          node_size=500, node_color='lightcoral')

# Example 3: Interactive visualization (requires plotly)
print("\n3. Interactive Graph (Plotly)")
print("-" * 60)

try:
    fig = plot_graph_interactive(G, layout="spring", title="Interactive Karate Club Network")
    print("Interactive plot created! Check your browser.")
    # Uncomment to save as HTML
    # fig.write_html("karate_club_interactive.html")
except ImportError as e:
    print(f"Skipping interactive plot: {e}")
    print("Install plotly with: pip install plotly")

# Example 4: Grid graph
print("\n4. Grid Graph Visualization")
print("-" * 60)

from logarithma.utils import generate_grid_graph

G_grid = generate_grid_graph(5, 5)
print(f"Created 5x5 grid: {G_grid.number_of_nodes()} nodes, {G_grid.number_of_edges()} edges")

plot_graph(G_grid, layout="kamada_kawai", title="5x5 Grid Graph",
          node_size=400, node_color='lightgreen')

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
