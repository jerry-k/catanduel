#!/usr/bin/env python3
"""Analyze why CatanatronMinimaxPlayer assigns low value to playing knights."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.enums import ActionType, KNIGHT

def analyze_knight_evaluation():
    """Analyze the evaluation function components when playing a knight."""
    
    print("Analyzing knight card evaluation...\n")
    
    # Create game with CatanatronMinimax
    p1 = CatanatronMinimaxPlayer(0, "CatanatronMM-0", max_depth=2)
    p2 = CatanatronMinimaxPlayer(1, "CatanatronMM-1", max_depth=2)
    game = Game([p1, p2])
    
    # Run through setup phase properly
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    # Give P0 knights and resources
    game.state.players[0].dev_cards[KNIGHT] = 3
    game.state.players[0].resources = [2, 2, 2, 2, 2]  # Plenty of resources
    
    # Print weight configuration
    print("CatanatronMinimax weights:")
    for key, value in p1.weights.items():
        print(f"  {key}: {value}")
    print()
    
    # Get to a state where we can play a knight
    actions = game.get_valid_actions()
    
    # Find knight action
    knight_actions = [a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    if not knight_actions:
        # Need to roll first
        roll_action = next(a for a in actions if a.action_type == ActionType.ROLL)
        game.execute(roll_action)
        actions = game.get_valid_actions()
        knight_actions = [a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    
    if knight_actions:
        knight_action = knight_actions[0]
        
        # Get current evaluation breakdown
        print("=== Current State Evaluation ===")
        eval_before = evaluate_with_breakdown(p1, game)
        
        # Execute knight action
        game_copy = game.copy()
        game_copy.execute(knight_action)
        
        print("\n=== After Playing Knight ===")
        eval_after = evaluate_with_breakdown(p1, game_copy)
        
        print(f"\n=== Evaluation Difference ===")
        print(f"Total change: {eval_after['total'] - eval_before['total']:.2f}")
        
        # Show what changed
        for key in eval_before:
            if key != 'total':
                diff = eval_after[key] - eval_before[key]
                if abs(diff) > 0.01:
                    print(f"  {key}: {diff:+.2f}")

def evaluate_with_breakdown(player, game):
    """Get detailed breakdown of evaluation components."""
    state = game.state
    my_player = state.players[player.player_id]
    opp_player = state.players[1 - player.player_id]
    
    breakdown = {}
    
    # Victory points
    vp_score = my_player.actual_vps() * player.weights["public_vps"]
    breakdown['vp_score'] = vp_score
    
    # Production
    my_production = player._calculate_production(state, player.player_id)
    opp_production = player._calculate_production(state, 1 - player.player_id)
    production_score = (
        my_production * player.weights["production"] +
        opp_production * player.weights["enemy_production"]
    )
    breakdown['my_production'] = my_production
    breakdown['opp_production'] = opp_production
    breakdown['production_score'] = production_score
    
    # Army size
    army_score = my_player.knights_played * player.weights["army_size"]
    breakdown['knights_played'] = my_player.knights_played
    breakdown['army_score'] = army_score
    
    # Dev cards in hand
    dev_score = my_player.total_dev_cards() * player.weights["hand_devs"]
    breakdown['dev_cards_in_hand'] = my_player.total_dev_cards()
    breakdown['dev_score'] = dev_score
    
    # Hand resources
    hand_resources = sum(my_player.resources) * player.weights["hand_resources"]
    breakdown['hand_resources'] = hand_resources
    
    # Total
    total = vp_score + production_score + army_score + dev_score + hand_resources
    breakdown['total'] = total
    
    # Print breakdown
    print(f"VP Score: {vp_score:.2f} (VPs: {my_player.actual_vps()})")
    print(f"Production Score: {production_score:.2f} (My: {my_production:.1f}, Opp: {opp_production:.1f})")
    print(f"Army Score: {army_score:.2f} (Knights: {my_player.knights_played})")
    print(f"Dev Card Score: {dev_score:.2f} (Cards: {my_player.total_dev_cards()})")
    print(f"Hand Resources: {hand_resources:.2f} (Total: {sum(my_player.resources)})")
    print(f"Total: {total:.2f}")
    
    return breakdown

if __name__ == "__main__":
    analyze_knight_evaluation()