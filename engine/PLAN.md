# CatanDuel Engine - Development Plan

## Overview

CatanDuel is a high-performance 1v1 Settlers of Catan engine designed specifically for AI development. **This is essentially a fork of catanatron**, keeping ~90% of its proven architecture and implementation patterns while making minimal changes for 1v1 gameplay and colonist.io compatibility.

### Implementation Philosophy

**Stay as close to catanatron as possible.** When in doubt, copy catanatron's approach exactly. Only deviate when necessary for:
- 2-player simplifications (removing player lists → fixed arrays)
- Colonist.io coordinate compatibility
- Removing player-to-player trading

This approach ensures we inherit catanatron's reliability, performance optimizations, and battle-tested game logic.

### Project Goals

1. **Primary Goal**: Create an AI capable of beating a 1900 ELO colonist.io player (top 10%)
2. **Performance**: Run 1000+ games per second for training
3. **Compatibility**: Use colonist.io's exact coordinate system for potential replay analysis
4. **Reliability**: Bug-free implementation with catanatron's proven patterns
5. **Simplicity**: Remove unnecessary complexity from 4-player variants

### Key Design Decisions

1. **Architecture**: Based on catanatron's immutable state pattern
2. **Players**: Exactly 2 players (Player 0 and Player 1)
3. **Trading**: Maritime trading only (4:1, 3:1, 2:1 ports)
4. **Coordinates**: Native colonist.io system (hexes 0-18, corners 0-53, edges 0-71)
5. **State**: Simplified representation optimized for 1v1

### What We're Building

A complete Catan game engine that:
- Implements all official 1v1 Catan rules
- Provides a clean API for AI development
- Runs efficiently for large-scale training
- Maintains compatibility with colonist.io for data analysis
- Supports multiple AI strategies (minimax, MCTS, neural networks)

### What We're NOT Building

- 3-4 player support
- Player-to-player trading
- UI/graphics (initially)
- Network multiplayer
- Expansions (Cities & Knights, etc.)

## Architecture Overview

```
catanduel/
├── engine/
│   ├── models/
│   │   ├── enums.py          # Constants and enumerations
│   │   ├── board.py          # Board topology and building placement
│   │   ├── actions.py        # Action generation and validation
│   │   └── player.py         # Player interface
│   ├── state.py              # Game state representation
│   ├── state_functions.py    # Pure functions for state manipulation
│   ├── game.py               # Main game controller
│   ├── colonist_map.py       # Colonist.io coordinate mappings
│   └── features.py           # Feature extraction for AI
├── ai/
│   ├── base_ai.py            # Base AI class
│   ├── minimax.py            # Minimax with alpha-beta pruning
│   ├── mcts.py               # Monte Carlo Tree Search
│   └── evaluation.py         # Board evaluation functions
└── tests/
    ├── test_state.py
    ├── test_actions.py
    └── test_game.py
```

## Detailed Component Specifications

### 1. Core Enumerations (`models/enums.py`)

Define all game constants matching colonist.io's system:

```python
# Resources (colonist.io uses 1-5, we'll use 0-4 internally)
# Colonist: 1=Wood, 2=Brick, 3=Sheep, 4=Wheat, 5=Ore
WOOD = 0
BRICK = 1
SHEEP = 2
WHEAT = 3
ORE = 4

# Hex Types (from colonist.io)
# 0=Desert, 1=Wood, 2=Brick, 3=Sheep, 4=Wheat, 5=Ore
HEX_TYPE_DESERT = 0
HEX_TYPE_WOOD = 1
HEX_TYPE_BRICK = 2
HEX_TYPE_SHEEP = 3
HEX_TYPE_WHEAT = 4
HEX_TYPE_ORE = 5

# Players - simple 0/1 system
PLAYER_0 = 0  # First player
PLAYER_1 = 1  # Second player

# When parsing colonist.io logs:
# - Map first player in playOrder to PLAYER_0
# - Map second player in playOrder to PLAYER_1
# - Ignore actual color codes (1-5)

# Development Cards
KNIGHT = 0
YEAR_OF_PLENTY = 1
MONOPOLY = 2
ROAD_BUILDING = 3
VICTORY_POINT = 4

# Action Types
class ActionType(Enum):
    ROLL = "ROLL"
    MOVE_ROBBER = "MOVE_ROBBER"
    DISCARD = "DISCARD"
    BUILD_ROAD = "BUILD_ROAD"
    BUILD_SETTLEMENT = "BUILD_SETTLEMENT"
    BUILD_CITY = "BUILD_CITY"
    BUY_DEVELOPMENT_CARD = "BUY_DEVELOPMENT_CARD"
    PLAY_KNIGHT = "PLAY_KNIGHT"
    PLAY_YEAR_OF_PLENTY = "PLAY_YEAR_OF_PLENTY"
    PLAY_MONOPOLY = "PLAY_MONOPOLY"
    PLAY_ROAD_BUILDING = "PLAY_ROAD_BUILDING"
    MARITIME_TRADE = "MARITIME_TRADE"
    END_TURN = "END_TURN"
```

