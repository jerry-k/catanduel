#!/usr/bin/env python3
"""Direct test of the longest road calculation."""

from engine.models.board import Board
from engine.models.enums import SETTLEMENT

# Create board
board = Board()

# Place settlements at corners 0 and 2 for player 0
board.buildings[0] = (SETTLEMENT, 0)
board.buildings[2] = (SETTLEMENT, 0)

# Place roads on edges 0-10 for player 0
for edge in range(11):
    board.roads[edge] = 0

# Get the result
result = board.get_player_road_length(0)
print(f"Engine calculates: {result} roads")

# Also test the underlying method
longest_path = board._get_longest_path(0)
print(f"Longest path returned by _get_longest_path: {longest_path}")
print(f"Path length: {len(longest_path) if longest_path else 0}")