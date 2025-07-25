#!/usr/bin/env python3
"""Test the CatanatronMinimaxPlayer implementation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.minimax_player import MinimaxPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer

def test_basic_game():
    """Test that CatanatronMinimaxPlayer can play a basic game."""
    print("Testing CatanatronMinimaxPlayer basic functionality...")
    
    p1 = CatanatronMinimaxPlayer(0, "CatanatronMM-0", max_depth=2, time_limit=5.0)
    p2 = MinimaxPlayer(1, "RegularMM-1")
    
    game = Game([p1, p2])
    
    turn = 0
    try:
        while not game.is_over() and turn < 50:
            actions = game.get_valid_actions()
            if not actions:
                print(f"No valid actions at turn {turn}")
                break
                
            current = game.state.current_player
            action = game.players[current].decide(game, actions)
            
            success = game.execute(action)
            if not success:
                print(f"Failed to execute action at turn {turn}")
                break
                
            if action.action_type.name == "END_TURN":
                turn += 1
                if turn % 10 == 0:
                    print(f"Turn {turn}: P0={game.state.players[0].public_vps} VP, P1={game.state.players[1].public_vps} VP")
        
        print(f"\nGame ended after {turn} turns")
        print(f"Final score: P0={game.state.players[0].public_vps} VP, P1={game.state.players[1].public_vps} VP")
        if game.is_over():
            print(f"Winner: Player {game.state.get_winner()}")
        
        return True
        
    except Exception as e:
        print(f"\nError at turn {turn}: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def compare_players():
    """Quick comparison between different minimax variants."""
    print("\n\nComparing minimax variants (5 games each)...")
    
    matchups = [
        ("Regular Minimax", MinimaxPlayer, MinimaxPlayer),
        ("Smart Minimax", SmartMinimaxPlayer, SmartMinimaxPlayer),
        ("Catanatron Minimax", CatanatronMinimaxPlayer, CatanatronMinimaxPlayer),
        ("Regular vs Catanatron", MinimaxPlayer, CatanatronMinimaxPlayer),
    ]
    
    for name, p1_class, p2_class in matchups:
        print(f"\n{name}:")
        wins = [0, 0]
        
        for i in range(5):
            p1 = p1_class(0, f"{p1_class.__name__}-0")
            p2 = p2_class(1, f"{p2_class.__name__}-1")
            
            # Reduce depth/time for faster testing
            if hasattr(p1, 'max_depth'):
                p1.max_depth = 2
                p1.time_limit = 2.0
            if hasattr(p2, 'max_depth'):
                p2.max_depth = 2
                p2.time_limit = 2.0
            
            game = Game([p1, p2])
            
            turn = 0
            while not game.is_over() and turn < 100:
                actions = game.get_valid_actions()
                if not actions:
                    break
                    
                current = game.state.current_player
                action = game.players[current].decide(game, actions)
                
                game.execute(action)
                
                if action.action_type.name == "END_TURN":
                    turn += 1
            
            if game.is_over():
                winner = game.state.get_winner()
                wins[winner] += 1
                print(f"  Game {i+1}: P{winner} wins in {turn} turns")
            else:
                print(f"  Game {i+1}: Draw after {turn} turns")
        
        print(f"  Results: P0 wins {wins[0]}, P1 wins {wins[1]}")

if __name__ == "__main__":
    # Test basic functionality
    if test_basic_game():
        print("\n✓ CatanatronMinimaxPlayer is working!")
        
        # Compare performance
        compare_players()
    else:
        print("\n✗ CatanatronMinimaxPlayer has issues")