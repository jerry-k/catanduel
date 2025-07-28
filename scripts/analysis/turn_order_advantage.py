#!/usr/bin/env python3
"""
Detailed analysis of turn order advantage in Catan.
Shows how being first compounds advantages over time.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.models.actions import ActionType

def analyze_turn_order_advantage():
    """Analyze how first player advantage accumulates."""
    
    print("Turn Order Advantage Analysis")
    print("=" * 80)
    print("\nKEY CONCEPT: In Catan, Player 0 goes first EVERY turn.")
    print("This creates several compounding advantages:\n")
    
    # Run a few games to demonstrate
    games_to_analyze = 3
    
    for game_num in range(games_to_analyze):
        players = [
            CatanatronMinimaxPlayer(0, "P0-First"),
            CatanatronAlphaBetaPlayer(1, "P1-Second")
        ]
        
        game = Game(players)
        
        print(f"\n{'='*60}")
        print(f"GAME {game_num + 1} ANALYSIS")
        print(f"{'='*60}")
        
        # Skip setup phase
        while game.state.initial_phase:
            actions = game.get_valid_actions()
            player = game.state.setup_phase_player_order()
            action = players[player].decide(game, actions)
            game.execute(action)
        
        # Track key metrics
        resources_gained = [[0,0,0,0,0], [0,0,0,0,0]]
        total_resources = [0, 0]
        buildings_built = [{"roads": 2, "settlements": 2, "cities": 0, "dev_cards": 0},
                          {"roads": 2, "settlements": 2, "cities": 0, "dev_cards": 0}]
        vps = [2, 2]
        first_to_milestones = []
        turn_count = 0
        
        print("\nTURN-BY-TURN ADVANTAGES:")
        print("-" * 60)
        
        while turn_count < 20 and not game.is_over():
            actions = game.get_valid_actions()
            current = game.state.current_player
            action = players[current].decide(game, actions)
            
            if action.action_type == ActionType.ROLL:
                game.execute(action)
                dice_sum = sum(game.state.last_dice_roll)
                
                # Track resources before and after
                resources_before = [sum(game.state.players[i].resources) for i in range(2)]
                
                # Execute remaining actions this turn
                while True:
                    actions = game.get_valid_actions()
                    if not actions:
                        break
                    action = players[current].decide(game, actions)
                    
                    # Track building
                    if action.action_type == ActionType.BUILD_ROAD:
                        buildings_built[current]["roads"] += 1
                    elif action.action_type == ActionType.BUILD_SETTLEMENT:
                        buildings_built[current]["settlements"] += 1
                        # Check if first to 5 settlements
                        if buildings_built[current]["settlements"] == 5 and "5_settlements" not in first_to_milestones:
                            first_to_milestones.append(f"P{current} first to 5 settlements (turn {turn_count})")
                    elif action.action_type == ActionType.BUILD_CITY:
                        buildings_built[current]["cities"] += 1
                    elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
                        buildings_built[current]["dev_cards"] += 1
                        # Check if first to buy dev card
                        if buildings_built[current]["dev_cards"] == 1 and "first_dev" not in [m.split()[0] for m in first_to_milestones]:
                            first_to_milestones.append(f"P{current} first to buy dev card (turn {turn_count})")
                    
                    game.execute(action)
                    
                    if action.action_type == ActionType.END_TURN:
                        break
                
                # Track resources after
                resources_after = [sum(game.state.players[i].resources) for i in range(2)]
                resources_this_turn = [resources_after[i] - resources_before[i] for i in range(2)]
                total_resources[0] += max(0, resources_this_turn[0])
                total_resources[1] += max(0, resources_this_turn[1])
                
                # Update VPs
                vps = [game.state.players[i].public_vps for i in range(2)]
                
                # Print turn summary only if interesting
                if turn_count < 10 or any(r > 0 for r in resources_this_turn):
                    print(f"Turn {turn_count + 1}: P{current} rolls {dice_sum}")
                    if resources_this_turn[0] > 0 or resources_this_turn[1] > 0:
                        print(f"  Resources: P0 +{resources_this_turn[0]}, P1 +{resources_this_turn[1]}")
                        print(f"  Total so far: P0={total_resources[0]}, P1={total_resources[1]}")
                    if vps[0] != 2 or vps[1] != 2:
                        print(f"  VPs: P0={vps[0]}, P1={vps[1]}")
                
                turn_count += 1
            else:
                game.execute(action)
        
        print(f"\nAFTER {turn_count} TURNS:")
        print(f"Total resources collected: P0={total_resources[0]}, P1={total_resources[1]}")
        print(f"Resource advantage for P0: +{total_resources[0] - total_resources[1]} ({(total_resources[0] - total_resources[1])/max(1, total_resources[1])*100:.1f}%)")
        
        print("\nFIRST TO MILESTONES:")
        for milestone in first_to_milestones:
            print(f"  - {milestone}")
        
        print("\nWHY THIS MATTERS:")
        print("1. TEMPO: P0 always acts first each turn")
        print("   - First to build when both players have resources")
        print("   - First to claim limited board positions")
        print("   - First to buy limited dev cards")
        
        print("\n2. COMPOUND EFFECT: Small advantages multiply")
        print(f"   - P0 collected {total_resources[0] - total_resources[1]} more resources in {turn_count} turns")
        print("   - More resources → more buildings → more production → even more resources")
        
        print("\n3. RACE DYNAMICS: In a race to 10 VPs")
        print("   - Being ahead forces opponent to play catch-up")
        print("   - P0 can play more efficiently when ahead")

    print("\n" + "="*80)
    print("MATHEMATICAL EXPLANATION:")
    print("="*80)
    print("""
Imagine both players have identical setups producing 1 resource per turn.

Turn 1: P0 rolls and gets 1 resource, P1 rolls and gets 1 resource
        P0=1, P1=1 (tied)

Turn 2: P0 has first chance to use their resource (e.g., build a road)
        P0 rolls again (now with better position), P1 rolls
        P0=2+bonus, P1=2

Turn 3: P0 continues to act first with accumulated advantages
        The gap widens...

Over 100+ turns, this "first action" advantage compounds significantly.
It's like compound interest - small advantages multiply over time.

In chess, white (first player) wins 52-56% at top level.
In our Catan implementation, first player wins nearly 100% between equal AIs!
This suggests the first-player advantage is much stronger than intended.
""")

if __name__ == "__main__":
    analyze_turn_order_advantage()