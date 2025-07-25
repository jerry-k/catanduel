#!/usr/bin/env python3
"""Test all player combinations to ensure stability."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer, GreedyPlayer
from engine.models.minimax_player import MinimaxPlayer, SimpleMinimaxPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.smart_minimax_player import SmartMinimaxPlayer, SmartSimpleMinimaxPlayer

def test_game(p1_class, p2_class, max_turns=100):
    """Run a game and report any errors."""
    p1_name = p1_class.__name__
    p2_name = p2_class.__name__
    
    try:
        p1 = p1_class(0, f"{p1_name}-0")
        p2 = p2_class(1, f"{p2_name}-1")
        game = Game([p1, p2])
        
        turn = 0
        while not game.is_over() and turn < max_turns:
            actions = game.get_valid_actions()
            if not actions:
                return f"No valid actions at turn {turn}", False
                
            current = game.state.current_player
            action = game.players[current].decide(game, actions)
            
            success = game.execute(action)
            if not success:
                return f"Failed to execute {action} at turn {turn}", False
                
            if action.action_type.name == "END_TURN":
                turn += 1
        
        if game.is_over():
            winner = game.state.get_winner()
            return f"Game ended at turn {turn}, winner: P{winner}", True
        else:
            return f"Game reached turn limit ({max_turns})", True
            
    except Exception as e:
        return f"Exception at turn {turn}: {type(e).__name__}: {str(e)}", False

def main():
    """Test all player combinations."""
    player_classes = [
        ("Random", RandomPlayer),
        ("Greedy", GreedyPlayer),
        ("SmartGreedy", SmartGreedyPlayer),
        ("SimpleMM", SimpleMinimaxPlayer),
        ("SmartSimpleMM", SmartSimpleMinimaxPlayer),
        ("Minimax", MinimaxPlayer),
        ("SmartMinimax", SmartMinimaxPlayer),
    ]
    
    print("Testing all player combinations (100 turn limit)...\n")
    
    failed = []
    passed = []
    
    for i, (name1, class1) in enumerate(player_classes):
        for j, (name2, class2) in enumerate(player_classes):
            if i > j:  # Skip duplicate matchups
                continue
                
            print(f"Testing {name1} vs {name2}...", end=" ")
            result, success = test_game(class1, class2)
            
            if success:
                print(f"✓ {result}")
                passed.append((name1, name2))
            else:
                print(f"✗ {result}")
                failed.append((name1, name2, result))
    
    print(f"\n=== SUMMARY ===")
    print(f"Passed: {len(passed)}/{len(passed) + len(failed)}")
    
    if failed:
        print(f"\nFailed matchups:")
        for name1, name2, error in failed:
            print(f"  {name1} vs {name2}: {error}")
    else:
        print("\nAll matchups completed successfully!")

if __name__ == "__main__":
    main()