#!/usr/bin/env python3
"""
Test script to debug AI behavior when rolling 7.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import ActionType, ActionPrompt
import engine.state_functions as sf

def test_ai_full_turn_with_seven():
    """Test a complete AI turn when rolling 7."""
    print("Testing complete AI turn with 7 roll...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Give players some points to bypass friendly robber
    game.state.players[0].public_vps = 3
    game.state.players[1].public_vps = 3
    
    # Complete setup phase
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Make it AI's turn
    game.state.current_player = 1
    game.state.current_turn_player = 1
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    game.state.dice_rolled = False
    
    print(f"\n=== Starting AI Turn ===")
    print(f"Current player: {game.state.current_player}")
    print(f"Current prompt: {game.state.current_prompt}")
    
    # Simulate what the web server does
    turn_complete = False
    action_count = 0
    max_actions = 20
    
    while game.state.current_player == 1 and not turn_complete and action_count < max_actions:
        actions = game.get_valid_actions()
        
        print(f"\n--- Action {action_count + 1} ---")
        print(f"Current prompt: {game.state.current_prompt}")
        print(f"Available actions: {len(actions)}")
        
        if not actions:
            print("No valid actions!")
            break
        
        # Show available action types
        action_types = set(a.action_type.name for a in actions)
        print(f"Action types: {sorted(action_types)}")
        
        # Take first action
        action = actions[0]
        print(f"AI choosing: {action.action_type.name}")
        
        # Debug: check if cache is the issue
        if game.state.current_prompt == ActionPrompt.MOVE_ROBBER and action.action_type == ActionType.ROLL:
            print("ERROR: Got ROLL action when expecting MOVE_ROBBER!")
            print(f"Cache status: {game.state._valid_actions_cache is not None}")
            # Clear cache and try again
            game.state.invalidate_actions_cache()
            actions = game.get_valid_actions()
            print(f"After cache clear, actions: {len(actions)}")
            if actions:
                action = actions[0]
                print(f"New action type: {action.action_type.name}")
        
        # For ROLL action, force a 7
        if action.action_type == ActionType.ROLL:
            # Execute the roll
            die1, die2 = sf.roll_dice(game.state)
            # Force it to be 7
            game.state.last_dice_roll = (3, 4)
            print(f"Forced dice roll: 7")
            
            # Manually trigger 7 logic
            game.state.current_turn_player = game.state.current_player
            
            # Check who needs to discard
            discarders = [
                game.state.players[i].total_resources() > 7
                for i in range(2)
            ]
            
            if any(discarders):
                print("Someone needs to discard")
                if discarders[0]:
                    game.state.current_player = 0
                else:
                    game.state.current_player = 1
                game.state.current_prompt = ActionPrompt.DISCARD
                game.state.is_discarding = True
            else:
                print("No one needs to discard")
                game.state.is_moving_robber = True
                sf.check_friendly_robber(game.state)
        else:
            # Execute other actions normally
            success = game.execute(action)
            print(f"Action success: {success}")
        
        # Check if turn ended
        if action.action_type == ActionType.END_TURN:
            turn_complete = True
            print("Turn ended")
        
        action_count += 1
        
        # Show state after action
        print(f"After action:")
        print(f"  Current player: {game.state.current_player}")
        print(f"  Current prompt: {game.state.current_prompt}")
        print(f"  Is moving robber: {game.state.is_moving_robber}")
        print(f"  Dice rolled: {game.state.dice_rolled}")
    
    if action_count >= max_actions:
        print("\n⚠️ Hit action limit - possible infinite loop!")
    
    print(f"\n=== Turn Summary ===")
    print(f"Total actions taken: {action_count}")
    print(f"Final current player: {game.state.current_player}")
    print(f"Turn complete: {turn_complete}")

if __name__ == "__main__":
    test_ai_full_turn_with_seven()
    print("\n✅ Test completed!")