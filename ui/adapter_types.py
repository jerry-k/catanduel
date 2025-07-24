"""
Data structures for UI-Engine communication.

These types represent the format expected by the JavaScript UI,
based on the rlcatan interface design.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum


class UIPhase(str, Enum):
    """Game phase from UI perspective"""
    SETUP = "setup"
    MAIN = "main"
    DISCARD = "discard"
    ROBBER = "robber"
    ROAD_BUILDING = "road_building"
    YEAR_OF_PLENTY = "year_of_plenty"
    MONOPOLY = "monopoly"


class UIActionType(str, Enum):
    """Action types that the UI can send"""
    # Setup actions
    BUILD_INITIAL_SETTLEMENT = "BUILD_INITIAL_SETTLEMENT"
    BUILD_INITIAL_ROAD = "BUILD_INITIAL_ROAD"
    
    # Main game actions
    ROLL = "ROLL"
    END_TURN = "END_TURN"
    
    # Building actions
    BUILD_ROAD = "BUILD_ROAD"
    BUILD_SETTLEMENT = "BUILD_SETTLEMENT"
    BUILD_CITY = "BUILD_CITY"
    BUY_DEVELOPMENT_CARD = "BUY_DEVELOPMENT_CARD"
    
    # Special actions
    MOVE_ROBBER = "MOVE_ROBBER"
    DISCARD = "DISCARD"
    
    # Development card actions
    PLAY_KNIGHT = "PLAY_KNIGHT"
    PLAY_ROAD_BUILDING = "PLAY_ROAD_BUILDING"
    PLAY_YEAR_OF_PLENTY = "PLAY_YEAR_OF_PLENTY"
    PLAY_MONOPOLY = "PLAY_MONOPOLY"
    
    # Trading
    MARITIME_TRADE = "MARITIME_TRADE"


@dataclass
class UIResources:
    """Resource counts in object format for UI"""
    wood: int = 0
    brick: int = 0
    sheep: int = 0
    wheat: int = 0
    ore: int = 0
    
    def to_array(self) -> List[int]:
        """Convert to engine format [wood, brick, sheep, wheat, ore]"""
        return [self.wood, self.brick, self.sheep, self.wheat, self.ore]
    
    @classmethod
    def from_array(cls, arr: List[int]) -> 'UIResources':
        """Create from engine format array"""
        return cls(wood=arr[0], brick=arr[1], sheep=arr[2], wheat=arr[3], ore=arr[4])
    
    def total(self) -> int:
        """Total number of resources"""
        return self.wood + self.brick + self.sheep + self.wheat + self.ore


@dataclass
class UIDevCards:
    """Development cards in object format"""
    knight: int = 0
    victory_point: int = 0
    road_building: int = 0
    year_of_plenty: int = 0
    monopoly: int = 0
    
    def to_array(self) -> List[int]:
        """Convert to engine format"""
        return [self.knight, self.year_of_plenty, self.monopoly, 
                self.road_building, self.victory_point]
    
    @classmethod
    def from_array(cls, arr: List[int]) -> 'UIDevCards':
        """Create from engine format array"""
        return cls(
            knight=arr[0],
            year_of_plenty=arr[1],
            monopoly=arr[2],
            road_building=arr[3],
            victory_point=arr[4]
        )
    
    def total(self) -> int:
        """Total number of dev cards"""
        return (self.knight + self.victory_point + self.road_building + 
                self.year_of_plenty + self.monopoly)


@dataclass
class UIHex:
    """Hex representation for UI"""
    id: int
    type: str  # "forest", "hills", "pasture", "fields", "mountains", "desert"
    number: Optional[int] = None
    has_robber: bool = False


@dataclass
class UIBuilding:
    """Building representation for UI"""
    type: str  # "settlement", "city", "road"
    player: int  # 0 or 1
    location: Union[int, Tuple[int, int]]  # corner_id or edge_id for roads


@dataclass
class UIPort:
    """Port representation for UI"""
    edge_id: int
    type: str  # "3:1", "wood", "brick", "sheep", "wheat", "ore"


@dataclass
class UIPlayer:
    """Player state for UI"""
    id: int
    name: str
    color: str  # "red" or "blue"
    resources: UIResources
    dev_cards: UIDevCards
    
    # Building counts
    settlements_left: int
    cities_left: int
    roads_left: int
    
    # Victory points
    public_vps: int
    
    # Special achievements
    has_longest_road: bool = False
    has_largest_army: bool = False
    knights_played: int = 0
    longest_road_length: int = 0
    
    # UI specific
    is_active: bool = False
    is_human: bool = True


@dataclass
class UIBoard:
    """Board state for UI"""
    hexes: List[UIHex]
    buildings: List[UIBuilding]
    ports: List[UIPort]
    robber_hex: int


@dataclass
class UIAction:
    """Action from UI to engine"""
    type: UIActionType
    data: Dict[str, Union[int, List[int], None]] = field(default_factory=dict)


@dataclass
class UIGameState:
    """Complete game state for UI"""
    # Game info
    phase: UIPhase
    current_player: int
    turn_number: int
    
    # Board state
    board: UIBoard
    
    # Player states
    players: List[UIPlayer]
    
    # Current turn info
    dice_rolled: bool = False
    last_roll: Optional[Tuple[int, int]] = None
    
    # Valid actions for current state
    valid_actions: List[UIAction] = field(default_factory=list)
    
    # UI helpers
    message: str = ""
    can_end_turn: bool = False
    
    # Special states
    discard_required: Optional[Dict[int, int]] = None  # player_id -> cards_to_discard
    robber_steal_options: Optional[List[int]] = None  # player IDs that can be stolen from
    road_building_remaining: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'phase': self.phase.value,
            'current_player': self.current_player,
            'turn_number': self.turn_number,
            'board': {
                'hexes': [
                    {
                        'id': h.id,
                        'type': h.type,
                        'number': h.number,
                        'has_robber': h.has_robber
                    } for h in self.board.hexes
                ],
                'buildings': [
                    {
                        'type': b.type,
                        'player': b.player,
                        'location': b.location
                    } for b in self.board.buildings
                ],
                'ports': [
                    {
                        'edge_id': p.edge_id,
                        'type': p.type
                    } for p in self.board.ports
                ],
                'robber_hex': self.board.robber_hex
            },
            'players': [
                {
                    'id': p.id,
                    'name': p.name,
                    'color': p.color,
                    'resources': {
                        'wood': p.resources.wood,
                        'brick': p.resources.brick,
                        'sheep': p.resources.sheep,
                        'wheat': p.resources.wheat,
                        'ore': p.resources.ore
                    },
                    'dev_cards': {
                        'knight': p.dev_cards.knight,
                        'victory_point': p.dev_cards.victory_point,
                        'road_building': p.dev_cards.road_building,
                        'year_of_plenty': p.dev_cards.year_of_plenty,
                        'monopoly': p.dev_cards.monopoly
                    },
                    'settlements_left': p.settlements_left,
                    'cities_left': p.cities_left,
                    'roads_left': p.roads_left,
                    'public_vps': p.public_vps,
                    'has_longest_road': p.has_longest_road,
                    'has_largest_army': p.has_largest_army,
                    'knights_played': p.knights_played,
                    'is_active': p.is_active,
                    'is_human': p.is_human
                } for p in self.players
            ],
            'dice_rolled': self.dice_rolled,
            'last_roll': self.last_roll,
            'valid_actions': [
                {
                    'type': a.type.value,
                    'data': a.data
                } for a in self.valid_actions
            ],
            'message': self.message,
            'can_end_turn': self.can_end_turn,
            'discard_required': self.discard_required,
            'robber_steal_options': self.robber_steal_options,
            'road_building_remaining': self.road_building_remaining
        }


@dataclass
class UIEvent:
    """Event for UI animations/updates"""
    type: str  # "resource_gained", "building_placed", "dice_rolled", etc.
    player: Optional[int] = None
    data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON"""
        return {
            'type': self.type,
            'player': self.player,
            'data': self.data
        }


# Hex type mappings
HEX_TYPE_TO_UI = {
    0: "desert",
    1: "forest",
    2: "hills",
    3: "pasture",
    4: "fields",
    5: "mountains"
}

UI_TO_HEX_TYPE = {v: k for k, v in HEX_TYPE_TO_UI.items()}

# Resource name mappings
RESOURCE_NAMES = ["wood", "brick", "sheep", "wheat", "ore"]

# Port type mappings  
PORT_TYPE_TO_UI = {
    1: "3:1",
    2: "wood",
    3: "brick",
    4: "sheep",
    5: "wheat",
    6: "ore"
}

UI_TO_PORT_TYPE = {v: k for k, v in PORT_TYPE_TO_UI.items()}