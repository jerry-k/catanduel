#!/usr/bin/env python3
"""Debug what path the algorithm is actually finding."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

def debug_dfs_with_path_tracking():
    """Modified version of the algorithm that tracks the actual path."""
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
    
    def dfs_with_path(node, visited_edges, path_edges):
        """Modified DFS that tracks the path."""
        max_length = 0
        best_path = list(path_edges)
        
        for neighbor in road_graph[node]:
            edge = (min(node, neighbor), max(node, neighbor))
            
            if edge not in visited_edges:
                visited_edges.add(edge)
                path_edges.append((node, neighbor))
                
                length, sub_path = dfs_with_path(neighbor, visited_edges, path_edges)
                if 1 + length > max_length:
                    max_length = 1 + length
                    best_path = sub_path
                
                path_edges.pop()
                visited_edges.remove(edge)
        
        return max_length, best_path
    
    print("Finding longest path with path tracking...")
    max_overall = 0
    best_path_edges = []
    best_start = None
    
    for start_node in sorted(road_graph.keys()):
        length, path = dfs_with_path(start_node, set(), [])
        if length > max_overall:
            max_overall = length
            best_path_edges = path
            best_start = start_node
    
    print(f"\nLongest path found: {max_overall} edges")
    print(f"Starting from corner: {best_start}")
    
    if best_path_edges:
        print("\nPath edges (corner pairs):")
        corners_in_path = [best_start]
        for i, (c1, c2) in enumerate(best_path_edges):
            print(f"  Edge {i+1}: {c1} → {c2}")
            if c1 == corners_in_path[-1]:
                corners_in_path.append(c2)
            else:
                corners_in_path.append(c1)
        
        print(f"\nCorners visited: {' → '.join(map(str, corners_in_path))}")
        
        # Map back to actual edge IDs
        print("\nActual road edges used:")
        edge_ids_used = []
        for c1, c2 in best_path_edges:
            # Find which edge ID connects these corners
            for edge_id in range(11):
                e1, e2 = EDGE_TO_CORNERS[edge_id]
                if (e1 == c1 and e2 == c2) or (e1 == c2 and e2 == c1):
                    edge_ids_used.append(edge_id)
                    print(f"  Edge {edge_id}: {c1} <-> {c2}")
                    break
        
        print(f"\nEdge IDs in order: {edge_ids_used}")
        print(f"Total edges used: {len(edge_ids_used)}")

if __name__ == "__main__":
    debug_dfs_with_path_tracking()