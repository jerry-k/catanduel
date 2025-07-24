#!/usr/bin/env python3
"""Test settlement building requirements after initial phase."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, ActionPrompt, SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS, get_adjacent_corners

def test_settlement_requirements():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Skip initial phase
    game.state.initial_phase = False
    game.state.turn_number = 5
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Give player resources for settlement
    game.state.players[0].resources = [1, 1, 1, 1, 0]  # Settlement cost
    game.state.players[0].settlements_left = 3  # Has settlements available
    
    # Place initial settlements for both players (to create distance constraints)
    game.state.board.buildings[10] = (0, SETTLEMENT)  # Player 0
    game.state.board.buildings[20] = (1, SETTLEMENT)  # Player 1
    
    print("Initial setup:")
    print(f"Player 0 has settlement at corner 10")
    print(f"Player 1 has settlement at corner 20")
    print(f"Player 0 resources: {game.state.players[0].resources}")
    print(f"Player 0 settlements left: {game.state.players[0].settlements_left}")
    
    # Test 1: No roads = no valid settlement locations
    print("\n=== Test 1: No roads ===")
    actions = game.get_valid_actions()
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    print(f"Valid settlement locations: {len(settlement_actions)}")
    print("Expected: 0 (no roads to connect to)")
    
    # Test 2: Add a road but no valid corners due to distance rule
    print("\n=== Test 2: Road exists but adjacent corners violate distance rule ===")
    # Find edges connected to corner 10
    connected_edges = []
    for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
        if c1 == 10 or c2 == 10:
            connected_edges.append(edge_id)
    
    if connected_edges:
        # Place a road
        edge = connected_edges[0]
        game.state.board.roads[edge] = 0
        c1, c2 = EDGE_TO_CORNERS[edge]
        other_corner = c1 if c1 != 10 else c2
        print(f"Added road at edge {edge} connecting corners {c1} and {c2}")
        print(f"Corner {other_corner} is connected by road but adjacent to settlement at 10")
        
        actions = game.get_valid_actions()
        settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
        print(f"Valid settlement locations: {len(settlement_actions)}")
        print("Expected: 0 (adjacent corner violates distance rule)")
    
    # Test 3: Build roads away from settlements to find valid location  
    print("\n=== Test 3: Building roads to reach valid settlement spot ===")
    # Clear previous roads
    game.state.board.roads.clear()
    
    # Build a road network starting from corner 10
    # Edge 11 connects corners 7 and 10
    game.state.board.roads[11] = 0
    print(f"Built road at edge 11 (connects corners 7 and 10)")
    
    # Edge 7 connects corners 6 and 7  
    game.state.board.roads[7] = 0
    print(f"Built road at edge 7 (connects corners 6 and 7)")
    
    # Now corner 6 should be valid if not adjacent to any settlements
    adjacent_to_6 = get_adjacent_corners(6)
    print(f"Corner 6 adjacent corners: {adjacent_to_6}")
    occupied_adjacent = [c for c in adjacent_to_6 if c in game.state.board.buildings]
    print(f"Occupied adjacent corners: {occupied_adjacent}")
    
    actions = game.get_valid_actions()
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    valid_corners = [a.value for a in settlement_actions]
    
    print(f"\nAfter building road network:")
    print(f"Valid settlement locations: {len(settlement_actions)}")
    print(f"Valid corners: {valid_corners}")
    
    # Check why each corner is valid
    for corner in valid_corners[:3]:  # Show first 3
        print(f"\nCorner {corner} is valid because:")
        # Check road connection
        for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
            if edge_id in game.state.board.roads and game.state.board.roads[edge_id] == 0:
                if c1 == corner or c2 == corner:
                    print(f"  - Connected to player's road at edge {edge_id}")
                    break
        # Check distance rule
        adjacent = get_adjacent_corners(corner)
        print(f"  - Adjacent corners {adjacent} have no settlements")

if __name__ == "__main__":
    test_settlement_requirements()