#!/usr/bin/env python3
"""Analyze the exact road network structure."""

from collections import defaultdict
from engine.colonist_map import EDGE_TO_CORNERS

def analyze_network():
    """Analyze the road network structure for edges 0-10."""
    print("Edge connections for roads 0-10:")
    edges = []
    for edge_id in range(11):
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        edges.append((edge_id, corner1, corner2))
        print(f"  Edge {edge_id}: {corner1} <-> {corner2}")
    
    print(f"\nTotal edges: {len(edges)}")
    
    # Build adjacency list
    graph = defaultdict(set)
    for _, c1, c2 in edges:
        graph[c1].add(c2)
        graph[c2].add(c1)
    
    # Find if there's a Hamiltonian path (visiting all nodes exactly once)
    all_nodes = set(graph.keys())
    print(f"\nNodes in graph: {sorted(all_nodes)}")
    print(f"Number of nodes: {len(all_nodes)}")
    
    # A Hamiltonian path in a graph with N nodes has N-1 edges
    print(f"\nFor a Hamiltonian path through {len(all_nodes)} nodes, we need {len(all_nodes)-1} edges")
    
    # Check actual connectivity
    print("\nNode degrees:")
    for node in sorted(graph.keys()):
        print(f"  Node {node}: degree {len(graph[node])} (connects to {sorted(graph[node])})")
    
    # The issue might be about counting roads vs counting edges in longest path
    print("\n\nKey insight:")
    print("- We have 11 roads (edges 0-10)")
    print("- The graph has 10 unique corners")
    print("- A path visiting all 10 corners uses 9 edges")
    print("- But the test expects 10, not 11 or 9")
    print("\nPossible explanation: Maybe one road doesn't contribute to the longest path?")

if __name__ == "__main__":
    analyze_network()