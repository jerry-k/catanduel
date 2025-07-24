#!/usr/bin/env python3
"""Trace the paths using edge numbers as shown in the test."""

from engine.colonist_map import EDGE_TO_CORNERS

def trace_edge_path(edges):
    """Trace a path given as a sequence of edge IDs."""
    print(f"\nTracing edge path: {edges}")
    print("Edge connections:")
    
    corners_visited = []
    for i, edge_id in enumerate(edges):
        c1, c2 = EDGE_TO_CORNERS[edge_id]
        print(f"  Edge {edge_id}: {c1} <-> {c2}")
        
        if i == 0:
            # First edge - we need to determine direction
            if len(corners_visited) == 0:
                corners_visited.extend([c1, c2])
            continue
            
        # Find which corner connects to previous
        prev_corner = corners_visited[-1]
        if c1 == prev_corner:
            corners_visited.append(c2)
        elif c2 == prev_corner:
            corners_visited.append(c1)
        else:
            print(f"    ERROR: Edge {edge_id} doesn't connect to previous corner {prev_corner}")
            return None
    
    print(f"\nCorners visited: {' → '.join(map(str, corners_visited))}")
    print(f"Number of edges: {len(edges)}")
    print(f"Number of unique corners: {len(set(corners_visited))}")
    
    return corners_visited

def main():
    """Analyze the paths from the test."""
    print("From the test file:")
    print('  print("  Path 1: 7→8→9→10→3→2→1→0→5→4 (10 roads)")')
    print('  print("  Path 2: 4→5→0→1→2→3→10→9→8→7 (10 roads)")')
    
    print("\nThese numbers (7,8,9,10,3,2,1,0,5,4) are EDGE IDs, not corner IDs!")
    
    # Trace Path 1
    path1_edges = [7, 8, 9, 10, 3, 2, 1, 0, 5, 4]
    corners1 = trace_edge_path(path1_edges)
    
    # Trace Path 2  
    path2_edges = [4, 5, 0, 1, 2, 3, 10, 9, 8, 7]
    corners2 = trace_edge_path(path2_edges)
    
    # Check if paths are valid
    print("\nAnalysis:")
    print("- Both paths use 10 edges (roads)")
    print("- This matches the expected longest road length of 10")
    print("- The current algorithm returns 9 because it counts nodes, not edges")
    print("- But actually, let me check if these paths are even valid...")
    
    # Let's manually check path 1 connectivity
    print("\nChecking Path 1 connectivity:")
    edges_data = [(7, 6, 7), (8, 7, 8), (9, 8, 9), (10, 9, 4), (3, 3, 4), 
                  (2, 2, 3), (1, 1, 2), (0, 0, 1), (5, 5, 0), (4, 4, 5)]
    
    current_corner = None
    for i, (edge_id, c1, c2) in enumerate(edges_data):
        if i == 0:
            print(f"  Starting at edge {edge_id}: {c1}-{c2}")
            current_corner = c2  # Assume we go 6->7
        else:
            if c1 == current_corner:
                print(f"  Edge {edge_id}: {c1}-{c2} (going to {c2})")
                current_corner = c2
            elif c2 == current_corner:
                print(f"  Edge {edge_id}: {c1}-{c2} (going to {c1})")
                current_corner = c1
            else:
                print(f"  Edge {edge_id}: {c1}-{c2} - NOT CONNECTED! Current corner: {current_corner}")

if __name__ == "__main__":
    main()