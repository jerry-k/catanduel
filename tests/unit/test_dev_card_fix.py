#!/usr/bin/env python3
"""Test the dev card fix to ensure cards aren't playable on the turn they're bought."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, KNIGHT

def test_dev_card_not_playable_same_turn():
    """Test that dev cards bought this turn can't be played."""
    print("Testing dev card fix...")
    
    # Create game
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Give player resources to buy dev card
    game.state.players[0].resources = [2, 2, 2, 2, 2]  # Plenty of resources
    
    # Player 0's turn - buy a dev card
    game.state.current_player = 0
    game.state.current_turn_player = 0
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    game.state.dice_rolled = True
    game.state.invalidate_actions_cache()
    
    # Find and execute BUY_DEVELOPMENT_CARD
    actions = game.get_valid_actions()
    buy_action = None
    for action in actions:
        if action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
            buy_action = action
            break
    
    if not buy_action:
        print("ERROR: No BUY_DEVELOPMENT_CARD action available")
        return False
    
    # Execute buy
    game.execute(buy_action)
    
    # Check that a dev card was bought this turn
    bought_this_turn = sum(game.state.players[0].dev_cards_bought_this_turn)
    print(f"Dev cards bought this turn: {bought_this_turn}")
    
    # Check valid actions - should NOT include playing the dev card
    actions = game.get_valid_actions()
    knight_actions = [a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    
    if knight_actions:
        print("ERROR: Knight card is playable on the turn it was bought!")
        return False
    
    # End turn
    end_turn_action = None
    for action in actions:
        if action.action_type == ActionType.END_TURN:
            end_turn_action = action
            break
    
    if end_turn_action:
        game.execute(end_turn_action)
        print("Turn ended successfully")
    
    # Check that cards were transferred properly
    total_cards_p0 = sum(game.state.players[0].dev_cards)
    bought_this_turn_p0 = sum(game.state.players[0].dev_cards_bought_this_turn)
    
    print(f"Player 0 after end turn - Regular cards: {total_cards_p0}, Bought this turn: {bought_this_turn_p0}")
    
    if bought_this_turn_p0 > 0:
        print("ERROR: Cards bought this turn not transferred!")
        return False
    
    print("✓ Test passed! Dev cards are properly managed.")
    return True

if __name__ == "__main__":
    from engine.models.enums import ActionPrompt
    test_dev_card_not_playable_same_turn()