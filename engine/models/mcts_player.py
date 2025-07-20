"""
MCTS (Monte Carlo Tree Search) AI player for CatanDuel.

Implements MCTS with UCT (Upper Confidence bounds applied to Trees) for
action selection. This is often stronger than minimax for games with
high branching factors.

Based on standard MCTS algorithm but optimized for 2-player Catan.
"""

import math
import time
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from engine.models.player import Player
from engine.models.enums import (
    Action, ActionType,
    PLAYER_0, PLAYER_1
)

# Type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.game import Game
    from engine.state import GameState


@dataclass
class MCTSNode:
    """
    Node in the MCTS search tree.
    
    Attributes:
        action: Action that led to this node (None for root)
        parent: Parent node
        children: Dict mapping actions to child nodes
        visits: Number of times this node has been visited
        total_value: Sum of all backpropagated values
        untried_actions: Actions not yet tried from this state
        player_id: Player to move at this node
    """
    action: Optional[Action] = None
    parent: Optional['MCTSNode'] = None
    children: Dict[Action, 'MCTSNode'] = field(default_factory=dict)
    visits: int = 0
    total_value: float = 0.0
    untried_actions: List[Action] = field(default_factory=list)
    player_id: int = 0
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0
    
    def is_fully_expanded(self) -> bool:
        """Check if all actions have been tried."""
        return len(self.untried_actions) == 0
    
    def best_child(self, c: float = 1.414) -> 'MCTSNode':
        """
        Select best child using UCB1 formula.
        
        Args:
            c: Exploration constant (higher = more exploration)
        """
        best_score = -float('inf')
        best_child = None
        
        for child in self.children.values():
            if child.visits == 0:
                score = float('inf')  # Prioritize unvisited nodes
            else:
                # UCB1 formula
                exploitation = child.total_value / child.visits
                exploration = c * math.sqrt(2 * math.log(self.visits) / child.visits)
                
                # Negate for opponent's nodes
                if child.player_id != self.player_id:
                    exploitation = -exploitation
                
                score = exploitation + exploration
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child
    
    def most_visited_child(self) -> 'MCTSNode':
        """Return child with most visits (for final selection)."""
        return max(self.children.values(), key=lambda c: c.visits)
    
    def update(self, value: float):
        """Update node statistics with backpropagated value."""
        self.visits += 1
        self.total_value += value


class MCTSPlayer(Player):
    """
    AI player using Monte Carlo Tree Search.
    
    MCTS builds a search tree through repeated simulations:
    1. Selection: Navigate tree using UCB1
    2. Expansion: Add new node
    3. Simulation: Random playout
    4. Backpropagation: Update statistics
    
    This often performs better than minimax for games with:
    - High branching factor
    - Hard to evaluate positions
    - Long games
    """
    
    def __init__(self, player_id: int, name: str = None,
                 time_limit: float = 2.0, 
                 exploration_constant: float = 1.414,
                 simulation_depth: int = 50):
        """
        Initialize MCTS player.
        
        Args:
            player_id: 0 or 1
            name: Player name
            time_limit: Time limit per move in seconds
            exploration_constant: UCB1 exploration parameter
            simulation_depth: Max depth for rollout simulations
        """
        super().__init__(player_id, name or f"MCTS-{player_id}")
        self.time_limit = time_limit
        self.exploration_constant = exploration_constant
        self.simulation_depth = simulation_depth
        self.simulations_run = 0
        
    def decide(self, game: "Game", valid_actions: List[Action]) -> Action:
        """Choose best action using MCTS."""
        if len(valid_actions) == 1:
            return valid_actions[0]
        
        self.simulations_run = 0
        start_time = time.time()
        
        # Create root node
        root = MCTSNode(
            player_id=game.state.current_player,
            untried_actions=valid_actions.copy()
        )
        
        # Run simulations until time limit
        while time.time() - start_time < self.time_limit:
            # MCTS phases
            node = self._select(root, game.copy())
            value = self._simulate(node, game.copy())
            self._backpropagate(node, value)
            self.simulations_run += 1
        
        # Return most visited action
        if root.children:
            best_child = root.most_visited_child()
            return best_child.action
        else:
            # Fallback if no simulations completed
            return random.choice(valid_actions)
    
    def _select(self, node: MCTSNode, game: "Game") -> MCTSNode:
        """
        Selection phase: Navigate tree to leaf node.
        
        Returns the selected node and updates game state.
        """
        while not node.is_leaf():
            if not node.is_fully_expanded():
                return self._expand(node, game)
            else:
                node = node.best_child(self.exploration_constant)
                try:
                    game.execute(node.action, validate=True)
                except:
                    # Action is no longer valid, treat as terminal
                    return node
        
        # Leaf node - expand if not terminal
        if not game.is_over() and not node.is_fully_expanded():
            return self._expand(node, game)
        
        return node
    
    def _expand(self, node: MCTSNode, game: "Game") -> MCTSNode:
        """
        Expansion phase: Add new child node.
        
        Returns the new child node.
        """
        # Try actions until we find one that works
        while node.untried_actions:
            # Pick random untried action
            idx = random.randint(0, len(node.untried_actions) - 1)
            action = node.untried_actions.pop(idx)
            
            try:
                # Execute action
                game.execute(action, validate=True)
                
                # Create child node
                child = MCTSNode(
                    action=action,
                    parent=node,
                    player_id=game.state.current_player,
                    untried_actions=game.get_valid_actions().copy()
                )
                
                node.children[action] = child
                return child
            except:
                # Action failed, try another
                continue
        
        # No valid actions to expand
        return node
    
    def _simulate(self, node: MCTSNode, game: "Game") -> float:
        """
        Simulation phase: Random playout from node.
        
        Returns evaluation from perspective of node.player_id.
        """
        # Random playout
        depth = 0
        while not game.is_over() and depth < self.simulation_depth:
            actions = game.get_valid_actions()
            if not actions:
                break
                
            # Use weighted random selection for better simulations
            action = self._select_simulation_action(game, actions)
            try:
                game.execute(action, validate=True)
            except:
                # Action failed, try another random action
                for _ in range(len(actions)):
                    action = random.choice(actions)
                    try:
                        game.execute(action, validate=True)
                        break
                    except:
                        continue
                else:
                    # No valid actions, end simulation
                    break
            depth += 1
        
        # Evaluate terminal position
        return self._evaluate_terminal(game, node.player_id)
    
    def _select_simulation_action(self, game: "Game", actions: List[Action]) -> Action:
        """
        Select action during simulation phase.
        
        Uses weighted random selection with simple heuristics.
        """
        # Weight actions by type
        weights = []
        for action in actions:
            if action.action_type == ActionType.BUILD_CITY:
                weight = 5.0  # Strongly prefer cities
            elif action.action_type == ActionType.BUILD_SETTLEMENT:
                weight = 4.0  # Prefer settlements
            elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
                weight = 3.0  # Dev cards are good
            elif action.action_type == ActionType.BUILD_ROAD:
                weight = 2.0  # Roads for longest road
            elif action.action_type in [ActionType.PLAY_KNIGHT_CARD,
                                       ActionType.PLAY_YEAR_OF_PLENTY,
                                       ActionType.PLAY_MONOPOLY]:
                weight = 3.5  # Playing dev cards is usually good
            elif action.action_type == ActionType.END_TURN:
                weight = 0.5  # Avoid ending turn if we can do something
            else:
                weight = 1.0  # Default weight
            
            weights.append(weight)
        
        # Weighted random choice
        total = sum(weights)
        r = random.uniform(0, total)
        cumsum = 0
        
        for action, weight in zip(actions, weights):
            cumsum += weight
            if r <= cumsum:
                return action
        
        return actions[-1]  # Fallback
    
    def _evaluate_terminal(self, game: "Game", player_id: int) -> float:
        """
        Evaluate terminal game state.
        
        Returns:
            1.0 for win, -1.0 for loss, 0.0 for draw
        """
        if game.is_over():
            winner = game.state.get_winner()
            if winner == player_id:
                return 1.0
            elif winner is not None:
                return -1.0
            else:
                return 0.0
        else:
            # Non-terminal - use simple heuristic
            my_vps = game.state.players[player_id].actual_vps()
            opp_vps = game.state.players[1 - player_id].actual_vps()
            
            # Normalize to [-1, 1]
            vp_diff = (my_vps - opp_vps) / 10.0
            return max(-0.9, min(0.9, vp_diff))
    
    def _backpropagate(self, node: MCTSNode, value: float):
        """
        Backpropagation phase: Update statistics up the tree.
        
        Value is from perspective of the player at the leaf.
        """
        while node is not None:
            # Flip value for opponent nodes
            node_value = value if node.player_id == self.player_id else -value
            node.update(node_value)
            node = node.parent


