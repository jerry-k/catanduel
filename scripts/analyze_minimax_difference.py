#!/usr/bin/env python3
"""Analyze why regular Minimax beats SmartMinimax despite worse initial placement."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.minimax_player import MinimaxPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer
from engine.models.enums import ActionType

def track_game_progress(p1_class, p2_class, game_name, max_turns=100):
    """Track key metrics throughout a game."""
    p1 = p1_class(0, f"{p1_class.__name__}-0")
    p2 = p2_class(1, f"{p2_class.__name__}-1")
    game = Game([p1, p2])
    
    print(f"\n=== {game_name} ===")
    
    # Track metrics
    buildings_built = [0, 0]
    dev_cards_bought = [0, 0]
    trades_made = [0, 0]
    
    turn = 0
    while not game.is_over() and turn < max_turns:
        actions = game.get_valid_actions()
        if not actions:
            break
            
        current = game.state.current_player
        action = game.players[current].decide(game, actions)
        
        # Track action types
        if action.action_type == ActionType.BUILD_SETTLEMENT:
            buildings_built[current] += 1
        elif action.action_type == ActionType.BUILD_CITY:
            buildings_built[current] += 2  # Cities worth more
        elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
            dev_cards_bought[current] += 1
        elif action.action_type == ActionType.MARITIME_TRADE:
            trades_made[current] += 1
        
        game.execute(action)
        
        if action.action_type == ActionType.END_TURN:
            turn += 1
            
        # Report progress at key points
        if turn in [25, 50, 75, 100]:
            print(f"\nTurn {turn}:")
            print(f"  VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")
            print(f"  Buildings: P0={buildings_built[0]}, P1={buildings_built[1]}")
            print(f"  Dev cards: P0={dev_cards_bought[0]}, P1={dev_cards_bought[1]}")
    
    print(f"\nFinal (Turn {turn}):")
    print(f"  VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")
    print(f"  Buildings built: P0={buildings_built[0]}, P1={buildings_built[1]}")
    print(f"  Dev cards bought: P0={dev_cards_bought[0]}, P1={dev_cards_bought[1]}")
    print(f"  Trades made: P0={trades_made[0]}, P1={trades_made[1]}")
    
    if game.is_over():
        print(f"  Winner: Player {game.state.get_winner()}")
    
    return game.state.get_winner() if game.is_over() else -1

def main():
    """Compare game progression between different player types."""
    
    print("Comparing game progression to understand why Minimax beats SmartMinimax...\n")
    
    # Run several games to see patterns
    wins = {"mm_vs_mm": [0, 0], "smm_vs_smm": [0, 0], "mm_vs_smm": [0, 0]}
    
    for i in range(3):
        print(f"\n{'='*60}")
        print(f"GAME SET {i+1}")
        print('='*60)
        
        # Regular Minimax vs Regular Minimax
        winner = track_game_progress(MinimaxPlayer, MinimaxPlayer, "Minimax vs Minimax")
        if winner >= 0:
            wins["mm_vs_mm"][winner] += 1
        
        # Smart Minimax vs Smart Minimax
        winner = track_game_progress(SmartMinimaxPlayer, SmartMinimaxPlayer, "SmartMinimax vs SmartMinimax")
        if winner >= 0:
            wins["smm_vs_smm"][winner] += 1
        
        # Regular Minimax vs Smart Minimax
        winner = track_game_progress(MinimaxPlayer, SmartMinimaxPlayer, "Minimax(P0) vs SmartMinimax(P1)")
        if winner >= 0:
            wins["mm_vs_smm"][winner] += 1
    
    print(f"\n{'='*60}")
    print("ANALYSIS")
    print('='*60)
    
    print("\nThe issue might be:")
    print("1. SmartMinimax inherits from both MinimaxPlayer and SmartGreedyPlayer")
    print("2. This could cause method resolution order (MRO) issues")
    print("3. The minimax evaluation function might not align with the greedy initial placement")
    print("4. Regular Minimax uses consistent evaluation throughout the game")
    
    # Check MRO
    print("\nMethod Resolution Order:")
    print(f"MinimaxPlayer MRO: {[c.__name__ for c in MinimaxPlayer.__mro__]}")
    print(f"SmartMinimaxPlayer MRO: {[c.__name__ for c in SmartMinimaxPlayer.__mro__]}")

if __name__ == "__main__":
    main()