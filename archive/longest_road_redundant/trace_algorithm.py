#!/usr/bin/env python3
"""Trace the exact execution of the algorithm."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

def trace_algorithm():
    """Trace the algorithm execution step by step."""
    # Create a board
    board = Board()
    
    # Place settlements at corners 0 and 2 for player 0
    board.buildings[0] = (0, SETTLEMENT)
    board.buildings[2] = (0, SETTLEMENT)
    
    # Place roads on edges 0-10 for player 0
    for edge in range(11):
        board.roads[edge] = 0
    
    # Build the road graph (same as in board.py)
    road_graph = defaultdict(set)
    player_roads = board.get_player_roads(0)
    
    for edge_id in player_roads:
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        
        # Player's own settlements don't block
        blocked1 = board._is_corner_blocked(corner1, 0)
        blocked2 = board._is_corner_blocked(corner2, 0)
        
        if not blocked1 and not blocked2:
            road_graph[corner1].add(corner2)
            road_graph[corner2].add(corner1)
    
    print("Road graph built:")
    for corner in sorted(road_graph.keys()):
        print(f"  Corner {corner}: {sorted(road_graph[corner])}")
    
    # Count edges in graph
    edge_count = sum(len(neighbors) for neighbors in road_graph.values()) // 2
    print(f"\nTotal edges in graph: {edge_count}")
    
    # Now let's manually trace the DFS to see what path gives us 11
    max_found = 0
    
    def trace_dfs(node, visited_edges, depth=0, path=[]):
        nonlocal max_found
        path = path + [node]
        
        found_longer = False
        for neighbor in road_graph[node]:
            edge = (min(node, neighbor), max(node, neighbor))
            
            if edge not in visited_edges:
                visited_edges.add(edge)
                
                result = trace_dfs(neighbor, visited_edges, depth + 1, path)
                
                if result + 1 > max_found:
                    max_found = result + 1
                    if max_found == 11:
                        print(f"\nFound path of length 11!")
                        print(f"Path: {path + [neighbor]}")
                        print(f"Edges used: {len(visited_edges)}")
                    found_longer = True
                
                visited_edges.remove(edge)
        
        return depth
    
    print("\nTracing DFS from each start node...")
    for start in sorted(road_graph.keys()):
        trace_dfs(start, set())
        if max_found == 11:
            break
    
    print(f"\nMaximum path length found: {max_found}")

if __name__ == "__main__":
    trace_algorithm()