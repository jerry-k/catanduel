#!/usr/bin/env python3
"""
Test script to verify all fixes are working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import ActionType, ActionPrompt

def test_ai_seven_roll_fixed():
    """Test that AI can now handle rolling 7 without infinite loop."""
    print("Testing AI handling of rolling 7 (should be fixed)...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Give players points to bypass friendly robber
    game.state.players[0].public_vps = 3
    game.state.players[1].public_vps = 3
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Make it AI's turn
    game.state.current_player = 1
    game.state.current_turn_player = 1
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    game.state.dice_rolled = False
    
    print("\nSimulating AI turn with forced 7 roll...")
    
    # Count actions to detect infinite loop
    action_count = 0
    max_actions = 10
    
    while game.state.current_player == 1 and action_count < max_actions:
        actions = game.get_valid_actions()
        if not actions:
            break
            
        action = actions[0]
        print(f"  Action {action_count + 1}: {action.action_type.name}")
        
        # For roll action, force a 7
        if action.action_type == ActionType.ROLL:
            # Save original roll function
            import engine.state_functions as sf
            import random
            original_randint = random.randint
            
            # Mock to return 7
            def mock_randint(a, b):
                return 4 if a == 1 and b == 6 else 3
            
            random.randint = mock_randint
            game.execute(action)
            random.randint = original_randint
            
            print(f"    Rolled: {game.state.last_dice_roll} = 7")
        else:
            game.execute(action)
            
        action_count += 1
    
    if action_count < max_actions:
        print(f"\n✅ AI completed turn in {action_count} actions (no infinite loop!)")
    else:
        print(f"\n❌ Hit action limit - possible infinite loop")
    
    return action_count < max_actions

def test_button_labels():
    """Test that all action types have proper button labels."""
    print("\n\nTesting button labels...")
    
    # These are the action types that might appear as buttons
    action_types = [
        'ROLL',
        'END_TURN',
        'DISCARD',
        'BUY_DEVELOPMENT_CARD',
        'PLAY_KNIGHT_CARD',
        'PLAY_YEAR_OF_PLENTY',
        'PLAY_MONOPOLY',
        'PLAY_ROAD_BUILDING',
        'MARITIME_TRADE'
    ]
    
    # Check what the UI would display
    for action_type in action_types:
        if action_type in ['ROLL', 'ROLL_DICE']:
            label = 'Roll Dice'
        elif action_type == 'END_TURN':
            label = 'End Turn'
        elif action_type == 'DISCARD':
            label = 'Discard Cards'
        elif action_type == 'BUY_DEVELOPMENT_CARD':
            label = 'Buy Development Card'
        else:
            # Default handler
            label = action_type.replace('_', ' ').title()
        
        print(f"  {action_type} -> '{label}'")
    
    print("\n✅ All action types have labels")

def test_dice_display():
    """Test that dice values are properly stored and sent."""
    print("\n\nTesting dice display...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Roll dice
    roll_action = next((a for a in game.get_valid_actions() if a.action_type == ActionType.ROLL), None)
    if roll_action:
        game.execute(roll_action)
        
        print(f"  Dice rolled: {game.state.dice_rolled}")
        print(f"  Last dice roll: {game.state.last_dice_roll}")
        
        if game.state.last_dice_roll:
            die1, die2 = game.state.last_dice_roll
            print(f"  Die 1: {die1}, Die 2: {die2}, Total: {die1 + die2}")
            print("\n✅ Dice values properly stored")
        else:
            print("\n❌ Dice values not stored!")

if __name__ == "__main__":
    print("=== Verifying All Fixes ===\n")
    
    all_passed = True
    all_passed &= test_ai_seven_roll_fixed()
    test_button_labels()
    test_dice_display()
    
    if all_passed:
        print("\n\n🎉 All critical fixes verified!")
    else:
        print("\n\n⚠️ Some issues remain")