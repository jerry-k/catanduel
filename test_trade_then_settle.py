#!/usr/bin/env python3
"""Test the exact scenario: trade for brick then try to build settlement."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, ActionPrompt, SETTLEMENT, WOOD, BRICK, SHEEP, WHEAT, ORE
from engine.colonist_map import EDGE_TO_CORNERS
from engine.state_functions import maritime_trade

def test_trade_then_settle():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2], seed=42)
    
    # Setup the exact scenario
    game.state.initial_phase = False
    game.state.turn_number = 10
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Place settlement at corner 23 and roads at edges 31, 35
    game.state.board.buildings[23] = (0, SETTLEMENT)
    game.state.board.roads[31] = 0  # Connects 26-27
    game.state.board.roads[35] = 0  # Connects 23-26
    
    # Give player resources BEFORE trade (wood and sheep, no brick)
    game.state.players[0].resources = [3, 0, 1, 1, 0]  # 3 wood, 0 brick, 1 sheep, 1 wheat
    game.state.players[0].settlements_left = 3
    
    # Test with Road Building active
    print("\n=== Testing with Road Building active ===")
    game.state._free_roads = 2  # Simulate Road Building card being played
    
    # Place a wood port at a corner the player controls
    # First find which corners player has access to
    # Edge 35 connects 23-26, so player has settlement at 23
    # Let's say edge 24 is a wood port that includes corner 23
    game.state.port_edges[26] = 2  # PORT_TYPE_WOOD at edge connecting to corner 23
    
    print("=== Initial State ===")
    print(f"Settlement at corner 23")
    print(f"Roads at edges 31 (26-27) and 35 (23-26)")
    print(f"Resources before trade: wood={game.state.players[0].resources[WOOD]}, "
          f"brick={game.state.players[0].resources[BRICK]}, "
          f"sheep={game.state.players[0].resources[SHEEP]}, "
          f"wheat={game.state.players[0].resources[WHEAT]}")
    
    # Check settlement actions BEFORE trade
    actions = game.get_valid_actions()
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    print(f"\nSettlement actions before trade: {len(settlement_actions)}")
    print(f"Can afford settlement: {game.state.can_afford(0, [1,1,1,1,0])}")
    
    # Execute maritime trade: 2 wood for 1 brick
    print("\n=== Executing Trade: 2 wood for 1 brick ===")
    try:
        maritime_trade(game.state, 0, WOOD, 2, BRICK)
        print("Trade successful!")
    except Exception as e:
        print(f"Trade failed: {e}")
        return
    
    # Check resources AFTER trade
    print(f"\nResources after trade: wood={game.state.players[0].resources[WOOD]}, "
          f"brick={game.state.players[0].resources[BRICK]}, "
          f"sheep={game.state.players[0].resources[SHEEP]}, "
          f"wheat={game.state.players[0].resources[WHEAT]}")
    print(f"Can afford settlement: {game.state.can_afford(0, [1,1,1,1,0])}")
    
    # Force cache invalidation to be sure
    game.state.invalidate_actions_cache()
    
    # Check settlement actions AFTER trade
    actions = game.get_valid_actions()
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    print(f"\nSettlement actions after trade: {len(settlement_actions)}")
    
    if settlement_actions:
        print("Available settlement corners:", [a.value for a in settlement_actions])
        if 27 in [a.value for a in settlement_actions]:
            print("✓ SUCCESS: Corner 27 is available for settlement!")
        else:
            print("✗ FAIL: Corner 27 is NOT in the available corners")
    else:
        print("✗ FAIL: No settlement actions available!")
        
        # Debug why
        print("\n=== Debugging ===")
        print(f"Checking corner 27:")
        print(f"- Connected via road: Yes (edge 31)")
        print(f"- Distance from corner 23: 2 edges (valid)")
        print(f"- Has resources: {game.state.can_afford(0, [1,1,1,1,0])}")
        print(f"- Settlements left: {game.state.players[0].settlements_left}")
        
        # Manually check if corner 27 should be valid
        if game.state.board.can_build_settlement(0, 27):
            print("- can_build_settlement(0, 27): True")
            print("\n⚠️  BUG CONFIRMED: Corner 27 should be buildable but isn't in actions!")
        else:
            print("- can_build_settlement(0, 27): False")
            
        # Check what generate_build_actions thinks
        from engine.models.actions import generate_build_actions
        print("\n=== Checking generate_build_actions directly ===")
        build_actions = generate_build_actions(game.state)
        settlement_actions = [a for a in build_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
        print(f"Build actions generated {len(settlement_actions)} settlement actions")
        
        # Check the specific conditions in generate_build_actions
        player = game.state.current_player_state()
        free_roads = getattr(game.state, '_free_roads', 0)
        print(f"\nConditions in generate_build_actions:")
        print(f"- player.settlements_left: {player.settlements_left} (need > 0)")
        print(f"- free_roads: {free_roads} (need == 0)")
        print(f"- can_afford: {game.state.can_afford(0, [1,1,1,1,0])}")

if __name__ == "__main__":
    test_trade_then_settle()