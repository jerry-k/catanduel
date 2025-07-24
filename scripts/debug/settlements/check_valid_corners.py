#!/usr/bin/env python3
"""Check which corners are valid for settlement given the current board state."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import get_adjacent_corners, get_connected_edges, EDGE_TO_CORNERS

# Current board state from user
settlements = {
    0: 1,   # Player 1
    2: 1,   # Player 1
    8: 0,   # Player 0
    10: 0,  # Player 0
    23: 0   # Player 0
}

roads = {
    0: 1,   # Player 1
    1: 1,   # Player 1
    8: 0,   # Player 0
    11: 0,  # Player 0
    31: 0,  # Player 0
    35: 0   # Player 0
}

print("=== Current Board State ===")
print("Player 0 settlements:", [c for c, p in settlements.items() if p == 0])
print("Player 1 settlements:", [c for c, p in settlements.items() if p == 1])
print("Player 0 roads:", [e for e, p in roads.items() if p == 0])

# Check which corners are connected to player 0's roads
print("\n=== Corners Connected to Player 0's Roads ===")
connected_corners = set()
for edge, player in roads.items():
    if player == 0:
        c1, c2 = EDGE_TO_CORNERS[edge]
        connected_corners.add(c1)
        connected_corners.add(c2)
        print(f"Edge {edge}: connects corners {c1} and {c2}")

print(f"\nAll corners connected to Player 0's roads: {sorted(connected_corners)}")

# Check which of these corners are valid for settlement
print("\n=== Valid Settlement Locations ===")
valid_corners = []

for corner in connected_corners:
    # Skip if already occupied
    if corner in settlements:
        continue
    
    # Check distance rule
    adjacent = get_adjacent_corners(corner)
    violates_distance = any(adj in settlements for adj in adjacent)
    
    if not violates_distance:
        valid_corners.append(corner)
        print(f"✓ Corner {corner} is VALID")
        print(f"  Adjacent corners: {adjacent}")
    else:
        occupied_adj = [adj for adj in adjacent if adj in settlements]
        print(f"✗ Corner {corner} violates distance rule")
        print(f"  Adjacent corners: {adjacent}")
        print(f"  Occupied adjacent: {occupied_adj}")

print(f"\n=== Summary ===")
print(f"Total valid corners for settlement: {len(valid_corners)}")
print(f"Valid corners: {valid_corners}")

# Specifically check corner 27
print(f"\n=== Checking Corner 27 ===")
if 27 in connected_corners:
    print("Corner 27 is connected to player 0's roads")
    adjacent_27 = get_adjacent_corners(27)
    print(f"Adjacent corners to 27: {adjacent_27}")
    occupied_adj_27 = [adj for adj in adjacent_27 if adj in settlements]
    if occupied_adj_27:
        print(f"Occupied adjacent corners: {occupied_adj_27}")
        print("❌ Corner 27 violates distance rule")
    else:
        print("✅ Corner 27 does not violate distance rule")
else:
    print("Corner 27 is NOT connected to player 0's roads")
    
    # Check which roads would connect to it
    connecting_edges = []
    for edge, (c1, c2) in EDGE_TO_CORNERS.items():
        if c1 == 27 or c2 == 27:
            connecting_edges.append(edge)
    print(f"Edges that connect to corner 27: {connecting_edges}")