"""
Greedy player with smarter initial settlement placement.
"""

import random
from typing import List, Dict, Tuple

from engine.models.player import GreedyPlayer
from engine.models.enums import Action, ActionType
from engine.colonist_map import HEX_TO_CORNERS, get_adjacent_corners

# Type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.game import Game


class SmartGreedyPlayer(GreedyPlayer):
    """
    GreedyPlayer that makes smarter initial settlement decisions.
    
    During setup phase, evaluates settlements based on:
    - Resource diversity
    - Number probabilities (6/8 are best)
    - Total production value
    """
    
    # Dice probability for each number
    NUMBER_PROBABILITIES = {
        2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
        7: 6/36,  # Robber, but we still count it
        8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
    }
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Override decide to use smart logic for initial settlements."""
        # Check if this is an initial settlement decision
        initial_settlement_actions = [
            a for a in valid_actions 
            if a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT
        ]
        
        if initial_settlement_actions:
            # Use smart evaluation for initial settlements
            return self._choose_initial_settlement(game, initial_settlement_actions)
        
        # Otherwise use parent's greedy logic
        return super().decide(game, valid_actions)
    
    def _choose_initial_settlement(self, game: "Game", 
                                 settlement_actions: List[Action]) -> Action:
        """Choose the best initial settlement location."""
        best_score = -1
        best_actions = []
        
        for action in settlement_actions:
            corner = action.value
            score = self._evaluate_settlement_spot(game, corner)
            
            if score > best_score:
                best_score = score
                best_actions = [action]
            elif score == best_score:
                best_actions.append(action)
        
        # Among equally good spots, choose randomly
        return random.choice(best_actions)
    
    def _evaluate_settlement_spot(self, game: "Game", corner: int) -> float:
        """
        Evaluate a settlement spot based on resources and probabilities.
        
        Returns a score where higher is better.
        """
        score = 0.0
        resources_available = set()
        hex_resources = []  # (resource_type, number)
        
        # Find all hexes adjacent to this corner
        for hex_id, corners in HEX_TO_CORNERS.items():
            if corner in corners:
                hex_type = game.state.hex_types[hex_id]
                number = game.state.hex_numbers[hex_id]
                
                if hex_type > 0:  # Not desert
                    # Resource types: 1=wood, 2=brick, 3=sheep, 4=wheat, 5=ore
                    resource = hex_type - 1  # Convert to 0-indexed
                    resources_available.add(resource)
                    hex_resources.append((resource, number))
                    
                    # Add production value (probability * 36 for easier numbers)
                    if number in self.NUMBER_PROBABILITIES:
                        production = self.NUMBER_PROBABILITIES[number] * 36
                        score += production
        
        # Bonus for resource diversity
        diversity_bonus = len(resources_available) * 5
        score += diversity_bonus
        
        # Extra bonus for having brick (critical for roads)
        if 1 in resources_available:  # 1 = brick (0-indexed)
            score += 10
        
        # Extra bonus for having wood (also needed for roads/settlements)
        if 0 in resources_available:  # 0 = wood (0-indexed)
            score += 8
        
        # Penalty if missing critical resources
        if len(resources_available) < 2:
            score -= 20
        
        # Small bonus for 6s and 8s
        for resource, number in hex_resources:
            if number in [6, 8]:
                score += 3
        
        # Consider distance from other settlements (avoid clustering)
        # This is important for the second settlement
        occupied_corners = set(game.state.board.buildings.keys())
        if occupied_corners:
            min_distance = float('inf')
            for other_corner in occupied_corners:
                # Simple distance heuristic: check if they share adjacent corners
                if other_corner != corner:
                    adjacent1 = set(get_adjacent_corners(corner))
                    adjacent2 = set(get_adjacent_corners(other_corner))
                    if adjacent1 & adjacent2:
                        min_distance = 1
                    else:
                        min_distance = min(min_distance, 2)
            
            # Small penalty for being too close
            if min_distance == 1:
                score -= 5
        
        return score