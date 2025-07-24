#!/usr/bin/env python3
"""Check the specific settlement case described by the user."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import EDGE_TO_CORNERS, get_adjacent_corners

# Check the specific case
print("=== Checking User's Specific Case ===")
print("Settlement at corner 23")
print("Roads at edges 31 and 35")
print("Want to settle at corner 27")

print("\n=== Edge Connections ===")
print(f"Edge 31 connects corners: {EDGE_TO_CORNERS[31]}")
print(f"Edge 35 connects corners: {EDGE_TO_CORNERS[35]}")

print("\n=== Path from corner 23 to corner 27 ===")
# Check if edges connect properly
edge_31_corners = EDGE_TO_CORNERS[31]
edge_35_corners = EDGE_TO_CORNERS[35]

if 23 in edge_31_corners:
    other_corner_31 = edge_31_corners[0] if edge_31_corners[1] == 23 else edge_31_corners[1]
    print(f"Edge 31 connects corner 23 to corner {other_corner_31}")
else:
    print("ERROR: Edge 31 does not connect to corner 23!")

if 23 in edge_35_corners:
    other_corner_35 = edge_35_corners[0] if edge_35_corners[1] == 23 else edge_35_corners[1]
    print(f"Edge 35 connects corner 23 to corner {other_corner_35}")
else:
    print("ERROR: Edge 35 does not connect to corner 23!")

# Check if corner 27 is reachable
if 27 in edge_31_corners:
    print("✓ Corner 27 is connected via edge 31")
elif 27 in edge_35_corners:
    print("✓ Corner 27 is connected via edge 35")
else:
    print("✗ Corner 27 is NOT directly connected to edges 31 or 35")

print("\n=== Distance Rule Check ===")
print(f"Corner 23 adjacent corners: {get_adjacent_corners(23)}")
print(f"Corner 27 adjacent corners: {get_adjacent_corners(27)}")

if 27 in get_adjacent_corners(23):
    print("✗ Corner 27 is ADJACENT to corner 23 - violates distance rule!")
else:
    print("✓ Corner 27 is NOT adjacent to corner 23 - distance rule OK")