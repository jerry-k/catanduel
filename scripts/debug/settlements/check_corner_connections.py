#!/usr/bin/env python3
"""Check specific corner connections."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import EDGE_TO_CORNERS, HEX_TO_CORNERS

# Check edges for corners 47 and 48
print("=== Checking corners 47 and 48 ===")

edges_with_47 = []
edges_with_48 = []

for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    if c1 == 47 or c2 == 47:
        edges_with_47.append((edge_id, (c1, c2)))
    if c1 == 48 or c2 == 48:
        edges_with_48.append((edge_id, (c1, c2)))

print(f"\nEdges connecting to corner 47:")
for edge_id, corners in sorted(edges_with_47):
    print(f"  Edge {edge_id}: {corners}")

print(f"\nEdges connecting to corner 48:")
for edge_id, corners in sorted(edges_with_48):
    print(f"  Edge {edge_id}: {corners}")

# Check if any edge connects 47 to 48
print(f"\nIs there an edge connecting 47 to 48? ", end="")
edge_exists = False
for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    if (c1 == 47 and c2 == 48) or (c1 == 48 and c2 == 47):
        print(f"YES - Edge {edge_id}")
        edge_exists = True
        break
if not edge_exists:
    print("NO")

# Check hexes that contain both corners
print("\n=== Hexes containing corners ===")
for corner in [47, 48]:
    hexes = []
    for hex_id, corners in HEX_TO_CORNERS.items():
        if corner in corners:
            hexes.append(hex_id)
    print(f"Corner {corner} is part of hexes: {hexes}")

# Check if they share a hex
print("\nDo corners 47 and 48 share a hex? ", end="")
hexes_47 = set()
hexes_48 = set()
for hex_id, corners in HEX_TO_CORNERS.items():
    if 47 in corners:
        hexes_47.add(hex_id)
    if 48 in corners:
        hexes_48.add(hex_id)

shared_hexes = hexes_47 & hexes_48
if shared_hexes:
    print(f"YES - Hex(es) {list(shared_hexes)}")
else:
    print("NO")

# For corner 27 and 48
print("\n\n=== Checking corners 27 and 48 ===")
print("Corner 27 edges:")
for edge_id, (c1, c2) in sorted(EDGE_TO_CORNERS.items()):
    if c1 == 27 or c2 == 27:
        print(f"  Edge {edge_id}: {(c1, c2)}")

# Is there an edge 60?
print(f"\nEdge 60 connects: {EDGE_TO_CORNERS.get(60, 'NOT FOUND')}")

# Double-check corner 27's real adjacencies
print("\nCorner 27 should be adjacent to:")
for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    if c1 == 27:
        print(f"  {c2} (via edge {edge_id})")
    elif c2 == 27:
        print(f"  {c1} (via edge {edge_id})")