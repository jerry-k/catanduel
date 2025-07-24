#!/usr/bin/env python3
"""Test with exact copy of board code."""

from collections import defaultdict
from typing import Dict, Set, Tuple

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

# Exact copy of the _find_longest_path method from board.py
def _find_longest_path(graph: Dict[int, Set[int]]) -> int:
    """
    Find the longest path in an undirected graph.
    
    In Catan, the longest road allows revisiting corners but not edges.
    Uses DFS tracking visited edges instead of visited nodes.
    """
    if not graph:
        return 0
    
    def dfs(node: int, visited_edges: Set[Tuple[int, int]]) -> int:
        """DFS that tracks visited edges instead of nodes."""
        max_length = 0
        
        for neighbor in graph[node]:
            # Create edge tuple (smaller_id, larger_id) for consistency
            edge = (min(node, neighbor), max(node, neighbor))
            
            if edge not in visited_edges:
                visited_edges.add(edge)
                length = 1 + dfs(neighbor, visited_edges)
                max_length = max(max_length, length)
                visited_edges.remove(edge)
        
        return max_length
    
    # Try starting from each node
    max_path = 0
    for start_node in list(graph.keys()):
        path_length = dfs(start_node, set())
        max_path = max(max_path, path_length)
    
    return max_path

# Test it
result = _find_longest_path(graph)
print(f"Result from exact copy of board code: {result}")

# Let's add some debug to see what's happening
def dfs_with_tracking(node, visited_edges, path=[]):
    """Modified DFS that tracks the actual path."""
    max_length = 0
    best_path = list(path)
    
    for neighbor in graph[node]:
        edge = (min(node, neighbor), max(node, neighbor))
        
        if edge not in visited_edges:
            visited_edges.add(edge)
            new_path = path + [neighbor]
            
            length = 1 + dfs_with_tracking(neighbor, visited_edges, new_path)
            if length > max_length:
                max_length = length
                best_path = new_path
                
            visited_edges.remove(edge)
    
    return max_length

# Find which starting node gives us the longest path
print("\nTesting from each start node:")
for start in sorted(graph.keys()):
    length = dfs_with_tracking(start, set(), [start])
    print(f"  From node {start}: length = {length}")
    if length == 11:
        print("    Found the 11-length path!")