"""
Core enumerations and constants for CatanDuel.

Based on catanatron's enums but simplified for 1v1 gameplay.
Removes player-to-player trading and supports only 2 players.
"""

from enum import Enum
from collections import namedtuple
from typing import Literal, Final, List

# Resources - using integers for efficient array indexing
# Colonist.io uses 1-5, we use 0-4 internally for array operations
WOOD: Final = 0
BRICK: Final = 1
SHEEP: Final = 2
WHEAT: Final = 3
ORE: Final = 4

# Type hints
FastResource = Literal[0, 1, 2, 3, 4]
RESOURCES: List[FastResource] = [WOOD, BRICK, SHEEP, WHEAT, ORE]
RESOURCE_NAMES = ["WOOD", "BRICK", "SHEEP", "WHEAT", "ORE"]

# Development Cards
KNIGHT: Final = 0
YEAR_OF_PLENTY: Final = 1
MONOPOLY: Final = 2
ROAD_BUILDING: Final = 3
VICTORY_POINT: Final = 4

FastDevCard = Literal[0, 1, 2, 3, 4]
DEVELOPMENT_CARDS: List[FastDevCard] = [
    KNIGHT,
    YEAR_OF_PLENTY,
    MONOPOLY,
    ROAD_BUILDING,
    VICTORY_POINT,
]
DEV_CARD_NAMES = ["KNIGHT", "YEAR_OF_PLENTY", "MONOPOLY", "ROAD_BUILDING", "VICTORY_POINT"]

# Building Types
SETTLEMENT: Final = 1  # Match colonist.io
CITY: Final = 2        # Match colonist.io
ROAD: Final = 0        # Internal use

FastBuildingType = Literal[0, 1, 2]
BUILDING_NAMES = ["ROAD", "SETTLEMENT", "CITY"]

# Hex Types (matching colonist.io)
HEX_TYPE_DESERT: Final = 0
HEX_TYPE_WOOD: Final = 1
HEX_TYPE_BRICK: Final = 2
HEX_TYPE_SHEEP: Final = 3
HEX_TYPE_WHEAT: Final = 4
HEX_TYPE_ORE: Final = 5

# Port Types (matching colonist.io)
PORT_TYPE_3_1: Final = 1
PORT_TYPE_WOOD: Final = 2
PORT_TYPE_BRICK: Final = 3
PORT_TYPE_SHEEP: Final = 4
PORT_TYPE_WHEAT: Final = 5
PORT_TYPE_ORE: Final = 6

# Players - simple 0/1 system
PLAYER_0: Final = 0
PLAYER_1: Final = 1
NUM_PLAYERS: Final = 2

# Game Constants
STARTING_RESOURCES_PER_TYPE: Final = 19
STARTING_SETTLEMENTS: Final = 5
STARTING_CITIES: Final = 4
STARTING_ROADS: Final = 15
VICTORY_POINTS_TO_WIN: Final = 10
HAND_LIMIT: Final = 7
MIN_LONGEST_ROAD: Final = 5
MIN_LARGEST_ARMY: Final = 3

# Development Card Deck Composition
DEV_CARD_COUNTS = {
    KNIGHT: 14,
    VICTORY_POINT: 5,
    ROAD_BUILDING: 2,
    YEAR_OF_PLENTY: 2,
    MONOPOLY: 2,
}

# Dice
DICE_VALUES = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]  # Note: no 7
DICE_PROBABILITIES = {
    2: 1/36,
    3: 2/36,
    4: 3/36,
    5: 4/36,
    6: 5/36,
    7: 6/36,  # Robber
    8: 5/36,
    9: 4/36,
    10: 3/36,
    11: 2/36,
    12: 1/36,
}


class ActionPrompt(Enum):
    """Prompts that determine what kind of action the game is waiting for."""
    BUILD_INITIAL_SETTLEMENT = "BUILD_INITIAL_SETTLEMENT"
    BUILD_INITIAL_ROAD = "BUILD_INITIAL_ROAD"
    PLAY_TURN = "PLAY_TURN"
    DISCARD = "DISCARD"
    MOVE_ROBBER = "MOVE_ROBBER"


class ActionType(Enum):
    """
    Types of actions a player can take.
    
    Simplified from catanatron - removed all player-to-player trading actions.
    """
    # Basic turn actions
    ROLL = "ROLL"
    END_TURN = "END_TURN"
    
    # Robber actions
    MOVE_ROBBER = "MOVE_ROBBER"  # value: (hex_id, player_to_steal_from)
    DISCARD = "DISCARD"  # value: [wood, brick, sheep, wheat, ore] to discard
    
    # Building actions
    BUILD_ROAD = "BUILD_ROAD"  # value: edge_id
    BUILD_SETTLEMENT = "BUILD_SETTLEMENT"  # value: corner_id
    BUILD_CITY = "BUILD_CITY"  # value: corner_id
    BUY_DEVELOPMENT_CARD = "BUY_DEVELOPMENT_CARD"  # value: None
    
    # Initial setup actions  
    BUILD_INITIAL_SETTLEMENT = "BUILD_INITIAL_SETTLEMENT"  # value: corner_id
    BUILD_INITIAL_ROAD = "BUILD_INITIAL_ROAD"  # value: edge_id
    
    # Development card actions
    PLAY_KNIGHT_CARD = "PLAY_KNIGHT_CARD"  # value: None
    PLAY_YEAR_OF_PLENTY = "PLAY_YEAR_OF_PLENTY"  # value: (resource1, resource2)
    PLAY_MONOPOLY = "PLAY_MONOPOLY"  # value: resource
    PLAY_ROAD_BUILDING = "PLAY_ROAD_BUILDING"  # value: None
    
    # Maritime trade only (no player-to-player trading)
    MARITIME_TRADE = "MARITIME_TRADE"  # value: (give_resource, give_amount, receive_resource)


# Action namedtuple - simplified without player field
Action = namedtuple("Action", ["action_type", "value"])
Action.__doc__ = """
Represents a player action in the game.

Attributes:
    action_type: Type of action from ActionType enum
    value: Parameters for the action (varies by action_type)
"""

# Building costs (as resource arrays: [wood, brick, sheep, wheat, ore])
ROAD_COST = [1, 1, 0, 0, 0]
SETTLEMENT_COST = [1, 1, 1, 1, 0]
CITY_COST = [0, 0, 0, 2, 3]
DEV_CARD_COST = [0, 0, 1, 1, 1]

# Helper function to create resource arrays
def resource_array(wood=0, brick=0, sheep=0, wheat=0, ore=0):
    """Create a resource array in the standard order."""
    return [wood, brick, sheep, wheat, ore]

# String names for display (overriding the integer lists above)
RESOURCES = ["wood", "brick", "sheep", "wheat", "ore"]
DEVELOPMENT_CARDS = ["knight", "year_of_plenty", "monopoly", "road_building", "victory_point"]