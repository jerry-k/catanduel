#!/usr/bin/env python3
"""Test turn sequence to ensure dev cards are transferred correctly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, KNIGHT, ActionPrompt
from engine.state_functions import buy_development_card, end_turn

def test_turn_sequence():
    """Test that dev cards are managed correctly across turns."""
    print("Testing turn sequence with dev cards...")
    
    # Create game
    players = [RandomPlayer(0, "Human"), RandomPlayer(1, "AI")]
    game = Game(players)
    
    # Set up a simple test state
    game.state.initial_phase = False
    game.state.current_player = 0
    game.state.current_turn_player = 0
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    game.state.dice_rolled = True
    
    # Give resources
    game.state.players[0].resources = [2, 2, 2, 2, 2]
    
    # Test buying a dev card
    print("\n1. Player 0 buys a dev card...")
    # Manually buy a knight card
    game.state.dev_card_deck = [KNIGHT] * 5  # Ensure we get a knight
    buy_development_card(game.state, 0)
    
    print(f"   Cards in hand: {game.state.players[0].dev_cards[KNIGHT]}")
    print(f"   Cards bought this turn: {game.state.players[0].dev_cards_bought_this_turn[KNIGHT]}")
    
    # Check that knight is not playable
    game.state.invalidate_actions_cache()
    actions = game.get_valid_actions()
    knight_actions = [a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    print(f"   Knight actions available: {len(knight_actions)} (should be 0)")
    
    # End turn
    print("\n2. Player 0 ends turn...")
    end_turn(game.state)
    
    print(f"   Current player after end turn: {game.state.current_player}")
    print(f"   P0 cards in hand: {game.state.players[0].dev_cards[KNIGHT]}")
    print(f"   P0 cards bought this turn: {game.state.players[0].dev_cards_bought_this_turn[KNIGHT]}")
    print(f"   P1 cards in hand: {game.state.players[1].dev_cards[KNIGHT]}")
    print(f"   P1 cards bought this turn: {game.state.players[1].dev_cards_bought_this_turn[KNIGHT]}")
    
    # Simulate AI turn (just end it)
    print("\n3. AI (Player 1) ends turn...")
    end_turn(game.state)
    
    print(f"   Current player after AI turn: {game.state.current_player}")
    
    # Now check if P0 can play the knight
    print("\n4. Back to Player 0's turn...")
    game.state.dice_rolled = True  # Skip roll for test
    game.state.invalidate_actions_cache()
    actions = game.get_valid_actions()
    knight_actions = [a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    print(f"   Knight actions available: {len(knight_actions)} (should be 1)")
    
    if len(knight_actions) == 1:
        print("\n✓ Test PASSED! Dev cards are transferred correctly.")
    else:
        print("\n✗ Test FAILED! Dev card management is broken.")
    
    return len(knight_actions) == 1

if __name__ == "__main__":
    test_turn_sequence()