#!/usr/bin/env python3
"""Test the complete port flow from edge to corner to trade."""

from engine.colonist_map import EDGE_TO_CORNERS
from engine.models.enums import (
    PORT_TYPE_3_1, PORT_TYPE_WOOD, PORT_TYPE_BRICK,
    PORT_TYPE_SHEEP, PORT_TYPE_WHEAT, PORT_TYPE_ORE,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    ActionType, ActionPrompt
)
from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.actions import get_trade_ratios, generate_actions

def resource_name(res_id):
    """Get resource name from ID."""
    return ['wood', 'brick', 'sheep', 'wheat', 'ore'][res_id]

def port_type_to_string(port_type):
    """Convert port type to string."""
    return {
        PORT_TYPE_3_1: "3:1 (Generic)",
        PORT_TYPE_WOOD: "2:1 Wood",
        PORT_TYPE_BRICK: "2:1 Brick",
        PORT_TYPE_SHEEP: "2:1 Sheep",
        PORT_TYPE_WHEAT: "2:1 Wheat",
        PORT_TYPE_ORE: "2:1 Ore"
    }.get(port_type, f"Unknown ({port_type})")

def main():
    print("=== Testing Complete Port Flow ===\n")
    
    # Create a game with a specific seed
    players = [RandomPlayer(0, "P0"), RandomPlayer(1, "P1")]
    game = Game(players, seed=100)  # Different seed for variety
    
    # Find which edge has the sheep port after shuffling
    sheep_port_edge = None
    for edge_id, port_type in game.state.port_edges.items():
        if port_type == PORT_TYPE_SHEEP:
            sheep_port_edge = edge_id
            break
    
    if sheep_port_edge is None:
        print("ERROR: No sheep port found after board generation!")
        return
    
    corner1, corner2 = EDGE_TO_CORNERS[sheep_port_edge]
    print(f"1. After board generation, sheep port is on edge {sheep_port_edge}")
    print(f"   This edge connects corners {corner1} and {corner2}")
    
    # Place a settlement on one of the sheep port corners
    test_corner = corner1
    game.state.board.place_initial_settlement(0, test_corner)
    print(f"\n2. Placed Player 0 settlement on corner {test_corner}")
    
    # Check trade ratios for Player 0
    ratios = get_trade_ratios(game.state, 0)
    print("\n3. Trade ratios for Player 0:")
    for res in range(5):
        res_name = resource_name(res)
        print(f"   {res_name}: {ratios[res]}")
    
    # Give Player 0 some sheep to test trading
    game.state.players[0].resources[SHEEP] = 10
    print("\n4. Gave Player 0 10 sheep")
    
    # Set the game to a state where trading is allowed
    game.state.initial_phase = False
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    game.state.dice_rolled = True
    
    # Generate all valid actions
    actions = generate_actions(game.state)
    
    # Filter for maritime trades involving sheep
    sheep_trades = [a for a in actions 
                   if a.action_type == ActionType.MARITIME_TRADE 
                   and a.value[0] == SHEEP]
    
    print(f"\n5. Maritime trade actions with sheep: {len(sheep_trades)}")
    for trade in sheep_trades:
        give_res, give_amount, get_res = trade.value
        print(f"   Trade {give_amount} sheep for 1 {resource_name(get_res)}")
    
    # Verify the sheep port is working
    expected_ratio = 2 if test_corner in [corner1, corner2] else 4
    actual_sheep_ratios = ratios[SHEEP]
    
    print(f"\n6. Verification:")
    print(f"   - Player has settlement on sheep port corner: {test_corner in [corner1, corner2]}")
    print(f"   - Expected sheep trade ratio: {expected_ratio}:1")
    print(f"   - Actual sheep trade ratios: {actual_sheep_ratios}")
    
    if 2 in actual_sheep_ratios:
        print("   ✓ SUCCESS: Player can trade sheep at 2:1 ratio!")
    else:
        print("   ✗ FAILURE: Player cannot trade sheep at 2:1 ratio!")
    
    # Show all ports in the game
    print("\n7. All ports in this game:")
    for edge_id, port_type in sorted(game.state.port_edges.items()):
        c1, c2 = EDGE_TO_CORNERS[edge_id]
        print(f"   Edge {edge_id} (corners {c1}, {c2}): {port_type_to_string(port_type)}")

if __name__ == "__main__":
    main()