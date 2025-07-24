#!/usr/bin/env python3
"""Verify the adjacent corners calculation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import CORNER_ADJACENCY, EDGE_TO_CORNERS, get_adjacent_corners

print("=== Verifying Corner Adjacency ===")

# Check corner 27's adjacency
print(f"\nCorner 27 adjacent corners: {get_adjacent_corners(27)}")
print(f"From CORNER_ADJACENCY dict: {CORNER_ADJACENCY.get(27, [])}")

# Find all edges that connect to corner 27
edges_with_27 = []
for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    if c1 == 27 or c2 == 27:
        other_corner = c2 if c1 == 27 else c1
        edges_with_27.append((edge_id, other_corner))

print(f"\nEdges connecting to corner 27:")
for edge_id, other_corner in sorted(edges_with_27):
    print(f"  Edge {edge_id}: connects 27 to corner {other_corner}")

# Check corner 2's adjacency
print(f"\nCorner 2 adjacent corners: {get_adjacent_corners(2)}")

# Find all edges that connect to corner 2
edges_with_2 = []
for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    if c1 == 2 or c2 == 2:
        other_corner = c2 if c1 == 2 else c1
        edges_with_2.append((edge_id, other_corner))

print(f"\nEdges connecting to corner 2:")
for edge_id, other_corner in sorted(edges_with_2):
    print(f"  Edge {edge_id}: connects 2 to corner {other_corner}")

# Verify if 2 and 27 are adjacent
if 2 in get_adjacent_corners(27):
    print("\n❌ ERROR: Corner 2 is listed as adjacent to 27")
else:
    print("\n✅ CORRECT: Corner 2 is NOT adjacent to 27")

if 27 in get_adjacent_corners(2):
    print("❌ ERROR: Corner 27 is listed as adjacent to 2")
else:
    print("✅ CORRECT: Corner 27 is NOT adjacent to 2")