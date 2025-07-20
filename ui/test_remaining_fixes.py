#!/usr/bin/env python3
"""
Test the remaining fixes for maritime trade, buy dev card, and dice display.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, WOOD, BRICK, SHEEP, WHEAT, ORE

def test_maritime_trade_action_format():
    """Test that maritime trade actions are properly formatted."""
    print("=== Testing Maritime Trade Action Format ===")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Give player resources for trading
    game.state.players[0].resources = [8, 0, 0, 0, 0]  # 8 wood
    game.state.dice_rolled = True
    game.state.invalidate_actions_cache()
    
    # Get maritime trade actions
    actions = game.get_valid_actions()
    trade_actions = [a for a in actions if a.action_type == ActionType.MARITIME_TRADE]
    
    print(f"Found {len(trade_actions)} maritime trade actions")
    
    # Check action format
    if trade_actions:
        sample_action = trade_actions[0]
        print(f"Sample action value: {sample_action.value}")
        print(f"Value type: {type(sample_action.value)}")
        print(f"Value length: {len(sample_action.value)}")
        
        give_res, give_amount, get_res = sample_action.value
        print(f"Format: give {give_amount} {['wood','brick','sheep','wheat','ore'][give_res]} for 1 {['wood','brick','sheep','wheat','ore'][get_res]}")
        print("✅ Maritime trade action format correct")
    else:
        print("❌ No maritime trade actions found")

def test_buy_dev_card_action_name():
    """Test that buy dev card action has correct name."""
    print("\n=== Testing Buy Dev Card Action Name ===")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Give resources to buy dev card
    game.state.players[0].resources = [0, 0, 1, 1, 1]  # sheep, wheat, ore
    game.state.dice_rolled = True
    game.state.invalidate_actions_cache()
    
    # Check for buy dev card action
    actions = game.get_valid_actions()
    buy_actions = [a for a in actions if a.action_type == ActionType.BUY_DEVELOPMENT_CARD]
    
    if buy_actions:
        print(f"Found BUY_DEVELOPMENT_CARD action")
        print(f"Action type name: {buy_actions[0].action_type.name}")
        print("✅ Buy dev card action available")
    else:
        print("❌ No buy dev card action found")

def test_dice_values_storage():
    """Test that dice values are properly stored for display."""
    print("\n=== Testing Dice Values Storage ===")
    
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
        
        if game.state.last_dice_roll:
            die1, die2 = game.state.last_dice_roll
            print(f"Dice rolled: {die1} + {die2} = {die1 + die2}")
            print(f"Last dice roll stored as: {game.state.last_dice_roll}")
            print(f"Type: {type(game.state.last_dice_roll)}")
            print("✅ Dice values properly stored")
        else:
            print("❌ Dice values not stored")
    else:
        print("❌ No roll action available")

if __name__ == "__main__":
    test_maritime_trade_action_format()
    test_buy_dev_card_action_name()
    test_dice_values_storage()
    print("\n🎉 All tests completed!")