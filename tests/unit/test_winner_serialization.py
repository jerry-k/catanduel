#!/usr/bin/env python3
"""
Test that the winner serialization bug is fixed.

This test simulates a game reaching 10 VP and verifies that the winner
is properly serialized as a player ID (int) rather than a Player object.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import VICTORY_POINTS_TO_WIN
import json


def test_winner_serialization():
    """Test that winner is returned as player ID, not Player object."""
    print("Testing winner serialization...")
    
    # Create game
    player1 = RandomPlayer(0, "Player 1")
    player2 = RandomPlayer(1, "Player 2")
    game = Game([player1, player2])
    
    # Manually set a player to have enough VPs to win
    game.state.players[0].public_vps = VICTORY_POINTS_TO_WIN
    
    # Check game is over
    assert game.is_over(), "Game should be over when player has 10 VPs"
    
    # Get winner using game.get_winner() (returns Player object)
    winner_player = game.get_winner()
    assert winner_player is not None, "Should have a winner"
    assert winner_player == player1, "Player 1 should be the winner"
    
    # Get winner using state.get_winner() (returns player ID)
    winner_id = game.state.get_winner()
    assert winner_id == 0, "Winner ID should be 0"
    
    # Test JSON serialization
    try:
        # This would fail with the old code
        json.dumps({'winner': winner_player})
        print("ERROR: Player object should not be JSON serializable!")
        return False
    except TypeError as e:
        print(f"Expected error when serializing Player object: {e}")
    
    # This should work with the new code
    try:
        result = json.dumps({'winner': winner_id})
        print(f"Success: Winner ID serialized correctly: {result}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to serialize winner ID: {e}")
        return False


def test_web_server_endpoints():
    """Test that web server endpoints use correct winner format."""
    print("\nChecking web server endpoints...")
    
    # Read the web server file
    web_server_path = os.path.join(os.path.dirname(__file__), 'ui', 'web_server.py')
    with open(web_server_path, 'r') as f:
        content = f.read()
    
    # Check that we're using state.get_winner() not game.get_winner()
    if 'game.state.get_winner()' in content:
        print("✓ Web server correctly uses game.state.get_winner()")
    else:
        print("✗ Web server should use game.state.get_winner(), not game.get_winner()")
        return False
    
    # Make sure we're not using game.get_winner() anywhere in the response
    import re
    # Look for patterns where winner is assigned from game.get_winner()
    bad_pattern = re.compile(r'winner\s*=\s*game\.get_winner\(\)')
    if bad_pattern.search(content):
        print("✗ Found usage of game.get_winner() in web server")
        return False
    
    print("✓ No problematic usage of game.get_winner() found")
    return True


if __name__ == "__main__":
    print("Testing winner serialization bug fix...\n")
    
    # Test the core issue
    test1_passed = test_winner_serialization()
    
    # Test the web server implementation
    test2_passed = test_web_server_endpoints()
    
    print("\n" + "="*50)
    if test1_passed and test2_passed:
        print("✓ All tests passed! The bug is fixed.")
        print("\nThe issue was that game.get_winner() returns a Player object,")
        print("which is not JSON serializable. The fix is to use")
        print("game.state.get_winner() which returns the player ID (int).")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    print("="*50)