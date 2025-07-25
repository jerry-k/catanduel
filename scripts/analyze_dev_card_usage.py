#!/usr/bin/env python3
"""Analyze development card usage by different bot types."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer, GreedyPlayer
from engine.models.minimax_player import MinimaxPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer
from engine.models.catanatron_minimax_player import CatanatronMinimaxPlayer
from engine.models.enums import ActionType, KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT

def track_dev_card_usage(player_class, num_games=10, max_turns=150):
    """Track development card purchases and usage for a player type."""
    stats = {
        'games': 0,
        'dev_cards_bought': 0,
        'dev_cards_played': 0,
        'knights_played': 0,
        'year_of_plenty_played': 0,
        'monopoly_played': 0,
        'road_building_played': 0,
        'victory_points_held': 0,
        'games_with_unused_cards': 0,
        'total_unused_cards': 0
    }
    
    for game_num in range(num_games):
        p1 = player_class(0, f"{player_class.__name__}-0")
        p2 = player_class(1, f"{player_class.__name__}-1")
        
        # Reduce search depth for faster testing
        if hasattr(p1, 'max_depth'):
            p1.max_depth = 2
            p1.time_limit = 2.0
        if hasattr(p2, 'max_depth'):
            p2.max_depth = 2  
            p2.time_limit = 2.0
        
        game = Game([p1, p2])
        
        dev_cards_bought = [0, 0]
        dev_cards_played = [0, 0]
        play_actions = {
            ActionType.PLAY_KNIGHT_CARD: 'knights_played',
            ActionType.PLAY_YEAR_OF_PLENTY: 'year_of_plenty_played',
            ActionType.PLAY_MONOPOLY: 'monopoly_played',
            ActionType.PLAY_ROAD_BUILDING: 'road_building_played'
        }
        
        turn = 0
        while not game.is_over() and turn < max_turns:
            actions = game.get_valid_actions()
            if not actions:
                break
                
            current = game.state.current_player
            
            # Check available play actions before decision
            play_dev_actions = [a for a in actions if a.action_type in play_actions]
            if play_dev_actions and game_num == 0 and turn < 30:
                print(f"Turn {turn}, P{current} can play: {[a.action_type.name for a in play_dev_actions]}")
            
            action = game.players[current].decide(game, actions)
            
            # Track purchases
            if action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
                dev_cards_bought[current] += 1
            
            # Track plays
            if action.action_type in play_actions:
                dev_cards_played[current] += 1
                stats[play_actions[action.action_type]] += 1
                if game_num == 0:
                    print(f"  -> P{current} played {action.action_type.name}")
            
            game.execute(action)
            
            if action.action_type == ActionType.END_TURN:
                turn += 1
        
        # Count unused cards at end
        for i in range(2):
            player_state = game.state.players[i]
            # Simply count unplayed action cards (not victory points)
            unplayed_action_cards = (
                player_state.dev_cards[KNIGHT] +
                player_state.dev_cards[YEAR_OF_PLENTY] +
                player_state.dev_cards[MONOPOLY] +
                player_state.dev_cards[ROAD_BUILDING]
            )
            if unplayed_action_cards > 0:
                stats['games_with_unused_cards'] += 0.5  # Count each player as half a game
                stats['total_unused_cards'] += unplayed_action_cards
            
            # Count victory points held
            stats['victory_points_held'] += player_state.dev_cards[VICTORY_POINT]
            
            # Add to totals
            stats['dev_cards_bought'] += dev_cards_bought[i]
            stats['dev_cards_played'] += dev_cards_played[i]
        
        stats['games'] += 1
    
    return stats

def main():
    """Analyze dev card usage across different player types."""
    player_types = [
        ("Random", RandomPlayer),
        ("Greedy", GreedyPlayer),
        ("SmartGreedy", SmartGreedyPlayer),
        ("Minimax", MinimaxPlayer),
        ("SmartMinimax", SmartMinimaxPlayer),
        ("CatanatronMM", CatanatronMinimaxPlayer),
    ]
    
    print("Analyzing development card usage patterns...\n")
    print("(Running 10 games per player type, max 150 turns each)\n")
    
    for name, player_class in player_types:
        print(f"\n=== {name} Player ===")
        stats = track_dev_card_usage(player_class, num_games=10)
        
        if stats['dev_cards_bought'] > 0:
            play_rate = (stats['dev_cards_played'] / stats['dev_cards_bought']) * 100
            print(f"Dev cards bought: {stats['dev_cards_bought']}")
            print(f"Dev cards played: {stats['dev_cards_played']} ({play_rate:.1f}%)")
            print(f"  Knights: {stats['knights_played']}")
            print(f"  Year of Plenty: {stats['year_of_plenty_played']}")
            print(f"  Monopoly: {stats['monopoly_played']}")
            print(f"  Road Building: {stats['road_building_played']}")
            print(f"Victory Points held: {stats['victory_points_held']}")
            print(f"Games with unused cards: {stats['games_with_unused_cards']:.0f}/{stats['games']*2} players")
            print(f"Average unused per player: {stats['total_unused_cards']/(stats['games']*2):.1f}")
        else:
            print("No development cards bought")
    
    # Check if dev card play actions are being generated
    print("\n\n=== Checking Dev Card Action Generation ===")
    p1 = SmartGreedyPlayer(0, "Test-0")
    p2 = SmartGreedyPlayer(1, "Test-1") 
    game = Game([p1, p2])
    
    # Give player some dev cards manually for testing
    game.state.players[0].dev_cards[KNIGHT] = 2
    game.state.players[0].dev_cards[YEAR_OF_PLENTY] = 1
    game.state.players[0].dev_cards[MONOPOLY] = 1
    
    # Skip to main game
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        current = game.state.setup_phase_player_order()
        action = game.players[current].decide(game, actions)
        game.execute(action)
    
    # Check what actions are available
    actions = game.get_valid_actions()
    dev_actions = [a for a in actions if 'PLAY' in a.action_type.name]
    print(f"\nWith dev cards in hand, available play actions: {[a.action_type.name for a in dev_actions]}")
    
    if not dev_actions:
        print("WARNING: No dev card play actions generated despite having cards!")

if __name__ == "__main__":
    main()