#!/usr/bin/env python3
"""Debug the DFS to see why it returns 11."""

from collections import defaultdict

# Create the exact graph
graph = defaultdict(set)
graph[0] = {1, 5}
graph[1] = {0, 2}
graph[2] = {1, 3}
graph[3] = {2, 4, 6}
graph[4] = {3, 5, 9}
graph[5] = {0, 4}
graph[6] = {3, 7}
graph[7] = {6, 8}
graph[8] = {7, 9}
graph[9] = {4, 8}

def dfs_debug(node, visited_edges, depth=0, indent=""):
    """DFS with debug output."""
    if depth > 11:  # Safety check
        return 0
        
    max_length = 0
    
    for neighbor in sorted(graph[node]):  # Sort for consistent output
        edge = (min(node, neighbor), max(node, neighbor))
        
        if edge not in visited_edges:
            visited_edges.add(edge)
            
            result = 1 + dfs_debug(neighbor, visited_edges, depth + 1, indent + "  ")
            
            if result > max_length:
                max_length = result
                
            visited_edges.remove(edge)
    
    if depth <= 2:  # Only print first few levels
        print(f"{indent}Node {node}: max_length = {max_length}")
    
    return max_length

print("Running DFS with debug output...")
print("\nStarting from node 0:")
result = dfs_debug(0, set())
print(f"\nFinal result: {result}")

# Let's also check if there's a path that uses all 11 edges
print("\n\nChecking if all 11 edges can form a valid path...")
all_edges = set()
for node, neighbors in graph.items():
    for neighbor in neighbors:
        edge = (min(node, neighbor), max(node, neighbor))
        all_edges.add(edge)

print(f"Total unique edges: {len(all_edges)}")
print("Edges:", sorted(all_edges))

# In a graph with 10 nodes and 11 edges, we have 2 cycles
# The maximum path length should be 10 (visiting some node twice)
print("\nGraph analysis:")
print("- 10 nodes, 11 edges")
print("- This creates a graph with 2 independent cycles")
print("- Maximum simple path (no repeated edges) cannot use all 11 edges")
print("- The algorithm might be counting something incorrectly")