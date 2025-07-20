"""
Unit tests for UI adapter.

Tests state translation, action translation, and event generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from ui.adapter import CatanDuelAdapter
from ui.adapter_types import (
    UIActionType, UIAction, UIPhase, UIResources, UIDevCards,
    RESOURCE_NAMES, HEX_TYPE_TO_UI
)
from engine.models.enums import (
    Action, ActionType,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    SETTLEMENT, CITY,
    HEX_TYPE_DESERT, HEX_TYPE_WOOD, HEX_TYPE_BRICK
)


class TestUIAdapter(unittest.TestCase):
    """Test cases for CatanDuel UI adapter."""
    
    def setUp(self):
        """Set up test adapter."""
        self.adapter = CatanDuelAdapter()
    
    def test_new_game_initialization(self):
        """Test creating a new game."""
        player1 = {'type': 'human', 'name': 'Alice'}
        player2 = {'type': 'random', 'name': 'Bob (AI)'}
        
        ui_state = self.adapter.new_game(player1, player2, seed=42)
        
        # Check basic state
        self.assertEqual(ui_state.phase, UIPhase.SETUP)
        self.assertEqual(ui_state.current_player, 0)
        self.assertEqual(len(ui_state.players), 2)
        
        # Check player setup
        self.assertEqual(ui_state.players[0].name, 'Alice')
        self.assertEqual(ui_state.players[1].name, 'Bob (AI)')
        self.assertEqual(ui_state.players[0].color, 'red')
        self.assertEqual(ui_state.players[1].color, 'blue')
        
        # Check initial resources (should be empty)
        for player in ui_state.players:
            self.assertEqual(player.resources.total(), 0)
            self.assertEqual(player.dev_cards.total(), 0)
        
        # Check board setup
        self.assertEqual(len(ui_state.board.hexes), 19)
        self.assertEqual(len(ui_state.board.buildings), 0)  # No buildings yet
        
        # Should have valid actions for setup
        self.assertGreater(len(ui_state.valid_actions), 0)
        self.assertTrue(all(
            a.type == UIActionType.BUILD_INITIAL_SETTLEMENT 
            for a in ui_state.valid_actions
        ))
    
    def test_resource_translation(self):
        """Test resource array to object conversion."""
        # From array
        resources = UIResources.from_array([1, 2, 3, 4, 5])
        self.assertEqual(resources.wood, 1)
        self.assertEqual(resources.brick, 2)
        self.assertEqual(resources.sheep, 3)
        self.assertEqual(resources.wheat, 4)
        self.assertEqual(resources.ore, 5)
        self.assertEqual(resources.total(), 15)
        
        # To array
        arr = resources.to_array()
        self.assertEqual(arr, [1, 2, 3, 4, 5])
    
    def test_dev_card_translation(self):
        """Test dev card array to object conversion."""
        # From array [knight, year_of_plenty, monopoly, road_building, victory_point]
        dev_cards = UIDevCards.from_array([2, 1, 0, 1, 3])
        self.assertEqual(dev_cards.knight, 2)
        self.assertEqual(dev_cards.year_of_plenty, 1)
        self.assertEqual(dev_cards.monopoly, 0)
        self.assertEqual(dev_cards.road_building, 1)
        self.assertEqual(dev_cards.victory_point, 3)
        self.assertEqual(dev_cards.total(), 7)
    
    def test_action_translation_build_settlement(self):
        """Test translating build settlement action."""
        # UI to Engine
        ui_action = UIAction(
            type=UIActionType.BUILD_SETTLEMENT,
            data={'corner': 23}
        )
        engine_action = self.adapter.translate_action(ui_action)
        
        self.assertEqual(engine_action.action_type, ActionType.BUILD_SETTLEMENT)
        self.assertEqual(engine_action.value, 23)
        
        # Engine to UI
        engine_action = Action(ActionType.BUILD_SETTLEMENT, 23)
        ui_action = self.adapter._translate_single_action(engine_action)
        
        self.assertEqual(ui_action.type, UIActionType.BUILD_SETTLEMENT)
        self.assertEqual(ui_action.data['corner'], 23)
    
    def test_action_translation_move_robber(self):
        """Test translating robber movement action."""
        # UI to Engine
        ui_action = UIAction(
            type=UIActionType.MOVE_ROBBER,
            data={'hex': 7, 'victim': 1}
        )
        engine_action = self.adapter.translate_action(ui_action)
        
        self.assertEqual(engine_action.action_type, ActionType.MOVE_ROBBER)
        self.assertEqual(engine_action.value, (7, 1))
        
        # Without victim
        ui_action = UIAction(
            type=UIActionType.MOVE_ROBBER,
            data={'hex': 7}
        )
        engine_action = self.adapter.translate_action(ui_action)
        self.assertEqual(engine_action.value, (7, None))
    
    def test_action_translation_discard(self):
        """Test translating discard action."""
        # UI to Engine
        ui_action = UIAction(
            type=UIActionType.DISCARD,
            data={'resources': {
                'wood': 2,
                'brick': 1,
                'sheep': 0,
                'wheat': 0,
                'ore': 1
            }}
        )
        engine_action = self.adapter.translate_action(ui_action)
        
        self.assertEqual(engine_action.action_type, ActionType.DISCARD)
        self.assertEqual(engine_action.value, [2, 1, 0, 0, 1])
    
    def test_action_translation_maritime_trade(self):
        """Test translating maritime trade action."""
        # UI to Engine
        ui_action = UIAction(
            type=UIActionType.MARITIME_TRADE,
            data={
                'give_resource': 'wood',
                'give_amount': 4,
                'get_resource': 'brick'
            }
        )
        engine_action = self.adapter.translate_action(ui_action)
        
        self.assertEqual(engine_action.action_type, ActionType.MARITIME_TRADE)
        self.assertEqual(engine_action.value, (WOOD, 4, BRICK))
    
    def test_action_translation_year_of_plenty(self):
        """Test translating year of plenty action."""
        # UI to Engine
        ui_action = UIAction(
            type=UIActionType.PLAY_YEAR_OF_PLENTY,
            data={'resource1': 'wheat', 'resource2': 'ore'}
        )
        engine_action = self.adapter.translate_action(ui_action)
        
        self.assertEqual(engine_action.action_type, ActionType.PLAY_YEAR_OF_PLENTY)
        self.assertEqual(engine_action.value, (WHEAT, ORE))
    
    def test_hex_type_mapping(self):
        """Test hex type conversions."""
        # Engine to UI
        self.assertEqual(HEX_TYPE_TO_UI[HEX_TYPE_DESERT], "desert")
        self.assertEqual(HEX_TYPE_TO_UI[HEX_TYPE_WOOD], "forest")
        self.assertEqual(HEX_TYPE_TO_UI[HEX_TYPE_BRICK], "hills")
        
        # Check all resource names
        self.assertEqual(RESOURCE_NAMES[WOOD], "wood")
        self.assertEqual(RESOURCE_NAMES[BRICK], "brick")
        self.assertEqual(RESOURCE_NAMES[SHEEP], "sheep")
        self.assertEqual(RESOURCE_NAMES[WHEAT], "wheat")
        self.assertEqual(RESOURCE_NAMES[ORE], "ore")
    
    def test_game_state_serialization(self):
        """Test converting game state to dictionary."""
        player1 = {'type': 'human', 'name': 'Test'}
        player2 = {'type': 'human', 'name': 'Test2'}
        
        ui_state = self.adapter.new_game(player1, player2, seed=42)
        state_dict = ui_state.to_dict()
        
        # Check structure
        self.assertIn('phase', state_dict)
        self.assertIn('current_player', state_dict)
        self.assertIn('board', state_dict)
        self.assertIn('players', state_dict)
        self.assertIn('valid_actions', state_dict)
        
        # Check board structure
        self.assertIn('hexes', state_dict['board'])
        self.assertIn('buildings', state_dict['board'])
        self.assertIn('ports', state_dict['board'])
        
        # Check player structure
        player = state_dict['players'][0]
        self.assertIn('resources', player)
        self.assertIn('dev_cards', player)
        self.assertIn('public_vps', player)
    
    def test_phase_detection(self):
        """Test game phase detection."""
        player1 = {'type': 'human', 'name': 'Test'}
        player2 = {'type': 'human', 'name': 'Test2'}
        
        ui_state = self.adapter.new_game(player1, player2, seed=42)
        
        # Should start in setup
        self.assertEqual(ui_state.phase, UIPhase.SETUP)
        
        # After setup (we'd need to play through setup to test other phases)
        # This would require executing actions, which we'll do in integration tests
    
    def test_execute_action_invalid(self):
        """Test executing invalid action."""
        player1 = {'type': 'human', 'name': 'Test'}
        player2 = {'type': 'human', 'name': 'Test2'}
        
        self.adapter.new_game(player1, player2, seed=42)
        
        # Try to build a city in setup phase (invalid)
        ui_action = UIAction(
            type=UIActionType.BUILD_CITY,
            data={'corner': 0}
        )
        
        with self.assertRaises(ValueError):
            self.adapter.execute_action(ui_action)
    
    def test_ai_action_detection(self):
        """Test AI action detection."""
        player1 = {'type': 'human', 'name': 'Human'}
        player2 = {'type': 'random', 'name': 'AI'}
        
        ui_state = self.adapter.new_game(player1, player2, seed=42)
        
        # Human turn - no AI action
        self.assertIsNone(self.adapter.get_ai_action())
        
        # We'd need to advance to AI turn to test positive case


if __name__ == '__main__':
    unittest.main()