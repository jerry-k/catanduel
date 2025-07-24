#!/usr/bin/env python3
"""Trace the longest path algorithm in detail."""

from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS
from collections import defaultdict


def trace_find_longest_path(graph):
    """
    Trace the longest path algorithm step by step.
    This is a copy of Board._find_longest_path with added debugging.
    """
    if not graph:
        return 0
    
    def dfs(node, visited, depth=0):
        indent = "  " * depth
        print(f"{indent}DFS at node {node}, visited: {sorted(visited)}")
        
        visited.add(node)
        max_length = 0
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                print(f"{indent}  Exploring neighbor {neighbor}")
                length = dfs(neighbor, visited, depth + 1)
                if length > max_length:
                    print(f"{indent}  New max from {neighbor}: {length}")
                max_length = max(max_length, length)
            else:
                print(f"{indent}  Skipping visited neighbor {neighbor}")
        
        visited.remove(node)
        result = max_length + 1
        print(f"{indent}Returning {result} from node {node}")
        return result
    
    # Try starting from each node
    max_path = 0
    for start_node in list(graph.keys()):
        print(f"\n\nStarting from node {start_node}:")
        path_length = dfs(start_node, set())
        print(f"Path length from {start_node}: {path_length}")
        if path_length > max_path:
            max_path = path_length
            print(f"New maximum path: {max_path}")
    
    # Convert from nodes to edges (roads)
    return max_path - 1 if max_path > 0 else 0


def main():
    """Debug longest road calculation with detailed tracing."""
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
    player_roads = board.get_player_roads(0)
    
    for edge_id in player_roads:
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        road_graph[corner1].add(corner2)
        road_graph[corner2].add(corner1)
    
    print("Road graph:")
    for corner, neighbors in sorted(road_graph.items()):
        print(f"  Corner {corner}: {sorted(neighbors)}")
    
    # Trace the algorithm
    print("\n\nTracing _find_longest_path algorithm:")
    longest = trace_find_longest_path(road_graph)
    print(f"\n\nFinal longest path: {longest} roads")
    
    # Let me manually find the longest path
    print("\n\nManual path check:")
    print("Path 1: 6 -> 7 -> 8 -> 9 -> 4 -> 5 -> 0 -> 1 -> 2 -> 3")
    print("This is 9 edges (10 corners)")
    
    print("\nPath 2: 6 -> 3 -> 2 -> 1 -> 0 -> 5 -> 4 -> 9 -> 8 -> 7")
    print("This is also 9 edges (10 corners)")
    
    print("\nThe graph forms a figure-8 shape with a loop and a branch.")
    print("Maximum possible path visits all 10 corners exactly once, using 9 edges.")


if __name__ == "__main__":
    main()