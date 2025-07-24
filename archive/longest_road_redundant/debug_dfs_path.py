#!/usr/bin/env python3
"""Debug the DFS path finding algorithm."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

def debug_dfs():
    """Debug the DFS algorithm with detailed tracing."""
    # Create a board
    board = Board()
    
    # Place settlements at corners 0 and 2 for player 0
    board.buildings[0] = (0, SETTLEMENT)
    board.buildings[2] = (0, SETTLEMENT)
    
    # Place roads on edges 0-10 for player 0
    for edge in range(11):
        board.roads[edge] = 0
    
    # Build the road graph
    road_graph = defaultdict(set)
    for edge_id in range(11):
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        road_graph[corner1].add(corner2)
        road_graph[corner2].add(corner1)
    
    print("Road graph:")
    for corner, neighbors in sorted(road_graph.items()):
        print(f"  Corner {corner}: {sorted(neighbors)}")
    
    # Test DFS from different starting points
    def dfs_with_path(node, visited, path):
        """Modified DFS that tracks the actual path."""
        visited.add(node)
        path.append(node)
        
        max_length = 0
        best_path = list(path)
        
        for neighbor in road_graph[node]:
            if neighbor not in visited:
                sub_length, sub_path = dfs_with_path(neighbor, visited, path)
                if sub_length > max_length:
                    max_length = sub_length
                    best_path = sub_path
        
        visited.remove(node)
        path.pop()
        
        return max_length + 1, best_path
    
    print("\nDFS from each starting corner:")
    max_overall = 0
    best_overall_path = []
    
    for start_node in sorted(road_graph.keys()):
        length, path = dfs_with_path(start_node, set(), [])
        print(f"  From corner {start_node}: length={length}, path={path[:10]}{'...' if len(path) > 10 else ''}")
        if length > max_overall:
            max_overall = length
            best_overall_path = path
    
    print(f"\nLongest path found by DFS:")
    print(f"  Length: {max_overall} nodes = {max_overall - 1} edges")
    print(f"  Path: {' → '.join(map(str, best_overall_path))}")
    
    # Verify it's a valid path
    print("\nVerifying path connectivity:")
    valid = True
    for i in range(len(best_overall_path) - 1):
        curr = best_overall_path[i]
        next = best_overall_path[i + 1]
        if next in road_graph[curr]:
            print(f"  {curr} → {next} ✓")
        else:
            print(f"  {curr} → {next} ✗")
            valid = False
    
    print(f"\nPath is {'valid' if valid else 'invalid'}")
    
    # Check why it's not finding the 10-edge path
    print("\nChecking specific 10-edge path: 5→4→9→8→7→6→3→2→1→0→5")
    path_to_check = [5, 4, 9, 8, 7, 6, 3, 2, 1, 0]
    print("This path visits corners:", path_to_check)
    print("Number of edges:", len(path_to_check) - 1, " (should be 9)")
    print("But wait, we can continue from 0 back to 5, making it 10 edges total!")
    print("However, DFS won't do this because it marks nodes as visited")

if __name__ == "__main__":
    debug_dfs()