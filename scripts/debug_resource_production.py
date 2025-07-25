#!/usr/bin/env python3
"""Debug resource production."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import GreedyPlayer
from engine.models.enums import ActionType
from engine.colonist_map import HEX_TO_CORNERS

def debug_resources():
    """Check resource production."""
    p1 = GreedyPlayer(0, "Greedy-0")
    p2 = GreedyPlayer(1, "Greedy-1")
    game = Game([p1, p2])
    
    # Skip to after setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    print("=== BOARD SETUP ===")
    # Show what resources each player can get
    for player_id in [0, 1]:
        print(f"\nPlayer {player_id} settlements:")
        buildings = [(c, t) for c, (p, t) in game.state.board.buildings.items() if p == player_id]
        for corner, building_type in buildings:
            print(f"  Corner {corner} ({['', 'Settlement', 'City'][building_type]}):")
            # Find adjacent hexes
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    number = game.state.hex_numbers[hex_id]
                    hex_type = game.state.hex_types[hex_id]
                    if hex_type > 0:  # Not desert (0)
                        # hex types: 0=desert, 1=wood, 2=brick, 3=sheep, 4=wheat, 5=ore
                        resource_name = ['desert', 'wood', 'brick', 'sheep', 'wheat', 'ore'][hex_type]
                        print(f"    Hex {hex_id}: {resource_name} on {number}")
    
    print("\n=== DICE ROLLS (first 20 turns) ===")
    resource_names = ['wood', 'brick', 'sheep', 'wheat', 'ore']
    total_resources = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    
    for turn in range(20):
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        
        # Look for roll action
        roll_action = next((a for a in actions if a.action_type == ActionType.ROLL), None)
        if roll_action:
            # Execute roll
            prev_resources = [list(game.state.players[0].resources), list(game.state.players[1].resources)]
            game.execute(roll_action)
            
            # Check dice result
            dice = game.state.last_dice_roll
            if dice:
                total = dice[0] + dice[1]
                print(f"Turn {turn}: Rolled {dice[0]}+{dice[1]}={total}")
                
                # Check resource gains
                for pid in [0, 1]:
                    gained = []
                    for i in range(5):
                        diff = game.state.players[pid].resources[i] - prev_resources[pid][i]
                        if diff > 0:
                            gained.append(f"{diff} {resource_names[i]}")
                            total_resources[pid][i] += diff
                    if gained:
                        print(f"  P{pid} gains: {', '.join(gained)}")
            
            # Continue turn
            actions = game.get_valid_actions()
            action = game.players[current].decide(game, actions)
            game.execute(action)
        else:
            # No roll action, just execute
            action = game.players[current].decide(game, actions)
            game.execute(action)
    
    print(f"\n=== TOTAL RESOURCES GAINED ===")
    for pid in [0, 1]:
        res_str = ', '.join(f"{total_resources[pid][i]} {resource_names[i]}" for i in range(5))
        print(f"Player {pid}: {res_str}")
    
    print(f"\n=== CURRENT RESOURCES ===")
    for pid in [0, 1]:
        player = game.state.players[pid]
        res_str = ', '.join(f"{player.resources[i]} {resource_names[i]}" for i in range(5))
        print(f"Player {pid}: {res_str}")

if __name__ == "__main__":
    debug_resources()