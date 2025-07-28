"""
Adaptation of catanatron's minimax player with probability-aware search.
"""

import time
import random
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from math import inf

from engine.models.player import Player
from engine.models.enums import (
    Action, ActionType,
    SETTLEMENT, CITY, ROAD,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    PLAYER_0, PLAYER_1
)

# Type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.game import Game
    from engine.state import GameState


# Dice probabilities
DICE_PROBABILITIES = {
    2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
    7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
}

# Deterministic actions (no randomness)
DETERMINISTIC_ACTIONS = {
    ActionType.BUILD_SETTLEMENT,
    ActionType.BUILD_INITIAL_SETTLEMENT,
    ActionType.BUILD_ROAD,
    ActionType.BUILD_INITIAL_ROAD,
    ActionType.BUILD_CITY,
    ActionType.MARITIME_TRADE,
    ActionType.END_TURN,
    ActionType.DISCARD,
    ActionType.MOVE_ROBBER,
    ActionType.PLAY_KNIGHT_CARD,
    ActionType.PLAY_YEAR_OF_PLENTY,
    ActionType.PLAY_MONOPOLY,
    ActionType.PLAY_ROAD_BUILDING,
}

# Default weights from catanatron
DEFAULT_WEIGHTS = {
    # Where to place. Note winning is best at all costs
    "public_vps": 3e14,
    "production": 1e8,
    "enemy_production": -1e8,
    "num_tiles": 1,
    # Towards where to expand and when
    "reachable_production_0": 0,
    "reachable_production_1": 1e4,
    "buildable_nodes": 1e3,
    "longest_road": 10,
    # Hand, when to hold and when to use.
    "hand_synergy": 1e2,
    "hand_resources": 1,
    "discard_penalty": -5,
    "hand_devs": 10,
    "army_size": 10.1,
}


