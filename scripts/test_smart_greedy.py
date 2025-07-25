#!/usr/bin/env python3
"""Test SmartGreedyPlayer to see if it avoids resource starvation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import GreedyPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.enums import ActionType
from engine.colonist_map import HEX_TO_CORNERS

def test_placement(player_class1, player_class2, name1, name2):
    """Test initial placement with given player types."""
    p1 = player_class1(0, f"{name1}-0")
    p2 = player_class2(1, f"{name2}-1")
    game = Game([p1, p2])
    
    print(f"\n=== {name1} vs {name2} ===")
    
    # Track setup phase
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    # Analyze placement
    for player_id in [0, 1]:
        print(f"\nPlayer {player_id} ({game.players[player_id].name}):")
        buildings = [(c, t) for c, (p, t) in game.state.board.buildings.items() if p == player_id]
        
        resources_available = set()
        total_production = 0.0
        
        for corner, _ in buildings:
            print(f"  Settlement at corner {corner}:")
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    hex_type = game.state.hex_types[hex_id]
                    number = game.state.hex_numbers[hex_id]
                    if hex_type > 0:  # Not desert
                        resource_name = ['desert', 'wood', 'brick', 'sheep', 'wheat', 'ore'][hex_type]
                        resources_available.add(resource_name)
                        
                        # Calculate production value
                        prob_map = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
                        production = prob_map.get(number, 0)
                        total_production += production
                        
                        print(f"    - {resource_name} on {number} (prod: {production})")
        
        print(f"  Total resources: {sorted(resources_available)}")
        print(f"  Total production value: {total_production}")
        print(f"  Has brick: {'YES ✅' if 'brick' in resources_available else 'NO ❌'}")
        print(f"  Has wood: {'YES ✅' if 'wood' in resources_available else 'NO ❌'}")
        
        # Starting resources (from second settlement)
        print(f"  Starting resources: {game.state.players[player_id].resources}")
    
    # Quick simulation
    print("\nQuick simulation (20 turns):")
    roads_built = [0, 0]
    settlements_built = [0, 0]
    
    for _ in range(40):  # 40 actions
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        action = game.players[current].decide(game, actions)
        
        if action.action_type == ActionType.BUILD_ROAD:
            roads_built[current] += 1
        elif action.action_type == ActionType.BUILD_SETTLEMENT:
            settlements_built[current] += 1
            
        game.execute(action)
        
        if action.action_type == ActionType.END_TURN and game.state.turn_number >= 20:
            break
    
    print(f"  P0: +{roads_built[0]} roads, +{settlements_built[0]} settlements")
    print(f"  P1: +{roads_built[1]} roads, +{settlements_built[1]} settlements")
    print(f"  Final VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")

# Test different combinations
print("Testing initial settlement placement strategies...\n")

# Regular Greedy vs Greedy (baseline)
test_placement(GreedyPlayer, GreedyPlayer, "Greedy", "Greedy")

# Smart Greedy vs Smart Greedy  
test_placement(SmartGreedyPlayer, SmartGreedyPlayer, "SmartGreedy", "SmartGreedy")

# Smart Greedy vs Regular Greedy
test_placement(SmartGreedyPlayer, GreedyPlayer, "SmartGreedy", "Greedy")