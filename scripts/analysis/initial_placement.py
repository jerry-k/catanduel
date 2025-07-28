#!/usr/bin/env python3
"""
Analyze initial settlement placement patterns between AI players.
Shows where and in what order players place their initial settlements.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import Player
from engine.models.actions import ActionType
from engine.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.colonist_map import (
    CORNER_TO_HEXES, HEX_TO_CORNERS,
    ALL_HEX_IDS
)

# Resource names mapping
RESOURCE_NAMES = {
    0: "wood",
    1: "brick", 
    2: "sheep",
    3: "wheat",
    4: "ore",
    5: "desert"
}

def get_corner_resources(state, corner):
    """Get resources and numbers for a corner."""
    resources = []
    for hex_id in CORNER_TO_HEXES.get(corner, []):
        if hex_id in ALL_HEX_IDS:
            hex_type = state.hex_types[hex_id]
            hex_number = state.hex_numbers[hex_id]
            if hex_type != 5 and hex_number > 0:  # Not desert
                resource_name = RESOURCE_NAMES[hex_type]
                resources.append((resource_name, hex_number))
    return resources

def analyze_placement(p1_class, p2_class, num_games=10):
    """Analyze initial placement patterns."""
    
    print(f"Analyzing initial placement: {p1_class.__name__} vs {p2_class.__name__}")
    print("=" * 80)
    
    for game_num in range(num_games):
        # Alternate who goes first
        if game_num % 2 == 0:
            p1 = p1_class(0, "P1")
            p2 = p2_class(1, "P2")
            first_player = "P1 (Catanatron)"
            second_player = "P2 (CatanatronAB)"
        else:
            p1 = p2_class(0, "P1")
            p2 = p1_class(1, "P2")
            first_player = "P1 (CatanatronAB)"
            second_player = "P2 (Catanatron)"
        
        game = Game([p1, p2])
        
        print(f"\nGame {game_num + 1}: {first_player} goes first")
        print("-" * 60)
        
        # Track placement order
        placements = []
        
        # Play through initial placement phase
        while game.state.is_setup_phase():
            actions = game.get_valid_actions()
            current = game.state.current_player
            action = game.players[current].decide(game, actions)
            
            if action.action_type == ActionType.BUILD_INITIAL_SETTLEMENT:
                corner = action.value  # value is just the corner ID
                resources = get_corner_resources(game.state, corner)
                player_name = first_player if current == 0 else second_player
                
                # Format resources nicely
                res_str = ", ".join([f"{r[1]}-{r[0]}" for r in resources])
                placements.append(f"{player_name} settlement at corner {corner}: [{res_str}]")
            
            game.execute(action)
        
        # Print placement order
        print("Placement order (snake draft: P1→P2→P2→P1):")
        if len(placements) >= 4:
            # Reorder to show actual snake draft
            actual_order = [placements[0], placements[2], placements[3], placements[1]]
            for i, placement in enumerate(actual_order):
                print(f"  {i+1}. {placement}")
        
        # Calculate resource diversity and production
        print("\nResource summary:")
        for player_idx, player_name in enumerate([first_player, second_player]):
            # Count resources
            resource_counts = {r: 0 for r in ["wood", "brick", "sheep", "wheat", "ore"]}
            production_values = {r: 0 for r in ["wood", "brick", "sheep", "wheat", "ore"]}
            total_dots = 0
            
            # Get player's settlements
            for corner in range(54):  # All corner IDs
                building = game.state.board.buildings.get(corner)
                if building and building[0] == player_idx:
                    for hex_id in CORNER_TO_HEXES.get(corner, []):
                        if hex_id in ALL_HEX_IDS:
                            hex_type = game.state.hex_types[hex_id]
                            hex_number = game.state.hex_numbers[hex_id]
                            if hex_type != 5 and hex_number > 0:
                                resource_name = RESOURCE_NAMES[hex_type]
                                resource_counts[resource_name] += 1
                                # Calculate dots (6 and 8 = 5 dots, 5 and 9 = 4 dots, etc)
                                dots = 6 - abs(7 - hex_number)
                                production_values[resource_name] += dots
                                total_dots += dots
            
            # Print summary
            unique_resources = sum(1 for count in resource_counts.values() if count > 0)
            print(f"  {player_name}: {unique_resources}/5 resources, {total_dots} total dots")
            print(f"    Resources: {', '.join([f'{r}:{c}' for r, c in resource_counts.items() if c > 0])}")
            print(f"    Production: {', '.join([f'{r}:{p}' for r, p in production_values.items() if p > 0])}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze initial settlement placement")
    parser.add_argument("--games", type=int, default=10, help="Number of games to analyze")
    args = parser.parse_args()
    
    analyze_placement(CatanatronMinimaxPlayer, CatanatronAlphaBetaPlayer, args.games)

if __name__ == "__main__":
    main()