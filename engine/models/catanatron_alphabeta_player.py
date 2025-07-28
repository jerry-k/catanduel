"""
Accurate implementation of catanatron's AlphaBetaPlayer.
Matches the original as closely as possible while working with our engine.
"""

import time
import random
from typing import List, Dict, Tuple, Optional, Set
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
from engine.probabilistic_expansion import execute_spectrum

# Type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.game import Game
    from engine.state import GameState


# Constants from catanatron
ALPHABETA_DEFAULT_DEPTH = 3
MAX_SEARCH_TIME_SECS = 20

# Dice probabilities (exact from catanatron)
DICE_PROBABILITIES = {
    2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
    7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
}

# Initial deck composition
INITIAL_DECK_COMPOSITION = {
    KNIGHT: 14,
    YEAR_OF_PLENTY: 2,
    ROAD_BUILDING: 2,
    MONOPOLY: 2,
    VICTORY_POINT: 5
}

# Weights from catanatron's value.py DEFAULT_WEIGHTS (used by base_fn)
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


class CatanatronAlphaBetaPlayer(Player):
    """
    Accurate implementation of catanatron's AlphaBetaPlayer.
    
    Uses expectimax search with alpha-beta pruning for deterministic nodes.
    Properly handles probabilistic outcomes for dice rolls, dev cards, and robber.
    """
    
    def __init__(self, player_id: int, name: str = None,
                 depth: int = ALPHABETA_DEFAULT_DEPTH,
                 max_time: float = MAX_SEARCH_TIME_SECS,
                 prunning: bool = True):
        """Initialize the player."""
        super().__init__(player_id, name or f"CatanatronAB-{player_id}")
        self.depth = depth
        self.max_time = max_time
        self.prunning = prunning
        self.weights = DEFAULT_WEIGHTS.copy()
        self.start_time = 0
        self.nodes_evaluated = 0
        
        # Track deck composition (updated as cards are bought)
        self.deck_composition = INITIAL_DECK_COMPOSITION.copy()
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose the best action using expectimax with alpha-beta pruning."""
        if not valid_actions:
            raise ValueError(f"No valid actions available for {self.name}")
            
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        self.start_time = time.time()
        self.nodes_evaluated = 0
        
        # Update deck composition based on game state
        self._update_deck_composition(game.state)
        
        # Get pruned actions if enabled
        actions = self._list_prunned_actions(game, valid_actions) if self.prunning else valid_actions
        
        # Expectimax search
        best_action = None
        best_value = -inf
        
        for action in actions:
            # Get expected value for this action
            value = self._expectimax_value(game, action, self.depth)
            
            if value > best_value:
                best_value = value
                best_action = action
            
            # Check time limit
            if time.time() - self.start_time > self.max_time:
                break
        
        return best_action or actions[0]
    
    def _expectimax_value(self, game: "Game", action: Action, depth: int) -> float:
        """Calculate expected value of an action using expectimax."""
        # Get all possible outcomes with probabilities
        outcomes = self._execute_spectrum(game, action)
        
        if not outcomes:
            return -inf
        
        # Calculate expected value
        expected_value = 0
        for outcome_game, probability in outcomes:
            if outcome_game.is_over():
                value = self._end_game_value(outcome_game)
            elif depth <= 0 or time.time() - self.start_time > self.max_time:
                value = self._evaluate_state(outcome_game.state)
            else:
                # Continue search
                value = self._alphabeta(
                    outcome_game,
                    depth - 1,
                    -inf,
                    inf,
                    outcome_game.state.current_player != self.player_id
                )
            
            expected_value += probability * value
        
        return expected_value
    
    def _alphabeta(self, game: "Game", depth: int, alpha: float, beta: float,
                   maximizing: bool) -> float:
        """Alpha-beta search for deterministic nodes."""
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if game.is_over():
            return self._end_game_value(game)
        
        if depth == 0 or time.time() - self.start_time > self.max_time:
            return self._evaluate_state(game.state)
        
        # Get actions
        valid_actions = game.get_valid_actions()
        actions = self._list_prunned_actions(game, valid_actions) if self.prunning else valid_actions
        
        if maximizing:
            max_eval = -inf
            for action in actions:
                # Use expectimax for this level
                value = self._expectimax_value(game, action, depth)
                max_eval = max(max_eval, value)
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            min_eval = inf
            for action in actions:
                # Use expectimax for this level
                value = self._expectimax_value(game, action, depth)
                min_eval = min(min_eval, value)
                beta = min(beta, value)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def _execute_spectrum(self, game: "Game", action: Action) -> List[Tuple["Game", float]]:
        """
        Execute action and return all possible outcomes with probabilities.
        Now uses our proper probabilistic expansion module.
        """
        return execute_spectrum(game, action)
    
    def _list_prunned_actions(self, game: "Game", actions: List[Action]) -> List[Action]:
        """Prune actions following catanatron's logic."""
        # During setup, prune 1-tile settlements
        if any(a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT for a in actions):
            pruned = []
            for action in actions:
                if action.action_type == ActionType.BUILD_INITIAL_SETTLEMENT:
                    corner = action.value
                    adjacent_hexes = self._get_adjacent_hexes(corner)
                    if len(adjacent_hexes) > 1:  # Not a 1-tile settlement
                        pruned.append(action)
                else:
                    pruned.append(action)
            return pruned if pruned else actions
        
        # Prune robber moves (keep only high-impact ones)
        robber_actions = [a for a in actions if a.action_type == ActionType.MOVE_ROBBER]
        if len(robber_actions) > 5:
            # Calculate impact for each robber placement
            robber_impacts = []
            for action in robber_actions:
                hex_id, victim_id = action.value
                impact = self._calculate_robber_impact(game.state, hex_id, victim_id)
                robber_impacts.append((action, impact))
            
            # Keep top 5 by impact
            robber_impacts.sort(key=lambda x: x[1], reverse=True)
            best_robber_actions = [a for a, _ in robber_impacts[:5]]
            
            # Replace robber actions with best ones
            actions = [a for a in actions if a.action_type != ActionType.MOVE_ROBBER] + best_robber_actions
        
        # Prune 4:1 trades if 3:1 port available
        maritime_actions = [a for a in actions if a.action_type == ActionType.MARITIME_TRADE]
        if maritime_actions and self._has_3_to_1_port(game.state):
            pruned_maritime = []
            for action in maritime_actions:
                give_res, give_amount, get_res = action.value
                if give_amount < 4:  # Keep 2:1 and 3:1 trades
                    pruned_maritime.append(action)
            
            if pruned_maritime:
                actions = [a for a in actions if a.action_type != ActionType.MARITIME_TRADE] + pruned_maritime
        
        return actions
    
    def _evaluate_state(self, state: "GameState") -> float:
        """Evaluate state using catanatron's feature weights."""
        features = self._extract_features(state)
        
        # Calculate weighted sum
        value = 0
        for feature_name, feature_value in features.items():
            if feature_name in DEFAULT_WEIGHTS:
                value += DEFAULT_WEIGHTS[feature_name] * feature_value
        
        return value
    
    def _extract_features(self, state: "GameState") -> Dict[str, float]:
        """Extract features matching catanatron's implementation."""
        my_player = state.players[self.player_id]
        opp_player = state.players[1 - self.player_id]
        
        features = {}
        
        # Victory points (only PUBLIC vps, not including hidden VP cards)
        features["public_vps"] = my_player.public_vps
        
        # Production (with variety bonus)
        my_production, my_variety = self._calculate_production_and_variety(state, self.player_id)
        opp_production, opp_variety = self._calculate_production_and_variety(state, 1 - self.player_id)
        
        features["production"] = my_production + my_variety * 4
        features["enemy_production"] = opp_production + opp_variety * 4
        
        # Roads and longest road
        # Use simple road count as approximation for performance
        # Full DFS calculation is too expensive for every evaluation
        my_road_count = len([e for e, p in state.board.roads.items() if p == self.player_id])
        features["longest_road"] = my_road_count
        
        # Army
        features["army_size"] = my_player.knights_played
        
        # Expansion potential
        features["buildable_nodes"] = self._count_buildable_nodes(state, self.player_id)
        features["reachable_production_0"] = len(state.board.get_player_buildings(self.player_id)[SETTLEMENT])
        features["reachable_production_1"] = features["buildable_nodes"]
        
        # Hand composition
        features["hand_resources"] = sum(my_player.resources)
        features["hand_devs"] = my_player.total_dev_cards()
        features["hand_synergy"] = self._calculate_hand_synergy(my_player)
        
        # Discard penalty
        num_cards = sum(my_player.resources)
        features["discard_penalty"] = 1 if num_cards > 7 else 0
        
        # Number of tiles
        features["num_tiles"] = self._count_controlled_tiles(state, self.player_id)
        
        return features
    
    def _calculate_production_and_variety(self, state: "GameState", player_id: int) -> Tuple[float, int]:
        """Calculate production value and resource variety."""
        from engine.colonist_map import HEX_TO_CORNERS
        
        production = 0
        resource_types = set()
        buildings = state.board.get_player_buildings(player_id)
        
        for corner in buildings[SETTLEMENT]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners and state.board.robber_hex != hex_id:
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:  # Not desert
                        number = state.hex_numbers[hex_id]
                        if number in DICE_PROBABILITIES:
                            production += DICE_PROBABILITIES[number] * 36
                            resource_types.add(hex_type)
        
        # Cities produce double
        for corner in buildings[CITY]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners and state.board.robber_hex != hex_id:
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:
                        number = state.hex_numbers[hex_id]
                        if number in DICE_PROBABILITIES:
                            production += DICE_PROBABILITIES[number] * 36 * 2
                            resource_types.add(hex_type)
        
        return production, len(resource_types)
    
    def _calculate_hand_synergy(self, player_state) -> float:
        """Calculate how close the hand is to building something useful."""
        # Match catanatron's calculation exactly
        distance_to_city = (
            max(2 - player_state.resources[WHEAT], 0) +
            max(3 - player_state.resources[ORE], 0)
        ) / 5.0  # 0 means good. 1 means bad.
        
        distance_to_settlement = (
            max(1 - player_state.resources[WHEAT], 0) +
            max(1 - player_state.resources[SHEEP], 0) +
            max(1 - player_state.resources[BRICK], 0) +
            max(1 - player_state.resources[WOOD], 0)
        ) / 4.0  # 0 means good. 1 means bad.
        
        hand_synergy = (2 - distance_to_city - distance_to_settlement) / 2
        
        return hand_synergy
    
    def _count_buildable_nodes(self, state: "GameState", player_id: int) -> int:
        """Count corners where player could build settlements."""
        from engine.colonist_map import can_build_settlement, get_connected_edges
        
        count = 0
        occupied = set(state.board.buildings.keys())
        
        for corner in range(54):
            if can_build_settlement(corner, occupied):
                for edge in get_connected_edges(corner):
                    if edge in state.board.roads and state.board.roads[edge] == player_id:
                        count += 1
                        break
        
        return count
    
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
    
    def _calculate_robber_impact(self, state: "GameState", hex_id: int, victim_id: Optional[int]) -> float:
        """Calculate impact of placing robber on a hex."""
        # Production blocked
        production_blocked = 0
        if hex_id in state.hex_numbers:
            number = state.hex_numbers[hex_id]
            if number in DICE_PROBABILITIES:
                probability = DICE_PROBABILITIES[number] * 36
                
                # Count buildings on this hex
                for corner, (player, building_type) in state.board.buildings.items():
                    if corner in self._get_hex_corners(hex_id):
                        multiplier = 2 if building_type == CITY else 1
                        if player == self.player_id:
                            production_blocked -= probability * multiplier
                        else:
                            production_blocked += probability * multiplier
        
        # Stealing value
        steal_value = 0
        if victim_id is not None:
            victim_resources = sum(state.players[victim_id].resources)
            steal_value = min(1, victim_resources) * 2
        
        return production_blocked + steal_value
    
    def _get_adjacent_hexes(self, corner: int) -> List[int]:
        """Get hexes adjacent to a corner."""
        from engine.colonist_map import HEX_TO_CORNERS
        
        adjacent = []
        for hex_id, corners in HEX_TO_CORNERS.items():
            if corner in corners:
                adjacent.append(hex_id)
        return adjacent
    
    def _get_hex_corners(self, hex_id: int) -> List[int]:
        """Get corners of a hex."""
        from engine.colonist_map import HEX_TO_CORNERS
        return HEX_TO_CORNERS.get(hex_id, [])
    
    def _has_3_to_1_port(self, state: "GameState") -> bool:
        """Check if player has access to 3:1 port."""
        from engine.colonist_map import PORT_CORNERS
        from engine.models.enums import PORT_TYPE_3_1
        
        buildings = state.board.get_player_buildings(self.player_id)
        for corner in buildings[SETTLEMENT] + buildings[CITY]:
            if corner in PORT_CORNERS and PORT_CORNERS[corner] == PORT_TYPE_3_1:
                return True
        return False
    
    def _update_deck_composition(self, state: "GameState"):
        """Update deck composition based on cards already drawn."""
        # Reset to initial
        self.deck_composition = INITIAL_DECK_COMPOSITION.copy()
        
        # Subtract cards in players' hands
        for player_state in state.players:
            for card_type, count in enumerate(player_state.dev_cards):
                if card_type in self.deck_composition:
                    self.deck_composition[card_type] -= count
            
            # Also subtract cards bought this turn
            for card_type, count in enumerate(player_state.dev_cards_bought_this_turn):
                if card_type in self.deck_composition:
                    self.deck_composition[card_type] -= count
        
        # Ensure non-negative
        for card_type in self.deck_composition:
            self.deck_composition[card_type] = max(0, self.deck_composition[card_type])
    
    def _end_game_value(self, game: "Game") -> float:
        """Value for terminal game states."""
        winner = game.state.get_winner()
        if winner == self.player_id:
            # Return a value higher than any possible evaluation
            # This ensures winning is always preferred
            return 1e16  # 10x higher than max VP evaluation
        elif winner is not None:
            return -1e16
        else:
            return 0