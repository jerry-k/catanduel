#!/usr/bin/env python3
"""Compare initial settlement placements between Minimax and SmartMinimax."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.minimax_player import MinimaxPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer
from engine.colonist_map import HEX_TO_CORNERS

def analyze_placement(game, player_id, player_name):
    """Analyze a player's settlement placement."""
    buildings = [(c, t) for c, (p, t) in game.state.board.buildings.items() if p == player_id]
    
    print(f"\n{player_name} (Player {player_id}):")
    
    total_production = 0
    resources = set()
    has_brick = False
    has_wood = False
    
    for corner, _ in buildings:
        print(f"  Settlement at corner {corner}:")
        for hex_id, corners in HEX_TO_CORNERS.items():
            if corner in corners:
                hex_type = game.state.hex_types[hex_id]
                number = game.state.hex_numbers[hex_id]
                if hex_type > 0:  # Not desert
                    resource_names = ['desert', 'wood', 'brick', 'sheep', 'wheat', 'ore']
                    resource = resource_names[hex_type]
                    resources.add(resource)
                    
                    if hex_type == 1:  # Wood
                        has_wood = True
                    elif hex_type == 2:  # Brick
                        has_brick = True
                    
                    # Production value
                    prob_map = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
                    production = prob_map.get(number, 0)
                    total_production += production
                    
                    print(f"    - {resource} on {number} (prod: {production})")
    
    print(f"  Resources: {sorted(resources)}")
    print(f"  Total production: {total_production}")
    print(f"  Has brick: {'YES' if has_brick else 'NO'}")
    print(f"  Has wood: {'YES' if has_wood else 'NO'}")

def compare_placements(num_games=10):
    """Compare initial placements over multiple games."""
    
    mm_stats = {"production": [], "resources": [], "brick": 0, "wood": 0}
    smm_stats = {"production": [], "resources": [], "brick": 0, "wood": 0}
    
    for i in range(num_games):
        print(f"\n{'='*60}")
        print(f"GAME {i+1}")
        print('='*60)
        
        # Regular Minimax
        p1 = MinimaxPlayer(0, "Minimax-0")
        p2 = MinimaxPlayer(1, "Minimax-1")
        game1 = Game([p1, p2])
        
        # Play through setup
        while game1.state.is_setup_phase():
            actions = game1.get_valid_actions()
            current = game1.state.setup_phase_player_order()
            action = game1.players[current].decide(game1, actions)
            game1.execute(action)
        
        print("\nRegular Minimax placement:")
        analyze_placement(game1, 0, "Minimax")
        
        # Smart Minimax (same board)
        p3 = SmartMinimaxPlayer(0, "SmartMinimax-0")
        p4 = SmartMinimaxPlayer(1, "SmartMinimax-1")
        # Use same board configuration
        game2 = Game([p3, p4])
        game2.state.hex_types = game1.state.hex_types.copy()
        game2.state.hex_numbers = game1.state.hex_numbers.copy()
        game2.state.port_edges = game1.state.port_edges.copy()
        
        # Play through setup
        while game2.state.is_setup_phase():
            actions = game2.get_valid_actions()
            current = game2.state.setup_phase_player_order()
            action = game2.players[current].decide(game2, actions)
            game2.execute(action)
        
        print("\nSmart Minimax placement (same board):")
        analyze_placement(game2, 0, "SmartMinimax")
        
        # Collect stats
        # For simplicity, just look at player 0
        for corner, _ in [(c, t) for c, (p, t) in game1.state.board.buildings.items() if p == 0]:
            prod = 0
            res = set()
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners and game1.state.hex_types[hex_id] > 0:
                    prob_map = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
                    prod += prob_map.get(game1.state.hex_numbers[hex_id], 0)
                    res.add(game1.state.hex_types[hex_id])
            
            if 1 in res:  # Wood
                mm_stats["wood"] += 1
            if 2 in res:  # Brick
                mm_stats["brick"] += 1
            mm_stats["production"].append(prod)
            mm_stats["resources"].append(len(res))
        
        for corner, _ in [(c, t) for c, (p, t) in game2.state.board.buildings.items() if p == 0]:
            prod = 0
            res = set()
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners and game2.state.hex_types[hex_id] > 0:
                    prob_map = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
                    prod += prob_map.get(game2.state.hex_numbers[hex_id], 0)
                    res.add(game2.state.hex_types[hex_id])
            
            if 1 in res:  # Wood
                smm_stats["wood"] += 1
            if 2 in res:  # Brick
                smm_stats["brick"] += 1
            smm_stats["production"].append(prod)
            smm_stats["resources"].append(len(res))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY OVER ALL GAMES")
    print('='*60)
    
    print(f"\nRegular Minimax:")
    print(f"  Avg production per settlement: {sum(mm_stats['production'])/len(mm_stats['production']):.1f}")
    print(f"  Avg resources per settlement: {sum(mm_stats['resources'])/len(mm_stats['resources']):.1f}")
    print(f"  Has wood: {mm_stats['wood']}/{len(mm_stats['production'])} times")
    print(f"  Has brick: {mm_stats['brick']}/{len(mm_stats['production'])} times")
    
    print(f"\nSmart Minimax:")
    print(f"  Avg production per settlement: {sum(smm_stats['production'])/len(smm_stats['production']):.1f}")
    print(f"  Avg resources per settlement: {sum(smm_stats['resources'])/len(smm_stats['resources']):.1f}")
    print(f"  Has wood: {smm_stats['wood']}/{len(smm_stats['production'])} times")
    print(f"  Has brick: {smm_stats['brick']}/{len(smm_stats['production'])} times")

if __name__ == "__main__":
    compare_placements(5)