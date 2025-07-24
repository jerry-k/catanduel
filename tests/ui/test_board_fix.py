#!/usr/bin/env python3
"""
Test script to verify the board generation and resource mapping fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import HEX_TYPE_DESERT, ActionType

def test_board_generation():
    """Test that board generation creates exactly one desert tile."""
    print("Testing board generation...")
    
    # Test multiple seeds
    for seed in [None, 42, 123, 999]:
        player1 = RandomPlayer(0, "Human")
        player2 = RandomPlayer(1, "AI")
        game = Game([player1, player2], seed=seed)
        
        # Count desert tiles
        desert_count = sum(1 for hex_type in game.state.hex_types if hex_type == HEX_TYPE_DESERT)
        
        # Check that desert has no number
        desert_hexes = [i for i, hex_type in enumerate(game.state.hex_types) if hex_type == HEX_TYPE_DESERT]
        desert_numbers = [game.state.hex_numbers[i] for i in desert_hexes]
        
        print(f"\nSeed {seed}:")
        print(f"  Desert tiles: {desert_count} (should be 1)")
        print(f"  Desert hex IDs: {desert_hexes}")
        print(f"  Desert numbers: {desert_numbers} (should be [0])")
        print(f"  Robber position: {game.state.board.robber_hex}")
        
        # Verify
        assert desert_count == 1, f"Expected 1 desert, got {desert_count}"
        assert all(num == 0 for num in desert_numbers), f"Desert should have no number, got {desert_numbers}"
        assert game.state.board.robber_hex in desert_hexes, "Robber should be on desert"

def test_initial_actions():
    """Test that initial actions are available."""
    print("\n\nTesting initial actions...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Get initial actions
    actions = game.get_valid_actions()
    
    print(f"Initial state:")
    print(f"  Current player: {game.state.current_player}")
    print(f"  Is setup phase: {game.state.is_setup_phase()}")
    print(f"  Number of valid actions: {len(actions)}")
    
    if actions:
        print(f"  First few actions:")
        for action in actions[:5]:
            print(f"    - {action.action_type.name}: {action.value}")
    
    # Verify we have BUILD_INITIAL_SETTLEMENT actions
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT]
    print(f"\n  Settlement placement options: {len(settlement_actions)}")
    
    assert len(settlement_actions) > 0, "Should have settlement placement options"

def test_resource_mapping():
    """Test the resource type mapping in web_server."""
    print("\n\nTesting resource mapping...")
    
    # Import the serialize_state function
    from ui.web_server import serialize_state
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI") 
    game = Game([player1, player2])
    
    # Serialize the state
    state_data = serialize_state(game)
    
    # Check hexes
    print("Hex resources in serialized state:")
    desert_count = 0
    for hex_id, hex_data in state_data['hexes'].items():
        if hex_data['resource'] == 'desert':
            desert_count += 1
            print(f"  Hex {hex_id}: desert (number: {hex_data['number']})")
    
    print(f"\nTotal desert hexes in UI: {desert_count}")
    
    # Also check a few other resources
    resource_counts = {}
    for hex_id, hex_data in state_data['hexes'].items():
        resource = hex_data['resource']
        resource_counts[resource] = resource_counts.get(resource, 0) + 1
    
    print("\nResource distribution:")
    for resource, count in sorted(resource_counts.items()):
        print(f"  {resource}: {count}")

if __name__ == "__main__":
    test_board_generation()
    test_initial_actions()
    test_resource_mapping()
    print("\n✅ All tests passed!")