"""
Game state representation for CatanDuel.

Simplified from catanatron for 2-player games. Uses fixed arrays
instead of dynamic player lists for better performance.
"""

from typing import List, Optional, Set, Tuple
from dataclasses import dataclass, field
import random
from copy import deepcopy

from engine.models.enums import (
    # Resources
    WOOD, BRICK, SHEEP, WHEAT, ORE, RESOURCES,
    # Development cards
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    DEVELOPMENT_CARDS, DEV_CARD_COUNTS,
    # Building types
    SETTLEMENT, CITY,
    # Game constants
    STARTING_RESOURCES_PER_TYPE, STARTING_SETTLEMENTS, STARTING_CITIES,
    STARTING_ROADS, HAND_LIMIT, MIN_LONGEST_ROAD, MIN_LARGEST_ARMY,
    VICTORY_POINTS_TO_WIN,
    # Actions
    ActionPrompt, Action, ActionType,
    # Players
    PLAYER_0, PLAYER_1, NUM_PLAYERS,
    # Board
    HEX_TYPE_DESERT
)
from engine.models.board import Board
from engine.colonist_map import (
    STANDARD_PORTS, PORT_EDGES, HEX_TO_CORNERS,
    get_adjacent_hexes, ALL_HEX_IDS,
    STANDARD_RESOURCES, STANDARD_NUMBERS
)


@dataclass
class PlayerState:
    """State for a single player."""
    # Resources [wood, brick, sheep, wheat, ore]
    resources: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    
    # Development cards in hand {card_type: count}
    dev_cards: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    
    # Dev cards bought this turn (can't play until next turn)
    dev_cards_bought_this_turn: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    
    # Building pieces remaining
    settlements_left: int = STARTING_SETTLEMENTS
    cities_left: int = STARTING_CITIES
    roads_left: int = STARTING_ROADS
    
    # Victory points
    public_vps: int = 0  # Visible to all
    hidden_vps: int = 0  # Victory point cards
    
    # Special achievements
    has_longest_road: bool = False
    has_largest_army: bool = False
    knights_played: int = 0
    
    # Turn state
    has_played_dev_card: bool = False
    
    def total_resources(self) -> int:
        """Total number of resource cards."""
        return sum(self.resources)
    
    def total_dev_cards(self) -> int:
        """Total number of development cards."""
        return sum(self.dev_cards)
    
    def actual_vps(self) -> int:
        """Total victory points including hidden ones."""
        return self.public_vps + self.hidden_vps
    
    def copy(self):
        """Create a deep copy."""
        return PlayerState(
            resources=self.resources.copy(),
            dev_cards=self.dev_cards.copy(),
            dev_cards_bought_this_turn=self.dev_cards_bought_this_turn.copy(),
            settlements_left=self.settlements_left,
            cities_left=self.cities_left,
            roads_left=self.roads_left,
            public_vps=self.public_vps,
            hidden_vps=self.hidden_vps,
            has_longest_road=self.has_longest_road,
            has_largest_army=self.has_largest_army,
            knights_played=self.knights_played,
            has_played_dev_card=self.has_played_dev_card
        )


