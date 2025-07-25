"""
Minimax players with smarter initial settlement placement.
"""

from typing import List
from engine.models.minimax_player import MinimaxPlayer, SimpleMinimaxPlayer
from engine.models.smart_greedy_player import SmartGreedyPlayer
from engine.models.enums import Action, ActionType

# Type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.game import Game


class SmartMinimaxPlayer(MinimaxPlayer, SmartGreedyPlayer):
    """
    MinimaxPlayer that uses smart initial settlement placement.
    
    Combines MinimaxPlayer's search with SmartGreedyPlayer's
    initial settlement evaluation.
    """
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Use smart placement for initial settlements, minimax for rest."""
        # Check if this is an initial settlement decision
        initial_settlement_actions = [
            a for a in valid_actions 
            if a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT
        ]
        
        if initial_settlement_actions:
            # Use SmartGreedyPlayer's evaluation
            return self._choose_initial_settlement(game, initial_settlement_actions)
        
        # Otherwise use MinimaxPlayer's search
        return MinimaxPlayer.decide(self, game, valid_actions)


class SmartSimpleMinimaxPlayer(SimpleMinimaxPlayer, SmartGreedyPlayer):
    """
    SimpleMinimaxPlayer that uses smart initial settlement placement.
    """
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Use smart placement for initial settlements, simple minimax for rest."""
        # Check if this is an initial settlement decision
        initial_settlement_actions = [
            a for a in valid_actions 
            if a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT
        ]
        
        if initial_settlement_actions:
            # Use SmartGreedyPlayer's evaluation
            return self._choose_initial_settlement(game, initial_settlement_actions)
        
        # Otherwise use SimpleMinimaxPlayer's search
        return SimpleMinimaxPlayer.decide(self, game, valid_actions)