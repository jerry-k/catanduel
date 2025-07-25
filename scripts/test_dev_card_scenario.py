#!/usr/bin/env python3
"""Test specific dev card scenario to see why bots don't play them."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.enums import ActionType, KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING

def test_dev_card_decisions():
    """Test why bots might not play dev cards."""
    
    print("Testing dev card decision-making...\n")
    
    # Set up a game
    p1 = CatanatronMinimaxPlayer(0, "CatanatronMM-0", max_depth=2, time_limit=5.0)
    p2 = SmartGreedyPlayer(1, "SmartGreedy-1")
    game = Game([p1, p2])
    
    # Skip setup - manually place settlements and roads to save time
    # P0 settlements
    game.state.board.place_initial_settlement(0, 20)
    game.state.board.place_initial_road(0, 23)
    game.state.board.place_initial_settlement(0, 33)
    game.state.board.place_initial_road(0, 40)
    
    # P1 settlements  
    game.state.board.place_initial_settlement(1, 12)
    game.state.board.place_initial_road(1, 13)  # Edge 13 connects to corner 12
    game.state.board.place_initial_settlement(1, 43)
    game.state.board.place_initial_road(1, 51)  # Edge 51 connects to corner 43
    
    # Give initial resources for second settlements
    game.state.players[0].resources = [1, 1, 1, 1, 0]  # wood, brick, sheep, wheat
    game.state.players[1].resources = [0, 2, 1, 1, 0]  # brick x2, sheep, wheat
    
    # Set to main game phase
    game.state.setup_phase = False
    game.state.current_player = 0
    
    # Give P0 some dev cards to test decision-making
    game.state.players[0].dev_cards[KNIGHT] = 2
    game.state.players[0].dev_cards[YEAR_OF_PLENTY] = 1
    print("Starting P0 with 2 Knights and 1 Year of Plenty card")
    
    # Track when cards are bought but not played
    dev_cards_in_hand = [0, 0]
    
    for turn in range(100):
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        
        # Update dev cards in hand
        player = game.state.players[current]
        cards_in_hand = (
            player.dev_cards[KNIGHT] +
            player.dev_cards[YEAR_OF_PLENTY] +
            player.dev_cards[MONOPOLY] +
            player.dev_cards[ROAD_BUILDING]
        )
        dev_cards_in_hand[current] = cards_in_hand
        
        # Check if player has cards but isn't playing them
        play_actions = [a for a in actions if 'PLAY' in a.action_type.name and 'PLAY_YEAR' not in a.action_type.name]
        
        if cards_in_hand > 0 and current == 0:  # Focus on P0 (Catanatron)
            print(f"\nTurn {turn}, P{current} has {cards_in_hand} dev cards:")
            print(f"  Knights: {player.dev_cards[KNIGHT]}")
            print(f"  Year of Plenty: {player.dev_cards[YEAR_OF_PLENTY]}")
            print(f"  Monopoly: {player.dev_cards[MONOPOLY]}")
            print(f"  Road Building: {player.dev_cards[ROAD_BUILDING]}")
            print(f"  Can play: {[a.action_type.name for a in play_actions]}")
            
            # Show other available actions
            other_actions = [a.action_type.name for a in actions if 'PLAY' not in a.action_type.name]
            print(f"  Other options: {set(other_actions)}")
        
        # Get decision
        action = game.players[current].decide(game, actions)
        
        # Log decision if they have cards
        if cards_in_hand > 0 and current == 0:
            print(f"  -> Chose: {action.action_type.name}")
            
            # If they didn't play a card, check why
            if 'PLAY' not in action.action_type.name and play_actions:
                # Check evaluation
                if hasattr(p1, '_evaluate_state'):
                    current_eval = p1._evaluate_state(game)
                    
                    # Simulate playing a knight
                    if any(a.action_type == ActionType.PLAY_KNIGHT_CARD for a in play_actions):
                        game_copy = game.copy()
                        knight_action = next(a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD)
                        game_copy.execute(knight_action)
                        knight_eval = p1._evaluate_state(game_copy)
                        
                        print(f"  Evaluation: current={current_eval:.2f}, after knight={knight_eval:.2f}")
                        print(f"  Diff: {knight_eval - current_eval:.2f}")
        
        # Execute action
        if action.action_type == ActionType.BUY_DEVELOPMENT_CARD and current == 0:
            print(f"  -> P{current} buying dev card (total will be {dev_cards_in_hand[current] + 1})")
        
        game.execute(action)
        
        if action.action_type == ActionType.END_TURN:
            turn += 1
    
    print(f"\n\nFinal dev cards in hand:")
    for i in range(2):
        player = game.state.players[i]
        cards = (
            player.dev_cards[KNIGHT] +
            player.dev_cards[YEAR_OF_PLENTY] +
            player.dev_cards[MONOPOLY] +
            player.dev_cards[ROAD_BUILDING]
        )
        if cards > 0:
            print(f"  P{i}: {cards} unplayed cards")

if __name__ == "__main__":
    test_dev_card_decisions()