### 2. Game State (`state.py`)

Simplified state representation for 1v1:

```python
class GameState:
    def __init__(self):
        # Player resources [wood, brick, sheep, wheat, ore]
        self.player_resources = [[0,0,0,0,0], [0,0,0,0,0]]
        
        # Development cards {card_type: count}
        self.player_dev_cards = [{}, {}]
        self.dev_cards_bought_this_turn = [{}, {}]
        
        # Buildings (using colonist.io coordinates)
        self.settlements = [set(), set()]  # corner ids
        self.cities = [set(), set()]       # corner ids
        self.roads = [set(), set()]        # edge ids as tuples
        
        # Board state (colonist.io format)
        self.hex_types = [0] * 19      # 0=Desert, 1-5 = resources
        self.hex_numbers = [0] * 19    # Dice numbers (0 for desert)
        self.robber_hex = 0            # Which hex has the robber
        self.port_edges = {}           # edge_id -> port_type (1-6)
        
        # Turn state (following catanatron's simple design)
        self.current_player = 0  # 0 or 1
        self.dice_rolled = False  # Key flag: False = can play dev cards or roll
                                 #            True = can build/trade/end turn
        self.turn_number = 0
        
        # Special prompts (only when needed)
        self.current_prompt = "PLAY_TURN"  # PLAY_TURN, DISCARD, MOVE_ROBBER
        
        # Special states
        self.must_discard = [False, False]
        self.cards_to_discard = [0, 0]
        
        # Victory points
        self.victory_points = [0, 0]
        self.largest_army_player = None
        self.longest_road_player = None
        
        # Development cards deck
        self.dev_card_deck = []
        
        # History
        self.action_history = []
```

### 3. State Functions (`state_functions.py`)

Pure functions for state manipulation:

```python
def roll_dice(state: GameState, die1: int, die2: int):
    """Process dice roll and distribute resources"""
    
def build_settlement(state: GameState, player: int, corner: int):
    """Build a settlement and update state"""
    
def build_road(state: GameState, player: int, edge: Tuple[int, int]):
    """Build a road and check for longest road"""
    
def buy_development_card(state: GameState, player: int):
    """Purchase a development card"""
    
def play_knight(state: GameState, player: int):
    """Play a knight card and check for largest army"""
    
def maritime_trade(state: GameState, player: int, give: List[int], receive: int):
    """Execute a maritime trade"""
```

### 4. Action System (`models/actions.py`)

```python
@dataclass
class Action:
    action_type: ActionType
    player: int
    data: Any  # Type depends on action_type
    
def get_valid_actions(state: GameState) -> List[Action]:
    """Generate all valid actions for current game state"""
    
def validate_action(state: GameState, action: Action) -> bool:
    """Check if an action is valid"""
    
def apply_action(state: GameState, action: Action) -> GameState:
    """Apply action and return new state (for immutability)"""
```

### 5. Colonist.io Compatibility (`colonist_map.py`)

#### Coordinate System Overview

Colonist.io uses a specific numbering system for hexes, corners, and edges:

**Hex Layout:**
- 19 hexes total (0-18)
- Arranged in rows of 3-4-5-4-3 hexes
- Counter-clockwise spiral numbering
- Layout visualization:
  ```
  Row 1:     0    11   10
  Row 2:   1   12   17   9
  Row 3: 2   13   18   16   8
  Row 4:   3   14   15   7
  Row 5:     4    5    6
  ```
- Desert is NOT fixed at hex 9 (randomized during board generation)

**Corner Numbering:**
- Each hex has 6 corners
- Hexes are oriented with a point at the top
- Corners numbered clockwise starting from the top point
- Total of 54 unique corners (0-53)

**Edge Numbering:**
- Each hex has 6 edges
- Edges numbered clockwise starting from the top-right edge
- Total of 72 unique edges (0-71)
- Each edge connects two corners

