"""
Main game controller for CatanDuel.

This is the main interface for running games. It handles:
- Game initialization and board generation
- Action execution
- Game flow control
- Win condition checking

Based on catanatron's game.py but simplified for 2 players.
"""

from typing import List, Optional, Tuple, Dict
import random
from copy import deepcopy

from models.enums import (
    Action, ActionType, ActionPrompt,
    PLAYER_0, PLAYER_1,
    VICTORY_POINTS_TO_WIN,
    # Resources
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    # Development cards
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    # For debugging
    RESOURCES, DEVELOPMENT_CARDS
)
from models.player import Player
from models.actions import generate_actions
from state import GameState
import state_functions as sf


class Game:
    """
    Main game controller.
    
    This class manages the overall game flow, from initialization
    through gameplay to determining the winner.
    """
    
    def __init__(self, players: List[Player], seed: Optional[int] = None):
        """
        Initialize a new game.
        
        Args:
            players: List of 2 Player objects
            seed: Random seed for reproducibility
        """
        if len(players) != 2:
            raise ValueError("CatanDuel requires exactly 2 players")
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
        
        # Store players
        self.players = players
        
        # Initialize game state
        self.state = GameState()
        
        # Generate random board
        self.state.generate_board()
        
        # Track game history
        self.action_history: List[Tuple[int, Action]] = []
        
    def copy(self) -> "Game":
        """Create a deep copy of the game."""
        new_game = Game.__new__(Game)
        new_game.players = self.players  # Players are stateless, can share
        new_game.state = self.state.copy()
        new_game.action_history = self.action_history.copy()
        return new_game
    
    def execute(self, action: Action, validate: bool = True) -> bool:
        """
        Execute an action.
        
        Args:
            action: The action to execute
            validate: Whether to validate the action first
            
        Returns:
            True if action was executed, False if invalid
        """
        # Validate if requested
        if validate:
            valid_actions = self.get_valid_actions()
            if action not in valid_actions:
                return False
        
        # Get current player
        player_id = self._get_acting_player()
        
        # Record action in history
        self.action_history.append((player_id, action))
        self.state.action_history.append(action)
        
        # Invalidate action cache
        self.state.invalidate_actions_cache()
        
        # Execute based on action type
        if action.action_type == ActionType.BUILD_INITIAL_SETTLEMENT:
            sf.place_initial_settlement(self.state, player_id, action.value)
            self._check_setup_phase_complete()
            
        elif action.action_type == ActionType.BUILD_INITIAL_ROAD:
            sf.place_initial_road(self.state, player_id, action.value)
            self._check_setup_phase_complete()
            
        elif action.action_type == ActionType.ROLL:
            die1, die2 = sf.roll_dice(self.state)
            # State functions handle prompt changes
            
        elif action.action_type == ActionType.DISCARD:
            sf.discard_resources(self.state, player_id, action.value)
            
        elif action.action_type == ActionType.MOVE_ROBBER:
            hex_id, victim_id = action.value
            sf.move_robber(self.state, hex_id, victim_id)
            
        elif action.action_type == ActionType.BUILD_SETTLEMENT:
            sf.build_settlement(self.state, player_id, action.value)
            
        elif action.action_type == ActionType.BUILD_CITY:
            sf.build_city(self.state, player_id, action.value)
            
        elif action.action_type == ActionType.BUILD_ROAD:
            sf.build_road(self.state, player_id, action.value)
            
        elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
            sf.buy_development_card(self.state, player_id)
            
        elif action.action_type == ActionType.PLAY_KNIGHT_CARD:
            sf.play_knight(self.state, player_id)
            # Prompt changes to MOVE_ROBBER
            
        elif action.action_type == ActionType.PLAY_YEAR_OF_PLENTY:
            res1, res2 = action.value
            sf.play_year_of_plenty(self.state, player_id, res1, res2)
            
        elif action.action_type == ActionType.PLAY_MONOPOLY:
            sf.play_monopoly(self.state, player_id, action.value)
            
        elif action.action_type == ActionType.PLAY_ROAD_BUILDING:
            sf.play_road_building(self.state, player_id)
            
        elif action.action_type == ActionType.MARITIME_TRADE:
            give_res, give_amount, get_res = action.value
            sf.maritime_trade(self.state, player_id, give_res, give_amount, get_res)
            
        elif action.action_type == ActionType.END_TURN:
            sf.end_turn(self.state)
        
        return True
    
    def get_valid_actions(self) -> List[Action]:
        """Get all valid actions for the current player."""
        return generate_actions(self.state)
    
    def is_over(self) -> bool:
        """Check if the game has ended."""
        return self.state.has_ended()
    
    def get_winner(self) -> Optional[Player]:
        """Get the winning player, or None if game not over."""
        winner_id = self.state.get_winner()
        if winner_id is not None:
            return self.players[winner_id]
        return None
    
    def play(self, max_turns: int = 1000) -> Optional[Player]:
        """
        Play a complete game.
        
        Args:
            max_turns: Maximum number of turns before declaring a draw
            
        Returns:
            The winning player, or None if draw
        """
        turns = 0
        
        while not self.is_over() and turns < max_turns:
            # Get current player
            player = self._get_current_player()
            
            # Get valid actions
            valid_actions = self.get_valid_actions()
            
            if not valid_actions:
                # No valid actions (shouldn't happen in a well-formed game)
                print(f"Warning: No valid actions for player {player.player_id}")
                print(f"Current prompt: {self.state.current_prompt}")
                print(f"Dice rolled: {self.state.dice_rolled}")
                print(f"Initial phase: {self.state.initial_phase}")
                break
            
            # Let player decide
            action = player.decide(self, valid_actions)
            
            # Execute action
            success = self.execute(action, validate=True)
            if not success:
                print(f"Warning: Player {player.player_id} chose invalid action: {action}")
                # In a tournament, this might be a forfeit
                break
            
            # Count turns (only full turns after setup)
            if not self.state.is_setup_phase() and self.state.current_player == PLAYER_1:
                turns += 1
        
        return self.get_winner()
    
    def _get_acting_player(self) -> int:
        """Get the player who should act next."""
        if self.state.is_setup_phase():
            return self.state.setup_phase_player_order()
        else:
            # During discard or robber, current_player is already set correctly
            return self.state.current_player
    
    def _get_current_player(self) -> Player:
        """Get the current Player object."""
        player_id = self._get_acting_player()
        return self.players[player_id]
    
    def _check_setup_phase_complete(self):
        """Check if setup phase is complete and transition if needed."""
        # Each player places 2 settlements and 2 roads
        roads_placed = len(self.state.board.roads)
        if self.state.initial_settlements_placed >= 4 and roads_placed >= 4:
            # Last road placed, setup complete
            sf.complete_setup_phase(self.state)
        else:
            # Determine next prompt
            settlements = self.state.initial_settlements_placed
            roads_placed = len(self.state.board.roads)
            
            if roads_placed < settlements:
                # Need to place road for current settlement
                self.state.current_prompt = ActionPrompt.BUILD_INITIAL_ROAD
            else:
                # Need to place next settlement
                self.state.current_prompt = ActionPrompt.BUILD_INITIAL_SETTLEMENT
    
    def get_game_info(self) -> Dict:
        """
        Get current game information for display/debugging.
        
        Returns a dictionary with useful game state information.
        """
        info = {
            'turn': self.state.turn_number,
            'current_player': self.state.current_player,
            'prompt': self.state.current_prompt.value,
            'dice_rolled': self.state.dice_rolled,
            'robber_hex': self.state.board.robber_hex,
            'longest_road': {
                'player': self.state.board.longest_road_player,
                'length': self.state.board.longest_road_length
            },
            'players': []
        }
        
        # Add player info
        for i, player in enumerate(self.players):
            player_state = self.state.players[i]
            player_info = {
                'id': i,
                'name': player.name,
                'resources': dict(zip(RESOURCES, player_state.resources)),
                'total_resources': player_state.total_resources(),
                'dev_cards': dict(zip(DEVELOPMENT_CARDS, player_state.dev_cards)),
                'dev_cards_bought': dict(zip(DEVELOPMENT_CARDS, player_state.dev_cards_bought_this_turn)),
                'knights_played': player_state.knights_played,
                'public_vps': player_state.public_vps,
                'hidden_vps': player_state.hidden_vps,
                'total_vps': player_state.actual_vps(),
                'has_longest_road': player_state.has_longest_road,
                'has_largest_army': player_state.has_largest_army,
                'settlements_left': player_state.settlements_left,
                'cities_left': player_state.cities_left,
                'roads_left': player_state.roads_left,
                'buildings': {
                    'settlements': len(self.state.board.get_player_buildings(i)[0]),
                    'cities': len(self.state.board.get_player_buildings(i)[1]),
                    'roads': len(self.state.board.get_player_roads(i))
                }
            }
            info['players'].append(player_info)
        
        # Add bank info
        info['resource_bank'] = dict(zip(RESOURCES, self.state.resource_bank))
        info['dev_cards_left'] = len(self.state.dev_card_deck)
        
        return info
    
    def render(self):
        """Print a text representation of the game state."""
        info = self.get_game_info()
        
        print(f"\n=== Turn {info['turn']} - Player {info['current_player']} ===")
        print(f"State: {info['prompt']}")
        print(f"Dice rolled: {info['dice_rolled']}")
        print(f"Robber on hex: {info['robber_hex']}")
        
        if info['longest_road']['player'] is not None:
            print(f"Longest road: Player {info['longest_road']['player']} ({info['longest_road']['length']})")
        
        for p in info['players']:
            print(f"\nPlayer {p['id']} ({p['name']}):")
            print(f"  VPs: {p['public_vps']} public + {p['hidden_vps']} hidden = {p['total_vps']}")
            print(f"  Resources: {p['total_resources']} total -", end='')
            for res, count in p['resources'].items():
                if count > 0:
                    print(f" {res}:{count}", end='')
            print()
            print(f"  Dev cards: {sum(p['dev_cards'].values())} -", end='')
            for card, count in p['dev_cards'].items():
                if count > 0:
                    print(f" {card}:{count}", end='')
            print()
            print(f"  Knights: {p['knights_played']}")
            print(f"  Buildings: {p['buildings']['settlements']}S {p['buildings']['cities']}C {p['buildings']['roads']}R")
            if p['has_longest_road']:
                print("  Has longest road!")
            if p['has_largest_army']:
                print("  Has largest army!")
        
        print(f"\nBank: {info['dev_cards_left']} dev cards")
        print("Resources:", end='')
        for res, count in info['resource_bank'].items():
            print(f" {res}:{count}", end='')
        print()


