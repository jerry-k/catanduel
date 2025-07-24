#!/usr/bin/env python3
"""Analyze why the longest path calculation differs from expectation."""

from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

def analyze_paths():
    """Analyze different possible paths in the road network."""
    
    # Create board with settlements and roads
    board = Board()
    board.buildings[0] = (SETTLEMENT, 0)
    board.buildings[2] = (SETTLEMENT, 0)
    
    for edge in range(11):
        board.roads[edge] = 0
    
    print("Setup:")
    print("- Settlements at corners 0 and 2")
    print("- Roads on edges 0-10")
    print()
    
    # Build adjacency from roads
    road_graph = {}
    for edge in range(11):
        if edge in board.roads and board.roads[edge] == 0:
            c1, c2 = EDGE_TO_CORNERS[edge]
            if c1 not in road_graph:
                road_graph[c1] = set()
            if c2 not in road_graph:
                road_graph[c2] = set()
            road_graph[c1].add(c2)
            road_graph[c2].add(c1)
    
    print("Graph structure:")
    print("- Corner 3 has degree 3 (connects to 2, 4, 6)")
    print("- Corner 4 has degree 3 (connects to 3, 5, 9)")
    print()
    
    # Find all simple paths (no repeated corners)
    def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        paths = []
        for node in graph.get(start, []):
            if node not in path:  # Avoid cycles
                newpaths = find_all_paths(graph, node, end, path)
                paths.extend(newpaths)
        return paths
    
    def find_longest_from_corner(graph, start, path=[]):
        path = path + [start]
        max_path = path
        
        for neighbor in graph.get(start, []):
            if neighbor not in path:  # Avoid revisiting corners
                new_path = find_longest_from_corner(graph, neighbor, path)
                if len(new_path) > len(max_path):
                    max_path = new_path
        
        return max_path
    
    # Find longest paths from each corner
    print("Finding longest paths from different starting points:")
    longest_overall = []
    
    for start_corner in road_graph.keys():
        longest = find_longest_from_corner(road_graph, start_corner, [])
        edge_count = len(longest) - 1
        print(f"  From corner {start_corner}: {edge_count} edges")
        if len(longest) > len(longest_overall):
            longest_overall = longest
    
    print(f"\nLongest path found: {' -> '.join(map(str, longest_overall))}")
    print(f"Number of edges: {len(longest_overall) - 1}")
    
    # Check specific paths
    print("\n\nChecking specific paths:")
    
    # Path that visits all edges would need to visit a corner twice
    print("1. Attempting to use all 11 edges:")
    print("   - Would require visiting 12 corners (start + 11 moves)")
    print("   - But there are only 10 unique corners in the network")
    print("   - Therefore, impossible to use all 11 edges in a simple path")
    
    # The issue with corner 4
    print("\n2. Why corner 4 limits the path:")
    print("   - Corner 4 connects edges 3, 4, and 10")
    print("   - To traverse all three edges from corner 4, you'd have to visit it multiple times")
    print("   - But longest road rules don't allow revisiting corners")
    
    # Verify the engine's calculation
    calculated = board.get_player_road_length(0)
    print(f"\n\nEngine's calculation: {calculated} roads")
    print(f"Manual calculation: {len(longest_overall) - 1} roads")
    
    if calculated == len(longest_overall) - 1:
        print("✅ Engine calculation matches manual calculation!")
    else:
        print("❌ Engine calculation differs from manual calculation")
        
        # Try to understand why
        print("\nDifference might be due to:")
        print("- How settlements are handled as endpoints")
        print("- Different path finding algorithm")


if __name__ == "__main__":
    analyze_paths()