#!/usr/bin/env python3
"""
Run a game between two bots and display a detailed log of all actions.

Usage:
    python3 scripts/bot_game_log.py [OPTIONS]

Options:
    --p1 TYPE       Player 1 type (default: greedy)
    --p2 TYPE       Player 2 type (default: simple_mm)
    --turns N       Maximum number of turns (default: 1000)
    --quiet         Less verbose output

Player Types:
    random          RandomPlayer - Makes completely random moves
    greedy          GreedyPlayer - Prioritizes cities > settlements > dev cards
    smart_greedy    SmartGreedyPlayer - Greedy with smart initial settlement placement
    simple_mm       SimpleMinimaxPlayer - Minimax search with depth 2
    smart_simple_mm SmartSimpleMinimaxPlayer - Simple minimax with smart initial placement
    minimax         MinimaxPlayer - Full minimax search with depth 3
    smart_minimax   SmartMinimaxPlayer - Full minimax with smart initial placement
    catanatron      CatanatronMinimaxPlayer - Simplified catanatron-style minimax
    catanatron_ab   CatanatronAlphaBetaPlayer - Accurate catanatron alphabeta (strongest)

Examples:
    # Default game (Greedy vs Simple Minimax)
    python3 scripts/bot_game_log.py
    
    # Smart players that avoid resource starvation
    python3 scripts/bot_game_log.py --p1 smart_greedy --p2 smart_minimax
    
    # Quick 50-turn game with minimal output
    python3 scripts/bot_game_log.py --turns 50 --quiet
    
    # Original stalling scenario
    python3 scripts/bot_game_log.py --p1 random --p2 minimax

Notes:
    - Smart variants ensure access to critical resources (brick/wood) during setup
    - Games may still stall with original players if they lack resource diversity
    - Use --quiet to see only major events (settlements, cities, victories)
    - Default turn limit is 1000 (same as catanatron) to handle stalled games
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer, GreedyPlayer
from engine.models.minimax_player import MinimaxPlayer, SimpleMinimaxPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer, SmartSimpleMinimaxPlayer
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.models.enums import ActionType

def format_action(action, player_id):
    """Format an action for display."""
    action_type = action.action_type.name
    value = action.value
    
    player_names = {0: "Player 0 (Red)", 1: "Player 1 (Black)"}
    player = player_names[player_id]
    
    # Format based on action type
    if action_type == "ROLL":
        return f"{player} rolls dice"
    elif action_type == "BUILD_SETTLEMENT":
        return f"{player} builds settlement at corner {value}"
    elif action_type == "BUILD_INITIAL_SETTLEMENT":
        return f"{player} places initial settlement at corner {value}"
    elif action_type == "BUILD_ROAD":
        return f"{player} builds road at edge {value}"
    elif action_type == "BUILD_INITIAL_ROAD":
        return f"{player} places initial road at edge {value}"
    elif action_type == "BUILD_CITY":
        return f"{player} upgrades settlement to city at corner {value}"
    elif action_type == "BUY_DEVELOPMENT_CARD":
        return f"{player} buys development card"
    elif action_type == "END_TURN":
        return f"{player} ends turn"
    elif action_type == "MARITIME_TRADE":
        give_res, give_amount, get_res = value
        resources = ["wood", "brick", "sheep", "wheat", "ore"]
        return f"{player} trades {give_amount} {resources[give_res]} for 1 {resources[get_res]}"
    elif action_type == "MOVE_ROBBER":
        hex_id, victim = value
        if victim is not None:
            victim_name = player_names[victim]
            return f"{player} moves robber to hex {hex_id} and steals from {victim_name}"
        else:
            return f"{player} moves robber to hex {hex_id}"
    elif action_type == "DISCARD":
        resources = ["wood", "brick", "sheep", "wheat", "ore"]
        discarded = []
        for i, count in enumerate(value):
            if count > 0:
                discarded.append(f"{count} {resources[i]}")
        return f"{player} discards {', '.join(discarded)}"
    elif action_type.startswith("PLAY_"):
        card_name = action_type.replace("PLAY_", "").replace("_CARD", "").replace("_", " ").title()
        return f"{player} plays {card_name} card"
    else:
        return f"{player} performs {action_type} {value if value else ''}"

def format_dice_result(state):
    """Format dice roll result."""
    if state.last_dice_roll:
        d1, d2 = state.last_dice_roll
        total = d1 + d2
        return f"  → Dice: {d1} + {d2} = {total}"
    return ""

def format_resources(player_state, name):
    """Format player resources."""
    resources = ["wood", "brick", "sheep", "wheat", "ore"]
    res_list = []
    for i, count in enumerate(player_state.resources):
        if count > 0:
            res_list.append(f"{count} {resources[i]}")
    
    if res_list:
        return f"{name} resources: {', '.join(res_list)}"
    else:
        return f"{name} resources: none"

def run_bot_game(player1_class, player2_class, max_turns=1000, verbose=True):
    """Run a game between two bots with detailed logging."""
    
    # Create players
    p1 = player1_class(0, f"{player1_class.__name__}-0")
    p2 = player2_class(1, f"{player2_class.__name__}-1")
    
    print(f"\n{'='*60}")
    print(f"Starting game: {p1.name} vs {p2.name}")
    print(f"{'='*60}\n")
    
    # Create game
    game = Game([p1, p2])
    
    turn = 0
    while not game.is_over() and turn < max_turns:
        # Get current state info
        state = game.state
        is_setup = state.is_setup_phase()
        current_player = state.setup_phase_player_order() if is_setup else state.current_player
        
        # Print turn header every 10 turns during main game
        if not is_setup and turn % 10 == 0:
            print(f"\n--- Turn {state.turn_number} ---")
            print(f"Victory Points: P0={state.players[0].public_vps} (hidden: {state.players[0].hidden_vps}), "
                  f"P1={state.players[1].public_vps} (hidden: {state.players[1].hidden_vps})")
            if verbose:
                print(format_resources(state.players[0], "P0"))
                print(format_resources(state.players[1], "P1"))
            print()
        
        # Get valid actions
        actions = game.get_valid_actions()
        if not actions:
            print("ERROR: No valid actions available!")
            break
        
        # Let current player decide
        action = game.players[current_player].decide(game, actions)
        
        # Log the action
        print(format_action(action, current_player))
        
        # Execute action
        state_before = game.state.copy()
        success = game.execute(action)
        
        if not success:
            print(f"  → ERROR: Action failed!")
            break
        
        # Log results
        if action.action_type == ActionType.ROLL:
            print(format_dice_result(game.state))
            
            # Check for resource production
            for i in range(2):
                gained = []
                resources = ["wood", "brick", "sheep", "wheat", "ore"]
                for j in range(5):
                    diff = game.state.players[i].resources[j] - state_before.players[i].resources[j]
                    if diff > 0:
                        gained.append(f"{diff} {resources[j]}")
                if gained:
                    player_name = f"Player {i}"
                    print(f"  → {player_name} gains {', '.join(gained)}")
        
        elif action.action_type == ActionType.BUILD_INITIAL_SETTLEMENT and current_player == 1:
            # Check for starting resources (second settlement)
            settlements = len([c for c, (p, t) in game.state.board.buildings.items() 
                             if p == current_player and t == 1])  # 1 = SETTLEMENT
            if settlements == 2:
                gained = []
                resources = ["wood", "brick", "sheep", "wheat", "ore"]
                for j in range(5):
                    diff = game.state.players[current_player].resources[j]
                    if diff > 0:
                        gained.append(f"{diff} {resources[j]}")
                if gained:
                    print(f"  → Starting resources: {', '.join(gained)}")
        
        turn += 1
    
    # Game end summary
    print(f"\n{'='*60}")
    if game.is_over():
        winner = game.state.get_winner()
        print(f"Game Over! Winner: Player {winner} ({game.players[winner].name})")
        print(f"Final VPs: P0={game.state.players[0].actual_vps()}, P1={game.state.players[1].actual_vps()}")
    else:
        print(f"Game stopped after {max_turns} turns")
        print(f"Current VPs: P0={game.state.players[0].public_vps}, P1={game.state.players[1].public_vps}")
    
    print(f"Total turns: {turn}")
    
    # Building counts
    print(f"\nFinal Building Counts:")
    for i in range(2):
        settlements = len([c for c, (p, t) in game.state.board.buildings.items() 
                          if p == i and t == 1])  # 1 = SETTLEMENT
        cities = len([c for c, (p, t) in game.state.board.buildings.items() 
                     if p == i and t == 2])  # 2 = CITY
        roads = len([e for e, p in game.state.board.roads.items() if p == i])
        print(f"  Player {i}: {settlements} settlements, {cities} cities, {roads} roads")
    
    # Longest road and largest army
    print(f"\nSpecial Achievements:")
    
    # Calculate actual road lengths for each player
    p0_road_length = game.state.board.get_player_road_length(0)
    p1_road_length = game.state.board.get_player_road_length(1)
    
    if game.state.board.longest_road_player is not None:
        print(f"  Longest Road: Player {game.state.board.longest_road_player} (2 VP)")
    else:
        print(f"  Longest Road: None")
    print(f"  Road Lengths: P0={p0_road_length}, P1={p1_road_length}")
    
    # Check largest army
    p0_knights = game.state.players[0].knights_played
    p1_knights = game.state.players[1].knights_played
    if game.state.players[0].has_largest_army:
        print(f"  Largest Army: Player 0 ({p0_knights} knights, 2 VP)")
    elif game.state.players[1].has_largest_army:
        print(f"  Largest Army: Player 1 ({p1_knights} knights, 2 VP)")
    else:
        print(f"  Largest Army: None (P0: {p0_knights} knights, P1: {p1_knights} knights)")
    
    print(f"{'='*60}\n")

def main():
    """Main function to run bot games."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CatanDuel games between bots with detailed logging")
    parser.add_argument("--p1", choices=["random", "greedy", "smart_greedy", "simple_mm", "smart_simple_mm", "minimax", "smart_minimax", "catanatron", "catanatron_ab"], 
                       default="greedy", help="Player 1 type")
    parser.add_argument("--p2", choices=["random", "greedy", "smart_greedy", "simple_mm", "smart_simple_mm", "minimax", "smart_minimax", "catanatron", "catanatron_ab"], 
                       default="simple_mm", help="Player 2 type")
    parser.add_argument("--turns", type=int, default=1000, help="Maximum turns")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    
    args = parser.parse_args()
    
    # Map player types
    player_types = {
        "random": RandomPlayer,
        "greedy": GreedyPlayer,
        "smart_greedy": SmartGreedyPlayer,
        "simple_mm": SimpleMinimaxPlayer,
        "smart_simple_mm": SmartSimpleMinimaxPlayer,
        "minimax": MinimaxPlayer,
        "smart_minimax": SmartMinimaxPlayer,
        "catanatron": CatanatronMinimaxPlayer,
        "catanatron_ab": CatanatronAlphaBetaPlayer
    }
    
    p1_class = player_types[args.p1]
    p2_class = player_types[args.p2]
    
    # Run game
    run_bot_game(p1_class, p2_class, max_turns=args.turns, verbose=not args.quiet)

if __name__ == "__main__":
    main()