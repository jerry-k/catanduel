"""
Integration tests for UI adapter with game engine.

Tests complete game flow through the adapter.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.adapter import CatanDuelAdapter
from ui.adapter_types import UIActionType, UIAction, UIPhase


def test_setup_phase():
    """Test playing through setup phase."""
    adapter = CatanDuelAdapter()
    
    # Create game with human vs AI
    player1 = {'type': 'human', 'name': 'Human'}
    player2 = {'type': 'random', 'name': 'AI'}
    
    state = adapter.new_game(player1, player2, seed=42)
    
    print("=== Setup Phase Test ===")
    print(f"Initial phase: {state.phase}")
    print(f"Current player: {state.current_player}")
    print(f"Valid actions: {len(state.valid_actions)}")
    
    # Player 0 places settlement
    if state.valid_actions:
        action = state.valid_actions[0]  # Pick first valid spot
        print(f"\nPlayer 0 placing settlement at corner {action.data['corner']}")
        state, events = adapter.execute_action(action)
        print(f"Events: {[e.type for e in events]}")
        print(f"Next prompt: {state.message}")
    
    # Player 0 places road
    if state.valid_actions:
        action = state.valid_actions[0]  # Pick first valid road
        print(f"\nPlayer 0 placing road at edge {action.data['edge']}")
        state, events = adapter.execute_action(action)
        print(f"Events: {[e.type for e in events]}")
    
    # Now it should be AI's turn
    print(f"\nCurrent player after P0 setup: {state.current_player}")
    print(f"Is AI turn: {not state.players[state.current_player].is_human}")
    
    # Get AI action
    ai_action = adapter.get_ai_action()
    if ai_action:
        print(f"\nAI action: {ai_action.type} at {ai_action.data}")
        state, events = adapter.execute_action(ai_action)
        print(f"Events: {[e.type for e in events]}")
    
    # Continue for a few more actions
    for i in range(6):  # Complete rest of setup
        if state.phase != UIPhase.SETUP:
            break
            
        if state.players[state.current_player].is_human:
            # Human action - pick first valid
            if state.valid_actions:
                action = state.valid_actions[0]
                print(f"\nHuman action: {action.type}")
                state, events = adapter.execute_action(action)
        else:
            # AI action
            ai_action = adapter.get_ai_action()
            if ai_action:
                print(f"\nAI action: {ai_action.type}")
                state, events = adapter.execute_action(ai_action)
    
    print(f"\n=== Setup Complete ===")
    print(f"Phase: {state.phase}")
    print(f"Buildings placed: {len(state.board.buildings)}")
    
    # Check resources from second settlement
    print("\nStarting resources:")
    for i, player in enumerate(state.players):
        print(f"  Player {i}: {player.resources.total()} total")
    
    return adapter, state


def test_main_game_actions():
    """Test main game actions."""
    adapter, state = test_setup_phase()
    
    print("\n\n=== Main Game Test ===")
    
    # Test rolling dice
    if state.phase == UIPhase.MAIN and not state.dice_rolled:
        roll_action = UIAction(type=UIActionType.ROLL, data={})
        print("\nRolling dice...")
        state, events = adapter.execute_action(roll_action)
        
        for event in events:
            if event.type == "dice_rolled":
                print(f"Rolled: {event.data['die1']} + {event.data['die2']} = {event.data['total']}")
            elif event.type == "resource_gained":
                print(f"Player {event.player} gained {event.data['amount']} {event.data['resource']}")
    
    # Test ending turn
    if state.can_end_turn:
        end_action = UIAction(type=UIActionType.END_TURN, data={})
        print("\nEnding turn...")
        state, events = adapter.execute_action(end_action)
        print(f"New current player: {state.current_player}")
    
    print("\n=== Test Complete ===")


def test_action_validation():
    """Test invalid actions are rejected."""
    adapter = CatanDuelAdapter()
    
    player1 = {'type': 'human', 'name': 'Test'}
    player2 = {'type': 'human', 'name': 'Test2'}
    
    state = adapter.new_game(player1, player2, seed=42)
    
    print("\n=== Action Validation Test ===")
    
    # Try invalid action (build city during setup)
    invalid_action = UIAction(
        type=UIActionType.BUILD_CITY,
        data={'corner': 0}
    )
    
    try:
        state, events = adapter.execute_action(invalid_action)
        print("ERROR: Invalid action was accepted!")
    except ValueError as e:
        print(f"Good: Invalid action rejected - {e}")
    
    # Try valid action
    if state.valid_actions:
        valid_action = state.valid_actions[0]
        try:
            state, events = adapter.execute_action(valid_action)
            print("Good: Valid action accepted")
        except ValueError as e:
            print(f"ERROR: Valid action rejected - {e}")


if __name__ == '__main__':
    test_setup_phase()
    print("\n" + "="*50 + "\n")
    test_main_game_actions()
    print("\n" + "="*50 + "\n") 
    test_action_validation()