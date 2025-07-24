#!/usr/bin/env python3
"""Test port functionality in CatanDuel."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import SHEEP, WOOD, BRICK, WHEAT, ORE
from engine.colonist_map import EDGE_TO_CORNERS

def test_ports():
    # Create a game with a fixed seed
    player1 = RandomPlayer(0, "Player 1")
    player2 = RandomPlayer(1, "Player 2")
    game = Game([player1, player2], seed=42)
    
    print("Port assignments in this game:")
    for edge_id, port_type in sorted(game.state.port_edges.items()):
        port_name = {1: "3:1", 2: "Wood 2:1", 3: "Brick 2:1", 4: "Sheep 2:1", 5: "Wheat 2:1", 6: "Ore 2:1"}
        corners = EDGE_TO_CORNERS[edge_id]
        print(f"  Edge {edge_id} (corners {corners}): {port_name.get(port_type, 'Unknown')}")
    
    # Test: Place a settlement on a port corner and check trade ratios
    # Find a sheep port
    sheep_port_edge = None
    sheep_port_corners = []
    for edge_id, port_type in game.state.port_edges.items():
        if port_type == 4:  # PORT_TYPE_SHEEP
            sheep_port_edge = edge_id
            sheep_port_corners = list(EDGE_TO_CORNERS[edge_id])
            break
    
    if sheep_port_edge:
        print(f"\nSheep port found at edge {sheep_port_edge}, corners {sheep_port_corners}")
        
        # Manually place a settlement on one of the sheep port corners
        corner = sheep_port_corners[0]
        game.state.board.buildings[corner] = (0, 1)  # Player 0, settlement
        
        # Check trade ratios
        from engine.models.actions import get_trade_ratios
        ratios = get_trade_ratios(game.state, 0)
        
        print(f"\nPlayer 0 trade ratios after settling on corner {corner}:")
        resources = ["Wood", "Brick", "Sheep", "Wheat", "Ore"]
        for i, resource_ratios in enumerate(ratios):
            print(f"  {resources[i]}: {resource_ratios}")
        
        # Verify sheep has 2:1 ratio
        if 2 in ratios[SHEEP]:
            print("\n✓ SUCCESS: Player can trade sheep at 2:1 ratio!")
        else:
            print("\n✗ FAIL: Player cannot trade sheep at 2:1 ratio")
    else:
        print("\nNo sheep port found in this game (ports were randomized)")

if __name__ == "__main__":
    test_ports()