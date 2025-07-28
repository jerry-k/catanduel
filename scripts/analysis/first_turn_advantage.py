#!/usr/bin/env python3
"""
Analyze what happens in the first few turns to understand first player advantage.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.models.actions import ActionType
from engine.models.enums import ActionType

def analyze_early_game(num_games=5):
    """Analyze the first 10 turns of each game."""
    
    print("Early Game Analysis - First 10 Turns")
    print("=" * 60)
    
    for game_num in range(num_games):
        # Alternate starting positions
        if game_num % 2 == 0:
            players = [
                CatanatronMinimaxPlayer(0, "Catanatron"),
                CatanatronAlphaBetaPlayer(1, "CatanatronAB")
            ]
            first_name = "Catanatron"
        else:
            players = [
                CatanatronAlphaBetaPlayer(0, "CatanatronAB"),
                CatanatronMinimaxPlayer(1, "Catanatron")
            ]
            first_name = "CatanatronAB"
        
        game = Game(players)
        
        print(f"\nGame {game_num + 1}: {first_name} (P0) goes first")
        print("-" * 40)
        
        # Play through initial setup quickly
        while game.state.initial_phase:
            actions = game.get_valid_actions()
            player = game.state.setup_phase_player_order()
            action = players[player].decide(game, actions)
            game.execute(action)
        
        # Track first 10 turns
        turn_count = 0
        resources_gained = [[0,0,0,0,0], [0,0,0,0,0]]
        buildings_built = [{"roads": 0, "settlements": 0, "cities": 0, "dev_cards": 0},
                          {"roads": 0, "settlements": 0, "cities": 0, "dev_cards": 0}]
        
        while turn_count < 10 and not game.is_over():
            actions = game.get_valid_actions()
            current = game.state.current_player
            action = players[current].decide(game, actions)
            
            # Track what happens
            if action.action_type == ActionType.ROLL:
                game.execute(action)
                dice_sum = sum(game.state.last_dice_roll)
                
                # Check resource gains
                print(f"\nTurn {turn_count + 1} - P{current} rolls {dice_sum}")
                
                # Count resources after roll
                for p_idx in range(2):
                    gained = []
                    for r_idx in range(5):
                        diff = game.state.players[p_idx].resources[r_idx] - resources_gained[p_idx][r_idx]
                        if diff > 0:
                            gained.append(f"{diff} {['wood','brick','sheep','wheat','ore'][r_idx]}")
                        resources_gained[p_idx][r_idx] = game.state.players[p_idx].resources[r_idx]
                    
                    if gained:
                        print(f"  P{p_idx} gains: {', '.join(gained)}")
                
            elif action.action_type == ActionType.BUILD_ROAD:
                buildings_built[current]["roads"] += 1
                print(f"  P{current} builds road")
                
            elif action.action_type == ActionType.BUILD_SETTLEMENT:
                buildings_built[current]["settlements"] += 1  
                print(f"  P{current} builds settlement")
                
            elif action.action_type == ActionType.BUILD_CITY:
                buildings_built[current]["cities"] += 1
                print(f"  P{current} upgrades to city")
                
            elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
                buildings_built[current]["dev_cards"] += 1
                print(f"  P{current} buys development card")
                
            elif action.action_type == ActionType.END_TURN:
                turn_count += 1
            
            game.execute(action)
        
        # Summary after 10 turns
        print(f"\nAfter 10 turns:")
        print(f"  P0 ({players[0].name}): {sum(resources_gained[0])} total resources")
        print(f"    Built: {buildings_built[0]['roads']} roads, {buildings_built[0]['settlements']} settlements, " +
              f"{buildings_built[0]['cities']} cities, {buildings_built[0]['dev_cards']} dev cards")
        print(f"  P1 ({players[1].name}): {sum(resources_gained[1])} total resources") 
        print(f"    Built: {buildings_built[1]['roads']} roads, {buildings_built[1]['settlements']} settlements, " +
              f"{buildings_built[1]['cities']} cities, {buildings_built[1]['dev_cards']} dev cards")
        print(f"  VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")

if __name__ == "__main__":
    analyze_early_game(3)