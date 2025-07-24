#!/usr/bin/env python3
"""Simple debug of the longest road calculation."""

from collections import defaultdict
from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS

# Create a board
board = Board()

# Place settlements at corners 0 and 2 for player 0
board.buildings[0] = (0, SETTLEMENT)
board.buildings[2] = (0, SETTLEMENT)

# Test with different numbers of roads
print("Testing with different road configurations:")

# First test with roads 0-9 (without edge 10)
board.roads = {}
for edge in range(10):
    board.roads[edge] = 0

length1 = board.get_player_road_length(0)
print(f"\nWith roads 0-9 (10 roads): longest path = {length1}")

# Now add edge 10
board.roads[10] = 0
length2 = board.get_player_road_length(0)
print(f"With roads 0-10 (11 roads): longest path = {length2}")

# Let's manually check what makes sense
print("\nManual analysis:")
print("- Without edge 10, the graph still forms one connected component")
print("- Edge 10 connects corners 9 and 4, creating an additional cycle")
print("- The longest simple path (no repeated edges) in this graph should be 10")

# Let's also check without edge 6
board.roads = {}
for edge in range(11):
    if edge != 6:
        board.roads[edge] = 0

length3 = board.get_player_road_length(0)
print(f"\nWithout edge 6 (10 roads): longest path = {length3}")

# Check the expected paths from the test
print("\nExpected paths from test (using edge IDs):")
print("  Path 1: 7→8→9→10→3→2→1→0→5→4 (10 edges)")
print("  Path 2: 4→5→0→1→2→3→10→9→8→7 (10 edges)")
print("\nBoth paths avoid edge 6, suggesting the longest path is 10 when all 11 edges present")