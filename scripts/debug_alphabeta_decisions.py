#!/usr/bin/env python3
"""Debug why CatanatronAlphaBetaPlayer doesn't buy dev cards."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.models.enums import ActionType

def debug_decisions():
    """Debug decision making process."""
    
    print("Debugging CatanatronAlphaBetaPlayer decisions...\n")
    
    # Create game
    p1 = CatanatronAlphaBetaPlayer(0, "AlphaBeta-0", depth=2)
    p2 = CatanatronAlphaBetaPlayer(1, "AlphaBeta-1", depth=2)
    game = Game([p1, p2])
    
    # Play until we have resources to buy dev card
    turn = 0
    found_dev_card_opportunity = False
    
    while not game.is_over() and turn < 50 and not found_dev_card_opportunity:
        actions = game.get_valid_actions()
        if not actions:
            break
        
        current = game.state.current_player
        
        # Check if can buy dev card
        buy_dev_actions = [a for a in actions if a.action_type == ActionType.BUY_DEVELOPMENT_CARD]
        if buy_dev_actions and current == 0:
            print(f"\nTurn {turn}, P{current} can buy dev card!")
            
            # Show current state
            player = game.state.players[current]
            resources = ["wood", "brick", "sheep", "wheat", "ore"]
            res_str = ", ".join([f"{r}={player.resources[i]}" for i, r in enumerate(resources)])
            print(f"Resources: {res_str}")
            print(f"Current VPs: {player.actual_vps()}")
            print(f"Dev cards in hand: {player.total_dev_cards()}")
            
            # Get evaluation for buy dev card
            print(f"\nEvaluating BUY_DEVELOPMENT_CARD...")
            dev_value = p1._expectimax_value(game, buy_dev_actions[0], 1)
            print(f"Value: {dev_value:.2f}")
            
            # Compare with other actions
            print(f"\nOther available actions:")
            for action in actions[:5]:  # Show first 5
                if action.action_type != ActionType.BUY_DEVELOPMENT_CARD:
                    value = p1._expectimax_value(game, action, 1)
                    print(f"  {action.action_type.name}: {value:.2f}")
            
            # Check END_TURN value
            end_turn_actions = [a for a in actions if a.action_type == ActionType.END_TURN]
            if end_turn_actions:
                end_value = p1._expectimax_value(game, end_turn_actions[0], 1)
                print(f"  END_TURN: {end_value:.2f}")
            
            # Show weights being used
            print(f"\nKey weights:")
            print(f"  public_vps: {p1.weights['public_vps']:.0e}")
            print(f"  hand_devs: {p1.weights['hand_devs']}")
            print(f"  production: {p1.weights['production']:.0e}")
            
            # Show decision
            decision = p1.decide(game, actions)
            print(f"\nDecision: {decision.action_type.name}")
            
            found_dev_card_opportunity = True
            break
        
        # Make decision
        action = game.players[current].decide(game, actions)
        game.execute(action)
        
        if action.action_type == ActionType.END_TURN:
            turn += 1
    
    if not found_dev_card_opportunity:
        print("No dev card buying opportunity found in 50 turns")

if __name__ == "__main__":
    debug_decisions()