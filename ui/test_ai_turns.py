#!/usr/bin/env python3
"""
Test script to verify AI turn handling.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import ActionType

def test_ai_execution():
    """Test that AI can take turns during setup phase."""
    print("Testing AI turn execution...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    print(f"\nInitial state:")
    print(f"  Current player: {game.state.current_player}")
    print(f"  Buildings placed: {len(game.state.board.buildings)}")
    print(f"  Roads placed: {len(game.state.board.roads)}")
    
    # Simulate human placing first settlement
    actions = game.get_valid_actions()
    settlement_actions = [a for a in actions if a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT]
    
    if settlement_actions:
        # Human places settlement
        action = settlement_actions[0]
        success = game.execute(action)
        print(f"\nHuman placed settlement at corner {action.value}: {success}")
        print(f"  Current player after: {game.state.current_player}")
        
        # Now human needs to place road
        actions = game.get_valid_actions()
        road_actions = [a for a in actions if a.action_type == ActionType.BUILD_INITIAL_ROAD]
        
        if road_actions:
            action = road_actions[0]
            success = game.execute(action)
            print(f"Human placed road at edge {action.value}: {success}")
            print(f"  Current player after: {game.state.current_player}")
            
            # Now it should be AI's turn
            if game.state.current_player == 1:
                print("\n✅ Successfully switched to AI player")
                
                # The web server's get_game_state would handle AI turns
                # Let's simulate what it does
                events = []
                turns_taken = 0
                while game.state.current_player == 1 and not game.is_over() and turns_taken < 10:
                    ai_actions = game.get_valid_actions()
                    if not ai_actions:
                        break
                    
                    # AI picks first action
                    ai_action = ai_actions[0]
                    success = game.execute(ai_action)
                    
                    if success:
                        events.append(f"AI played {ai_action.action_type.name} at {ai_action.value}")
                        turns_taken += 1
                    else:
                        break
                
                print(f"\nAI took {turns_taken} actions:")
                for event in events:
                    print(f"  - {event}")
                
                print(f"\nFinal state:")
                print(f"  Current player: {game.state.current_player}")
                print(f"  Buildings placed: {len(game.state.board.buildings)}")
                print(f"  Roads placed: {len(game.state.board.roads)}")

if __name__ == "__main__":
    test_ai_execution()
    print("\n✅ Test completed!")