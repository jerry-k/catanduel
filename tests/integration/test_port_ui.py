#!/usr/bin/env python3
"""Test port functionality through the web server interface."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, SHEEP, WOOD, BRICK, WHEAT, ORE
from engine.colonist_map import EDGE_TO_CORNERS
from ui.web_server import serialize_state

def test_port_ui():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    print("=== Port assignments in this game ===")
    port_names = {1: "3:1", 2: "Wood 2:1", 3: "Brick 2:1", 4: "Sheep 2:1", 5: "Wheat 2:1", 6: "Ore 2:1"}
    for edge_id, port_type in sorted(game.state.port_edges.items()):
        corners = EDGE_TO_CORNERS[edge_id]
        print(f"Edge {edge_id} (corners {corners}): {port_names.get(port_type, 'Unknown')}")
    
    # Find a sheep port
    sheep_port_corners = []
    for edge_id, port_type in game.state.port_edges.items():
        if port_type == 4:  # PORT_TYPE_SHEEP
            sheep_port_corners = list(EDGE_TO_CORNERS[edge_id])
            print(f"\nSheep port at edge {edge_id}, corners {sheep_port_corners}")
            break
    
    # Skip initial settlement phase by setting up the board
    from engine.models.enums import ActionPrompt
    game.state.initial_phase = False
    game.state.initial_roads_placed = 2
    game.state.initial_settlements_placed = 2
    game.state.turn_number = 3
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Give player resources
    game.state.players[0].resources = [5, 5, 10, 5, 5]  # Lots of sheep
    
    # Place settlement on sheep port
    if sheep_port_corners:
        corner = sheep_port_corners[0]
        game.state.board.buildings[corner] = (0, 1)  # Player 0, settlement
        print(f"Placed settlement on corner {corner}")
    
    # Debug: Check resource bank
    print(f"\nResource bank: {game.state.resource_bank}")
    print(f"Player resources: {game.state.players[0].resources}")
    
    # Get trade ratios
    from engine.models.actions import get_trade_ratios
    ratios = get_trade_ratios(game.state, 0)
    resource_names = ["Wood", "Brick", "Sheep", "Wheat", "Ore"]
    print(f"\nTrade ratios for player 0:")
    for i, res_ratios in enumerate(ratios):
        print(f"  {resource_names[i]}: {res_ratios}")
    
    # Debug trade generation
    from engine.models.actions import generate_trade_actions
    print(f"\nDebug: Generating trade actions manually...")
    print(f"Current player: {game.state.current_player}")
    print(f"Dice rolled: {game.state.dice_rolled}")
    trade_actions = generate_trade_actions(game.state)
    print(f"Trade actions generated: {len(trade_actions)}")
    
    # Get maritime trade actions
    actions = game.get_valid_actions()
    print(f"\nAll valid actions: {[a.action_type.name for a in actions]}")
    maritime_actions = [a for a in actions if a.action_type == ActionType.MARITIME_TRADE]
    
    print(f"\n=== Maritime trade actions available ({len(maritime_actions)} total) ===")
    resource_names = ["Wood", "Brick", "Sheep", "Wheat", "Ore"]
    for action in maritime_actions:
        give_res, give_count, get_res = action.value
        print(f"  Trade {give_count} {resource_names[give_res]} for 1 {resource_names[get_res]}")
    
    # Check what the UI would see
    ui_state = serialize_state(game)
    print(f"\n=== UI State ===")
    print(f"Ports in UI format: {ui_state['ports']}")
    
    # Count sheep trades
    sheep_trades = [a for a in maritime_actions if a.value[0] == SHEEP]
    sheep_2_1_trades = [a for a in sheep_trades if a.value[1] == 2]
    sheep_4_1_trades = [a for a in sheep_trades if a.value[1] == 4]
    
    print(f"\n=== Sheep trading analysis ===")
    print(f"Total sheep trades: {len(sheep_trades)}")
    print(f"2:1 sheep trades: {len(sheep_2_1_trades)}")
    print(f"4:1 sheep trades: {len(sheep_4_1_trades)}")
    
    if sheep_2_1_trades:
        print("✓ SUCCESS: 2:1 sheep trades are available!")
    else:
        print("✗ FAIL: No 2:1 sheep trades available")

if __name__ == "__main__":
    test_port_ui()