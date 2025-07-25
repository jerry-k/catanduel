#!/usr/bin/env python3
"""Test improved bot games to see if they progress better."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer

def run_quick_game(p1_class, p2_class, max_turns=50):
    """Run a quick game and report progress."""
    p1 = p1_class(0, f"{p1_class.__name__}-0")
    p2 = p2_class(1, f"{p2_class.__name__}-1")
    game = Game([p1, p2])
    
    # Skip setup phase
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    # Check initial resources
    has_brick = [False, False]
    has_wood = [False, False]
    
    from engine.colonist_map import HEX_TO_CORNERS
    for player_id in [0, 1]:
        buildings = [(c, t) for c, (p, t) in game.state.board.buildings.items() if p == player_id]
        for corner, _ in buildings:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    hex_type = game.state.hex_types[hex_id]
                    if hex_type == 2:  # Brick
                        has_brick[player_id] = True
                    elif hex_type == 1:  # Wood
                        has_wood[player_id] = True
    
    # Run game
    turn = 0
    buildings_built = [0, 0]
    
    while not game.is_over() and turn < max_turns:
        actions = game.get_valid_actions()
        current = game.state.current_player
        action = game.players[current].decide(game, actions)
        
        if action.action_type.name.startswith("BUILD_") and action.action_type.name != "BUILD_INITIAL_ROAD":
            buildings_built[current] += 1
            
        game.execute(action)
        
        if action.action_type.name == "END_TURN":
            turn += 1
    
    return {
        'p1_name': p1.name,
        'p2_name': p2.name,
        'turns': turn,
        'vps': [game.state.players[0].public_vps, game.state.players[1].public_vps],
        'has_brick': has_brick,
        'has_wood': has_wood,
        'buildings_built': buildings_built,
        'winner': game.state.get_winner() if game.is_over() else None
    }

# Test different combinations
print("Testing improved bot games...\n")

games = [
    ("Original Random vs Random", RandomPlayer, RandomPlayer),
    ("Smart Greedy vs Smart Greedy", SmartGreedyPlayer, SmartGreedyPlayer),
    ("Random vs Smart Minimax", RandomPlayer, SmartMinimaxPlayer),
    ("Smart Greedy vs Smart Minimax", SmartGreedyPlayer, SmartMinimaxPlayer),
]

for name, p1_class, p2_class in games:
    print(f"=== {name} ===")
    
    # Run 3 games to get a sense of consistency
    results = []
    for i in range(3):
        result = run_quick_game(p1_class, p2_class)
        results.append(result)
    
    # Summary
    avg_vps = [sum(r['vps'][0] for r in results) / 3, 
               sum(r['vps'][1] for r in results) / 3]
    brick_rate = [sum(r['has_brick'][0] for r in results) / 3,
                  sum(r['has_brick'][1] for r in results) / 3]
    wood_rate = [sum(r['has_wood'][0] for r in results) / 3,
                 sum(r['has_wood'][1] for r in results) / 3]
    avg_buildings = [sum(r['buildings_built'][0] for r in results) / 3,
                     sum(r['buildings_built'][1] for r in results) / 3]
    
    print(f"  Average VPs: P0={avg_vps[0]:.1f}, P1={avg_vps[1]:.1f}")
    print(f"  Brick access: P0={brick_rate[0]*100:.0f}%, P1={brick_rate[1]*100:.0f}%")
    print(f"  Wood access: P0={wood_rate[0]*100:.0f}%, P1={wood_rate[1]*100:.0f}%")
    print(f"  Avg buildings: P0={avg_buildings[0]:.1f}, P1={avg_buildings[1]:.1f}")
    
    # Individual results
    for i, r in enumerate(results):
        winner_str = f"P{r['winner']}" if r['winner'] is not None else "ongoing"
        print(f"  Game {i+1}: {r['vps'][0]}-{r['vps'][1]} after {r['turns']} turns ({winner_str})")
    print()