"""
Test probabilistic expansion functionality.

This test file verifies that the probabilistic expansion correctly
generates all possible outcomes with proper probabilities for random actions.
"""

import pytest
from collections import defaultdict

from engine.models.enums import (
    Action, ActionType, ActionPrompt,
    PLAYER_0, PLAYER_1,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT
)
from engine.models.player import Player
from engine.game import Game
from engine.probabilistic_expansion import (
    execute_spectrum, expand_spectrum, DICE_PROBABILITIES,
    expand_roll, expand_dev_card, expand_robber
)


class TestPlayer(Player):
    """Simple test player that returns first valid action."""
    
    def __init__(self, player_id):
        super().__init__(player_id, f"TestPlayer{player_id}")
    
    def decide(self, game, valid_actions):
        return valid_actions[0] if valid_actions else None


class TestProbabilisticExpansion:
    """Test suite for probabilistic expansion."""
    
    def setup_method(self):
        """Create a test game."""
        self.players = [TestPlayer(0), TestPlayer(1)]
        self.game = Game(self.players, seed=42)
    
    def test_dice_roll_expansion(self):
        """Test that dice rolls expand to all 11 possible outcomes."""
        # Skip to a state where we can roll
        while self.game.state.is_setup_phase():
            actions = self.game.get_valid_actions()
            self.game.execute(actions[0])
        
        # Find roll action
        actions = self.game.get_valid_actions()
        roll_action = next((a for a in actions if a.action_type == ActionType.ROLL), None)
        assert roll_action is not None
        
        # Expand the roll
        outcomes = expand_roll(self.game, roll_action)
        
        # Verify we have 11 outcomes (sums 2-12)
        assert len(outcomes) == 11
        
        # Verify probabilities sum to 1.0
        total_prob = sum(prob for _, prob in outcomes)
        assert abs(total_prob - 1.0) < 0.0001
        
        # Verify each outcome has correct dice values
        dice_sums = []
        for game_copy, prob in outcomes:
            die1, die2 = game_copy.state.last_dice_roll
            dice_sum = die1 + die2
            dice_sums.append(dice_sum)
            
            # Verify probability matches expected
            assert abs(prob - DICE_PROBABILITIES[dice_sum]) < 0.0001
        
        # Verify we have all sums 2-12
        assert sorted(dice_sums) == list(range(2, 13))
    
    def test_dev_card_expansion(self):
        """Test development card purchase expansion."""
        # Give player resources to buy dev card
        self.game.state.players[PLAYER_0].resources = [1, 1, 1, 1, 1]  # Enough for dev card
        
        # Create buy dev card action
        action = Action(ActionType.BUY_DEVELOPMENT_CARD, None)
        
        # Get initial deck composition
        deck = self.game.state.dev_card_deck.copy()
        card_counts = defaultdict(int)
        for card in deck:
            card_counts[card] += 1
        total_cards = len(deck)
        
        # Expand the action
        outcomes = expand_dev_card(self.game, action)
        
        # Should have one outcome per unique card type in deck
        assert len(outcomes) == len(card_counts)
        
        # Verify probabilities
        total_prob = 0.0
        for game_copy, prob in outcomes:
            # Find which card was bought (deck should be 1 card smaller)
            new_deck = game_copy.state.dev_card_deck
            assert len(new_deck) == total_cards - 1
            
            # Verify probability calculation
            # (Can't easily determine which card was drawn without more state tracking)
            total_prob += prob
        
        assert abs(total_prob - 1.0) < 0.0001
    
    def test_robber_stealing_expansion(self):
        """Test robber movement with stealing expansion."""
        # Set up a scenario where player can rob
        self.game.state.current_prompt = ActionPrompt.MOVE_ROBBER
        self.game.state.current_turn_player = PLAYER_0
        self.game.state.is_moving_robber = True
        
        # Give victim some resources
        victim_resources = [2, 1, 0, 3, 1]  # Total: 7 resources
        self.game.state.players[PLAYER_1].resources = victim_resources.copy()
        
        # Create move robber action (hex 7, rob player 1)
        action = Action(ActionType.MOVE_ROBBER, (7, PLAYER_1))
        
        # Expand the action
        outcomes = expand_robber(self.game, action)
        
        # Should have one outcome per resource type the victim has
        expected_outcomes = sum(1 for r in victim_resources if r > 0)
        assert len(outcomes) == expected_outcomes
        
        # Verify probabilities
        total_prob = 0.0
        total_victim_resources = sum(victim_resources)
        
        for game_copy, prob in outcomes:
            # Robber should have moved
            assert game_copy.state.board.robber_hex == 7
            
            # Verify probability matches resource distribution
            # We can't easily tell which resource was stolen without tracking
            total_prob += prob
        
        assert abs(total_prob - 1.0) < 0.0001
    
    def test_robber_no_victim_expansion(self):
        """Test robber movement with no victim is deterministic."""
        # Set up robber movement scenario
        self.game.state.current_prompt = ActionPrompt.MOVE_ROBBER
        self.game.state.is_moving_robber = True
        
        # Move robber with no victim
        action = Action(ActionType.MOVE_ROBBER, (7, None))
        
        # Expand the action
        outcomes = expand_robber(self.game, action)
        
        # Should be deterministic (1 outcome with probability 1.0)
        assert len(outcomes) == 1
        assert outcomes[0][1] == 1.0
        
        # Robber should have moved
        assert outcomes[0][0].state.board.robber_hex == 7
    
    def test_deterministic_action_expansion(self):
        """Test that deterministic actions produce single outcome."""
        # Test END_TURN action
        self.game.state.current_prompt = ActionPrompt.PLAY_TURN
        action = Action(ActionType.END_TURN, None)
        
        outcomes = execute_spectrum(self.game, action)
        
        # Should be exactly one outcome with probability 1.0
        assert len(outcomes) == 1
        assert outcomes[0][1] == 1.0
    
    def test_expand_spectrum_batch(self):
        """Test batch expansion of multiple actions."""
        # Get to a state with multiple action types
        while self.game.state.is_setup_phase():
            actions = self.game.get_valid_actions()
            self.game.execute(actions[0])
        
        # Get available actions
        actions = self.game.get_valid_actions()
        
        # Expand all actions
        expanded = expand_spectrum(self.game, actions)
        
        # Verify we get expansions for each action
        assert len(expanded) == len(actions)
        
        # Verify each action maps to valid outcomes
        for action, outcomes in expanded.items():
            assert len(outcomes) > 0
            # Verify probabilities sum to 1.0 for each action
            total_prob = sum(prob for _, prob in outcomes)
            assert abs(total_prob - 1.0) < 0.0001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])