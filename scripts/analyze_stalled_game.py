#!/usr/bin/env python3
"""Analyze a specific stalled game in detail."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.minimax_player import MinimaxPlayer
from engine.models.enums import ActionType

def analyze_stalled_game():
    """Run the exact game that was reported as stalled."""
    # Recreate the reported scenario
    p1 = RandomPlayer(0, "RandomPlayer-0")
    p2 = MinimaxPlayer(1, "MinimaxPlayer-1")
    game = Game([p1, p2])
    
    print("=== ANALYZING STALLED GAME: Random vs Minimax ===\n")
    
    # Track setup phase to see initial placement
    print("SETUP PHASE:")
    setup_moves = []
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        
        if action.action_type in [ActionType.BUILD_INITIAL_SETTLEMENT, ActionType.BUILD_INITIAL_ROAD]:
            setup_moves.append(f"P{current}: {action.action_type.name} at {action.value}")
            print(f"  {setup_moves[-1]}")
        
        game.execute(action)
    
    # Analyze board after setup
    print("\nBOARD ANALYSIS AFTER SETUP:")
    
    # Check what resources each player can get
    from engine.colonist_map import HEX_TO_CORNERS
    
    for player_id in [0, 1]:
        print(f"\nPlayer {player_id}:")
        buildings = [(c, t) for c, (p, t) in game.state.board.buildings.items() if p == player_id]
        
        resources_available = set()
        numbers_covered = []
        
        for corner, _ in buildings:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    hex_type = game.state.hex_types[hex_id]
                    number = game.state.hex_numbers[hex_id]
                    if hex_type > 0:  # Not desert
                        resource_name = ['desert', 'wood', 'brick', 'sheep', 'wheat', 'ore'][hex_type]
                        resources_available.add(resource_name)
                        numbers_covered.append((resource_name, number))
        
        print(f"  Resources available: {sorted(resources_available)}")
        print(f"  Numbers: {numbers_covered}")
        
        # Critical check: do they have brick?
        has_brick = 'brick' in resources_available
        print(f"  Has brick production: {'YES' if has_brick else 'NO ❌'}")
    
    # Simulate some turns
    print("\n\nSIMULATING FIRST 50 TURNS:")
    
    resource_totals = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    turn_count = 0
    
    for _ in range(100):  # 100 actions, not turns
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        
        # Track resource gains
        if any(a.action_type == ActionType.ROLL for a in actions):
            prev_resources = [list(game.state.players[0].resources), 
                            list(game.state.players[1].resources)]
            
        action = game.players[current].decide(game, actions)
        game.execute(action)
        
        if action.action_type == ActionType.ROLL:
            # Check what was gained
            for pid in [0, 1]:
                for i in range(5):
                    gained = game.state.players[pid].resources[i] - prev_resources[pid][i]
                    if gained > 0:
                        resource_totals[pid][i] += gained
        
        elif action.action_type == ActionType.END_TURN:
            turn_count += 1
            if turn_count >= 50:
                break
    
    # Final analysis
    print(f"\nAFTER {turn_count} TURNS:")
    resource_names = ['wood', 'brick', 'sheep', 'wheat', 'ore']
    
    for pid in [0, 1]:
        print(f"\nPlayer {pid}:")
        print(f"  Total resources gained: {dict(zip(resource_names, resource_totals[pid]))}")
        print(f"  Current resources: {dict(zip(resource_names, game.state.players[pid].resources))}")
        print(f"  Victory points: {game.state.players[pid].public_vps}")
        print(f"  Roads built: {len([e for e, p in game.state.board.roads.items() if p == pid])}")
        
        # Can they build?
        player = game.state.players[pid]
        can_build_road = player.resources[0] >= 1 and player.resources[1] >= 1  # wood & brick
        can_build_settlement = (player.resources[0] >= 1 and player.resources[1] >= 1 and 
                              player.resources[2] >= 1 and player.resources[3] >= 1)
        print(f"  Can afford road: {can_build_road}")
        print(f"  Can afford settlement: {can_build_settlement}")

if __name__ == "__main__":
    analyze_stalled_game()