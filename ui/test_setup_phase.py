#!/usr/bin/env python3
"""
Test script to understand setup phase player switching.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import ActionType

def test_setup_phase_flow():
    """Test the complete setup phase flow."""
    print("Testing setup phase flow...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    print(f"\nInitial state:")
    print(f"  setup_phase_player_order(): {game.state.setup_phase_player_order()}")
    print(f"  current_player: {game.state.current_player}")
    print(f"  current_prompt: {game.state.current_prompt.name}")
    
    action_count = 0
    max_actions = 10  # Prevent infinite loop
    
    while game.state.is_setup_phase() and action_count < max_actions:
        # Get who should act
        acting_player = game.state.setup_phase_player_order()
        
        # Get valid actions
        actions = game.get_valid_actions()
        
        print(f"\nAction {action_count + 1}:")
        print(f"  Acting player (from setup_phase_player_order): {acting_player}")
        print(f"  Current player (state.current_player): {game.state.current_player}")
        print(f"  Prompt: {game.state.current_prompt.name}")
        print(f"  Valid actions: {len(actions)}")
        
        if actions:
            # Take first action
            action = actions[0]
            print(f"  Taking action: {action.action_type.name} at {action.value}")
            
            success = game.execute(action)
            print(f"  Success: {success}")
            
            # Show state after action
            print(f"  After action:")
            print(f"    Settlements placed: {game.state.initial_settlements_placed}")
            print(f"    Roads placed: {len(game.state.board.roads)}")
            print(f"    setup_phase_player_order(): {game.state.setup_phase_player_order()}")
            print(f"    current_player: {game.state.current_player}")
        else:
            print("  ERROR: No valid actions!")
            break
            
        action_count += 1
    
    print(f"\nSetup phase complete: {not game.state.is_setup_phase()}")
    print(f"Final current player: {game.state.current_player}")
    print(f"Final prompt: {game.state.current_prompt.name}")

if __name__ == "__main__":
    test_setup_phase_flow()
    print("\n✅ Test completed!")