@dataclass
class GameState:
    """
    Complete game state.
    
    This is the core data structure that represents everything about
    the current game situation.
    """
    # Board state
    board: Board = field(default_factory=Board)
    
    # Board configuration (set during initialization)
    hex_types: List[int] = field(default_factory=lambda: [0] * 19)
    hex_numbers: List[int] = field(default_factory=lambda: [0] * 19)
    port_edges: dict = field(default_factory=dict)
    
    # Player states
    players: List[PlayerState] = field(
        default_factory=lambda: [PlayerState(), PlayerState()]
    )
    
    # Resource bank
    resource_bank: List[int] = field(
        default_factory=lambda: [STARTING_RESOURCES_PER_TYPE] * 5
    )
    
    # Development card deck
    dev_card_deck: List[int] = field(default_factory=list)
    
    # Turn management
    current_player: int = PLAYER_0
    current_turn_player: int = PLAYER_0  # Whose turn it actually is
    dice_rolled: bool = False
    last_dice_roll: Optional[Tuple[int, int]] = None  # (die1, die2)
    current_prompt: ActionPrompt = ActionPrompt.BUILD_INITIAL_SETTLEMENT
    turn_number: int = 0
    
    # Special states
    is_discarding: bool = False
    is_moving_robber: bool = False
    is_road_building: bool = False
    
    # Initial build phase tracking
    initial_phase: bool = True
    initial_settlements_placed: int = 0
    
    # Action history (for replay/analysis)
    action_history: List[Action] = field(default_factory=list)
    
    # Valid actions cache (recomputed when state changes)
    _valid_actions_cache: Optional[List[Action]] = None
    
    def __post_init__(self):
        """Initialize the game state."""
        if not self.dev_card_deck:
            self._initialize_dev_deck()
    
    def _initialize_dev_deck(self):
        """Create and shuffle the development card deck."""
        self.dev_card_deck = []
        for card_type, count in DEV_CARD_COUNTS.items():
            self.dev_card_deck.extend([card_type] * count)
        random.shuffle(self.dev_card_deck)
    
    def copy(self) -> "GameState":
        """Create a deep copy of the game state."""
        # Create new instance without triggering __init__
        new_state = object.__new__(GameState)
        
        # Copy board
        new_state.board = self.board.copy()
        
        # Copy lists
        new_state.hex_types = self.hex_types.copy()
        new_state.hex_numbers = self.hex_numbers.copy()
        new_state.port_edges = self.port_edges.copy()
        
        # Copy player states
        new_state.players = [p.copy() for p in self.players]
        
        # Copy banks and decks
        new_state.resource_bank = self.resource_bank.copy()
        new_state.dev_card_deck = self.dev_card_deck.copy()
        
        # Copy turn state
        new_state.current_player = self.current_player
        new_state.current_turn_player = self.current_turn_player
        new_state.dice_rolled = self.dice_rolled
        new_state.last_dice_roll = self.last_dice_roll
        new_state.current_prompt = self.current_prompt
        new_state.turn_number = self.turn_number
        
        # Copy special states
        new_state.is_discarding = self.is_discarding
        new_state.is_moving_robber = self.is_moving_robber
        new_state.is_road_building = self.is_road_building
        
        # Copy phase tracking
        new_state.initial_phase = self.initial_phase
        new_state.initial_settlements_placed = self.initial_settlements_placed
        
        # Copy history (limit size for AI planning)
        new_state.action_history = self.action_history[-10:] if len(self.action_history) > 10 else self.action_history.copy()
        
        # Don't copy cache
        new_state._valid_actions_cache = None
        
        return new_state
    
    def current_player_state(self) -> PlayerState:
        """Get the current player's state."""
        return self.players[self.current_player]
    
    def get_player_state(self, player_id: int) -> PlayerState:
        """Get a specific player's state."""
        return self.players[player_id]
    
    def has_ended(self) -> bool:
        """Check if the game has ended."""
        return any(p.actual_vps() >= VICTORY_POINTS_TO_WIN for p in self.players)
    
    def get_winner(self) -> Optional[int]:
        """Get the winning player ID, or None if game not over."""
        for i, player in enumerate(self.players):
            if player.actual_vps() >= VICTORY_POINTS_TO_WIN:
                return i
        return None
    
    def is_setup_phase(self) -> bool:
        """Check if we're still in the initial setup phase."""
        return self.initial_phase
    
    def setup_phase_player_order(self) -> int:
        """
        Get which player should act during setup phase.
        
        Order is: P0, P1, P1, P0 for settlements/roads
        Each player places settlement then road before switching.
        """
        # Count total actions (settlements + roads)
        roads_placed = len(self.board.roads)
        total_actions = self.initial_settlements_placed + roads_placed
        
        # Pattern: P0-settle, P0-road, P1-settle, P1-road, P1-settle, P1-road, P0-settle, P0-road
        # Actions:     0          1         2          3         4          5         6          7
        if total_actions < 2:
            return 0  # P0 first settlement and road
        elif total_actions < 4:
            return 1  # P1 first settlement and road  
        elif total_actions < 6:
            return 1  # P1 second settlement and road
        else:
            return 0  # P0 second settlement and road
    
    def can_afford(self, player_id: int, cost: List[int]) -> bool:
        """Check if a player can afford a cost."""
        player = self.players[player_id]
        for i, amount in enumerate(cost):
            if player.resources[i] < amount:
                return False
        return True
    
    def bank_has_resources(self, resources: List[int]) -> bool:
        """Check if the bank has enough resources."""
        for i, amount in enumerate(resources):
            if self.resource_bank[i] < amount:
                return False
        return True
    
    def invalidate_actions_cache(self):
        """Clear the cached valid actions."""
        self._valid_actions_cache = None
    
    def generate_board(self, 
                      resources: Optional[List[int]] = None,
                      numbers: Optional[List[int]] = None,
                      ports: Optional[dict] = None):
        """
        Generate a random board configuration.
        
        Args:
            resources: Optional fixed resource layout
            numbers: Optional fixed number layout
            ports: Optional fixed port layout
        """
        # Use provided layouts or generate random ones
        if resources is None:
            resources = STANDARD_RESOURCES.copy()
            random.shuffle(resources)
        if numbers is None:
            numbers = STANDARD_NUMBERS.copy()
            random.shuffle(numbers)
        if ports is None:
            # Randomly assign ports to the standard port edges
            port_types = STANDARD_PORTS.copy()
            random.shuffle(port_types)
            ports = {}
            for edge, port_type in zip(sorted(PORT_EDGES.keys()), port_types):
                ports[edge] = port_type
        
        # Assign resources and numbers to hexes
        number_idx = 0
        for hex_id in ALL_HEX_IDS:
            self.hex_types[hex_id] = resources[hex_id]
            
            if resources[hex_id] == HEX_TYPE_DESERT:
                self.hex_numbers[hex_id] = 0  # No number on desert
                self.board.robber_hex = hex_id
            else:
                self.hex_numbers[hex_id] = numbers[number_idx]
                number_idx += 1
        
        # Apply board balance rules
        self._apply_balance_rules()
        
        # Set ports
        self.port_edges = ports
    
    def _apply_balance_rules(self):
        """
        Apply board balance rules:
        - No identical numbers on adjacent hexes
        - No 6 and 8 on adjacent hexes
        """
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            valid = True
            
            # Check all hex pairs
            for hex_id in ALL_HEX_IDS:
                if self.hex_types[hex_id] == HEX_TYPE_DESERT:
                    continue
                    
                current_number = self.hex_numbers[hex_id]
                
                for adj_hex in get_adjacent_hexes(hex_id):
                    if self.hex_types[adj_hex] == HEX_TYPE_DESERT:
                        continue
                    
                    adj_number = self.hex_numbers[adj_hex]
                    
                    # Check identical numbers
                    if current_number == adj_number:
                        valid = False
                        break
                    
                    # Check 6/8 adjacency
                    if {current_number, adj_number} == {6, 8}:
                        valid = False
                        break
                
                if not valid:
                    break
            
            if valid:
                return  # Board is valid
            
            # Swap two random non-desert hex numbers
            non_desert_hexes = [
                h for h in ALL_HEX_IDS 
                if self.hex_types[h] != HEX_TYPE_DESERT
            ]
            if len(non_desert_hexes) >= 2:
                hex1, hex2 = random.sample(non_desert_hexes, 2)
                self.hex_numbers[hex1], self.hex_numbers[hex2] = \
                    self.hex_numbers[hex2], self.hex_numbers[hex1]
            
            attempts += 1
        
        # If we couldn't find a valid configuration, just use what we have
        print(f"Warning: Could not satisfy all balance rules after {max_attempts} attempts")