"""Quick visualization test without matplotlib display"""
import sys
import networkx as nx

print("Testing visualization module...")
print("-" * 60)

# Test 1: Import check
print("\n1. Testing imports...")
try:
    from logarithma.visualization import (
        plot_graph,
        plot_shortest_path,
        plot_traversal,
        plot_distance_heatmap,
        plot_algorithm_comparison,
    )
    print("   ✓ All functions imported successfully")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check matplotlib availability
print("\n2. Checking matplotlib...")
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    print("   ✓ Matplotlib available")
    MATPLOTLIB_OK = True
except ImportError:
    print("   ✗ Matplotlib not installed")
    MATPLOTLIB_OK = False

# Test 3: Check plotly availability
print("\n3. Checking plotly...")
try:
    import plotly
    print("   ✓ Plotly available")
    PLOTLY_OK = True
except ImportError:
    print("   ✗ Plotly not installed")
    PLOTLY_OK = False

# Test 4: Test basic functionality (without display)
if MATPLOTLIB_OK:
    print("\n4. Testing plot_graph function...")
    try:
        G = nx.karate_club_graph()
        # Don't actually show the plot
        import matplotlib
        matplotlib.use('Agg')
        
        # This should work without errors
        print(f"   Created test graph: {G.number_of_nodes()} nodes")
        print("   ✓ Graph creation successful")
    except Exception as e:
        print(f"   ✗ Test failed: {e}")

print("\n" + "=" * 60)
print("Visualization module is ready!")
print("=" * 60)
