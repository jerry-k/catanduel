#!/usr/bin/env python3
"""Test that maritime trades work correctly with ports."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
from engine.colonist_map import EDGE_TO_CORNERS
from engine.state_functions import maritime_trade

def test_3_1_port():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Find a 3:1 port
    port_3_1_corners = []
    for edge_id, port_type in game.state.port_edges.items():
        if port_type == 1:  # PORT_TYPE_3_1
            port_3_1_corners = list(EDGE_TO_CORNERS[edge_id])
            print(f"3:1 port at edge {edge_id}, corners {port_3_1_corners}")
            break
    
    # Setup game state
    game.state.initial_phase = False
    game.state.turn_number = 3
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Give player resources
    game.state.players[0].resources = [5, 5, 5, 5, 5]  # 5 of each
    
    # Place settlement on 3:1 port
    if port_3_1_corners:
        corner = port_3_1_corners[0]
        game.state.board.buildings[corner] = (0, 1)  # Player 0, settlement
        print(f"Placed settlement on corner {corner}")
        
        # Test 3:1 trade (ore for wheat)
        print("\nTesting 3:1 trade: 3 ore for 1 wheat")
        try:
            maritime_trade(game.state, 0, ORE, 3, WHEAT)
            print("✓ SUCCESS: 3:1 trade executed")
            print(f"Player resources after trade: {game.state.players[0].resources}")
        except Exception as e:
            print(f"✗ FAIL: {e}")

def test_2_1_port():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Find a sheep port
    sheep_port_corners = []
    for edge_id, port_type in game.state.port_edges.items():
        if port_type == 4:  # PORT_TYPE_SHEEP
            sheep_port_corners = list(EDGE_TO_CORNERS[edge_id])
            print(f"\nSheep 2:1 port at edge {edge_id}, corners {sheep_port_corners}")
            break
    
    # Setup game state
    game.state.initial_phase = False
    game.state.turn_number = 3
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Give player resources
    game.state.players[0].resources = [0, 0, 5, 0, 0]  # 5 sheep
    
    # Place settlement on sheep port
    if sheep_port_corners:
        corner = sheep_port_corners[0]
        game.state.board.buildings[corner] = (0, 1)  # Player 0, settlement
        print(f"Placed settlement on corner {corner}")
        
        # Test 2:1 trade (sheep for brick)
        print("\nTesting 2:1 trade: 2 sheep for 1 brick")
        try:
            maritime_trade(game.state, 0, SHEEP, 2, BRICK)
            print("✓ SUCCESS: 2:1 trade executed")
            print(f"Player resources after trade: {game.state.players[0].resources}")
        except Exception as e:
            print(f"✗ FAIL: {e}")

if __name__ == "__main__":
    print("=== Testing Maritime Trade Fix ===")
    test_3_1_port()
    test_2_1_port()
    print("\nAll tests completed!")