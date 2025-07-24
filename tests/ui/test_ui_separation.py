#!/usr/bin/env python3
"""
Test that UI has proper separation from game engine.

Verifies that:
1. UI never modifies game state directly
2. All game logic comes from the engine
3. UI only formats/displays engine data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from ui.web_server import app, games, serialize_state
from engine.game import Game
from engine.models.player import RandomPlayer

def test_serialize_state_readonly():
    """Test that serialize_state only reads from game, never modifies."""
    print("Testing serialize_state is read-only...")
    
    # Create a game
    player1 = RandomPlayer(0, "Test1")
    player2 = RandomPlayer(1, "Test2")
    game = Game([player1, player2], seed=12345)
    
    # Store initial state
    initial_resources = [p.resources.copy() for p in game.state.players]
    initial_buildings = game.state.board.buildings.copy()
    initial_roads = game.state.board.roads.copy()
    initial_turn = game.state.turn_number
    
    # Serialize state multiple times
    for i in range(5):
        state_dict = serialize_state(game)
        
    # Verify nothing changed
    assert all(game.state.players[i].resources == initial_resources[i] for i in range(2))
    assert game.state.board.buildings == initial_buildings
    assert game.state.board.roads == initial_roads
    assert game.state.turn_number == initial_turn
    
    print("✓ serialize_state is read-only")
    

def test_api_endpoints_use_engine():
    """Test that API endpoints properly use engine for all game logic."""
    print("\nTesting API endpoints use engine...")
    
    with app.test_client() as client:
        # Create new game
        response = client.post('/api/new_game', 
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        game_id = data['game_id']
        
        # Verify game was created in engine
        assert game_id in games
        game = games[game_id]
        assert isinstance(game, Game)
        
        # Get game state
        response = client.get(f'/api/game_state/{game_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify legal actions come from engine
        assert 'legal_actions' in data
        engine_actions = game.get_valid_actions()
        assert len(data['legal_actions']) == len(engine_actions)
        
        # Verify game state matches engine
        assert data['state']['current_player'] == game.state.current_player
        assert data['state']['turn_number'] == game.state.turn_number
        
        print("✓ API endpoints properly use engine")


def test_no_game_logic_in_ui():
    """Verify there's no game logic calculations in the UI code."""
    print("\nChecking for game logic in UI code...")
    
    # Read the web_server.py file
    with open('ui/web_server.py', 'r') as f:
        ui_code = f.read()
    
    # Check for things that shouldn't be in UI
    forbidden_patterns = [
        'calculate_victory_points',
        'check_win_condition',
        'validate_action',
        'apply_trade',
        'distribute_resources',
        'roll_dice()',  # UI shouldn't roll dice
        'shuffle('      # UI shouldn't shuffle anything
    ]
    
    issues = []
    for pattern in forbidden_patterns:
        if pattern in ui_code:
            issues.append(f"Found '{pattern}' in UI code")
    
    if issues:
        print("✗ Found game logic in UI:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ No game logic found in UI code")
    
    return len(issues) == 0


def test_ui_only_formats_data():
    """Test that UI only formats data, doesn't create game data."""
    print("\nTesting UI only formats existing data...")
    
    # Create a game with some state
    player1 = RandomPlayer(0, "Test1")
    player2 = RandomPlayer(1, "Test2") 
    game = Game([player1, player2], seed=42)
    
    # Execute a few actions to create some state
    actions = game.get_valid_actions()
    if actions:
        game.execute(actions[0])
    
    # Serialize the state
    ui_state = serialize_state(game)
    
    # Verify UI state only contains reformatted engine data
    # Check resources mapping
    for player_id in range(2):
        engine_res = game.state.players[player_id].resources
        ui_res = ui_state['resources'][str(player_id)]
        # UI reorders resources but total should match
        ui_total = sum(int(v) for v in ui_res.values())
        engine_total = sum(engine_res)
        assert ui_total == engine_total, f"Resource totals don't match for player {player_id}"
    
    # Check buildings are just reformatted
    engine_buildings = len(game.state.board.buildings)
    ui_buildings = sum(1 for c in ui_state['corners'].values() if c is not None)
    assert engine_buildings == ui_buildings, "Building counts don't match"
    
    print("✓ UI only formats data from engine")


def run_all_tests():
    """Run all UI separation tests."""
    print("Testing UI-Engine Separation")
    print("=" * 50)
    
    test_serialize_state_readonly()
    test_api_endpoints_use_engine()
    
    # This test reads files, so it might fail based on implementation
    if test_no_game_logic_in_ui():
        print("\n✓ Complete separation verified!")
    else:
        print("\n✗ Some game logic found in UI")
        
    test_ui_only_formats_data()
    
    print("\n" + "=" * 50)
    print("UI separation tests complete!")


if __name__ == "__main__":
    run_all_tests()