class FastMCTSPlayer(MCTSPlayer):
    """
    Faster MCTS variant with shorter time limit and shallower simulations.
    Good for real-time play or when computation is limited.
    """
    
    def __init__(self, player_id: int, name: str = None):
        super().__init__(
            player_id,
            name or f"FastMCTS-{player_id}",
            time_limit=0.5,
            exploration_constant=1.0,  # Less exploration
            simulation_depth=20
        )


class StrongMCTSPlayer(MCTSPlayer):
    """
    Stronger MCTS variant with more time and deeper simulations.
    Use this when you want the strongest possible play.
    """
    
    def __init__(self, player_id: int, name: str = None):
        super().__init__(
            player_id,
            name or f"StrongMCTS-{player_id}",
            time_limit=5.0,
            exploration_constant=1.414,
            simulation_depth=100
        )
    
    def _select_simulation_action(self, game: "Game", actions: List[Action]) -> Action:
        """Enhanced action selection with better heuristics."""
        # Get current player state
        player = game.state.players[game.state.current_player]
        
        # Calculate weights with more sophisticated heuristics
        weights = []
        for action in actions:
            weight = 1.0
            
            if action.action_type == ActionType.BUILD_CITY:
                # Cities are almost always good
                weight = 10.0
            
            elif action.action_type == ActionType.BUILD_SETTLEMENT:
                # Settlements good early, less so late
                if player.actual_vps() < 6:
                    weight = 8.0
                else:
                    weight = 4.0
            
            elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
                # Dev cards better with more knights for army
                weight = 3.0 + player.knights_played * 0.5
            
            elif action.action_type == ActionType.BUILD_ROAD:
                # Roads mainly for longest road
                if game.state.board.longest_road_player != player.player_id:
                    weight = 3.0
                else:
                    weight = 1.0
            
            elif action.action_type == ActionType.MARITIME_TRADE:
                # Only good trades
                _, give_amount, _ = action.value
                if give_amount <= 3:
                    weight = 2.0
                else:
                    weight = 0.2  # Avoid 4:1
            
            elif action.action_type == ActionType.END_TURN:
                # End turn only if nothing good to do
                weight = 0.1
            
            weights.append(weight)
        
        # Weighted random choice
        total = sum(weights)
        r = random.uniform(0, total)
        cumsum = 0
        
        for action, weight in zip(actions, weights):
            cumsum += weight
            if r <= cumsum:
                return action
        
        return actions[-1]