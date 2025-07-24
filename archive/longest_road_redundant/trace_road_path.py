#!/usr/bin/env python3
"""Trace the exact path through the road network."""

from engine.colonist_map import EDGE_TO_CORNERS, CORNER_ADJACENCY

def trace_road_network():
    """Trace through the road network step by step."""
    
    # Define which edges player 0 owns
    player_roads = set(range(11))  # edges 0-10
    
    # Map edges to their corners
    print("Edge to Corner mappings:")
    for edge in range(11):
        c1, c2 = EDGE_TO_CORNERS[edge]
        print(f"  Edge {edge}: {c1} <-> {c2}")
    
    print("\n\nBuilding the adjacency graph from roads:")
    # Build adjacency graph from roads
    road_graph = {}
    for edge in player_roads:
        c1, c2 = EDGE_TO_CORNERS[edge]
        if c1 not in road_graph:
            road_graph[c1] = set()
        if c2 not in road_graph:
            road_graph[c2] = set()
        road_graph[c1].add(c2)
        road_graph[c2].add(c1)
    
    for corner, neighbors in sorted(road_graph.items()):
        print(f"  Corner {corner}: connected to {sorted(neighbors)}")
    
    print("\n\nTrying to trace the path 7→8→9→10→3→2→1→0→5→4:")
    path = [7, 8, 9, 4, 3, 2, 1, 0, 5, 4]
    
    valid = True
    for i in range(len(path) - 1):
        curr = path[i]
        next_corner = path[i + 1]
        if next_corner in road_graph.get(curr, set()):
            print(f"  ✓ {curr} -> {next_corner}")
        else:
            print(f"  ✗ {curr} -> {next_corner} (NOT CONNECTED)")
            valid = False
    
    if not valid:
        print("\nThe suggested path is NOT valid. Let me find the actual longest path...")
        
        # Try the corrected path based on edge connections
        print("\nCorrected path following edges 7→8→9→10→3→2→1→0→5→4:")
        edge_path = [7, 8, 9, 10, 3, 2, 1, 0, 5, 4]
        corner_path = []
        
        for i, edge in enumerate(edge_path):
            c1, c2 = EDGE_TO_CORNERS[edge]
            print(f"  Edge {edge}: connects {c1} and {c2}")
            
            if i == 0:
                # Start with edge 7
                corner_path.extend([c1, c2])
            else:
                # Find which corner connects to previous
                if c1 in corner_path:
                    if c2 not in corner_path:
                        corner_path.append(c2)
                elif c2 in corner_path:
                    if c1 not in corner_path:
                        corner_path.append(c1)
        
        print(f"\nActual corner path: {' -> '.join(map(str, corner_path))}")
        print(f"Number of corners in path: {len(corner_path)}")
        print(f"Number of edges in path: {len(corner_path) - 1}")
    
    # Check for cycles
    print("\n\nChecking for cycles that might limit path length:")
    print("Corners with degree > 2 (branch points):")
    for corner, neighbors in road_graph.items():
        if len(neighbors) > 2:
            print(f"  Corner {corner}: degree {len(neighbors)}, connected to {sorted(neighbors)}")


if __name__ == "__main__":
    trace_road_network()