#!/usr/bin/env python3
"""Test specific game that was failing."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer

def test_problematic_game():
    """Run the game that was failing."""
    print("Testing Random vs SmartMinimax for 200 turns...")
    
    p1 = RandomPlayer(0, "RandomPlayer-0")
    p2 = SmartMinimaxPlayer(1, "SmartMinimaxPlayer-1")
    game = Game([p1, p2])
    
    turn = 0
    error_count = 0
    
    try:
        while not game.is_over() and turn < 200:
            actions = game.get_valid_actions()
            if not actions:
                print(f"No valid actions at turn {turn}")
                break
                
            current = game.state.current_player
            
            # Extra logging around turn 52 where it failed
            if 50 <= turn <= 55:
                print(f"\nTurn {turn}, Player {current}:")
                print(f"  Resources: {game.state.players[current].resources}")
                print(f"  Valid actions: {len(actions)}")
                
            action = game.players[current].decide(game, actions)
            
            success = game.execute(action)
            if not success:
                error_count += 1
                print(f"Failed to execute {action} at turn {turn}")
                if error_count > 5:
                    print("Too many errors, stopping")
                    break
                    
            if action.action_type.name == "END_TURN":
                turn += 1
        
        print(f"\nGame completed successfully!")
        print(f"Final turn: {turn}")
        print(f"Game over: {game.is_over()}")
        if game.is_over():
            print(f"Winner: Player {game.state.get_winner()}")
        print(f"Final VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")
        
    except Exception as e:
        print(f"\nException at turn {turn}:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        print(f"  Current player: {current}")
        print(f"  Resources: {game.state.players[current].resources}")
        
        # Check specific resource requirements
        if "road" in str(e).lower():
            print(f"  Wood: {game.state.players[current].resources[0]}")
            print(f"  Brick: {game.state.players[current].resources[1]}")
            
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_problematic_game()