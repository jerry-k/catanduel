#!/usr/bin/env python3
"""Debug why games are stalling with no building."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import GreedyPlayer
from engine.models.enums import ActionType

def analyze_game():
    """Run a game and analyze why players aren't building."""
    p1 = GreedyPlayer(0, "Greedy-0")
    p2 = GreedyPlayer(1, "Greedy-1")
    game = Game([p1, p2])
    
    # Skip to after setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    print("Setup complete. Analyzing main game...")
    print(f"P0 starting resources: {game.state.players[0].resources}")
    print(f"P1 starting resources: {game.state.players[1].resources}")
    print()
    
    # Track building opportunities
    turns_with_settlement_option = 0
    turns_with_city_option = 0
    total_turns = 0
    
    for turn in range(50):
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        
        # Check for building options
        has_settlement = any(a.action_type == ActionType.BUILD_SETTLEMENT for a in actions)
        has_city = any(a.action_type == ActionType.BUILD_CITY for a in actions)
        
        if has_settlement:
            turns_with_settlement_option += 1
            print(f"Turn {turn}: Player {current} CAN build settlement!")
            print(f"  Resources: {game.state.players[current].resources}")
            print(f"  Action chosen: ", end="")
        
        if has_city:
            turns_with_city_option += 1
            
        # Execute turn
        action = game.players[current].decide(game, actions)
        if has_settlement:
            print(f"{action.action_type.name}")
            
        game.execute(action)
        
        # Count actual turns (not just actions)
        if action.action_type == ActionType.END_TURN:
            total_turns += 1
    
    print(f"\nSummary after {total_turns} turns:")
    print(f"Turns where settlement was possible: {turns_with_settlement_option}")
    print(f"Turns where city was possible: {turns_with_city_option}")
    print(f"Final VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")
    
    # Check for valid settlement spots
    print("\nChecking for valid settlement locations...")
    for player_id in [0, 1]:
        valid_spots = 0
        for corner in range(54):
            if game.state.board.can_build_settlement(player_id, corner):
                valid_spots += 1
        print(f"Player {player_id} has {valid_spots} valid settlement spots")

if __name__ == "__main__":
    analyze_game()