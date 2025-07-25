#!/usr/bin/env python3
"""
Run a tournament of multiple games between two bot players.

Usage:
    python3 scripts/tournament.py [OPTIONS]

Options:
    --p1 TYPE       Player 1 type (default: greedy)
    --p2 TYPE       Player 2 type (default: simple_mm)
    --games N       Number of games to play (default: 100)
    --turns N       Maximum turns per game (default: 1000)
    --quiet         Minimal output (only show final results)
    --verbose       Show result of each game

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
    # Default tournament (100 games of Greedy vs Simple Minimax)
    python3 scripts/tournament.py
    
    # Quick 10-game tournament between smart players
    python3 scripts/tournament.py --games 10 --p1 smart_greedy --p2 smart_minimax
    
    # Large tournament with verbose output
    python3 scripts/tournament.py --games 200 --verbose --p1 random --p2 smart_greedy
    
    # Silent mode - only show final results
    python3 scripts/tournament.py --quiet --p1 minimax --p2 minimax

Notes:
    - Games are played with alternating starting positions
    - Timeouts count as draws
    - Results show win rates and average game length
"""

import sys
import os
import time
from typing import Tuple, Type

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import Player, RandomPlayer, GreedyPlayer
from engine.models.minimax_player import MinimaxPlayer, SimpleMinimaxPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer, SmartSimpleMinimaxPlayer
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.models.enums import ActionType

def play_game(p1_class: Type[Player], p2_class: Type[Player], 
              p1_name: str, p2_name: str, game_num: int,
              max_turns: int = 1000) -> Tuple[int, int, float]:
    """
    Play a single game between two players.
    
    Returns:
        (winner, turns, duration) where winner is 0, 1, or -1 (draw)
    """
    start_time = time.time()
    
    # Alternate starting positions
    if game_num % 2 == 0:
        p1 = p1_class(0, f"{p1_name}-0")
        p2 = p2_class(1, f"{p2_name}-1")
        player_map = {0: 0, 1: 1}  # P1 is red, P2 is black
    else:
        p1 = p2_class(0, f"{p2_name}-0")
        p2 = p1_class(1, f"{p1_name}-1")
        player_map = {0: 1, 1: 0}  # P2 is red, P1 is black
    
    game = Game([p1, p2])
    
    turn = 0
    while not game.is_over() and turn < max_turns:
        actions = game.get_valid_actions()
        if not actions:
            break
            
        current = game.state.current_player
        action = game.players[current].decide(game, actions)
        
        success = game.execute(action)
        if not success:
            break
            
        if action.action_type == ActionType.END_TURN:
            turn += 1
    
    duration = time.time() - start_time
    
    if game.is_over():
        winner_color = game.state.get_winner()
        # Map back to original player numbers
        winner = player_map[winner_color]
        return winner, turn, duration
    else:
        # Draw (timeout)
        return -1, turn, duration

def run_tournament(p1_class: Type[Player], p2_class: Type[Player],
                  p1_name: str, p2_name: str,
                  num_games: int, max_turns: int,
                  quiet: bool, verbose: bool):
    """Run a tournament between two players."""
    
    if not quiet:
        print(f"Starting tournament: {p1_name} vs {p2_name}")
        print(f"Playing {num_games} games with {max_turns} turn limit each")
        print(f"Players alternate starting positions")
        print("-" * 60)
    
    wins = [0, 0]  # P1 wins, P2 wins
    draws = 0
    total_turns = 0
    total_duration = 0
    turn_counts = []
    
    for i in range(num_games):
        if not quiet and not verbose:
            # Progress indicator
            if i % 10 == 0:
                print(f"Playing games {i+1}-{min(i+10, num_games)}...", end="", flush=True)
        
        winner, turns, duration = play_game(
            p1_class, p2_class, p1_name, p2_name, i, max_turns
        )
        
        total_turns += turns
        total_duration += duration
        turn_counts.append(turns)
        
        if winner == 0:
            wins[0] += 1
            result = f"P1 ({p1_name})"
        elif winner == 1:
            wins[1] += 1
            result = f"P2 ({p2_name})"
        else:
            draws += 1
            result = "Draw"
        
        if verbose:
            starting = "P1" if i % 2 == 0 else "P2"
            print(f"Game {i+1}: {result} wins in {turns} turns ({duration:.1f}s) - {starting} started")
        elif not quiet and i % 10 == 9:
            print(f" Done! (P1: {wins[0]}, P2: {wins[1]}, Draws: {draws})")
    
    # Final statistics
    if not quiet and not verbose and num_games % 10 != 0:
        print(f" Done! (P1: {wins[0]}, P2: {wins[1]}, Draws: {draws})")
    
    print("\n" + "=" * 60)
    print(f"TOURNAMENT RESULTS: {p1_name} vs {p2_name}")
    print("=" * 60)
    print(f"Games played: {num_games}")
    print(f"\n{p1_name} (P1): {wins[0]} wins ({wins[0]/num_games*100:.1f}%)")
    print(f"{p2_name} (P2): {wins[1]} wins ({wins[1]/num_games*100:.1f}%)")
    print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
    
    if num_games > 0:
        avg_turns = total_turns / num_games
        avg_duration = total_duration / num_games
        print(f"\nAverage game length: {avg_turns:.1f} turns")
        print(f"Average game duration: {avg_duration:.1f} seconds")
        
        # Show min/max turns
        if turn_counts:
            print(f"Shortest game: {min(turn_counts)} turns")
            print(f"Longest game: {max(turn_counts)} turns")

def main():
    """Main function to run tournaments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run CatanDuel tournament between two bot players",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1].split("Notes:")[0]
    )
    
    parser.add_argument("--p1", 
                       choices=["random", "greedy", "smart_greedy", "simple_mm", 
                               "smart_simple_mm", "minimax", "smart_minimax", "catanatron", "catanatron_ab"], 
                       default="greedy", help="Player 1 type")
    parser.add_argument("--p2", 
                       choices=["random", "greedy", "smart_greedy", "simple_mm", 
                               "smart_simple_mm", "minimax", "smart_minimax", "catanatron", "catanatron_ab"], 
                       default="simple_mm", help="Player 2 type")
    parser.add_argument("--games", type=int, default=100, 
                       help="Number of games to play")
    parser.add_argument("--turns", type=int, default=1000, 
                       help="Maximum turns per game")
    parser.add_argument("--quiet", action="store_true", 
                       help="Minimal output")
    parser.add_argument("--verbose", action="store_true", 
                       help="Show each game result")
    
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
    
    # Run tournament
    run_tournament(
        p1_class, p2_class,
        args.p1, args.p2,
        args.games, args.turns,
        args.quiet, args.verbose
    )

if __name__ == "__main__":
    main()