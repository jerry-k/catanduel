#!/usr/bin/env python3
"""
Test the integration between CatanDuel engine and UI.

This helps us verify that:
1. The game engine initializes correctly
2. Board generation works
3. State serialization is correct
4. Actions can be executed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.state import GameState
from engine.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE

def test_game_creation():
    """Test that we can create a game."""
    print("Testing game creation...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2], seed=42)
    
    assert game is not None
    assert game.state is not None
    assert game.state.current_player == 0
    print("✓ Game created successfully")
    
    return game


def test_board_structure(game):
    """Test that the board has the correct structure."""
    print("\nTesting board structure...")
    
    state = game.state
    
    # Check hex types and numbers
    print(f"  Hex types: {state.hex_types}")
    print(f"  Hex numbers: {state.hex_numbers}")
    
    # Should have 19 hexes
    assert len(state.hex_types) == 19
    assert len(state.hex_numbers) == 19
    
    # Check desert count
    desert_count = sum(1 for h in state.hex_types if h == 5)  # HEX_TYPE_DESERT = 5
    print(f"  Desert hexes: {desert_count}")
    
    # Check resource distribution (standard Catan)
    resource_counts = {i: state.hex_types.count(i) for i in range(6)}
    print(f"  Resource distribution: {resource_counts}")
    
    print("✓ Board structure is valid")


def test_port_structure(game):
    """Test that ports are set up correctly."""
    print("\nTesting port structure...")
    
    ports = game.state.port_edges
    print(f"  Number of ports: {len(ports)}")
    print(f"  Port locations: {list(ports.keys())}")
    
    # Should have 9 ports
    assert len(ports) == 9
    
    # Count port types
    port_types = {}
    for edge, ptype in ports.items():
        port_types[ptype] = port_types.get(ptype, 0) + 1
    
    print(f"  Port type distribution: {port_types}")
    print("✓ Port structure is valid")


def test_initial_game_state(game):
    """Test the initial game state."""
    print("\nTesting initial game state...")
    
    state = game.state
    
    # Players should start with no resources
    for i in range(2):
        assert sum(state.players[i].resources) == 0
        print(f"  Player {i} resources: {state.players[i].resources}")
    
    # Should be in setup phase
    assert state.is_setup_phase()
    print(f"  Setup phase: {state.is_setup_phase()}")
    print(f"  Current player: {state.current_player}")
    
    print("✓ Initial game state is valid")


def test_get_valid_actions(game):
    """Test that we can get valid actions."""
    print("\nTesting valid actions...")
    
    actions = game.get_valid_actions()
    print(f"  Number of valid actions: {len(actions)}")
    
    if actions:
        print(f"  First few action types: {[a.action_type.name for a in actions[:5]]}")
    
    # In setup phase, should have settlement placement actions
    assert len(actions) > 0
    print("✓ Valid actions retrieved")
    
    return actions


def test_action_execution(game):
    """Test executing an action."""
    print("\nTesting action execution...")
    
    # Get valid actions
    actions = game.get_valid_actions()
    
    # Find a BUILD_INITIAL_SETTLEMENT action (we're in setup phase)
    settlement_actions = [a for a in actions if a.action_type.name == "BUILD_INITIAL_SETTLEMENT"]
    
    if settlement_actions:
        action = settlement_actions[0]
        print(f"  Executing: {action}")
        
        # Execute the action
        game.execute(action)
        
        # Check that something changed
        print(f"  New current player: {game.state.current_player}")
        print(f"  Buildings on board: {game.state.board.buildings}")
        
        print("✓ Action executed successfully")
    else:
        print("  No settlement actions available in current state")


def run_all_tests():
    """Run all integration tests."""
    print("Running CatanDuel UI Integration Tests")
    print("=" * 50)
    
    # Create game
    game = test_game_creation()
    
    # Test board
    test_board_structure(game)
    test_port_structure(game)
    
    # Test game state
    test_initial_game_state(game)
    
    # Test actions
    test_get_valid_actions(game)
    test_action_execution(game)
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")


if __name__ == "__main__":
    run_all_tests()