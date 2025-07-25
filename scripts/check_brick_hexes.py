#!/usr/bin/env python3
"""Check if there are any brick hexes on the board."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer

def check_brick():
    """Check brick hex distribution."""
    # Run multiple games to see the pattern
    for game_num in range(5):
        p1 = RandomPlayer(0, "P0")
        p2 = RandomPlayer(1, "P1")
        game = Game([p1, p2])
        
        print(f"\n=== GAME {game_num + 1} ===")
        
        # Check all hexes
        brick_hexes = []
        for hex_id in range(19):
            hex_type = game.state.hex_types[hex_id]
            if hex_type == 2:  # Brick
                number = game.state.hex_numbers[hex_id]
                brick_hexes.append((hex_id, number))
        
        print(f"Brick hexes: {brick_hexes}")
        
        # Check resource distribution
        resource_counts = [0, 0, 0, 0, 0, 0]  # desert, wood, brick, sheep, wheat, ore
        for hex_id in range(19):
            hex_type = game.state.hex_types[hex_id]
            resource_counts[hex_type] += 1
        
        resource_names = ['desert', 'wood', 'brick', 'sheep', 'wheat', 'ore']
        print("Resource distribution:")
        for i, name in enumerate(resource_names):
            print(f"  {name}: {resource_counts[i]}")

if __name__ == "__main__":
    check_brick()