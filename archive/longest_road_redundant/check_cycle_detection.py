#!/usr/bin/env python3
"""Check if the road network forms a cycle and calculate the correct longest road."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

def find_cycles_and_longest_road(graph):
    """Find if graph has cycles and calculate longest road considering cycles."""
    
    def dfs_cycle(node, parent, visited, path):
        """DFS to detect cycles and track the cycle path."""
        visited.add(node)
        path.append(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                cycle_found, cycle_path = dfs_cycle(neighbor, node, visited, path)
                if cycle_found:
                    return True, cycle_path
            elif neighbor != parent and neighbor in path:
                # Found a cycle! 
                cycle_start_idx = path.index(neighbor)
                return True, path[cycle_start_idx:] + [neighbor]
        
        path.pop()
        return False, []
    
    # Check for cycles
    visited = set()
    for node in graph:
        if node not in visited:
            has_cycle, cycle_path = dfs_cycle(node, -1, visited, [])
            if has_cycle:
                return True, cycle_path, len(cycle_path) - 1
    
    return False, [], 0

def main():
    """Test cycle detection on our road network."""
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
    
    print("Checking for cycles in the road network...")
    has_cycle, cycle_path, cycle_length = find_cycles_and_longest_road(road_graph)
    
    if has_cycle:
        print(f"\n✓ Found a cycle with {cycle_length} edges!")
        print(f"  Cycle path: {' → '.join(map(str, cycle_path))}")
    else:
        print("\n✗ No cycle found")
    
    # Count total edges in the graph
    total_edges = sum(len(neighbors) for neighbors in road_graph.values()) // 2
    print(f"\nTotal edges in graph: {total_edges}")
    
    # For a connected graph with a cycle, the longest road should include all edges
    if has_cycle and total_edges == 10:
        print("\nIn Catan, when all roads form a single connected cycle,")
        print("the longest road should count all edges in the cycle.")
        print(f"Therefore, longest road = {total_edges} (not {cycle_length})")
    
    # Let's also check if all nodes are in one connected component
    def get_connected_component(start, graph):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend(graph[node] - visited)
        return visited
    
    if road_graph:
        component = get_connected_component(next(iter(road_graph)), road_graph)
        if len(component) == len(road_graph):
            print("\n✓ All roads form a single connected network")
        else:
            print(f"\n✗ Roads form multiple components: {len(component)} vs {len(road_graph)} nodes")

if __name__ == "__main__":
    main()