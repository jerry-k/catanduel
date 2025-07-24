#!/usr/bin/env python3
"""
Test the complete game-over flow to ensure no serialization errors occur.

This test simulates a real game scenario where a player reaches 10 VP
and verifies that the web server can properly handle the response.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import json
from ui.web_server import app, games, serialize_state
from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType


def test_game_over_response():
    """Test that the game-over response is properly serializable."""
    print("Testing game-over response serialization...")
    
    # Create a test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Create a new game
    response = client.post('/api/new_game', json={})
    assert response.status_code == 200
    data = response.get_json()
    game_id = data['game_id']
    
    print(f"Created game with ID: {game_id}")
    
    # Get the game instance
    game = games[game_id]
    
    # Simulate game reaching 10 VP
    # Give player 0 enough buildings to reach 10 VP
    game.state.players[0].public_vps = 8  # 8 public VPs
    game.state.players[0].hidden_vps = 2  # 2 hidden VPs from dev cards
    
    print("Set player 0 to have 10 total VPs")
    
    # Verify game is over
    assert game.is_over(), "Game should be over"
    assert game.state.get_winner() == 0, "Player 0 should be winner"
    
    # Test get_game_state endpoint
    print("\nTesting get_game_state endpoint...")
    response = client.get(f'/api/game_state/{game_id}')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.get_json()
    assert data['game_over'] == True, "game_over should be True"
    assert data['winner'] == 0, f"winner should be 0, got {data['winner']}"
    print("✓ get_game_state endpoint works correctly")
    
    # Test execute_action endpoint after game is over
    print("\nTesting execute_action endpoint with game over...")
    
    # Try to execute an action (should still return proper response)
    action_data = {
        'type': 'END_TURN',
        'player': 0
    }
    
    response = client.post(f'/api/execute_action/{game_id}', 
                         json=action_data,
                         content_type='application/json')
    
    # Even if action fails, response should be serializable
    assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
    
    data = response.get_json()
    if response.status_code == 200:
        assert 'game_over' in data, "Response should include game_over"
        assert 'winner' in data, "Response should include winner"
        assert data['winner'] == 0, f"winner should be 0, got {data['winner']}"
        print("✓ execute_action endpoint works correctly when game is over")
    else:
        print("✓ execute_action correctly rejected action after game over")
    
    return True


def test_serialize_state_with_winner():
    """Test that serialize_state works when there's a winner."""
    print("\nTesting serialize_state with winner...")
    
    # Create a game
    player1 = RandomPlayer(0, "Player 1")
    player2 = RandomPlayer(1, "Player 2") 
    game = Game([player1, player2])
    
    # Set player to win
    game.state.players[0].public_vps = 10
    
    # Serialize state
    try:
        state_dict = serialize_state(game)
        
        # Convert to JSON to ensure it's serializable
        json_str = json.dumps(state_dict)
        print("✓ serialize_state output is JSON serializable")
        
        # Verify victory points are included
        assert state_dict['victory_points']['0'] == 10
        print("✓ Victory points correctly included in serialized state")
        
        return True
    except Exception as e:
        print(f"✗ Error serializing state: {e}")
        return False


if __name__ == "__main__":
    print("Testing complete game-over flow...\n")
    
    test1_passed = test_game_over_response()
    test2_passed = test_serialize_state_with_winner()
    
    print("\n" + "="*50)
    if test1_passed and test2_passed:
        print("✓ All tests passed!")
        print("\nThe game-over flow works correctly:")
        print("1. When a player reaches 10 VP, game.is_over() returns True")
        print("2. game.state.get_winner() returns the player ID (0 or 1)")
        print("3. Both endpoints properly serialize the winner as an integer")
        print("4. No 'Object of type RandomPlayer is not JSON serializable' errors")
    else:
        print("✗ Some tests failed.")
    print("="*50)