"""
Improved CatanatronAlphaBetaPlayer that better exploits probabilistic expansion.
"""

import time
import random
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from math import inf, sqrt

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

# Dice probabilities 
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

# Improved weights with dynamic adjustments
BASE_WEIGHTS = {
    # Core features (balanced between original and reduced)
    "public_vps": 1e12,  # Reduced from 3e14 but still dominant
    "production": 1e6,  # Reduced from 1e8 but still significant
    "enemy_production": -5e5,  # Less negative than -1e8
    "num_tiles": 1,
    
    # Expansion
    "reachable_production_0": 0,
    "reachable_production_1": 1e3,  # Reduced from 1e4
    "buildable_nodes": 500,  # Reduced from 1e3
    "longest_road": 10,
    
    # Hand management (increased importance)
    "hand_synergy": 1e3,  # Increased from 1e2
    "hand_resources": 1,
    "discard_penalty": -100,  # Increased penalty
    "hand_devs": 10,
    "army_size": 10.1,
    
    # New features
    "dev_card_potential": 5000,  # Value of unknown dev cards
    "robber_vulnerability": -1000,  # Penalty for blockable production
    "position_variance": -50,  # Risk adjustment
    "hidden_vp_potential": 10000,  # Value of secret victory path
}


class CatanatronAlphaBetaImproved(Player):
    """
    Improved CatanatronAlphaBetaPlayer that better exploits probabilistic expansion.
    
    Key improvements:
    1. Risk-aware evaluation using variance from probabilistic outcomes
    2. Dynamic weight adjustment based on game phase
    3. Better dev card and robber strategies
    4. Exploitation of hidden information
    """
    
    def __init__(self, player_id: int, name: str = None,
                 depth: int = ALPHABETA_DEFAULT_DEPTH,
                 max_time: float = MAX_SEARCH_TIME_SECS,
                 prunning: bool = True):
        """Initialize the improved player."""
        super().__init__(player_id, name or f"CatanatronAB++{player_id}")
        self.depth = depth
        self.max_time = max_time
        self.prunning = prunning
        self.start_time = 0
        self.nodes_evaluated = 0
        
        # Track deck composition
        self.deck_composition = INITIAL_DECK_COMPOSITION.copy()
        
        # Dynamic weights (will be adjusted based on game state)
        self.weights = BASE_WEIGHTS.copy()
    
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose the best action using improved expectimax with alpha-beta pruning."""
        if not valid_actions:
            raise ValueError(f"No valid actions available for {self.name}")
            
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        self.start_time = time.time()
        self.nodes_evaluated = 0
        
        # Update strategy based on game state
        self._update_weights_for_game_state(game)
        
        # Update deck composition
        self._update_deck_composition(game.state)
        
        # Get pruned actions if enabled
        actions = self._list_prunned_actions(game, valid_actions) if self.prunning else valid_actions
        
        # Enhanced expectimax search
        best_action = None
        best_value = -inf
        best_variance = 0
        
        for action in actions:
            # Get expected value AND variance for risk assessment
            value, variance = self._expectimax_value_with_variance(game, action, self.depth)
            
            # Risk-adjusted value
            risk_adjusted_value = self._risk_adjust_value(value, variance, game)
            
            if risk_adjusted_value > best_value:
                best_value = risk_adjusted_value
                best_action = action
                best_variance = variance
            
            # Check time limit
            if time.time() - self.start_time > self.max_time:
                break
        
        return best_action or actions[0]
    
    def _update_weights_for_game_state(self, game: "Game"):
        """Dynamically adjust weights based on game phase and position."""
        state = game.state
        my_vps = state.players[self.player_id].public_vps
        opp_vps = state.players[1 - self.player_id].public_vps
        
        # Estimate game phase
        total_vps = my_vps + opp_vps
        if total_vps < 8:  # Early game
            phase = "early"
        elif total_vps < 14:  # Mid game
            phase = "mid"
        else:  # Late game
            phase = "late"
        
        # Reset to base weights
        self.weights = BASE_WEIGHTS.copy()
        
        # Phase-based adjustments
        if phase == "early":
            self.weights["production"] *= 3  # Much more emphasis on production early
            self.weights["reachable_production_1"] *= 3
            self.weights["buildable_nodes"] *= 2
            self.weights["public_vps"] *= 0.1  # Much less VP focus early
            self.weights["dev_card_potential"] *= 0.5  # Less dev cards early
        elif phase == "late":
            self.weights["public_vps"] *= 10  # Extreme VP focus late game
            self.weights["hidden_vp_potential"] *= 5
            self.weights["dev_card_potential"] *= 3
            self.weights["production"] *= 0.3  # Much less production focus
            self.weights["buildable_nodes"] *= 0.2  # Less expansion
        
        # Position-based adjustments
        vp_diff = my_vps - opp_vps
        if vp_diff <= -2:  # Significantly behind
            self.weights["dev_card_potential"] *= 4  # Heavily pursue hidden VPs
            self.weights["position_variance"] = 1000  # Strong risk-taking
            self.weights["robber_vulnerability"] *= 0.2  # Ignore defensive play
            self.weights["hidden_vp_potential"] *= 3
        elif vp_diff >= 2:  # Significantly ahead
            self.weights["position_variance"] = -2000  # Very risk-averse
            self.weights["robber_vulnerability"] *= 3  # Very defensive
            self.weights["production"] *= 1.5  # Secure wins
            self.weights["public_vps"] *= 2  # Push for victory
        
        # Endgame adjustments
        if my_vps >= 8 or opp_vps >= 8:
            self.weights["public_vps"] *= 5  # Heavily prioritize winning
            if my_vps == 9:
                self.weights["public_vps"] *= 10  # One VP from victory!
    
    def _expectimax_value_with_variance(self, game: "Game", action: Action, depth: int) -> Tuple[float, float]:
        """Calculate expected value AND variance of an action."""
        outcomes = self._execute_spectrum(game, action)
        
        if not outcomes:
            return -inf, 0
        
        # Calculate expected value and variance
        values = []
        probabilities = []
        
        for outcome_game, probability in outcomes:
            if outcome_game.is_over():
                value = self._end_game_value(outcome_game)
            elif depth <= 0 or time.time() - self.start_time > self.max_time:
                value = self._evaluate_state_improved(outcome_game.state)
            else:
                # Continue search
                value = self._alphabeta(
                    outcome_game,
                    depth - 1,
                    -inf,
                    inf,
                    outcome_game.state.current_player != self.player_id
                )
            
            values.append(value)
            probabilities.append(probability)
        
        # Calculate expected value
        expected_value = sum(v * p for v, p in zip(values, probabilities))
        
        # Calculate variance
        variance = sum(p * (v - expected_value) ** 2 for v, p in zip(values, probabilities))
        
        return expected_value, variance
    
    def _risk_adjust_value(self, value: float, variance: float, game: "Game") -> float:
        """Adjust value based on risk (variance) and game position."""
        # Get position variance weight (positive = risk-seeking, negative = risk-averse)
        risk_preference = self.weights.get("position_variance", -20)
        
        # Risk adjustment: value + risk_preference * sqrt(variance)
        # sqrt to reduce impact of extreme variances
        risk_adjustment = risk_preference * sqrt(variance) if variance > 0 else 0
        
        return value + risk_adjustment
    
    def _evaluate_state_improved(self, state: "GameState") -> float:
        """Enhanced evaluation with new features."""
        features = self._extract_features_improved(state)
        
        # Calculate weighted sum
        value = 0
        for feature_name, feature_value in features.items():
            if feature_name in self.weights:
                value += self.weights[feature_name] * feature_value
        
        return value
    
    def _extract_features_improved(self, state: "GameState") -> Dict[str, float]:
        """Extract enhanced features including risk metrics."""
        features = {}
        my_player = state.players[self.player_id]
        opp_player = state.players[1 - self.player_id]
        
        # Original features
        features["public_vps"] = my_player.public_vps
        
        # Production with robber vulnerability
        my_prod, my_variety, my_robber_vuln = self._calculate_production_metrics(state, self.player_id)
        opp_prod, opp_variety, opp_robber_vuln = self._calculate_production_metrics(state, 1 - self.player_id)
        
        features["production"] = my_prod + my_variety * 4
        features["enemy_production"] = opp_prod + opp_variety * 4
        features["robber_vulnerability"] = my_robber_vuln
        
        # Development card potential
        features["dev_card_potential"] = self._calculate_dev_card_potential(state)
        features["hidden_vp_potential"] = self._calculate_hidden_vp_potential(state)
        
        # Hand features
        features["hand_resources"] = sum(my_player.resources)
        features["hand_devs"] = my_player.total_dev_cards()
        features["hand_synergy"] = self._calculate_hand_synergy(my_player)
        
        # Army and roads
        features["army_size"] = my_player.knights_played
        features["longest_road"] = self._estimate_road_length(state, self.player_id)
        
        # Expansion
        features["buildable_nodes"] = self._count_buildable_nodes(state, self.player_id)
        features["reachable_production_0"] = len(state.board.get_player_buildings(self.player_id)[SETTLEMENT])
        features["reachable_production_1"] = features["buildable_nodes"]
        
        # Other
        features["num_tiles"] = self._count_controlled_tiles(state, self.player_id)
        
        # Discard penalty (increased if over 7 cards)
        if features["hand_resources"] > 7:
            features["discard_penalty"] = features["hand_resources"] - 7
        else:
            features["discard_penalty"] = 0
        
        return features
    
    def _calculate_production_metrics(self, state: "GameState", player_id: int) -> Tuple[float, int, float]:
        """Calculate production, variety, and robber vulnerability."""
        from engine.colonist_map import HEX_TO_CORNERS
        
        production = 0
        robber_vulnerability = 0
        resource_types = set()
        buildings = state.board.get_player_buildings(player_id)
        
        # Production by hex
        hex_production = defaultdict(float)
        
        for corner in buildings[SETTLEMENT]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    if state.board.robber_hex == hex_id:
                        continue
                    
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:
                        resource_types.add(hex_type)
                        number = state.hex_numbers[hex_id]
                        if number in DICE_PROBABILITIES:
                            prod = DICE_PROBABILITIES[number] * 36
                            production += prod
                            hex_production[hex_id] += prod
        
        # Cities produce double
        for corner in buildings[CITY]:
            for hex_id, corners in HEX_TO_CORNERS.items():
                if corner in corners:
                    if state.board.robber_hex == hex_id:
                        continue
                    
                    hex_type = state.hex_types[hex_id]
                    if hex_type > 0:
                        resource_types.add(hex_type)
                        number = state.hex_numbers[hex_id]
                        if number in DICE_PROBABILITIES:
                            prod = DICE_PROBABILITIES[number] * 36 * 2
                            production += prod
                            hex_production[hex_id] += prod
        
        # Calculate robber vulnerability (concentration of production)
        if hex_production:
            # Higher vulnerability if production is concentrated on few hexes
            max_hex_prod = max(hex_production.values())
            robber_vulnerability = max_hex_prod / production if production > 0 else 0
        
        return production, len(resource_types), robber_vulnerability
    
    def _calculate_dev_card_potential(self, state: "GameState") -> float:
        """Calculate the strategic value of buying dev cards."""
        my_player = state.players[self.player_id]
        
        # Base value
        value = 0
        
        # VP card probability and value
        vp_cards_left = self.deck_composition.get(VICTORY_POINT, 0)
        total_cards = sum(self.deck_composition.values())
        
        if total_cards > 0:
            vp_probability = vp_cards_left / total_cards
            # VP cards more valuable when closer to winning
            vp_value = 1000 * (1 + my_player.public_vps / 10)
            value += vp_probability * vp_value
            
            # Knight probability and value
            knight_probability = self.deck_composition.get(KNIGHT, 0) / total_cards
            # Knights more valuable if we can get largest army or robber is on us
            knight_value = 200
            if my_player.knights_played >= 2:
                knight_value = 500  # Close to largest army
            value += knight_probability * knight_value
        
        return value
    
    def _calculate_hidden_vp_potential(self, state: "GameState") -> float:
        """Calculate value of hidden VP strategy."""
        my_player = state.players[self.player_id]
        
        # More valuable when we have dev cards opponents don't know about
        hidden_value = 0
        
        # Each unknown dev card has potential
        unknown_dev_cards = my_player.dev_cards_bought_this_turn
        hidden_value += sum(unknown_dev_cards) * 100
        
        # VP cards we're holding
        hidden_value += my_player.dev_cards[VICTORY_POINT] * 500
        
        # More valuable when close to winning
        if my_player.public_vps >= 8:
            hidden_value *= 2
        
        return hidden_value
    
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
        
        # Distance to dev card
        distance_to_dev = (
            max(1 - player_state.resources[SHEEP], 0) +
            max(1 - player_state.resources[WHEAT], 0) +
            max(1 - player_state.resources[ORE], 0)
        ) / 3.0
        
        # Higher synergy = closer to building
        synergy = (3 - distance_to_city - distance_to_settlement - distance_to_dev) / 3
        return max(0, synergy)
    
    # Keep all the helper methods from original CatanatronAlphaBetaPlayer
    def _alphabeta(self, game: "Game", depth: int, alpha: float, beta: float,
                   maximizing: bool) -> float:
        """Alpha-beta search for deterministic nodes."""
        self.nodes_evaluated += 1
        
        if game.is_over():
            return self._end_game_value(game)
        
        if depth == 0 or time.time() - self.start_time > self.max_time:
            return self._evaluate_state_improved(game.state)
        
        valid_actions = game.get_valid_actions()
        actions = self._list_prunned_actions(game, valid_actions) if self.prunning else valid_actions
        
        if maximizing:
            max_eval = -inf
            for action in actions:
                value, _ = self._expectimax_value_with_variance(game, action, depth)
                max_eval = max(max_eval, value)
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break
            
            return max_eval
        else:
            min_eval = inf
            for action in actions:
                value, _ = self._expectimax_value_with_variance(game, action, depth)
                min_eval = min(min_eval, value)
                beta = min(beta, value)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _execute_spectrum(self, game: "Game", action: Action) -> List[Tuple["Game", float]]:
        """Execute action and return all possible outcomes with probabilities."""
        return execute_spectrum(game, action)
    
    def _update_deck_composition(self, state: "GameState"):
        """Update our knowledge of the deck composition."""
        # Reset to initial
        self.deck_composition = INITIAL_DECK_COMPOSITION.copy()
        
        # Subtract cards that have been played
        for player_state in state.players:
            self.deck_composition[KNIGHT] -= player_state.knights_played
            # Subtract cards in players' hands
            for card_type in range(5):
                self.deck_composition[card_type] -= player_state.dev_cards[card_type]
    
    def _end_game_value(self, game: "Game") -> float:
        """Value for terminal game states."""
        winner = game.state.get_winner()
        if winner == self.player_id:
            return 1e16
        elif winner is not None:
            return -1e16
        else:
            return 0
    
    def _list_prunned_actions(self, game: "Game", actions: List[Action]) -> List[Action]:
        """Enhanced pruning using probabilistic information."""
        # During setup, prune 1-tile settlements
        if any(a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT for a in actions):
            pruned = []
            for action in actions:
                if action.action_type == ActionType.BUILD_INITIAL_SETTLEMENT:
                    corner = action.value
                    adjacent_hexes = self._get_adjacent_hexes(corner)
                    if len(adjacent_hexes) > 1:
                        pruned.append(action)
                else:
                    pruned.append(action)
            return pruned if pruned else actions
        
        # Enhanced robber pruning using expected value
        robber_actions = [a for a in actions if a.action_type == ActionType.MOVE_ROBBER]
        if len(robber_actions) > 5:
            robber_values = []
            for action in robber_actions:
                # Calculate expected value of robber placement
                outcomes = self._execute_spectrum(game, action)
                if outcomes:
                    expected_value = sum(self._evaluate_state_improved(og.state) * p 
                                       for og, p in outcomes)
                    robber_values.append((action, expected_value))
            
            # Keep top 5 by expected value
            robber_values.sort(key=lambda x: x[1], reverse=True)
            best_robber_actions = [a for a, _ in robber_values[:5]]
            
            actions = [a for a in actions if a.action_type != ActionType.MOVE_ROBBER] + best_robber_actions
        
        # Prune poor trades more aggressively
        maritime_actions = [a for a in actions if a.action_type == ActionType.MARITIME_TRADE]
        if maritime_actions:
            pruned_maritime = []
            for action in maritime_actions:
                give_res, give_amount, get_res = action.value
                # Keep good trades based on need
                my_resources = game.state.players[self.player_id].resources
                if my_resources[get_res] < 2 and give_amount <= 3:
                    pruned_maritime.append(action)
                elif give_amount == 2:  # Always keep 2:1 trades
                    pruned_maritime.append(action)
            
            if pruned_maritime:
                actions = [a for a in actions if a.action_type != ActionType.MARITIME_TRADE] + pruned_maritime
        
        return actions
    
    # Helper methods (keep from original)
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
    
    def _estimate_road_length(self, state: "GameState", player_id: int) -> int:
        """Estimate road length (simplified for performance)."""
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