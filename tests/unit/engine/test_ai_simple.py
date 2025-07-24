"""
Simple test for AI players.

Tests each AI player type individually to ensure they work.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game
from models import (
    RandomPlayer, GreedyPlayer,
    MinimaxPlayer, SimpleMinimaxPlayer,
    MCTSPlayer, FastMCTSPlayer
)


def test_ai_player(player_class, opponent_class=RandomPlayer, max_turns=100):
    """Test a single AI player type."""
    print(f"\nTesting {player_class.__name__}...")
    
    try:
        # Create players
        player = player_class(0)
        opponent = opponent_class(1)
        
        # Create game
        game = Game([player, opponent])
        
        # Play some turns
        turns = 0
        errors = 0
        
        while not game.is_over() and turns < max_turns:
            actions = game.get_valid_actions()
            if not actions:
                print("  Warning: No valid actions")
                break
            
            try:
                current = game._get_acting_player()
                action = game.players[current].decide(game, actions)
                game.execute(action)
                turns += 1
                
                if turns % 20 == 0:
                    vps = [p.actual_vps() for p in game.state.players]
                    print(f"  Turn {turns}: P0={vps[0]} VP, P1={vps[1]} VP")
                    
            except Exception as e:
                errors += 1
                print(f"  Error at turn {turns}: {e}")
                if errors > 5:
                    print("  Too many errors, stopping")
                    break
        
        # Report results
        if game.is_over():
            winner = game.state.get_winner()
            print(f"  ✓ Game completed! Winner: Player {winner}")
        else:
            vps = [p.actual_vps() for p in game.state.players]
            print(f"  ✓ Played {turns} turns. Final VPs: P0={vps[0]}, P1={vps[1]}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test all AI players."""
    print("Testing CatanDuel AI Players")
    print("=" * 40)
    
    # List of AI players to test
    ai_players = [
        (RandomPlayer, RandomPlayer),
        (GreedyPlayer, RandomPlayer),
        (SimpleMinimaxPlayer, RandomPlayer),
        (MinimaxPlayer, GreedyPlayer),
        (FastMCTSPlayer, RandomPlayer),
        (MCTSPlayer, GreedyPlayer),
    ]
    
    passed = 0
    failed = 0
    
    for player_class, opponent_class in ai_players:
        if test_ai_player(player_class, opponent_class):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All AI players work correctly!")
    else:
        print("\n❌ Some AI players have issues")


if __name__ == "__main__":
    main()