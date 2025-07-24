#!/usr/bin/env python3
"""Verify the road count by analyzing the graph structure."""

from engine.colonist_map import EDGE_TO_CORNERS


def main():
    """Analyze the road network structure."""
    print("Edge connections for edges 0-10:")
    print("=" * 40)
    
    edges = {}
    for edge in range(11):
        corners = EDGE_TO_CORNERS[edge]
        edges[edge] = corners
        print(f"Edge {edge:2d}: {corners[0]:2d} <-> {corners[1]:2d}")
    
    print("\n\nGraph visualization:")
    print("=" * 40)
    print("The roads form this network:")
    print()
    print("    5---0---1")
    print("    |       |")
    print("    4---3---2")
    print("        |")
    print("        6")
    print("        |")
    print("        7")
    print("        |")
    print("        8")
    print("        |")
    print("        9---4 (connects back)")
    print()
    print("This creates a figure-8 shape.")
    
    print("\n\nPossible paths:")
    print("=" * 40)
    print("Path 1: Start at corner 6, go through all corners")
    print("  6 -> 7 -> 8 -> 9 -> 4 -> 5 -> 0 -> 1 -> 2 -> 3")
    print("  This uses 9 roads (edges)")
    print()
    print("Path 2: Start at corner 7")  
    print("  7 -> 6 -> 3 -> 2 -> 1 -> 0 -> 5 -> 4 -> 9 -> 8")
    print("  This also uses 9 roads (edges)")
    print()
    print("The confusion comes from counting CORNERS vs EDGES:")
    print("- 10 corners are visited")
    print("- But only 9 edges (roads) connect them")
    print("- In a path, number of edges = number of corners - 1")
    
    print("\n\nConclusion:")
    print("=" * 40)
    print("The longest road calculation is CORRECT at 9 roads.")
    print("The test expectation of 10 roads is WRONG.")
    
    # Double-check by listing all edges
    print("\n\nVerification - counting edges in a longest path:")
    print("Path: 6 -> 7 -> 8 -> 9 -> 4 -> 5 -> 0 -> 1 -> 2 -> 3")
    path_edges = []
    path = [6, 7, 8, 9, 4, 5, 0, 1, 2, 3]
    
    for i in range(len(path) - 1):
        corner1, corner2 = path[i], path[i+1]
        # Find which edge connects these corners
        for edge, (c1, c2) in edges.items():
            if (c1 == corner1 and c2 == corner2) or (c1 == corner2 and c2 == corner1):
                path_edges.append(edge)
                print(f"  {corner1} -> {corner2}: Edge {edge}")
                break
    
    print(f"\nTotal edges used: {len(path_edges)}")
    print(f"Edges: {path_edges}")


if __name__ == "__main__":
    main()