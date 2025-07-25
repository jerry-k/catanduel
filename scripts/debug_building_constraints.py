#!/usr/bin/env python3
"""Debug building constraints and why players can't build."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import GreedyPlayer
from engine.models.enums import ActionType, WOOD, BRICK, SHEEP, WHEAT, ORE
from engine.colonist_map import get_connected_edges, get_adjacent_corners

def analyze_building_constraints():
    """Analyze why players can't build settlements."""
    p1 = GreedyPlayer(0, "Greedy-0")
    p2 = GreedyPlayer(1, "Greedy-1")
    game = Game([p1, p2])
    
    # Skip to after setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    print("=== INITIAL BUILDINGS ===")
    print(f"Buildings: {game.state.board.buildings}")
    print(f"Roads: {game.state.board.roads}")
    print()
    
    # Play some turns to accumulate resources
    for turn in range(20):
        if game.is_over():
            break
            
        actions = game.get_valid_actions()
        current = game.state.current_player
        action = game.players[current].decide(game, actions)
        game.execute(action)
        
        # Check after some turns
        if turn == 10:
            print("=== AFTER 10 TURNS ===")
            print(f"P0 resources: {game.state.players[0].resources}")
            print(f"P1 resources: {game.state.players[1].resources}")
            print()
            
            # Check building materials
            for pid in [0, 1]:
                player = game.state.players[pid]
                has_settlement_resources = (
                    player.resources[WOOD] >= 1 and
                    player.resources[BRICK] >= 1 and
                    player.resources[SHEEP] >= 1 and
                    player.resources[WHEAT] >= 1
                )
                print(f"Player {pid} can afford settlement: {has_settlement_resources}")
            print()
    
    print("=== FINAL STATE ===")
    print(f"P0 resources: {game.state.players[0].resources}")
    print(f"P1 resources: {game.state.players[1].resources}")
    print(f"Roads: {game.state.board.roads}")
    print()
    
    # Analyze each player's building opportunities
    for player_id in [0, 1]:
        print(f"\n=== PLAYER {player_id} ANALYSIS ===")
        
        # Find all corners connected to their road network
        player_roads = [edge for edge, pid in game.state.board.roads.items() if pid == player_id]
        print(f"Player roads: {player_roads}")
        
        # Find all corners they could potentially build on
        connected_corners = set()
        for edge in player_roads:
            # Find corners connected to this edge
            for corner in range(54):
                if edge in get_connected_edges(corner):
                    connected_corners.add(corner)
        
        print(f"Corners connected to roads: {connected_corners}")
        
        # Check which are actually valid
        valid_corners = []
        blocked_corners = []
        for corner in connected_corners:
            # Check if occupied
            if corner in game.state.board.buildings:
                blocked_corners.append((corner, "occupied"))
                continue
                
            # Check distance rule
            adjacent = get_adjacent_corners(corner)
            has_adjacent_building = any(adj in game.state.board.buildings for adj in adjacent)
            if has_adjacent_building:
                blocked_corners.append((corner, "distance rule"))
                continue
                
            valid_corners.append(corner)
        
        print(f"Valid settlement spots: {valid_corners}")
        print(f"Blocked spots: {blocked_corners}")
        
        # Check resources
        player = game.state.players[player_id]
        print(f"Resources: wood={player.resources[WOOD]}, brick={player.resources[BRICK]}, "
              f"sheep={player.resources[SHEEP]}, wheat={player.resources[WHEAT]}, ore={player.resources[ORE]}")
        can_afford = (
            player.resources[WOOD] >= 1 and
            player.resources[BRICK] >= 1 and
            player.resources[SHEEP] >= 1 and
            player.resources[WHEAT] >= 1
        )
        print(f"Can afford settlement: {can_afford}")

if __name__ == "__main__":
    analyze_building_constraints()