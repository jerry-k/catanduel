#!/usr/bin/env python3
"""Dump all adjacency data to understand the board topology."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import (
    CORNER_ADJACENCY, EDGE_TO_CORNERS, HEX_TO_CORNERS, 
    get_adjacent_corners, get_connected_edges
)

print("=== CORNER ADJACENCY DATA ===")
print("Format: Corner X: [adjacent corners via edges]")
print()

# First, let's build the TRUE adjacency from edge data
true_adjacency = {}
for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    if c1 not in true_adjacency:
        true_adjacency[c1] = []
    if c2 not in true_adjacency:
        true_adjacency[c2] = []
    
    if c2 not in true_adjacency[c1]:
        true_adjacency[c1].append(c2)
    if c1 not in true_adjacency[c2]:
        true_adjacency[c2].append(c1)

# Sort for consistency
for corner in true_adjacency:
    true_adjacency[corner].sort()

# Compare hardcoded vs computed
mismatches = []
for corner in range(54):
    hardcoded = sorted(CORNER_ADJACENCY.get(corner, []))
    computed = sorted(true_adjacency.get(corner, []))
    
    status = "✓" if hardcoded == computed else "✗"
    if hardcoded != computed:
        mismatches.append(corner)
    
    print(f"{status} Corner {corner:2d}: {hardcoded}")
    if hardcoded != computed:
        print(f"            Should be: {computed}")
        print(f"            Edges connecting to {corner}: ", end="")
        edges = []
        for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
            if c1 == corner or c2 == corner:
                edges.append(edge_id)
        print(sorted(edges))

print(f"\nTotal mismatches: {len(mismatches)}")
print(f"Mismatched corners: {mismatches}")

print("\n\n=== EDGE TO CORNERS DATA ===")
print("Format: Edge X: connects corners (A, B)")
print()

# Group edges by the corners they connect
for edge_id in sorted(EDGE_TO_CORNERS.keys()):
    c1, c2 = EDGE_TO_CORNERS[edge_id]
    print(f"Edge {edge_id:2d}: ({c1:2d}, {c2:2d})")

print("\n\n=== CORNERS AROUND EACH HEX ===")
print("Format: Hex X: [corners in clockwise order]")
print()

for hex_id in sorted(HEX_TO_CORNERS.keys()):
    corners = HEX_TO_CORNERS[hex_id]
    print(f"Hex {hex_id:2d}: {corners}")

# Verify specific problematic corners
print("\n\n=== DETAILED ANALYSIS OF PROBLEMATIC CORNERS ===")
for corner in [2, 27, 48]:
    print(f"\nCorner {corner}:")
    print(f"  Hardcoded adjacent: {CORNER_ADJACENCY.get(corner, [])}")
    print(f"  Computed adjacent: {true_adjacency.get(corner, [])}")
    print(f"  Connected edges: ", end="")
    edges = []
    for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
        if c1 == corner or c2 == corner:
            other = c2 if c1 == corner else c1
            edges.append(f"{edge_id}→{other}")
    print(", ".join(edges))