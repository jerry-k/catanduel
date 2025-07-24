#!/usr/bin/env python3
"""Build correct corner adjacency from edge data."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.colonist_map import EDGE_TO_CORNERS, CORNER_ADJACENCY

# Build adjacency from edges (the ground truth)
correct_adjacency = {}
for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
    # c1 and c2 are adjacent via this edge
    if c1 not in correct_adjacency:
        correct_adjacency[c1] = []
    if c2 not in correct_adjacency:
        correct_adjacency[c2] = []
    
    if c2 not in correct_adjacency[c1]:
        correct_adjacency[c1].append(c2)
    if c1 not in correct_adjacency[c2]:
        correct_adjacency[c2].append(c1)

# Sort for consistency
for corner in correct_adjacency:
    correct_adjacency[corner].sort()

print("=== Checking CORNER_ADJACENCY Correctness ===")

# Check specific corners
for corner in [2, 27]:
    hardcoded = CORNER_ADJACENCY.get(corner, [])
    computed = correct_adjacency.get(corner, [])
    
    print(f"\nCorner {corner}:")
    print(f"  Hardcoded adjacency: {hardcoded}")
    print(f"  Computed from edges: {computed}")
    
    if set(hardcoded) != set(computed):
        print(f"  ❌ MISMATCH!")
        extra_in_hardcoded = set(hardcoded) - set(computed)
        missing_from_hardcoded = set(computed) - set(hardcoded)
        if extra_in_hardcoded:
            print(f"    Extra in hardcoded: {extra_in_hardcoded}")
        if missing_from_hardcoded:
            print(f"    Missing from hardcoded: {missing_from_hardcoded}")

# Check all corners
mismatches = 0
for corner in range(54):
    hardcoded = set(CORNER_ADJACENCY.get(corner, []))
    computed = set(correct_adjacency.get(corner, []))
    if hardcoded != computed:
        mismatches += 1

print(f"\nTotal mismatches: {mismatches} out of 54 corners")

# Generate correct CORNER_ADJACENCY dict
if mismatches > 0:
    print("\n=== Correct CORNER_ADJACENCY ===")
    print("CORNER_ADJACENCY = {")
    for corner in sorted(correct_adjacency.keys()):
        print(f"    {corner}: {correct_adjacency[corner]},")
    print("}")