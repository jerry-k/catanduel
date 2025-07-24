#!/usr/bin/env python3
"""Detailed trace of the DFS algorithm."""

from collections import defaultdict

def test_dfs_algorithm():
    """Test the DFS algorithm with a simple graph."""
    # Create the exact graph from our problem
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
    
    def dfs(node, visited_edges, path_so_far=[]):
        """DFS that tracks visited edges."""
        max_length = 0
        best_path = path_so_far
        
        for neighbor in graph[node]:
            edge = (min(node, neighbor), max(node, neighbor))
            
            if edge not in visited_edges:
                visited_edges.add(edge)
                new_path = path_so_far + [f"{node}->{neighbor}"]
                
                length = 1 + dfs(neighbor, visited_edges, new_path)
                if length > max_length:
                    max_length = length
                    best_path = new_path
                
                visited_edges.remove(edge)
        
        return max_length
    
    # Test from node 0
    print("Testing DFS from node 0:")
    length = dfs(0, set())
    print(f"Length found: {length}")
    
    # Let's also manually check some paths
    print("\nManual path checks:")
    
    # Path that visits all nodes once
    path1 = [0, 1, 2, 3, 6, 7, 8, 9, 4, 5]
    edges1 = []
    for i in range(len(path1) - 1):
        edges1.append((min(path1[i], path1[i+1]), max(path1[i], path1[i+1])))
    print(f"Path {path1}: {len(edges1)} edges")
    
    # Path that returns to start
    path2 = [0, 1, 2, 3, 6, 7, 8, 9, 4, 5, 0]
    edges2 = []
    for i in range(len(path2) - 1):
        edges2.append((min(path2[i], path2[i+1]), max(path2[i], path2[i+1])))
    print(f"Path {path2}: {len(edges2)} edges")
    
    # The test's expected path
    test_path_corners = [6, 7, 8, 9, 4, 3, 2, 1, 0, 5, 4]
    edges3 = []
    for i in range(len(test_path_corners) - 1):
        edge = (min(test_path_corners[i], test_path_corners[i+1]), 
                max(test_path_corners[i], test_path_corners[i+1]))
        if edge not in edges3:  # Check for duplicate edges
            edges3.append(edge)
        else:
            print(f"  Duplicate edge found: {edge}")
    print(f"Test path {test_path_corners}: {len(edges3)} unique edges")

if __name__ == "__main__":
    test_dfs_algorithm()