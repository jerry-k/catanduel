#!/usr/bin/env python3
"""Debug the longest road calculation."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

def debug_longest_road():
    """Debug the longest road calculation with detailed graph analysis."""
    # Create a board
    board = Board()
    
    # Place settlements at corners 0 and 2 for player 0
    board.buildings[0] = (0, SETTLEMENT)
    board.buildings[2] = (0, SETTLEMENT)
    
    # Place roads on edges 0-10 for player 0
    for edge in range(11):
        board.roads[edge] = 0
    
    # Build the road graph manually to see what's happening
    road_graph = defaultdict(set)
    player_roads = board.get_player_roads(0)
    
    print("Building road graph for player 0:")
    print(f"Player has settlements at: {[c for c, (p, _) in board.buildings.items() if p == 0]}")
    print(f"Player has roads on edges: {player_roads}")
    print()
    
    for edge_id in player_roads:
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        
        # Check if corners are blocked
        blocked1 = board._is_corner_blocked(corner1, 0)
        blocked2 = board._is_corner_blocked(corner2, 0)
        
        print(f"Edge {edge_id}: {corner1} <-> {corner2}")
        print(f"  Corner {corner1} blocked: {blocked1}")
        print(f"  Corner {corner2} blocked: {blocked2}")
        
        if not blocked1 and not blocked2:
            road_graph[corner1].add(corner2)
            road_graph[corner2].add(corner1)
            print(f"  Added bidirectional connection")
        elif not blocked1 and blocked2:
            road_graph[corner1].add(corner2)
            print(f"  Added one-way connection from {corner1} to {corner2}")
        elif blocked1 and not blocked2:
            road_graph[corner2].add(corner1)
            print(f"  Added one-way connection from {corner2} to {corner1}")
        else:
            print(f"  No connection added (both blocked)")
    
    print("\nFinal road graph:")
    for corner, neighbors in sorted(road_graph.items()):
        print(f"  Corner {corner}: {sorted(neighbors)}")
    
    # Calculate longest path
    longest = board.get_player_road_length(0)
    print(f"\nCalculated longest road: {longest}")
    
    # Find a specific path manually
    print("\nTracing possible path: 0→1→2→3→6→7→8→9→4→5→0")
    path = [0, 1, 2, 3, 6, 7, 8, 9, 4, 5, 0]
    valid = True
    for i in range(len(path) - 1):
        if path[i+1] in road_graph.get(path[i], set()):
            print(f"  {path[i]} → {path[i+1]} ✓")
        else:
            print(f"  {path[i]} → {path[i+1]} ✗ (not connected)")
            valid = False
    
    if valid:
        print(f"Path is valid with {len(path) - 1} edges")
    else:
        print("Path is broken!")
    
    # Count unique edges in the path
    edges_used = set()
    for i in range(len(path) - 1):
        c1, c2 = min(path[i], path[i+1]), max(path[i], path[i+1])
        edges_used.add((c1, c2))
    print(f"Unique edges in path: {len(edges_used)}")

if __name__ == "__main__":
    debug_longest_road()