```python
# Hex arrangement in rows for easy reference
HEX_ROWS = [
    [0, 11, 10],         # Row 1
    [1, 12, 17, 9],      # Row 2
    [2, 13, 18, 16, 8],  # Row 3
    [3, 14, 15, 7],      # Row 4
    [4, 5, 6]            # Row 5
]

# Each hex's 6 corners (clockwise from top)
HEX_TO_CORNERS = {
    # Will be populated from Excel data
    # Format: hex_id: [top, top_right, bottom_right, bottom, bottom_left, top_left]
}

# Each hex's 6 edges (clockwise from top-right)
HEX_TO_EDGES = {
    # Will be populated from Excel data
    # Format: hex_id: [top_right, right, bottom_right, bottom_left, left, top_left]
}

# Reverse mappings for quick lookups
CORNER_TO_HEXES = {}  # corner_id: [hex_ids]
EDGE_TO_HEXES = {}    # edge_id: [hex_ids]

# Adjacent corners for each corner (for road building)
CORNER_ADJACENCY = {}  # corner_id: [adjacent_corner_ids]

# Edges that connect to each corner
CORNER_TO_EDGES = {}   # corner_id: [edge_ids]

# The two corners that each edge connects
EDGE_TO_CORNERS = {}   # edge_id: (corner1, corner2)

# Port locations and types (from colonist.io)
# Port types: 1=3:1, 2=Wood, 3=Brick, 4=Sheep, 5=Wheat, 6=Ore
PORT_TYPES = {
    1: "3:1",
    2: "2:1 WOOD",
    3: "2:1 BRICK", 
    4: "2:1 SHEEP",
    5: "2:1 WHEAT",
    6: "2:1 ORE"
}

# Each port is associated with an edge
# Will be populated from ports.xlsx
PORT_EDGES = {}  # edge_id: port_type (1-6)

# Corners affected by each port (for maritime trading)
# A settlement/city on these corners can use the port
PORT_CORNERS = {}  # corner_id: port_type (1-6)

# Reverse mapping for quick lookups
EDGE_TO_PORT = {}  # edge_id: port_type
CORNER_TO_PORT = {}  # corner_id: port_type
```

### 6. Game Controller (`game.py`)

```python
class Game:
    def __init__(self, players: List[Player], board_config=None):
        self.state = GameState()
        self.players = players
        
        # Initialize board with config or random
        if board_config:
            self._setup_board(board_config)
        else:
            self._random_board()
    
    def play(self) -> int:
        """Play a complete game, return winner (0 or 1)"""
        
    def step(self) -> Tuple[GameState, Action, bool]:
        """Execute one action, return (new_state, action_taken, game_over)"""
        
    def get_valid_actions(self) -> List[Action]:
        """Get all valid actions for current player"""
```

### 7. Player Interface (`models/player.py`)

```python
class Player:
    def choose_action(self, state: GameState, valid_actions: List[Action]) -> Action:
        """Choose an action from valid actions"""
        raise NotImplementedError
        
class RandomPlayer(Player):
    def choose_action(self, state: GameState, valid_actions: List[Action]) -> Action:
        return random.choice(valid_actions)
```

## Implementation Strategy

**Core Principle**: Start by copying catanatron files directly, then modify only what's necessary.

1. **Copy these catanatron modules with minimal changes**:
   - `state_functions.py` - Most functions work as-is
   - `game.py` - Main game loop stays the same
   - `models/player.py` - Interface unchanged
   - `models/actions.py` - Remove trading actions only

2. **Modify these modules for 1v1**:
   - `state.py` - Simplify to fixed 2-player arrays
   - `models/enums.py` - Remove trading action types

3. **Replace completely**:
   - `models/map.py` → `colonist_map.py` - New coordinate system
   - `models/board.py` - Adapt to colonist coordinates

## Implementation Phases

