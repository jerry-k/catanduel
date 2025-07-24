#!/usr/bin/env python3
"""Check all hexes for missing edges."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import HEX_TO_CORNERS, EDGE_TO_CORNERS

print("=== Checking All Hexes for Missing Edges ===")

missing_edges = []
total_expected = 0
total_found = 0

for hex_id in sorted(HEX_TO_CORNERS.keys()):
    corners = HEX_TO_CORNERS[hex_id]
    hex_missing = []
    
    # Check each consecutive pair
    for i in range(6):
        c1 = corners[i]
        c2 = corners[(i + 1) % 6]
        total_expected += 1
        
        # Find if edge exists
        edge_found = None
        for edge_id, (e1, e2) in EDGE_TO_CORNERS.items():
            if (e1 == c1 and e2 == c2) or (e1 == c2 and e2 == c1):
                edge_found = edge_id
                total_found += 1
                break
        
        if not edge_found:
            hex_missing.append((c1, c2))
            missing_edges.append((hex_id, c1, c2))
    
    if hex_missing:
        print(f"\nHex {hex_id}: {len(hex_missing)} missing edge(s)")
        print(f"  Corners: {corners}")
        for c1, c2 in hex_missing:
            print(f"  Missing: {c1} → {c2}")

print(f"\n=== Summary ===")
print(f"Total expected edges: {total_expected}")
print(f"Total found edges: {total_found}")
print(f"Missing edges: {len(missing_edges)}")

if missing_edges:
    print(f"\nAll missing edges:")
    for hex_id, c1, c2 in missing_edges:
        print(f"  Hex {hex_id}: {c1} → {c2}")

# Check how many edges we have total
print(f"\nTotal edges in EDGE_TO_CORNERS: {len(EDGE_TO_CORNERS)}")
print(f"Edge IDs range from {min(EDGE_TO_CORNERS.keys())} to {max(EDGE_TO_CORNERS.keys())}")