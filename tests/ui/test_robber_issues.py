#!/usr/bin/env python3
"""
Test script to investigate robber and AI issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import ActionType, ActionPrompt
import engine.state_functions as sf

def test_friendly_robber():
    """Test that friendly robber rule works correctly."""
    print("Testing friendly robber mechanic...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup phase
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    print(f"\nAfter setup:")
    print(f"  Player 0 VPs: {game.state.players[0].public_vps}")
    print(f"  Player 1 VPs: {game.state.players[1].public_vps}")
    
    # Force a 7 roll
    game.state.dice_rolled = False
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Manually simulate rolling a 7
    game.state.dice_rolled = True
    game.state.last_dice_roll = (3, 4)  # Total of 7
    
    # Check if anyone needs to discard
    discarders = [
        game.state.players[i].total_resources() > 7
        for i in range(2)
    ]
    
    if not any(discarders):
        # No one needs to discard, should check friendly robber
        game.state.is_moving_robber = True
        sf.check_friendly_robber(game.state)
        
        print(f"\nAfter rolling 7 (no discards needed):")
        print(f"  Current prompt: {game.state.current_prompt}")
        print(f"  Is moving robber: {game.state.is_moving_robber}")
        
        if game.state.current_prompt == ActionPrompt.PLAY_TURN:
            print("  ✅ Friendly robber applied correctly!")
        else:
            print("  ❌ Friendly robber NOT applied - robber can be moved")

def test_ai_robber_handling():
    """Test that AI can handle robber movement."""
    print("\n\nTesting AI robber handling...")
    
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
    
    print(f"\nBefore AI rolls:")
    print(f"  Current player: {game.state.current_player}")
    print(f"  Current prompt: {game.state.current_prompt}")
    
    # AI rolls
    roll_action = next((a for a in game.get_valid_actions() if a.action_type == ActionType.ROLL), None)
    if roll_action:
        # Force a 7
        game.execute(roll_action)
        game.state.last_dice_roll = (3, 4)
        
        # Manually trigger 7 logic
        game.state.current_turn_player = game.state.current_player
        game.state.is_moving_robber = True
        sf.check_friendly_robber(game.state)
        
        print(f"\nAfter AI rolls 7:")
        print(f"  Current player: {game.state.current_player}")
        print(f"  Current prompt: {game.state.current_prompt}")
        print(f"  Is moving robber: {game.state.is_moving_robber}")
        
        # Check if AI can move robber
        robber_actions = game.get_valid_actions()
        print(f"  Valid actions: {len(robber_actions)}")
        if robber_actions:
            print(f"  First action type: {robber_actions[0].action_type}")
            
            # Execute robber movement
            game.execute(robber_actions[0])
            
            print(f"\nAfter AI moves robber:")
            print(f"  Current player: {game.state.current_player}")
            print(f"  Current prompt: {game.state.current_prompt}")
            print(f"  Is moving robber: {game.state.is_moving_robber}")

def test_action_types():
    """Test what action types are available."""
    print("\n\nTesting action types...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Give resources for buying dev card
    game.state.players[0].resources = [5, 5, 5, 5, 5]  # Plenty of everything
    
    # Get all possible actions
    actions = game.get_valid_actions()
    
    print(f"\nAvailable action types:")
    action_types = set(a.action_type.name for a in actions)
    for action_type in sorted(action_types):
        count = sum(1 for a in actions if a.action_type.name == action_type)
        print(f"  {action_type}: {count} actions")

if __name__ == "__main__":
    test_friendly_robber()
    test_ai_robber_handling()
    test_action_types()
    print("\n✅ Tests completed!")