### Phase 1: Core Game Logic (Week 1)
- [ ] Copy catanatron's base files
- [ ] Basic enumerations and constants
- [ ] Colonist.io coordinate mappings (from Excel files)
- [ ] Game state representation (adapting catanatron's)
- [ ] State manipulation functions (mostly unchanged)
- [ ] Action generation (remove trading actions)
- [ ] Basic game flow (identical to catanatron)

### Phase 2: Complete Rules (Week 2)
- [ ] Full action system
- [ ] Development cards
- [ ] Robber mechanics
- [ ] Maritime trading
- [ ] Longest road calculation
- [ ] Largest army tracking
- [ ] Victory condition checking

### Phase 3: AI Foundation (Week 3)
- [ ] Feature extraction
- [ ] Basic evaluation function
- [ ] Random and greedy players
- [ ] Performance profiling
- [ ] State copying optimization

### Phase 4: Advanced AI (Weeks 4-5)
- [ ] Minimax with alpha-beta pruning
- [ ] Monte Carlo Tree Search
- [ ] Opening book for settlements
- [ ] Endgame detection
- [ ] Parameter tuning

### Phase 5: Training & Optimization (Week 6+)
- [ ] Self-play training
- [ ] Evaluation against baseline
- [ ] Performance optimization
- [ ] Strategy refinement

## Performance Targets

- State copy: < 100 microseconds
- Action generation: < 1 millisecond
- Full game simulation: < 100 milliseconds
- Games per second: > 1000

## Testing Strategy

1. **Unit Tests**: Every function in state_functions.py
2. **Integration Tests**: Complete game scenarios
3. **Performance Tests**: Benchmark critical operations
4. **Validation Tests**: Compare against known colonist.io games
5. **AI Tests**: Ensure AI makes legal moves

## Success Criteria

1. **Correctness**: Passes all rule tests
2. **Performance**: Meets speed targets
3. **AI Strength**: Beats random player 95%+ of games
4. **Stability**: No crashes in 10,000 games
5. **Final Goal**: AI achieves 1900+ ELO equivalent

## Colonist.io Compatibility Notes

Based on analysis of colonist.io game logs:

### Data Formats
1. **Hex Types**: 0=Desert, 1=Wood, 2=Brick, 3=Sheep, 4=Wheat, 5=Ore
2. **Player Colors**: 1-5 represent different colors (we'll map to 0/1 internally)
3. **Resource Cards**: 1=Wood, 2=Brick, 3=Sheep, 4=Wheat, 5=Ore
4. **Port Types**: 1=3:1, 2=Wood, 3=Brick, 4=Sheep, 5=Wheat, 6=Ore
5. **Building Types**: 1=Settlement, 2=City

### Game State Structure
Colonist.io organizes state into:
- `mapState`: Board layout (hexes, corners, edges, ports)
- `bankState`: Available resources and dev cards
- `playerStates`: Individual player resources, buildings, points
- `currentState`: Turn info, action state, timing
- `mechanicStates`: Various game mechanics (longest road, largest army, etc.)

### Event System
Each action creates an event with:
- `input`: Timing information
- `stateChange`: What changed in the game state
- State changes are minimal diffs (only what changed)

### Key Differences from Catanatron
1. Uses numeric types instead of string enums
2. Events are state changes, not action descriptions
3. Explicit coordinate system (x,y,z for edges in logs)

### Our Simplifications for CatanDuel
1. Always use players 0 and 1 internally
2. Map colonist.io's player colors to 0/1 based on play order when parsing
3. Ignore color information - just track first vs second player
4. Keep catanatron's simple turn state design (dice_rolled flag) instead of colonist.io's numeric action states

## Game Rules Clarifications

### Setup Phase
- Order: P0 settlement+road, P1 settlement+road, P1 settlement+road, P0 settlement+road
- Second settlement gives starting resources from adjacent hexes

### Robber Rules
- **Friendly Robber**: No robber activation on 7 until someone has 3+ victory points
- Can place robber on any hex (even with only your buildings)
- Steal randomly from opponent if they have buildings there and resources

### Development Cards
- Cannot play cards bought this turn
- Can play multiple cards per turn (but only one per type)
- Knights can be played before rolling; if you then roll 7, move robber again
- Victory Point cards don't need to be revealed at 10 points

### Building Limits (per player)
- 5 settlements initially, +1 for each city upgrade
- 4 cities maximum
- 15 roads maximum
- Road Building card: build 0-2 roads based on availability

### Resource Bank Limits
- 19 of each resource type in bank (from colonist.io logs)

### Trading
- Can do multiple maritime trades per turn
- Port trading:
  - 4:1 (no port): Trade 4 of any single resource for 1 of any other
  - 3:1 port: Trade 3 of any single resource for 1 of any other
  - 2:1 port: Trade 2 of the specified resource for 1 of any other

### Longest Road
- Minimum 5 connected roads
- Ties go to current holder

### Board Generation
- Random shuffle of resources, numbers, and ports (like catanatron)
- Constraints for balanced boards:
  - No two identical numbers on adjacent hexes
  - No red numbers (6 and 8) on adjacent hexes
- Desert gets no number (or 0)

## Next Steps

1. Review and finalize this plan
2. Set up project structure
3. Implement Phase 1
4. Iterate based on testing

---

*This plan is a living document and will be updated as development progresses.*