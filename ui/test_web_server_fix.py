#!/usr/bin/env python3
"""
Test script to verify the web server correctly handles setup phase player switching.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# Test server URL
BASE_URL = "http://localhost:5555"

def test_setup_phase():
    """Test that the web server correctly handles setup phase."""
    print("Testing setup phase through web server...")
    
    # Create new game
    response = requests.post(f"{BASE_URL}/api/new_game", json={})
    assert response.status_code == 200
    data = response.json()
    
    game_id = data['game_id']
    print(f"\nCreated game: {game_id}")
    print(f"Initial current_player: {data['state']['current_player']}")
    print(f"Initial legal actions for player: {data['legal_actions'][0]['player'] if data['legal_actions'] else 'none'}")
    
    # Track setup phase
    action_count = 0
    max_actions = 10
    
    while action_count < max_actions:
        # Get game state
        response = requests.get(f"{BASE_URL}/api/game_state/{game_id}")
        assert response.status_code == 200
        state_data = response.json()
        
        if not state_data['state']['setup_phase']:
            print("\nSetup phase complete!")
            break
            
        print(f"\nAction {action_count + 1}:")
        print(f"  Current player (from state): {state_data['state']['current_player']}")
        print(f"  Legal actions: {len(state_data['legal_actions'])}")
        
        if state_data['legal_actions']:
            # Check player in legal actions
            action_player = state_data['legal_actions'][0]['player']
            print(f"  Player for actions: {action_player}")
            
            # If it's AI's turn, the server should have already executed it
            if action_player == 1 and state_data['events']:
                print(f"  AI actions executed: {len(state_data['events'])}")
                for event in state_data['events']:
                    print(f"    - {event['message']}")
            elif action_player == 0:
                # Human's turn - take first action
                action = state_data['legal_actions'][0]
                print(f"  Human taking action: {action['type']}")
                
                # Execute action
                response = requests.post(f"{BASE_URL}/api/execute_action/{game_id}", json=action)
                assert response.status_code == 200
                exec_data = response.json()
                print(f"  Success: {exec_data['success']}")
        else:
            print("  No legal actions!")
            break
            
        action_count += 1
    
    # Check final state
    response = requests.get(f"{BASE_URL}/api/game_state/{game_id}")
    assert response.status_code == 200
    final_data = response.json()
    
    print(f"\nFinal state:")
    print(f"  Setup phase: {final_data['state']['setup_phase']}")
    print(f"  Current player: {final_data['state']['current_player']}")
    print(f"  Buildings on board: {sum(1 for c in final_data['state']['corners'].values() if c is not None)}")
    print(f"  Roads on board: {sum(1 for e, p in final_data['state']['edges'].items() if p is not None)}")

if __name__ == "__main__":
    try:
        test_setup_phase()
        print("\n✅ Test completed!")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server. Make sure the server is running on port 5555.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()