class CatanatronMinimaxPlayer(Player):
    """
    Minimax player adapted from catanatron with probability-aware search.
    
    Key features:
    - Considers dice roll probabilities
    - Sophisticated evaluation function
    - Action pruning for efficiency
    - Configurable search depth and time limit
    """
    
    def __init__(self, player_id: int, name: str = None,
                 max_depth: int = 3, time_limit: float = 20.0,
                 pruning: bool = True, weights: dict = None):
        """Initialize the player."""
        super().__init__(player_id, name or f"CatanatronMM-{player_id}")
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.pruning = pruning
        self.weights = weights or DEFAULT_WEIGHTS
        self.start_time = 0
        self.nodes_evaluated = 0
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose the best action using probability-aware minimax search."""
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        self.start_time = time.time()
        self.nodes_evaluated = 0
        
        # Get actions to consider (with pruning if enabled)
        actions = self._get_pruned_actions(game, valid_actions) if self.pruning else valid_actions
        
        best_action = actions[0]
        best_value = -inf
        
        # Evaluate each action considering probabilities
        for action in actions:
            # Get all possible outcomes with probabilities
            outcomes = self._expand_action(game, action)
            
            # Calculate expected value
            expected_value = 0
            for outcome_game, probability in outcomes:
                value = self._alphabeta(
                    outcome_game,
                    self.max_depth - 1,
                    -inf,
                    inf,
                    outcome_game.state.current_player != self.player_id
                )
                expected_value += probability * value
            
            if expected_value > best_value:
                best_value = expected_value
                best_action = action
            
            # Check time limit
            if time.time() - self.start_time > self.time_limit:
                break
        
        return best_action
    
    def _alphabeta(self, game: "Game", depth: int, alpha: float, beta: float,
                   maximizing: bool) -> float:
        """Alpha-beta search with probability consideration."""
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if game.is_over():
            winner = game.state.get_winner()
            if winner == self.player_id:
                # Return value higher than any possible evaluation
                return 1e16  # 10x higher than max VP evaluation
            elif winner is not None:
                return -1e16
            else:
                return 0
        
        if depth == 0 or time.time() - self.start_time > self.time_limit:
            return self._evaluate_state(game)
        
        # Get actions
        valid_actions = game.get_valid_actions()
        actions = self._get_pruned_actions(game, valid_actions) if self.pruning else valid_actions
        
        if maximizing:
            max_eval = -inf
            for action in actions:
                outcomes = self._expand_action(game, action)
                expected_value = 0
                
                for outcome_game, probability in outcomes:
                    value = self._alphabeta(
                        outcome_game,
                        depth - 1,
                        alpha,
                        beta,
                        outcome_game.state.current_player == self.player_id
                    )
                    expected_value += probability * value
                
                max_eval = max(max_eval, expected_value)
                alpha = max(alpha, expected_value)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            min_eval = inf
            for action in actions:
                outcomes = self._expand_action(game, action)
                expected_value = 0
                
                for outcome_game, probability in outcomes:
                    value = self._alphabeta(
                        outcome_game,
                        depth - 1,
                        alpha,
                        beta,
                        outcome_game.state.current_player == self.player_id
                    )
                    expected_value += probability * value
                
                min_eval = min(min_eval, expected_value)
                beta = min(beta, expected_value)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def _expand_action(self, game: "Game", action: Action) -> List[Tuple["Game", float]]:
        """
        Expand an action into all possible outcomes with probabilities.
        
        Returns:
            List of (game_copy, probability) tuples
        """
        if action.action_type in DETERMINISTIC_ACTIONS:
            # Deterministic action - single outcome with probability 1
            game_copy = game.copy()
            try:
                game_copy.execute(action, validate=False)
                return [(game_copy, 1.0)]
            except:
                return []  # Invalid action
        
        elif action.action_type == ActionType.ROLL:
            # Dice roll - for now treat as deterministic since we can't force specific rolls
            # A full implementation would need engine support for hypothetical rolls
            game_copy = game.copy()
            try:
                game_copy.execute(action, validate=False)
                return [(game_copy, 1.0)]
            except:
                return []
        
        elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
            # Development card - consider deck composition
            # For simplicity, assume equal probability for now
            game_copy = game.copy()
            try:
                game_copy.execute(action, validate=False)
                return [(game_copy, 1.0)]
            except:
                return []
        
        else:
            # Unknown action type - treat as deterministic
            game_copy = game.copy()
            try:
                game_copy.execute(action, validate=False)
                return [(game_copy, 1.0)]
            except:
                return []
    
    def _get_pruned_actions(self, game: "Game", actions: List[Action]) -> List[Action]:
        """Prune obviously bad actions to improve search efficiency."""
        if not self.pruning:
            return actions
        
        pruned = []
        action_types = set(a.action_type for a in actions)
        
        for action in actions:
            # Skip 1-tile settlements in initial placement
            if (action.action_type == ActionType.BUILD_INITIAL_SETTLEMENT and
                len(self._get_adjacent_hexes(action.value)) == 1):
                continue
            
            # Skip 4:1 trades if we have 3:1 ports
            if action.action_type == ActionType.MARITIME_TRADE:
                give_res, give_amount, get_res = action.value
                if give_amount == 4 and self._has_3_to_1_port(game.state):
                    continue
            
            # Skip ending turn if we can build something valuable
            if action.action_type == ActionType.END_TURN:
                player = game.state.players[game.state.current_player]
                can_build_city = (
                    ActionType.BUILD_CITY in action_types and
                    player.cities_left > 0
                )
                can_build_settlement = (
                    ActionType.BUILD_SETTLEMENT in action_types and
                    player.settlements_left > 0
                )
                if can_build_city or can_build_settlement:
                    continue
            
            pruned.append(action)
        
        # If we pruned everything, return original actions
        return pruned if pruned else actions
    
    def _evaluate_state(self, game: "Game") -> float:
        """
        Evaluate game state using catanatron's sophisticated features.
        """
        state = game.state
        my_player = state.players[self.player_id]
        opp_player = state.players[1 - self.player_id]
        
        # Victory points (most important) - use only PUBLIC vps
        vp_score = my_player.public_vps * self.weights["public_vps"]
        
        # Production calculation
        my_production = self._calculate_production(state, self.player_id)
        opp_production = self._calculate_production(state, 1 - self.player_id)
        production_score = (
            my_production * self.weights["production"] +
            opp_production * self.weights["enemy_production"]
        )
        
        # Reachable production (expansion potential)
        reachable_0 = self._calculate_reachable_production(state, self.player_id, 0)
        reachable_1 = self._calculate_reachable_production(state, self.player_id, 1)
        reachable_score = (
            reachable_0 * self.weights["reachable_production_0"] +
            reachable_1 * self.weights["reachable_production_1"]
        )
        
        # Building potential
        buildable_nodes = self._count_buildable_nodes(state, self.player_id)
        buildable_score = buildable_nodes * self.weights["buildable_nodes"]
        
        # Hand synergy (how close to building)
        hand_synergy = self._calculate_hand_synergy(my_player)
        hand_score = (
            hand_synergy * self.weights["hand_synergy"] +
            sum(my_player.resources) * self.weights["hand_resources"]
        )
        
        # Discard penalty
        num_cards = sum(my_player.resources)
        discard_penalty = self.weights["discard_penalty"] if num_cards > 7 else 0
        
        # Development cards and army
        dev_score = (
            my_player.total_dev_cards() * self.weights["hand_devs"] +
            my_player.knights_played * self.weights["army_size"]
        )
        
        # Longest road
        road_length = self._get_longest_road_length(state, self.player_id)
        road_score = road_length * self.weights["longest_road"]
        
        # Number of tiles controlled (blockability)
        num_tiles = self._count_controlled_tiles(state, self.player_id)
        tile_score = num_tiles * self.weights["num_tiles"]
        
        # Combine all scores
        total_score = (
            vp_score + production_score + reachable_score + buildable_score +
            hand_score + discard_penalty + dev_score + road_score + tile_score
        )
        
        return total_score
    
    def _calculate_production(self, state: "GameState", player_id: int) -> float:
        """Calculate total production value for a player."""
        from engine.colonist_map import HEX_TO_CORNERS
        
        production = 0
        buildings = state.board.get_player_buildings(player_id)
        
        for corner in buildings[SETTLEMENT]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    # Skip if robber is on this hex
                    if state.board.robber_hex == hex_id:
                        continue
                    
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:  # Not desert
                        number = state.hex_numbers[hex_id]
                        if number in DICE_PROBABILITIES:
                            production += DICE_PROBABILITIES[number] * 36
        
        # Cities produce double
        for corner in buildings[CITY]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    if state.board.robber_hex == hex_id:
                        continue
                    
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:
                        number = state.hex_numbers[hex_id]
                        if number in DICE_PROBABILITIES:
                            production += DICE_PROBABILITIES[number] * 36 * 2
        
        # Add variety bonus (4 points per resource type)
        resource_types = set()
        for corner in buildings[SETTLEMENT] + buildings[CITY]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:
                        resource_types.add(hex_type)
        
        production += len(resource_types) * 4
        
        return production
    
    def _calculate_reachable_production(self, state: "GameState", player_id: int, 
                                      distance: int) -> float:
        """Calculate production reachable within N roads."""
        # Simplified version - just count buildable spots
        if distance == 0:
            return len(state.board.get_player_buildings(player_id)[SETTLEMENT])
        else:
            return self._count_buildable_nodes(state, player_id)
    
    def _calculate_hand_synergy(self, player_state) -> float:
        """Calculate how close the hand is to building something useful."""
        # Distance to city
        distance_to_city = (
            max(2 - player_state.resources[WHEAT], 0) +
            max(3 - player_state.resources[ORE], 0)
        ) / 5.0
        
        # Distance to settlement
        distance_to_settlement = (
            max(1 - player_state.resources[WOOD], 0) +
            max(1 - player_state.resources[BRICK], 0) +
            max(1 - player_state.resources[SHEEP], 0) +
            max(1 - player_state.resources[WHEAT], 0)
        ) / 4.0
        
        # Higher synergy = closer to building
        synergy = (2 - distance_to_city - distance_to_settlement) / 2
        return max(0, synergy)
    
    def _count_buildable_nodes(self, state: "GameState", player_id: int) -> int:
        """Count corners where player could build settlements."""
        from engine.colonist_map import can_build_settlement, get_connected_edges
        
        count = 0
        occupied = set(state.board.buildings.keys())
        
        for corner in range(54):
            # Check basic settlement rules
            if can_build_settlement(corner, occupied):
                # Check if connected by road
                for edge in get_connected_edges(corner):
                    if edge in state.board.roads and state.board.roads[edge] == player_id:
                        count += 1
                        break
        return count
    
    def _get_longest_road_length(self, state: "GameState", player_id: int) -> int:
        """Get player's longest road length."""
        # This would require implementing road graph traversal
        # For now, return road count as approximation
        return len([e for e, p in state.board.roads.items() if p == player_id])
    
    def _count_controlled_tiles(self, state: "GameState", player_id: int) -> int:
        """Count unique hexes where player has buildings."""
        from engine.colonist_map import HEX_TO_CORNERS
        
        controlled_hexes = set()
        buildings = state.board.get_player_buildings(player_id)
        
        for corner in buildings[SETTLEMENT] + buildings[CITY]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    controlled_hexes.add(hex_id)
        
        return len(controlled_hexes)
    
    def _get_adjacent_hexes(self, corner: int) -> List[int]:
        """Get hexes adjacent to a corner."""
        from engine.colonist_map import HEX_TO_CORNERS
        
        adjacent = []
        for hex_id, corners in HEX_TO_CORNERS.items():
            if corner in corners:
                adjacent.append(hex_id)
        return adjacent
    
    def _has_3_to_1_port(self, state: "GameState") -> bool:
        """Check if player has access to 3:1 port."""
        from engine.colonist_map import PORT_CORNERS
        from engine.models.enums import PORT_TYPE_3_1
        
        buildings = state.board.get_player_buildings(self.player_id)
        for corner in buildings[SETTLEMENT] + buildings[CITY]:
            if corner in PORT_CORNERS and PORT_CORNERS[corner] == PORT_TYPE_3_1:
                return True
        return False