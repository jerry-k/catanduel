#!/usr/bin/env python3
"""
Manual test script for CatanDuel server.
Tests API endpoints directly.
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:5001"

def test_api():
    """Test the API endpoints."""
    print("Testing CatanDuel API...")
    
    # Create session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Create new game
        print("\n1. Creating new game...")
        config = {
            "player1": {"type": "human", "name": "Test Player"},
            "player2": {"type": "random", "name": "AI Player"}
        }
        
        response = session.post(f"{BASE_URL}/api/new_game", json=config)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Game created with ID: {data['game_id']}")
            print(f"   ✓ Phase: {data['state']['phase']}")
            print(f"   ✓ Current player: {data['state']['current_player']}")
            print(f"   ✓ Valid actions: {len(data['state']['valid_actions'])}")
        else:
            print(f"   ✗ Failed: {response.status_code} - {response.text}")
            return
        
        # Test 2: Get game state
        print("\n2. Getting game state...")
        response = session.get(f"{BASE_URL}/api/game_state")
        if response.status_code == 200:
            data = response.json()
            state = data['state']
            print(f"   ✓ Phase: {state['phase']}")
            print(f"   ✓ Players: {[p['name'] for p in state['players']]}")
            print(f"   ✓ Board hexes: {len(state['board']['hexes'])}")
        else:
            print(f"   ✗ Failed: {response.status_code} - {response.text}")
            return
        
        # Test 3: Execute an action
        print("\n3. Executing action...")
        if state['valid_actions']:
            action = state['valid_actions'][0]
            print(f"   Executing: {action['type']}")
            
            response = session.post(f"{BASE_URL}/api/action", json=action)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Action executed successfully")
                print(f"   ✓ Events generated: {len(data['events'])}")
                if data['events']:
                    print(f"   ✓ First event: {data['events'][0]['type']}")
            else:
                print(f"   ✗ Failed: {response.status_code} - {response.text}")
        else:
            print("   - No valid actions to test")
        
        # Test 4: Debug endpoint
        print("\n4. Testing debug endpoint...")
        response = session.get(f"{BASE_URL}/api/debug/state")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Turn: {data['turn_number']}")
            print(f"   ✓ Players resources: {[p['total_resources'] for p in data['players']]}")
        else:
            print(f"   ✗ Failed: {response.status_code} - {response.text}")
        
        print("\n✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 5001.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()