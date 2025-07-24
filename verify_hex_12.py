#!/usr/bin/env python3
"""Verify hex 12 corner arrangement."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import HEX_TO_CORNERS, EDGE_TO_CORNERS

print("=== Hex 12 Analysis ===")
hex_12_corners = HEX_TO_CORNERS[12]
print(f"Hex 12 corners (in order): {hex_12_corners}")

# Find all edges between these corners
print("\nEdges between Hex 12 corners:")
hex_12_corner_set = set(hex_12_corners)

for edge_id, (c1, c2) in sorted(EDGE_TO_CORNERS.items()):
    if c1 in hex_12_corner_set and c2 in hex_12_corner_set:
        # Find positions in the hex
        pos1 = hex_12_corners.index(c1)
        pos2 = hex_12_corners.index(c2)
        print(f"  Edge {edge_id}: connects {c1} (pos {pos1}) to {c2} (pos {pos2})")

# Check if corners should be adjacent based on hex position
print("\nExpected adjacencies based on hex positions:")
for i in range(6):
    corner = hex_12_corners[i]
    next_corner = hex_12_corners[(i + 1) % 6]
    prev_corner = hex_12_corners[(i - 1) % 6]
    print(f"  Corner {corner} should be adjacent to {prev_corner} and {next_corner}")

# Check actual edges
print("\nVerifying expected edges exist:")
for i in range(6):
    c1 = hex_12_corners[i]
    c2 = hex_12_corners[(i + 1) % 6]
    
    # Find if edge exists
    edge_found = None
    for edge_id, (e1, e2) in EDGE_TO_CORNERS.items():
        if (e1 == c1 and e2 == c2) or (e1 == c2 and e2 == c1):
            edge_found = edge_id
            break
    
    if edge_found:
        print(f"  ✓ {c1} → {c2}: Edge {edge_found}")
    else:
        print(f"  ✗ {c1} → {c2}: NO EDGE FOUND!")