#!/usr/bin/env python3
"""Debug why settlements aren't showing as valid actions."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, ActionPrompt, SETTLEMENT, CITY
from engine.colonist_map import EDGE_TO_CORNERS, get_adjacent_corners, get_connected_edges
from engine.models.actions import generate_build_actions

def debug_settlement_actions():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2], seed=123)
    
    # Skip initial phase
    game.state.initial_phase = False
    game.state.turn_number = 5
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Give player resources for settlement
    game.state.players[0].resources = [1, 1, 1, 1, 0]  # Settlement cost
    game.state.players[0].settlements_left = 3
    
    # Simulate a realistic game state
    # Player 0 (red) has settlements and roads in bottom right
    # Let's say settlement at corner 40 with roads extending from it
    game.state.board.buildings[40] = (0, SETTLEMENT)
    game.state.board.roads[48] = 0  # Road from corner 40 to 37
    game.state.board.roads[49] = 0  # Road from corner 40 to 41
    
    print("\n=== SCENARIO 1: Roads only 1 edge away ===")
    print("Settlement at corner 40")
    print("Roads to corners 37 and 41 (adjacent to settlement)")
    
    # Player 1 (blue) has some settlements elsewhere
    game.state.board.buildings[10] = (1, SETTLEMENT)
    game.state.board.buildings[25] = (1, SETTLEMENT)
    
    print("=== Game State ===")
    print(f"Player 0 resources: {game.state.players[0].resources} (need [1,1,1,1,0] for settlement)")
    print(f"Player 0 settlements left: {game.state.players[0].settlements_left}")
    print(f"Can afford settlement: {game.state.can_afford(0, [1,1,1,1,0])}")
    
    print("\n=== Buildings on board ===")
    for corner, (player, building_type) in game.state.board.buildings.items():
        building_name = "Settlement" if building_type == SETTLEMENT else "City"
        print(f"Corner {corner}: Player {player} {building_name}")
    
    print("\n=== Roads on board ===")
    for edge, player in game.state.board.roads.items():
        corners = EDGE_TO_CORNERS[edge]
        print(f"Edge {edge} (connects corners {corners}): Player {player}")
    
    # Check each corner to see why it's not valid for settlement
    print("\n=== Checking all corners for settlement validity ===")
    valid_corners = []
    
    for corner_id in range(54):
        # Skip if already occupied
        if corner_id in game.state.board.buildings:
            continue
            
        # Check if connected to player's road
        connected_to_road = False
        for edge_id in get_connected_edges(corner_id):
            if edge_id in game.state.board.roads and game.state.board.roads[edge_id] == 0:
                connected_to_road = True
                break
        
        if not connected_to_road:
            continue
            
        # Check distance rule
        adjacent_corners = get_adjacent_corners(corner_id)
        violates_distance = False
        for adj in adjacent_corners:
            if adj in game.state.board.buildings:
                violates_distance = True
                break
        
        if not violates_distance:
            valid_corners.append(corner_id)
            print(f"✓ Corner {corner_id} is VALID for settlement")
            print(f"  - Connected to road at edge(s): {[e for e in get_connected_edges(corner_id) if e in game.state.board.roads and game.state.board.roads[e] == 0]}")
            print(f"  - Adjacent corners {adjacent_corners} are clear")
        else:
            print(f"✗ Corner {corner_id} connected to road but violates distance rule")
            print(f"  - Adjacent corners: {adjacent_corners}")
            print(f"  - Occupied adjacent: {[a for a in adjacent_corners if a in game.state.board.buildings]}")
    
    print(f"\n=== Summary ===")
    print(f"Total valid corners for settlement: {len(valid_corners)}")
    
    # Now check what the action generator says
    actions = generate_build_actions(game.state)
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    print(f"Settlement actions generated: {len(settlement_actions)}")
    
    if len(valid_corners) != len(settlement_actions):
        print("\n⚠️  MISMATCH between expected and generated actions!")
        generated_corners = [a.value for a in settlement_actions]
        print(f"Expected corners: {valid_corners}")
        print(f"Generated corners: {generated_corners}")
    
    # Now show what happens when we extend roads
    print("\n\n=== SCENARIO 2: Extending roads 2 edges away ===")
    
    # Add more roads to get 2 edges away
    # From corner 37, we can build to corner 30 or 34
    game.state.board.roads[44] = 0  # Edge 44 connects corners 30 and 37
    print("Added road from corner 37 to corner 30")
    
    # Now check if corner 30 is valid
    print("\nChecking corner 30:")
    print(f"- Adjacent corners: {get_adjacent_corners(30)}")
    print(f"- Connected to road: Yes (via edge 44)")
    
    # Check for occupied adjacent
    occupied_adj = [c for c in get_adjacent_corners(30) if c in game.state.board.buildings]
    if occupied_adj:
        print(f"- Has occupied adjacent corners: {occupied_adj}")
    else:
        print("- No adjacent settlements! ✓")
    
    # Re-run the action generation
    actions = generate_build_actions(game.state)
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    print(f"\nSettlement actions after extending roads: {len(settlement_actions)}")
    if settlement_actions:
        print(f"Can now build at corners: {[a.value for a in settlement_actions]}")

if __name__ == "__main__":
    debug_settlement_actions()