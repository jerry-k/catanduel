"""
Minimax AI player for CatanDuel.

Implements minimax search with alpha-beta pruning and heuristic evaluation.
Based on catanatron's minimax implementation but optimized for 2-player games.
"""

import time
from typing import List, Tuple, Optional, Dict
from math import inf

from models.player import Player
from models.enums import (
    Action, ActionType,
    SETTLEMENT, CITY, ROAD,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    PLAYER_0, PLAYER_1
)

# Type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game import Game
    from state import GameState


class MinimaxPlayer(Player):
    """
    AI player using minimax search with alpha-beta pruning.
    
    Features:
    - Configurable search depth
    - Alpha-beta pruning for efficiency
    - Heuristic evaluation function
    - Time-limited search
    """
    
    def __init__(self, player_id: int, name: str = None, 
                 max_depth: int = 3, time_limit: float = 2.0):
        """
        Initialize minimax player.
        
        Args:
            player_id: 0 or 1
            name: Player name
            max_depth: Maximum search depth
            time_limit: Time limit per move in seconds
        """
        super().__init__(player_id, name or f"Minimax-{player_id}")
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.start_time = 0
        
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose the best action using minimax search."""
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        self.nodes_evaluated = 0
        self.start_time = time.time()
        
        # For each action, evaluate the resulting state
        best_action = valid_actions[0]
        best_value = -inf if game.state.current_player == self.player_id else inf
        
        for action in valid_actions:
            # Skip obviously bad moves in the interest of time
            if self._should_skip_action(action, game.state):
                continue
                
            # Make a copy and apply the action
            game_copy = game.copy()
            game_copy.execute(action, validate=False)
            
            # Evaluate using minimax
            value = self._minimax(
                game_copy, 
                self.max_depth - 1,
                -inf, 
                inf,
                game_copy.state.current_player == self.player_id
            )
            
            # Update best action
            if game.state.current_player == self.player_id:
                if value > best_value:
                    best_value = value
                    best_action = action
            else:
                if value < best_value:
                    best_value = value
                    best_action = action
            
            # Check time limit
            if time.time() - self.start_time > self.time_limit:
                break
        
        return best_action
    
    def _minimax(self, game: "Game", depth: int, alpha: float, beta: float, 
                 maximizing: bool) -> float:
        """
        Minimax with alpha-beta pruning.
        
        Args:
            game: Current game state
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player
            
        Returns:
            Evaluation score
        """
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if game.is_over():
            winner = game.state.get_winner()
            if winner == self.player_id:
                return 1000
            elif winner is not None:
                return -1000
            else:
                return 0
        
        if depth == 0 or time.time() - self.start_time > self.time_limit:
            return self._evaluate_state(game.state)
        
        # Get valid actions
        valid_actions = game.get_valid_actions()
        
        if maximizing:
            max_eval = -inf
            for action in valid_actions:
                if self._should_skip_action(action, game.state):
                    continue
                    
                game_copy = game.copy()
                game_copy.execute(action, validate=False)
                
                eval_score = self._minimax(
                    game_copy, 
                    depth - 1, 
                    alpha, 
                    beta, 
                    game_copy.state.current_player == self.player_id
                )
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
                    
            return max_eval
        else:
            min_eval = inf
            for action in valid_actions:
                if self._should_skip_action(action, game.state):
                    continue
                    
                game_copy = game.copy()
                game_copy.execute(action, validate=False)
                
                eval_score = self._minimax(
                    game_copy, 
                    depth - 1, 
                    alpha, 
                    beta, 
                    game_copy.state.current_player == self.player_id
                )
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
                    
            return min_eval
    
    def _evaluate_state(self, state: "GameState") -> float:
        """
        Evaluate a game state from this player's perspective.
        
        Returns a score where positive is good for this player.
        """
        my_state = state.players[self.player_id]
        opp_state = state.players[1 - self.player_id]
        
        # Victory points (most important)
        vp_score = (my_state.actual_vps() - opp_state.actual_vps()) * 100
        
        # Development cards
        dev_score = (my_state.total_dev_cards() - opp_state.total_dev_cards()) * 10
        
        # Knights (for largest army)
        knight_score = (my_state.knights_played - opp_state.knights_played) * 5
        
        # Resources
        my_resources = sum(my_state.resources)
        opp_resources = sum(opp_state.resources)
        resource_score = (my_resources - opp_resources) * 2
        
        # Resource diversity
        my_diversity = sum(1 for r in my_state.resources if r > 0)
        opp_diversity = sum(1 for r in opp_state.resources if r > 0)
        diversity_score = (my_diversity - opp_diversity) * 3
        
        # Building pieces left (potential)
        my_potential = my_state.settlements_left * 10 + my_state.cities_left * 20
        opp_potential = opp_state.settlements_left * 10 + opp_state.cities_left * 20
        potential_score = (my_potential - opp_potential)
        
        # Longest road bonus
        if state.board.longest_road_player == self.player_id:
            longest_road_score = 20
        elif state.board.longest_road_player == 1 - self.player_id:
            longest_road_score = -20
        else:
            longest_road_score = 0
        
        # Largest army bonus  
        if my_state.has_largest_army:
            largest_army_score = 20
        elif opp_state.has_largest_army:
            largest_army_score = -20
        else:
            largest_army_score = 0
        
        # Port access (check if player has settlements/cities on ports)
        my_port_access = self._count_port_access(state, self.player_id)
        opp_port_access = self._count_port_access(state, 1 - self.player_id)
        port_score = (my_port_access - opp_port_access) * 5
        
        # Combine scores
        total_score = (
            vp_score + 
            dev_score + 
            knight_score + 
            resource_score + 
            diversity_score + 
            potential_score + 
            longest_road_score +
            largest_army_score +
            port_score
        )
        
        return total_score
    
    def _count_port_access(self, state: "GameState", player_id: int) -> int:
        """Count number of different port types player has access to."""
        from colonist_map import PORT_CORNERS
        
        port_types = set()
        buildings = state.board.get_player_buildings(player_id)
        
        for corner in buildings[SETTLEMENT] + buildings[CITY]:
            if corner in PORT_CORNERS:
                port_types.add(PORT_CORNERS[corner])
        
        return len(port_types)
    
    def _should_skip_action(self, action: Action, state: "GameState") -> bool:
        """
        Quick heuristic to skip obviously bad actions.
        
        This speeds up search by pruning bad moves early.
        """
        # Don't skip forced actions
        if action.action_type in [ActionType.ROLL, ActionType.DISCARD]:
            return False
        
        # Skip ending turn if we have good building options
        if action.action_type == ActionType.END_TURN:
            player = state.players[state.current_player]
            can_build_settlement = (
                player.settlements_left > 0 and
                player.resources[WOOD] >= 1 and
                player.resources[BRICK] >= 1 and
                player.resources[SHEEP] >= 1 and
                player.resources[WHEAT] >= 1
            )
            can_build_city = (
                player.cities_left > 0 and
                player.resources[WHEAT] >= 2 and
                player.resources[ORE] >= 3
            )
            if can_build_settlement or can_build_city:
                return True
        
        # Skip bad trades
        if action.action_type == ActionType.MARITIME_TRADE:
            give_res, give_amount, get_res = action.value
            # Skip 4:1 trades if we have better options
            if give_amount == 4:
                player = state.players[state.current_player]
                # Check if we need this specific resource urgently
                if get_res in [WHEAT, ORE] and player.resources[get_res] == 0:
                    return False  # Might need for city
                return True  # Otherwise skip 4:1 trades
        
        return False


class AlphaBetaPlayer(MinimaxPlayer):
    """Alias for MinimaxPlayer with alpha-beta pruning."""
    pass


class SimpleMinimaxPlayer(MinimaxPlayer):
    """
    Simplified minimax player with lower depth and simpler evaluation.
    Good for faster games or weaker opponents.
    """
    
    def __init__(self, player_id: int, name: str = None):
        super().__init__(player_id, name or f"SimpleMM-{player_id}", 
                        max_depth=2, time_limit=1.0)
    
    def _evaluate_state(self, state: "GameState") -> float:
        """Simplified evaluation focusing on VPs and resources."""
        my_state = state.players[self.player_id]
        opp_state = state.players[1 - self.player_id]
        
        # Focus mainly on victory points
        vp_diff = my_state.actual_vps() - opp_state.actual_vps()
        
        # Some resource consideration
        resource_diff = (
            sum(my_state.resources) - sum(opp_state.resources)
        ) / 10.0
        
        return vp_diff * 100 + resource_diff