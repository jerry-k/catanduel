#!/usr/bin/env python3
"""Comprehensive debug of why settlements aren't appearing in actions."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, ActionPrompt, SETTLEMENT
from engine.models.actions import generate_actions, generate_build_actions
from engine.colonist_map import get_adjacent_corners

def debug_settlement_blocking():
    # Create a game
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Setup exact scenario
    game.state.initial_phase = False
    game.state.turn_number = 10
    game.state.dice_rolled = True
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Settlement at 23, roads at 31 and 35
    game.state.board.buildings[23] = (0, SETTLEMENT)
    game.state.board.roads[31] = 0
    game.state.board.roads[35] = 0
    
    # Resources after trade: 1 wood, 1 brick, 1 sheep, 1 wheat
    game.state.players[0].resources = [1, 1, 1, 1, 0]
    game.state.players[0].settlements_left = 3
    
    # Test with different settlements_left values
    print("\n=== Testing with different settlements_left values ===")
    for settlements_left in [0, 1, 2, 3, 4, 5]:
        game.state.players[0].settlements_left = settlements_left
        build_actions = generate_build_actions(game.state)
        settlement_actions = [a for a in build_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
        print(f"settlements_left={settlements_left}: {len(settlement_actions)} settlement actions")
    
    # Reset to 3
    game.state.players[0].settlements_left = 3
    
    # Add some opponent settlements to make it more realistic
    game.state.board.buildings[10] = (1, SETTLEMENT)
    game.state.board.buildings[40] = (1, SETTLEMENT)
    
    # Update player VPs
    game.state.players[0].public_vps = 1
    game.state.players[1].public_vps = 2
    
    print("=== Game State ===")
    print(f"Current player: {game.state.current_player}")
    print(f"Turn player: {game.state.current_turn_player}")
    print(f"Current prompt: {game.state.current_prompt}")
    print(f"Dice rolled: {game.state.dice_rolled}")
    print(f"Is setup phase: {game.state.is_setup_phase()}")
    print(f"Is discarding: {game.state.is_discarding}")
    print(f"Is moving robber: {game.state.is_moving_robber}")
    
    print("\n=== Player State ===")
    player = game.state.players[0]
    print(f"Resources: {player.resources}")
    print(f"Can afford settlement: {game.state.can_afford(0, [1,1,1,1,0])}")
    print(f"Settlements left: {player.settlements_left}")
    print(f"Has played dev card: {player.has_played_dev_card}")
    
    print("\n=== Special State Checks ===")
    free_roads = getattr(game.state, '_free_roads', 0)
    print(f"Free roads (_free_roads): {free_roads}")
    
    # Check for any other special attributes
    special_attrs = [attr for attr in dir(game.state) if attr.startswith('_') and not attr.startswith('__')]
    print(f"All special attributes: {special_attrs}")
    for attr in special_attrs:
        if attr != '_free_roads':
            print(f"  {attr}: {getattr(game.state, attr, 'N/A')}")
    
    print("\n=== Generate Actions Analysis ===")
    # Call generate_actions to see what it produces
    all_actions = generate_actions(game.state)
    print(f"Total actions from generate_actions: {len(all_actions)}")
    
    # Group by type
    action_types = {}
    for action in all_actions:
        action_type = action.action_type.name
        if action_type not in action_types:
            action_types[action_type] = 0
        action_types[action_type] += 1
    
    print("Actions by type:")
    for action_type, count in sorted(action_types.items()):
        print(f"  {action_type}: {count}")
    
    print("\n=== Build Actions Analysis ===")
    build_actions = generate_build_actions(game.state)
    print(f"Total build actions: {len(build_actions)}")
    
    settlement_actions = [a for a in build_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
    print(f"Settlement actions: {len(settlement_actions)}")
    
    if not settlement_actions:
        print("\nNo settlement actions generated. Checking why...")
        
        # Manually check the conditions from generate_build_actions
        print("\nChecking generate_build_actions conditions:")
        print(f"1. player.settlements_left > 0: {player.settlements_left > 0} ({player.settlements_left})")
        print(f"2. free_roads == 0: {free_roads == 0} ({free_roads})")
        print(f"3. can_afford(SETTLEMENT_COST): {game.state.can_afford(0, [1,1,1,1,0])}")
        
        if player.settlements_left > 0 and free_roads == 0 and game.state.can_afford(0, [1,1,1,1,0]):
            print("\nAll conditions met! Checking individual corners...")
            
            # Check each corner
            valid_corners = []
            for corner_id in range(54):
                if game.state.board.can_build_settlement(0, corner_id):
                    valid_corners.append(corner_id)
            
            print(f"Valid settlement corners: {valid_corners}")
            
            # Specifically check corner 27
            print(f"\nSpecific check for corner 27:")
            print(f"  can_build_settlement(0, 27): {game.state.board.can_build_settlement(0, 27)}")
            
            if 27 in valid_corners:
                print("\n🐛 BUG CONFIRMED: Corner 27 is valid but not in generated actions!")
    
    # Check the actual legal actions as the UI would see them
    print("\n=== Legal Actions (as UI sees them) ===")
    legal_actions = []
    acting_player = game.state.setup_phase_player_order() if game.state.is_setup_phase() else game.state.current_player
    
    for action in game.get_valid_actions():
        action_data = {
            'type': action.action_type.name,
            'player': acting_player
        }
        if action.value is not None:
            if action.action_type.name in ['BUILD_SETTLEMENT', 'BUILD_INITIAL_SETTLEMENT', 'BUILD_CITY']:
                action_data['corner'] = action.value
            elif action.action_type.name in ['BUILD_ROAD', 'BUILD_INITIAL_ROAD']:
                action_data['edge'] = action.value
            else:
                action_data['value'] = action.value
        legal_actions.append(action_data)
    
    print(f"Total legal actions: {len(legal_actions)}")
    settlement_ui_actions = [a for a in legal_actions if a['type'] == 'BUILD_SETTLEMENT']
    print(f"BUILD_SETTLEMENT actions: {len(settlement_ui_actions)}")

if __name__ == "__main__":
    debug_settlement_blocking()