#!/usr/bin/env python3
"""Find the exact 11-edge path."""

from collections import defaultdict

# Create the graph
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

def find_path_of_length(start, target_length):
    """Find a path of specific length from start node."""
    
    def dfs(node, visited_edges, path, edges_used):
        if len(edges_used) == target_length:
            return path, edges_used
        
        for neighbor in sorted(graph[node]):
            edge = (min(node, neighbor), max(node, neighbor))
            
            if edge not in visited_edges:
                visited_edges.add(edge)
                
                result = dfs(neighbor, visited_edges, path + [neighbor], edges_used + [edge])
                if result:
                    return result
                    
                visited_edges.remove(edge)
        
        return None
    
    return dfs(start, set(), [start], [])

# Find the 11-edge path starting from node 3
print("Finding 11-edge path from node 3...")
result = find_path_of_length(3, 11)

if result:
    path, edges = result
    print(f"\nPath found: {' → '.join(map(str, path))}")
    print(f"Number of nodes in path: {len(path)}")
    print(f"Number of edges: {len(edges)}")
    
    # Check for repeated nodes
    unique_nodes = set(path)
    if len(unique_nodes) < len(path):
        print(f"\nPath visits {len(unique_nodes)} unique nodes")
        print("Repeated nodes:")
        node_counts = {}
        for node in path:
            node_counts[node] = node_counts.get(node, 0) + 1
        for node, count in node_counts.items():
            if count > 1:
                print(f"  Node {node}: visited {count} times")
    
    # Verify all edges are unique
    unique_edges = set(edges)
    print(f"\nUnique edges: {len(unique_edges)} (should be {len(edges)})")
    
    if len(unique_edges) == 11:
        print("\nThis path uses ALL 11 edges in the graph!")
        print("This should not be possible in a simple path...")
        
        # Let's trace through the path
        print("\nPath details:")
        for i, edge in enumerate(edges):
            print(f"  Step {i+1}: Edge {edge}")
else:
    print("No 11-edge path found!")