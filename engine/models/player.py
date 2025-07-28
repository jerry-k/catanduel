"""
Player interface for CatanDuel.

This is almost identical to catanatron's player.py, just simplified
for 2 players and without the Color enum (we use 0/1 internally).
"""

import random
from typing import TYPE_CHECKING, List

from .enums import Action

if TYPE_CHECKING:
    # Avoid circular imports
    from ..game import Game


class Player:
    """
    Base class for all players (human or AI).
    
    The main interface is the decide() method which takes the current
    game state and returns an action to play.
    """
    
    def __init__(self, player_id: int, name: str = None):
        """
        Initialize a player.
        
        Args:
            player_id: 0 or 1
            name: Optional player name for display
        """
        if player_id not in (0, 1):
            raise ValueError(f"Player ID must be 0 or 1, got {player_id}")
        
        self.player_id = player_id
        self.name = name or f"Player {player_id}"
        
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """
        Choose an action from the list of valid actions.
        
        This is the main method that AI players override.
        
        Args:
            game: Current game state (read-only)
            valid_actions: List of legal actions to choose from
            
        Returns:
            The chosen action
        """
        raise NotImplementedError("Subclasses must implement decide()")
    
    def reset(self):
        """
        Reset any internal state between games.
        
        Most players don't need this, but some AI players might
        cache information that needs to be cleared.
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.player_id}, '{self.name}')"
    
    def __str__(self):
        return self.name


class RandomPlayer(Player):
    """AI player that chooses actions uniformly at random."""
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose a random valid action."""
        if not valid_actions:
            raise ValueError(f"No valid actions available for {self.name}")
        return random.choice(valid_actions)


class HumanPlayer(Player):
    """
    Human player that chooses actions via user input.
    
    This is primarily for testing/debugging. A real UI would
    handle human input differently.
    """
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """
        Display valid actions and prompt user to choose one.
        
        Note: This is a simple text-based implementation.
        A real game would have a proper UI.
        """
        print(f"\n{self.name}'s turn. Valid actions:")
        
        # Group actions by type for better display
        actions_by_type = {}
        for i, action in enumerate(valid_actions):
            action_type = action.action_type.value
            if action_type not in actions_by_type:
                actions_by_type[action_type] = []
            actions_by_type[action_type].append((i, action))
        
        # Display grouped actions
        for action_type, actions in actions_by_type.items():
            print(f"\n{action_type}:")
            for i, action in actions:
                if action.value is None:
                    print(f"  [{i}] {action_type}")
                else:
                    print(f"  [{i}] {action_type}: {action.value}")
        
        # Get user choice
        while True:
            try:
                choice = input("\nEnter action number: ")
                index = int(choice)
                if 0 <= index < len(valid_actions):
                    return valid_actions[index]
                else:
                    print(f"Please enter a number between 0 and {len(valid_actions)-1}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nGame interrupted")
                raise


class GreedyPlayer(Player):
    """
    Simple AI that prioritizes certain actions over others.
    
    Priority order:
    1. Build city (if possible)
    2. Build settlement (if possible) 
    3. Buy development card
    4. Build road
    5. Play development cards
    6. Trade at ports
    7. Everything else (roll, end turn, etc.)
    """
    
    # Action priorities (lower number = higher priority)
    ACTION_PRIORITIES = {
        "BUILD_CITY": 1,
        "BUILD_SETTLEMENT": 2,
        "BUILD_INITIAL_SETTLEMENT": 2,  # Same priority as regular settlement
        "BUY_DEVELOPMENT_CARD": 3,
        "BUILD_ROAD": 4,
        "BUILD_INITIAL_ROAD": 4,  # Same priority as regular road
        "PLAY_KNIGHT_CARD": 5,
        "PLAY_YEAR_OF_PLENTY": 5,
        "PLAY_MONOPOLY": 5,
        "PLAY_ROAD_BUILDING": 5,
        "MARITIME_TRADE": 6,
        "ROLL": 7,
        "END_TURN": 8,
        "MOVE_ROBBER": 9,
        "DISCARD": 9,
    }
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose the highest priority action available."""
        # Sort actions by priority
        def priority(action):
            return self.ACTION_PRIORITIES.get(
                action.action_type.value, 
                10  # Default priority for unknown actions
            )
        
        if not valid_actions:
            raise ValueError(f"No valid actions available for {self.name}")
            
        sorted_actions = sorted(valid_actions, key=priority)
        
        # Among actions with the same priority, choose randomly
        best_priority = priority(sorted_actions[0])
        best_actions = [a for a in sorted_actions if priority(a) == best_priority]
        
        return random.choice(best_actions)