def play_random_game(seed: Optional[int] = None) -> Tuple[Optional[Player], int]:
    """
    Play a game with two random players.
    
    Returns:
        (winner, number_of_turns)
    """
    from models.player import RandomPlayer
    
    players = [
        RandomPlayer(0, "Random 0"),
        RandomPlayer(1, "Random 1")
    ]
    
    game = Game(players, seed=seed)
    winner = game.play()
    
    return winner, game.state.turn_number


def benchmark_games(n_games: int = 100) -> Dict:
    """
    Run multiple games for benchmarking.
    
    Returns statistics about the games.
    """
    import time
    
    wins = [0, 0]
    total_turns = 0
    min_turns = float('inf')
    max_turns = 0
    
    start_time = time.time()
    
    for i in range(n_games):
        winner, turns = play_random_game(seed=i)
        
        if winner:
            wins[winner.player_id] += 1
        
        total_turns += turns
        min_turns = min(min_turns, turns)
        max_turns = max(max_turns, turns)
    
    end_time = time.time()
    duration = end_time - start_time
    
    return {
        'games': n_games,
        'duration': duration,
        'games_per_second': n_games / duration,
        'wins': {'player_0': wins[0], 'player_1': wins[1]},
        'win_rates': {
            'player_0': wins[0] / n_games,
            'player_1': wins[1] / n_games
        },
        'turns': {
            'average': total_turns / n_games,
            'min': min_turns,
            'max': max_turns
        }
    }


if __name__ == "__main__":
    # Quick test
    print("Running benchmark with 100 random games...")
    stats = benchmark_games(100)
    
    print(f"\nCompleted {stats['games']} games in {stats['duration']:.2f} seconds")
    print(f"Performance: {stats['games_per_second']:.1f} games/second")
    print(f"\nWin rates: P0={stats['win_rates']['player_0']:.1%}, P1={stats['win_rates']['player_1']:.1%}")
    print(f"Turns: avg={stats['turns']['average']:.1f}, min={stats['turns']['min']}, max={stats['turns']['max']}")