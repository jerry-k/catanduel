"""
Test and compare different AI players for CatanDuel.

This script runs matches between different AI implementations to
evaluate their relative strengths.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from typing import Tuple, List, Dict
from collections import defaultdict

from game import Game
from models import (
    RandomPlayer, GreedyPlayer,
    MinimaxPlayer, SimpleMinimaxPlayer,
    MCTSPlayer, FastMCTSPlayer, StrongMCTSPlayer
)


def play_match(player1, player2, max_turns: int = 500, verbose: bool = False) -> Tuple[int, int, float]:
    """
    Play a single match between two players.
    
    Returns:
        (winner_id, turns, time_taken)
    """
    start_time = time.time()
    game = Game([player1, player2])
    
    turns = 0
    while not game.is_over() and turns < max_turns:
        if verbose and turns % 50 == 0:
            print(f"  Turn {turns}: P0={game.state.players[0].actual_vps()} VP, "
                  f"P1={game.state.players[1].actual_vps()} VP")
        
        actions = game.get_valid_actions()
        if not actions:
            print(f"Warning: No valid actions at turn {turns}")
            break
        
        current_player = game._get_acting_player()
        action = game.players[current_player].decide(game, actions)
        game.execute(action)
        
        turns += 1
    
    time_taken = time.time() - start_time
    
    if game.is_over():
        winner = game.state.get_winner()
        return winner, turns, time_taken
    else:
        # Game hit turn limit - winner is player with most VPs
        vps = [p.actual_vps() for p in game.state.players]
        if vps[0] > vps[1]:
            return 0, turns, time_taken
        elif vps[1] > vps[0]:
            return 1, turns, time_taken
        else:
            return None, turns, time_taken  # Draw


def run_tournament(player_types: List[type], games_per_matchup: int = 10) -> Dict:
    """
    Run a round-robin tournament between different player types.
    
    Returns:
        Dictionary with results
    """
    results = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "games": 0, "total_time": 0}))
    
    print("Running AI Tournament...")
    print(f"Players: {[p.__name__ for p in player_types]}")
    print(f"Games per matchup: {games_per_matchup}")
    print()
    
    for i, player1_type in enumerate(player_types):
        for j, player2_type in enumerate(player_types):
            if i >= j:  # Skip self-play and duplicate matchups
                continue
            
            print(f"\n{player1_type.__name__} vs {player2_type.__name__}:")
            
            p1_wins = 0
            p2_wins = 0
            draws = 0
            total_turns = 0
            total_time = 0
            
            for game_num in range(games_per_matchup):
                # Alternate who goes first
                if game_num % 2 == 0:
                    p1 = player1_type(0)
                    p2 = player2_type(1)
                    first_is_p1 = True
                else:
                    p1 = player2_type(0)
                    p2 = player1_type(1)
                    first_is_p1 = False
                
                winner, turns, time_taken = play_match(p1, p2, verbose=False)
                total_turns += turns
                total_time += time_taken
                
                if winner == 0:
                    if first_is_p1:
                        p1_wins += 1
                    else:
                        p2_wins += 1
                elif winner == 1:
                    if first_is_p1:
                        p2_wins += 1
                    else:
                        p1_wins += 1
                else:
                    draws += 1
                
                print(".", end="", flush=True)
            
            print()
            print(f"  {player1_type.__name__}: {p1_wins} wins")
            print(f"  {player2_type.__name__}: {p2_wins} wins")
            print(f"  Draws: {draws}")
            print(f"  Avg turns: {total_turns / games_per_matchup:.1f}")
            print(f"  Avg time: {total_time / games_per_matchup:.1f}s")
            
            # Store results
            results[player1_type.__name__][player2_type.__name__] = {
                "wins": p1_wins,
                "games": games_per_matchup,
                "total_time": total_time
            }
            results[player2_type.__name__][player1_type.__name__] = {
                "wins": p2_wins,
                "games": games_per_matchup,
                "total_time": total_time
            }
    
    return results


def display_results(results: Dict):
    """Display tournament results in a nice format."""
    players = sorted(results.keys())
    
    print("\n" + "="*60)
    print("TOURNAMENT RESULTS")
    print("="*60)
    
    # Win rates
    print("\nWin Rates:")
    print("-" * 40)
    
    total_wins = defaultdict(int)
    total_games = defaultdict(int)
    
    for p1 in players:
        for p2, stats in results[p1].items():
            total_wins[p1] += stats["wins"]
            total_games[p1] += stats["games"]
    
    sorted_players = sorted(players, key=lambda p: total_wins[p] / max(1, total_games[p]), reverse=True)
    
    for player in sorted_players:
        if total_games[player] > 0:
            win_rate = total_wins[player] / total_games[player]
            print(f"{player:20} {win_rate:6.1%} ({total_wins[player]}/{total_games[player]})")


def test_individual_ai():
    """Test individual AI implementations."""
    print("Testing individual AI players...\n")
    
    # Test Minimax
    print("1. Testing MinimaxPlayer...")
    p1 = MinimaxPlayer(0, "Minimax-0", max_depth=3)
    p2 = RandomPlayer(1, "Random-1")
    winner, turns, time_taken = play_match(p1, p2, verbose=True)
    print(f"   Result: Player {winner} won in {turns} turns ({time_taken:.1f}s)\n")
    
    # Test MCTS
    print("2. Testing MCTSPlayer...")
    p1 = MCTSPlayer(0, "MCTS-0", time_limit=1.0)
    p2 = GreedyPlayer(1, "Greedy-1")
    winner, turns, time_taken = play_match(p1, p2, verbose=True)
    print(f"   Result: Player {winner} won in {turns} turns ({time_taken:.1f}s)\n")
    
    # Test Strong players against each other
    print("3. Testing strong AI matchup...")
    p1 = MinimaxPlayer(0, "Minimax-0", max_depth=3)
    p2 = StrongMCTSPlayer(1, "StrongMCTS-1")
    winner, turns, time_taken = play_match(p1, p2, verbose=True)
    print(f"   Result: Player {winner} won in {turns} turns ({time_taken:.1f}s)\n")


def main():
    """Run AI player tests and tournament."""
    print("CatanDuel AI Player Testing\n")
    
    # Test individual AIs first
    test_individual_ai()
    
    # Run tournament
    print("\n" + "="*60)
    print("Starting AI Tournament")
    print("="*60)
    
    # Select player types for tournament
    player_types = [
        RandomPlayer,
        GreedyPlayer,
        SimpleMinimaxPlayer,
        MinimaxPlayer,
        FastMCTSPlayer,
        MCTSPlayer,
        # StrongMCTSPlayer  # Commented out as it's slow
    ]
    
    # Run tournament with fewer games for testing
    results = run_tournament(player_types, games_per_matchup=6)
    
    # Display results
    display_results(results)
    
    # Performance analysis
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS")
    print("="*60)
    
    print("\nExpected strength ranking:")
    print("1. MCTSPlayer / MinimaxPlayer (strongest)")
    print("2. FastMCTSPlayer / SimpleMinimaxPlayer")
    print("3. GreedyPlayer")
    print("4. RandomPlayer (weakest)")
    
    print("\nNotes:")
    print("- MCTS typically performs better with more time")
    print("- Minimax is more consistent but limited by search depth")
    print("- Greedy uses simple heuristics without lookahead")
    print("- Random is purely for baseline comparison")


if __name__ == "__main__":
    main()