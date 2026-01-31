"""
Utils Module - Showcase Examples
=================================

This example demonstrates the utility functions.
"""

import logarithma as lg
from logarithma.utils import *
import networkx as nx


def example_1_graph_generators():
    """Example 1: Generate different types of graphs"""
    print("=" * 60)
    print("Example 1: Graph Generators")
    print("=" * 60)
    
    # Random graph
    random_g = generate_random_graph(50, edge_probability=0.1)
    print(f"\nRandom Graph (Erdős-Rényi):")
    print(f"  Nodes: {random_g.number_of_nodes()}")
    print(f"  Edges: {random_g.number_of_edges()}")
    
    # Grid graph (for pathfinding)
    grid = generate_grid_graph(10, 10, diagonal=True)
    print(f"\nGrid Graph (10x10 with diagonals):")
    print(f"  Nodes: {grid.number_of_nodes()}")
    print(f"  Edges: {grid.number_of_edges()}")
    
    # Scale-free graph (social network)
    social = generate_scale_free_graph(100)
    print(f"\nScale-Free Graph (social network):")
    print(f"  Nodes: {social.number_of_nodes()}")
    print(f"  Edges: {social.number_of_edges()}")


def example_2_validators():
    """Example 2: Validate graph properties"""
    print("\n" + "=" * 60)
    print("Example 2: Graph Validators")
    print("=" * 60)
    
    # Create test graphs
    connected_g = generate_path_graph(10)
    disconnected_g = nx.Graph()
    disconnected_g.add_edges_from([(1, 2), (3, 4)])
    
    print(f"\nPath graph (10 nodes):")
    print(f"  Connected: {is_connected(connected_g)}")
    print(f"  Has cycles: {not is_dag(connected_g.to_directed())}")
    
    print(f"\nDisconnected graph:")
    print(f"  Connected: {is_connected(disconnected_g)}")
    
    # Validate requirements
    requirements = {
        'connected': True,
        'no_negative_weights': True,
        'min_nodes': 5
    }
    
    result = validate_graph(connected_g, requirements)
    print(f"\nValidation result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")


def example_3_converters():
    """Example 3: Convert between formats"""
    print("\n" + "=" * 60)
    print("Example 3: Format Converters")
    print("=" * 60)
    
    # Create graph
    G = nx.Graph()
    G.add_edge('A', 'B', weight=5)
    G.add_edge('B', 'C', weight=3)
    G.add_edge('A', 'C', weight=8)
    
    # Convert to edge list
    edge_list = to_edge_list(G)
    print(f"\nEdge list format:")
    for edge in edge_list:
        print(f"  {edge}")
    
    # Convert to dictionary
    graph_dict = to_dict(G)
    print(f"\nDictionary format:")
    for node, neighbors in graph_dict.items():
        print(f"  {node}: {neighbors}")
    
    # Convert to adjacency matrix
    matrix = to_adjacency_matrix(G)
    print(f"\nAdjacency matrix shape: {matrix.shape}")


def example_4_metrics():
    """Example 4: Calculate graph metrics"""
    print("\n" + "=" * 60)
    print("Example 4: Graph Metrics")
    print("=" * 60)
    
    # Create a small social network
    network = generate_scale_free_graph(30, seed=42)
    
    # Calculate metrics
    density = graph_density(network)
    avg_deg = average_degree(network)
    
    print(f"\nNetwork metrics:")
    print(f"  Density: {density:.3f}")
    print(f"  Average degree: {avg_deg:.2f}")
    
    # Centrality measures
    deg_cent = degree_centrality(network)
    top_nodes = sorted(deg_cent.items(), key=lambda x: x[1], reverse=True)[:3]
    
    print(f"\nMost connected nodes:")
    for node, centrality in top_nodes:
        print(f"  Node {node}: {centrality:.3f}")


def example_5_graph_summary():
    """Example 5: Comprehensive graph summary"""
    print("\n" + "=" * 60)
    print("Example 5: Graph Summary")
    print("=" * 60)
    
    # Create test graph
    G = generate_small_world_graph(50, k=4, p=0.1, seed=42)
    
    # Get comprehensive summary
    summary = graph_summary(G)
    
    print(f"\nGraph Summary:")
    print(f"  Nodes: {summary['nodes']}")
    print(f"  Edges: {summary['edges']}")
    print(f"  Density: {summary['density']:.4f}")
    print(f"  Average degree: {summary['average_degree']:.2f}")
    print(f"  Connected: {summary['is_connected']}")
    
    if summary['diameter']:
        print(f"  Diameter: {summary['diameter']}")
        print(f"  Avg path length: {summary['average_path_length']:.2f}")


def example_6_real_world_workflow():
    """Example 6: Complete workflow"""
    print("\n" + "=" * 60)
    print("Example 6: Complete Workflow")
    print("=" * 60)
    
    print("\n1. Generate graph")
    G = generate_random_graph(30, edge_probability=0.15, seed=42)
    print(f"   Created graph with {G.number_of_nodes()} nodes")
    
    print("\n2. Validate graph")
    requirements = {
        'connected': True,
        'no_negative_weights': True
    }
    validation = validate_graph(G, requirements)
    print(f"   Valid: {validation['valid']}")
    
    if not validation['valid']:
        print(f"   Errors: {validation['errors']}")
    else:
        print("\n3. Calculate metrics")
        summary = graph_summary(G)
        print(f"   Density: {summary['density']:.3f}")
        print(f"   Diameter: {summary['diameter']}")
        
        print("\n4. Find shortest paths")
        distances = lg.dijkstra(G, 0)
        max_dist_node = max(distances.items(), key=lambda x: x[1])
        print(f"   Farthest node from 0: {max_dist_node[0]} (distance: {max_dist_node[1]:.2f})")
        
        print("\n5. Export graph")
        edge_list = to_edge_list(G)
        print(f"   Exported {len(edge_list)} edges")


if __name__ == "__main__":
    print("\n" + "🔷" * 30)
    print("LOGARITHMA - Utils Module Showcase")
    print("🔷" * 30)
    
    example_1_graph_generators()
    example_2_validators()
    example_3_converters()
    example_4_metrics()
    example_5_graph_summary()
    example_6_real_world_workflow()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60 + "\n")
