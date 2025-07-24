#!/usr/bin/env python3
"""Trace exactly how blocking works."""

from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS
from collections import defaultdict


def trace_with_blocking():
    """Trace road graph construction with opponent blocking."""
    # Create a board
    board = Board()
    
    # Place settlements
    board.buildings[0] = (0, SETTLEMENT)
    board.buildings[2] = (0, SETTLEMENT)
    board.buildings[6] = (1, SETTLEMENT)  # Opponent
    
    # Place roads for player 0
    for edge in range(11):
        board.roads[edge] = 0
    
    # Build road graph with detailed tracing
    road_graph = defaultdict(set)
    player_roads = board.get_player_roads(0)
    
    print("Building road graph for player 0 with opponent at corner 6:")
    print("=" * 60)
    
    for edge_id in player_roads:
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        
        # Check if path is blocked
        blocked1 = board._is_corner_blocked(corner1, 0)
        blocked2 = board._is_corner_blocked(corner2, 0)
        
        print(f"\nEdge {edge_id}: {corner1} <-> {corner2}")
        
        # Check buildings at corners
        if corner1 in board.buildings:
            owner, _ = board.buildings[corner1]
            print(f"  Corner {corner1}: owned by player {owner}")
        if corner2 in board.buildings:
            owner, _ = board.buildings[corner2]
            print(f"  Corner {corner2}: owned by player {owner}")
            
        print(f"  Blocked status: corner {corner1}={blocked1}, corner {corner2}={blocked2}")
        
        if not blocked1 and not blocked2:
            road_graph[corner1].add(corner2)
            road_graph[corner2].add(corner1)
            print(f"  -> Added bidirectional edge")
        elif not blocked1:
            road_graph[corner1].add(corner2)
            print(f"  -> Added edge from {corner1} to {corner2} only (dead end at {corner2})")
        elif not blocked2:
            road_graph[corner2].add(corner1)
            print(f"  -> Added edge from {corner2} to {corner1} only (dead end at {corner1})")
        else:
            print(f"  -> No connection (both ends blocked)")
    
    print("\n\nFinal road graph:")
    print("=" * 60)
    for corner in sorted(road_graph.keys()):
        print(f"Corner {corner}: -> {sorted(road_graph[corner])}")
    
    # Find connected components
    print("\n\nConnected components:")
    print("=" * 60)
    visited = set()
    components = []
    
    def dfs_component(start):
        component = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                component.add(node)
                for neighbor in road_graph[node]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return component
    
    for corner in list(road_graph.keys()):
        if corner not in visited:
            comp = dfs_component(corner)
            components.append(comp)
            print(f"Component {len(components)}: {sorted(comp)}")
    
    # Calculate longest path in each component
    print("\n\nLongest path in each component:")
    print("=" * 60)
    
    for i, component in enumerate(components):
        # Build subgraph for this component
        subgraph = {}
        for corner in component:
            subgraph[corner] = road_graph[corner] & component
        
        # Find longest path
        longest = board._find_longest_path(subgraph)
        print(f"Component {i+1}: {longest} roads")
        
        # Find an actual longest path
        if subgraph:
            start = list(subgraph.keys())[0]
            path = find_a_longest_path(subgraph, start)
            if path:
                print(f"  Example path: {' -> '.join(map(str, path))}")


def find_a_longest_path(graph, start):
    """Find one of the longest paths starting from a node."""
    best_path = []
    
    def dfs(node, path, visited):
        nonlocal best_path
        if len(path) > len(best_path):
            best_path = path[:]
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                dfs(neighbor, path + [neighbor], visited)
                visited.remove(neighbor)
    
    dfs(start, [start], {start})
    return best_path


if __name__ == "__main__":
    trace_with_blocking()