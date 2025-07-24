#!/usr/bin/env python3
"""Final debug to understand the discrepancy."""

from collections import defaultdict
from engine.colonist_map import EDGE_TO_CORNERS

def find_all_paths_length_10():
    """Find all possible paths of length 10 in the graph."""
    # Build adjacency list with edge tracking
    edges = {}
    graph = defaultdict(list)
    
    for edge_id in range(11):
        c1, c2 = EDGE_TO_CORNERS[edge_id]
        edges[(min(c1, c2), max(c1, c2))] = edge_id
        graph[c1].append((c2, edge_id))
        graph[c2].append((c1, edge_id))
    
    def dfs(node, visited_edges, path, edge_path):
        if len(edge_path) == 10:
            return [(list(path), list(edge_path))]
        
        all_paths = []
        for neighbor, edge_id in graph[node]:
            if edge_id not in visited_edges:
                visited_edges.add(edge_id)
                path.append(neighbor)
                edge_path.append(edge_id)
                
                all_paths.extend(dfs(neighbor, visited_edges, path, edge_path))
                
                edge_path.pop()
                path.pop()
                visited_edges.remove(edge_id)
        
        return all_paths
    
    # Find all paths of length 10
    all_10_paths = []
    for start in range(10):
        paths = dfs(start, set(), [start], [])
        all_10_paths.extend(paths)
    
    print(f"Found {len(all_10_paths)} paths of length 10")
    
    # Check the specific paths from the test
    test_path1_edges = [7, 8, 9, 10, 3, 2, 1, 0, 5, 4]
    test_path2_edges = [4, 5, 0, 1, 2, 3, 10, 9, 8, 7]
    
    print("\nChecking test paths:")
    for i, test_edges in enumerate([test_path1_edges, test_path2_edges], 1):
        found = False
        for path, edge_path in all_10_paths:
            if edge_path == test_edges:
                print(f"  Test path {i}: FOUND")
                print(f"    Corners: {path}")
                found = True
                break
        if not found:
            # Check if it's a valid path at all
            print(f"  Test path {i}: Checking validity...")
            current = None
            valid = True
            for j, edge_id in enumerate(test_edges):
                c1, c2 = EDGE_TO_CORNERS[edge_id]
                if j == 0:
                    print(f"    Starting with edge {edge_id}: {c1}-{c2}")
                else:
                    if current == c1:
                        current = c2
                    elif current == c2:
                        current = c1
                    else:
                        print(f"    INVALID at edge {edge_id}")
                        valid = False
                        break
            
            if valid:
                print(f"    Path is valid but not found in DFS")

if __name__ == "__main__":
    find_all_paths_length_10()