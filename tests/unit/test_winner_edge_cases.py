#!/usr/bin/env python3
"""
Test edge cases for the winner serialization fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.state import GameState
import json


def test_no_winner_case():
    """Test that winner is None when game is not over."""
    print("Testing no winner case...")
    
    game = Game([RandomPlayer(0, "P1"), RandomPlayer(1, "P2")])
    
    # Game just started, no winner
    assert not game.is_over(), "New game should not be over"
    assert game.state.get_winner() is None, "Should have no winner"
    
    # Test JSON serialization
    result = json.dumps({'winner': game.state.get_winner()})
    assert result == '{"winner": null}', f"Expected null winner, got: {result}"
    print("✓ No winner case works correctly")
    return True


def test_player_1_wins():
    """Test that player 1 (AI) winning is handled correctly."""
    print("\nTesting player 1 (AI) wins...")
    
    game = Game([RandomPlayer(0, "Human"), RandomPlayer(1, "AI")])
    
    # Set AI to win
    game.state.players[1].public_vps = 10
    
    assert game.is_over(), "Game should be over"
    assert game.state.get_winner() == 1, "Player 1 should be winner"
    
    # Test JSON serialization
    result = json.dumps({'winner': game.state.get_winner()})
    assert result == '{"winner": 1}', f"Expected winner 1, got: {result}"
    print("✓ Player 1 winning works correctly")
    return True


def test_exact_10_vp():
    """Test winning with exactly 10 VP."""
    print("\nTesting exact 10 VP win...")
    
    game = Game([RandomPlayer(0, "P1"), RandomPlayer(1, "P2")])
    
    # Test different combinations that sum to 10
    test_cases = [
        (10, 0),  # All public VPs
        (8, 2),   # Mix of public and hidden
        (5, 5),   # Even split
        (9, 1),   # Mostly public
    ]
    
    for public_vps, hidden_vps in test_cases:
        game.state.players[0].public_vps = public_vps
        game.state.players[0].hidden_vps = hidden_vps
        
        assert game.state.players[0].actual_vps() == 10, f"Should have 10 total VPs"
        assert game.is_over(), f"Game should be over with {public_vps}+{hidden_vps} VPs"
        assert game.state.get_winner() == 0, "Player 0 should be winner"
        
        print(f"  ✓ {public_vps} public + {hidden_vps} hidden = 10 VP win")
    
    return True


def test_both_players_10_vp():
    """Test edge case where both players reach 10 VP (shouldn't happen in real game)."""
    print("\nTesting both players at 10 VP...")
    
    game = Game([RandomPlayer(0, "P1"), RandomPlayer(1, "P2")])
    
    # Set both to 10 VP
    game.state.players[0].public_vps = 10
    game.state.players[1].public_vps = 10
    
    assert game.is_over(), "Game should be over"
    
    # First player in check order wins
    winner = game.state.get_winner()
    assert winner == 0, f"Player 0 should win when both have 10 VP, got {winner}"
    
    print("✓ First player wins when both reach 10 VP")
    return True


def test_web_server_import():
    """Test that web_server can be imported without errors."""
    print("\nTesting web_server import...")
    
    try:
        from ui.web_server import serialize_state, games
        print("✓ web_server imports successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import web_server: {e}")
        return False


if __name__ == "__main__":
    print("Testing winner serialization edge cases...\n")
    
    tests = [
        test_no_winner_case(),
        test_player_1_wins(),
        test_exact_10_vp(),
        test_both_players_10_vp(),
        test_web_server_import()
    ]
    
    print("\n" + "="*50)
    if all(tests):
        print("✓ All edge case tests passed!")
        print("\nSummary of the fix:")
        print("- Changed 'winner = game.get_winner()' to 'winner = game.state.get_winner()'")
        print("- This ensures winner is always a player ID (int) or None")
        print("- Player IDs are JSON serializable, Player objects are not")
        print("- The fix applies to both get_game_state and execute_action endpoints")
    else:
        print("✗ Some tests failed.")
    print("="*50)