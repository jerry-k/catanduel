#!/usr/bin/env python3
"""Compare development card usage between our two Catanatron implementations."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.catanatron_alphabeta_player import CatanatronAlphaBetaPlayer
from engine.models.enums import ActionType, KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT

def analyze_player(player_class, num_games=5):
    """Analyze dev card usage for a player type."""
    stats = {
        'dev_cards_bought': 0,
        'dev_cards_played': 0,
        'knights': 0,
        'year_of_plenty': 0,
        'monopoly': 0,
        'road_building': 0,
        'games': 0
    }
    
    for _ in range(num_games):
        p1 = player_class(0, f"{player_class.__name__}-0")
        p2 = player_class(1, f"{player_class.__name__}-1")
        
        # Set lower depth for faster testing
        if hasattr(p1, 'max_depth'):
            p1.max_depth = 2
            p2.max_depth = 2
        if hasattr(p1, 'depth'):
            p1.depth = 2
            p2.depth = 2
        
        game = Game([p1, p2])
        
        cards_bought = [0, 0]
        
        # Play game
        turn = 0
        while not game.is_over() and turn < 100:
            actions = game.get_valid_actions()
            if not actions:
                break
            
            current = game.state.current_player
            action = game.players[current].decide(game, actions)
            
            # Track purchases and plays
            if action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
                cards_bought[current] += 1
            elif action.action_type == ActionType.PLAY_KNIGHT_CARD:
                stats['knights'] += 1
            elif action.action_type == ActionType.PLAY_YEAR_OF_PLENTY:
                stats['year_of_plenty'] += 1
            elif action.action_type == ActionType.PLAY_MONOPOLY:
                stats['monopoly'] += 1
            elif action.action_type == ActionType.PLAY_ROAD_BUILDING:
                stats['road_building'] += 1
            
            game.execute(action)
            
            if action.action_type == ActionType.END_TURN:
                turn += 1
        
        stats['dev_cards_bought'] += sum(cards_bought)
        stats['dev_cards_played'] += (stats['knights'] + stats['year_of_plenty'] + 
                                     stats['monopoly'] + stats['road_building'])
        stats['games'] += 1
    
    return stats

def main():
    """Compare the two implementations."""
    print("Comparing Catanatron player implementations...\n")
    print("(Running 5 games each, max 100 turns)\n")
    
    # Test original simplified version
    print("=== CatanatronMinimaxPlayer (Simplified) ===")
    minimax_stats = analyze_player(CatanatronMinimaxPlayer)
    
    if minimax_stats['dev_cards_bought'] > 0:
        play_rate = (minimax_stats['dev_cards_played'] / minimax_stats['dev_cards_bought']) * 100
        print(f"Dev cards bought: {minimax_stats['dev_cards_bought']}")
        print(f"Dev cards played: {minimax_stats['dev_cards_played']} ({play_rate:.1f}%)")
        print(f"  Knights: {minimax_stats['knights']}")
        print(f"  Year of Plenty: {minimax_stats['year_of_plenty']}")
        print(f"  Monopoly: {minimax_stats['monopoly']}")
        print(f"  Road Building: {minimax_stats['road_building']}")
    else:
        print("No development cards bought")
    
    # Test new accurate version
    print("\n=== CatanatronAlphaBetaPlayer (Accurate) ===")
    alphabeta_stats = analyze_player(CatanatronAlphaBetaPlayer)
    
    if alphabeta_stats['dev_cards_bought'] > 0:
        play_rate = (alphabeta_stats['dev_cards_played'] / alphabeta_stats['dev_cards_bought']) * 100
        print(f"Dev cards bought: {alphabeta_stats['dev_cards_bought']}")
        print(f"Dev cards played: {alphabeta_stats['dev_cards_played']} ({play_rate:.1f}%)")
        print(f"  Knights: {alphabeta_stats['knights']}")
        print(f"  Year of Plenty: {alphabeta_stats['year_of_plenty']}")
        print(f"  Monopoly: {alphabeta_stats['monopoly']}")
        print(f"  Road Building: {alphabeta_stats['road_building']}")
    else:
        print("No development cards bought")
    
    # Summary
    print("\n=== Key Differences ===")
    if minimax_stats['dev_cards_bought'] > 0 and alphabeta_stats['dev_cards_bought'] > 0:
        minimax_play_rate = (minimax_stats['dev_cards_played'] / minimax_stats['dev_cards_bought']) * 100
        alphabeta_play_rate = (alphabeta_stats['dev_cards_played'] / alphabeta_stats['dev_cards_bought']) * 100
        
        print(f"Play rate: {minimax_play_rate:.1f}% vs {alphabeta_play_rate:.1f}%")
        print(f"Cards per game: {minimax_stats['dev_cards_bought']/minimax_stats['games']:.1f} vs {alphabeta_stats['dev_cards_bought']/alphabeta_stats['games']:.1f}")

if __name__ == "__main__":
    main()