#!/usr/bin/env python3
"""Test the exact board graph construction."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

# Create a board
board = Board()

# Place settlements at corners 0 and 2 for player 0
board.buildings[0] = (0, SETTLEMENT)
board.buildings[2] = (0, SETTLEMENT)

# Place roads on edges 0-10 for player 0
for edge in range(11):
    board.roads[edge] = 0

# Build the road graph exactly as board.py does
road_graph = defaultdict(set)
player_roads = board.get_player_roads(0)

print("Building road graph for player 0...")
print(f"Player roads: {player_roads}")

for edge_id in player_roads:
    corner1, corner2 = EDGE_TO_CORNERS[edge_id]
    
    # Check if path is blocked by opponent's building
    blocked1 = board._is_corner_blocked(corner1, 0)
    blocked2 = board._is_corner_blocked(corner2, 0)
    
    print(f"\nEdge {edge_id}: {corner1} <-> {corner2}")
    print(f"  Corner {corner1} blocked: {blocked1}")
    print(f"  Corner {corner2} blocked: {blocked2}")
    
    if not blocked1 and not blocked2:
        road_graph[corner1].add(corner2)
        road_graph[corner2].add(corner1)
        print(f"  Added bidirectional connection")

print("\nFinal road graph:")
for corner in sorted(road_graph.keys()):
    print(f"  Corner {corner}: {sorted(road_graph[corner])}")

# Count total edges
edge_count = sum(len(neighbors) for neighbors in road_graph.values()) // 2
print(f"\nTotal edges in graph: {edge_count}")

# Now test the _find_longest_path method directly
longest = board._find_longest_path(road_graph)
print(f"\nLongest path found by _find_longest_path: {longest}")

# Also test the full method
full_longest = board.get_player_road_length(0)
print(f"Longest path found by get_player_road_length: {full_longest}")

# Check if there's any difference
if longest != full_longest:
    print("\nERROR: Different results from direct method vs full method!")
elif longest == 11:
    print("\nThe issue is confirmed: algorithm returns 11 instead of 10")