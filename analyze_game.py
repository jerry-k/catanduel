#!/usr/bin/env python3
"""Analyze game log to understand first player advantage."""

import re

def analyze_game_log(filename):
    """Extract key statistics from game log."""
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Track key metrics
    vp_progression = []
    resource_counts = []
    dev_cards_bought = [0, 0]
    settlements_built = [0, 0]
    cities_built = [0, 0]
    roads_built = [0, 0]
    
    current_turn = 0
    
    for line in lines:
        # Track VP progression
        if "Victory Points:" in line and "---" not in line:
            # Extract VPs
            match = re.search(r'P0=(\d+).*P1=(\d+)', line)
            if match:
                p0_vp = int(match.group(1))
                p1_vp = int(match.group(2))
                vp_progression.append((current_turn, p0_vp, p1_vp))
        
        # Track turn number
        if "--- Turn" in line:
            match = re.search(r'Turn (\d+)', line)
            if match:
                current_turn = int(match.group(1))
        
        # Track actions
        if "buys development card" in line:
            if "Player 0" in line:
                dev_cards_bought[0] += 1
            else:
                dev_cards_bought[1] += 1
        
        if "builds settlement" in line and "initial" not in line:
            if "Player 0" in line:
                settlements_built[0] += 1
            else:
                settlements_built[1] += 1
        
        if "upgrades settlement to city" in line:
            if "Player 0" in line:
                cities_built[0] += 1
            else:
                cities_built[1] += 1
        
        if "builds road" in line and "initial" not in line:
            if "Player 0" in line:
                roads_built[0] += 1
            else:
                roads_built[1] += 1
    
    # Print analysis
    print("Game Analysis")
    print("=" * 50)
    
    # Extract starting positions
    print("\nInitial Placement Analysis:")
    print("-" * 40)
    placement_order = []
    for i, line in enumerate(lines[:20]):
        if "places initial settlement at corner" in line:
            match = re.search(r'Player (\d+).*corner (\d+)', line)
            if match:
                player = int(match.group(1))
                corner = int(match.group(2))
                placement_order.append((player, corner))
                print(f"Player {player} settlement at corner {corner}")
    
    print(f"\nPlacement order: {['P'+str(p) for p, _ in placement_order]}")
    
    # Resource analysis
    print("\nResource Generation (first 20 turns):")
    print("-" * 40)
    resources_gained = [[0,0,0,0,0], [0,0,0,0,0]]  # [wood, brick, sheep, wheat, ore]
    resource_map = {'wood': 0, 'brick': 1, 'sheep': 2, 'wheat': 3, 'ore': 4}
    
    for line in lines[:300]:  # First ~60 turns
        if "gains" in line and "Player" in line:
            for res_name, idx in resource_map.items():
                match = re.search(rf'Player (\d+) gains (\d+) {res_name}', line)
                if match:
                    player = int(match.group(1))
                    amount = int(match.group(2))
                    resources_gained[player][idx] += amount
    
    print("P0 resources:", dict(zip(['wood','brick','sheep','wheat','ore'], resources_gained[0])))
    print("P1 resources:", dict(zip(['wood','brick','sheep','wheat','ore'], resources_gained[1])))
    
    print("\nVP Progression:")
    print("Turn | P0 VP | P1 VP | Leader")
    print("-" * 40)
    for turn, p0_vp, p1_vp in vp_progression:
        leader = "P0" if p0_vp > p1_vp else "P1" if p1_vp > p0_vp else "Tied"
        print(f"{turn:4d} | {p0_vp:5d} | {p1_vp:5d} | {leader}")
    
    print("\nBuilding Summary:")
    print(f"Player 0 (Catanatron): {settlements_built[0]} settlements, {cities_built[0]} cities, {roads_built[0]} roads")
    print(f"Player 1 (CatanatronAB): {settlements_built[1]} settlements, {cities_built[1]} cities, {roads_built[1]} roads")
    
    print(f"\nDevelopment Cards:")
    print(f"Player 0: {dev_cards_bought[0]} cards")
    print(f"Player 1: {dev_cards_bought[1]} cards")
    
    # Find when P1 took the lead
    for i, (turn, p0_vp, p1_vp) in enumerate(vp_progression):
        if p1_vp > p0_vp:
            print(f"\nP1 first took lead at turn {turn}")
            break
    
    # Check if P0 ever regained lead
    p0_led_after_p1 = False
    for i, (turn, p0_vp, p1_vp) in enumerate(vp_progression):
        if i > 0 and p0_vp > p1_vp:
            prev_turn, prev_p0, prev_p1 = vp_progression[i-1]
            if prev_p1 >= prev_p0:
                p0_led_after_p1 = True
                print(f"P0 regained lead at turn {turn}")
                break
    
    if not p0_led_after_p1:
        print("P0 never regained the lead after P1 took it")

if __name__ == "__main__":
    analyze_game_log("game_analysis.txt")