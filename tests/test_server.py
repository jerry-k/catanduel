"""
Test Flask server functionality.

Tests API endpoints and server responses.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
from ui.server import app


class TestFlaskServer(unittest.TestCase):
    """Test cases for Flask server."""
    
    def setUp(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up."""
        self.app_context.pop()
    
    def test_index_route(self):
        """Test main page loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CatanDuel', response.data)
    
    def test_new_game_endpoint(self):
        """Test creating new game."""
        config = {
            'player1': {'type': 'human', 'name': 'Test Player'},
            'player2': {'type': 'random', 'name': 'AI Player'}
        }
        
        response = self.client.post('/api/new_game',
                                  json=config,
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('game_id', data)
        self.assertIn('state', data)
        self.assertEqual(data['state']['phase'], 'setup')
        self.assertEqual(len(data['state']['players']), 2)
    
    def test_new_game_invalid_request(self):
        """Test invalid new game request."""
        response = self.client.post('/api/new_game',
                                  json={},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_state_no_game(self):
        """Test getting state without active game."""
        response = self.client.get('/api/game_state')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_game_flow(self):
        """Test basic game flow."""
        # Create game
        config = {
            'player1': {'type': 'human', 'name': 'Human'},
            'player2': {'type': 'random', 'name': 'AI'}
        }
        
        with self.client.session_transaction() as sess:
            pass  # This ensures we have a session
        
        response = self.client.post('/api/new_game',
                                  json=config,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Get state
        response = self.client.get('/api/game_state')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        state = data['state']
        
        # Should be in setup phase
        self.assertEqual(state['phase'], 'setup')
        self.assertTrue(len(state['valid_actions']) > 0)
        
        # Execute first valid action
        if state['valid_actions']:
            action = state['valid_actions'][0]
            
            response = self.client.post('/api/action',
                                      json=action,
                                      content_type='application/json')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertIn('state', data)
                self.assertIn('events', data)
    
    def test_invalid_action(self):
        """Test executing invalid action."""
        # Create game first
        config = {
            'player1': {'type': 'human', 'name': 'Test'},
            'player2': {'type': 'human', 'name': 'Test2'}
        }
        
        with self.client.session_transaction() as sess:
            pass
        
        self.client.post('/api/new_game',
                        json=config,
                        content_type='application/json')
        
        # Try invalid action
        invalid_action = {
            'type': 'BUILD_CITY',
            'data': {'corner': 0}
        }
        
        response = self.client.post('/api/action',
                                  json=invalid_action,
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_debug_endpoints(self):
        """Test debug endpoints."""
        # Create game first
        config = {
            'player1': {'type': 'human', 'name': 'Test'},
            'player2': {'type': 'human', 'name': 'Test2'}
        }
        
        with self.client.session_transaction() as sess:
            pass
        
        self.client.post('/api/new_game',
                        json=config,
                        content_type='application/json')
        
        # Test debug state
        response = self.client.get('/api/debug/state')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('turn_number', data)
        self.assertIn('players', data)
        
        # Test games list
        response = self.client.get('/api/games')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('games', data)
        self.assertIn('current', data)


if __name__ == '__main__':
    unittest.main()