#!/usr/bin/env python3
"""Debug road building opportunities."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import GreedyPlayer
from engine.models.enums import ActionType, WOOD, BRICK

def debug_roads():
    """Check road building opportunities."""
    p1 = GreedyPlayer(0, "Greedy-0")
    p2 = GreedyPlayer(1, "Greedy-1")
    game = Game([p1, p2])
    
    # Skip to after setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    print("=== INITIAL STATE ===")
    print(f"P0 resources: {game.state.players[0].resources}")
    print(f"P1 resources: {game.state.players[1].resources}")
    print()
    
    # Play turns and watch for road opportunities
    road_opportunities = []
    
    for turn in range(30):
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        
        # Check for road building actions
        road_actions = [a for a in actions if a.action_type == ActionType.BUILD_ROAD]
        if road_actions:
            player = game.state.players[current]
            can_afford = player.resources[WOOD] >= 1 and player.resources[BRICK] >= 1
            road_opportunities.append({
                'turn': turn,
                'player': current,
                'num_road_actions': len(road_actions),
                'can_afford': can_afford,
                'resources': list(player.resources)
            })
            
            print(f"Turn {turn}: Player {current} has {len(road_actions)} road options")
            print(f"  Resources: {player.resources}")
            print(f"  Can afford: {can_afford}")
            
            # What action did they choose?
            action = game.players[current].decide(game, actions)
            print(f"  Chose: {action.action_type.name}")
            
            if action.action_type == ActionType.BUILD_ROAD:
                print(f"  Built road at edge {action.value}")
            print()
        
        # Execute the action
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    print("\n=== SUMMARY ===")
    print(f"Road building opportunities: {len(road_opportunities)}")
    print(f"Final roads: {game.state.board.roads}")
    print(f"Final VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")

if __name__ == "__main__":
    debug_roads()