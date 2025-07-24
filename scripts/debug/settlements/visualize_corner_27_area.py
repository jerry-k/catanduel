#!/usr/bin/env python3
"""Visualize the area around corner 27."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import EDGE_TO_CORNERS, HEX_TO_CORNERS, get_adjacent_corners

print("=== Area around Corner 27 ===")
print()
print("Corner 27 is adjacent to: ", get_adjacent_corners(27))
print()

# Find all hexes that include corner 27
hexes_with_27 = []
for hex_id, corners in HEX_TO_CORNERS.items():
    if 27 in corners:
        hexes_with_27.append((hex_id, corners))

print("Hexes containing corner 27:")
for hex_id, corners in hexes_with_27:
    print(f"  Hex {hex_id}: corners {corners}")

# Show the edges
print("\nEdges from corner 27:")
for edge_id, (c1, c2) in sorted(EDGE_TO_CORNERS.items()):
    if c1 == 27 or c2 == 27:
        other = c2 if c1 == 27 else c1
        print(f"  Edge {edge_id}: 27 → {other}")

# Show what's at each adjacent corner in the current game
settlements = {0: 1, 2: 1, 8: 0, 10: 0, 23: 0}  # From user's game state

print("\n=== Settlement Check ===")
for corner in get_adjacent_corners(27):
    if corner in settlements:
        player = settlements[corner]
        print(f"  Corner {corner}: Player {player} settlement ❌")
    else:
        print(f"  Corner {corner}: Empty ✓")

# ASCII art representation (simplified)
print("\n=== Simplified Map ===")
print("(Numbers are corners, -- are edges)")
print()
print("        26")
print("       /  \\")
print("     31    edge")
print("     /      \\")
print("   27 --32-- 28")
print("    |\\")
print("    | edge")
print("   60  \\")
print("    |   38")
print("    |    \\")
print("   48     32")
print()
print("Settlement locations:")
print("  Corner 2: Player 1 (opponent)")
print("  Corner 23: Player 0 (you)")
print()

# Find which hexes contain corner 2
hexes_with_2 = []
for hex_id, corners in HEX_TO_CORNERS.items():
    if 2 in corners:
        hexes_with_2.append(hex_id)

print(f"Corner 2 is part of hexes: {hexes_with_2}")
print(f"Corner 27 is part of hexes: {[h[0] for h in hexes_with_27]}")

# Check if they share any hexes
shared_hexes = set(hexes_with_2) & set(h[0] for h in hexes_with_27)
if shared_hexes:
    print(f"Corners 2 and 27 share hex(es): {list(shared_hexes)}")