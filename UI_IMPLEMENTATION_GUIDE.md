# CatanDuel UI Implementation Guide

## Exhaustive Step-by-Step Plan

This guide provides a detailed, actionable plan to implement the CatanDuel web UI by adapting the rlcatan interface.

## Prerequisites

Before starting, ensure you have:
- [ ] Access to rlcatan repository/codebase
- [ ] CatanDuel engine fully tested and working
- [ ] Python environment with Flask installed
- [ ] Basic understanding of both codebases
- [ ] Development web server setup

## Phase 1: Initial Setup and Analysis (Days 1-2)

### Step 1.1: Analyze rlcatan Structure
1. Clone/download rlcatan repository
2. Document the file structure:
   ```
   rlcatan/
   ├── web_server.py (main Flask app)
   ├── templates/
   │   └── index.html (main game page)
   ├── static/
   │   ├── js/
   │   │   ├── game.js (game logic)
   │   │   ├── board.js (board rendering)
   │   │   └── ui.js (UI interactions)
   │   └── css/
   │       └── game.css (styling)
   └── assets/ (SVG files)
   ```
3. Identify key components:
   - [ ] State representation format
   - [ ] Action message format
   - [ ] WebSocket vs HTTP endpoints
   - [ ] SVG rendering approach
   - [ ] Event handling system

### Step 1.2: Create UI Directory Structure
```bash
cd catanduel
mkdir -p ui/templates ui/static/js ui/static/css ui/assets
touch ui/__init__.py ui/adapter.py ui/server.py
```

### Step 1.3: Copy Non-Code Assets
1. Copy all SVG assets from rlcatan:
   ```bash
   cp -r /path/to/rlcatan/assets/* catanduel/ui/assets/
   ```
2. Copy CSS files:
   ```bash
   cp /path/to/rlcatan/static/css/* catanduel/ui/static/css/
   ```
3. Document all asset files and their purposes

### Step 1.4: Initial Documentation
Create `ui/README.md` documenting:
- [ ] All copied files and their sources
- [ ] Known differences between rlcatan and CatanDuel
- [ ] Coordinate system mapping requirements
- [ ] State format differences

## Phase 2: Adapter Layer Foundation (Days 3-5)

### Step 2.1: Define Data Structures
Create `ui/adapter_types.py`:
```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class UIState:
    """State format expected by the UI"""
    current_player: int
    phase: str  # 'setup', 'main', 'discard', 'robber'
    board: 'UIBoard'
    players: List['UIPlayer']
    dice: Optional[Tuple[int, int]]
    valid_actions: List['UIAction']
    last_action: Optional['UIAction']
    message: str

@dataclass
class UIBoard:
    """Board representation for UI"""
    hexes: List['UIHex']
    corners: Dict[int, 'UICorner']
    edges: Dict[int, 'UIEdge']
    robber_hex: int
    ports: Dict[int, int]  # edge_id -> port_type

# ... define all UI data structures
```

### Step 2.2: Create Basic Adapter
Implement `ui/adapter.py`:
```python
class CatanDuelAdapter:
    def __init__(self):
        self.game = None
        self.ui_state_cache = None
    
    def new_game(self, player_types):
        """Initialize new game with specified players"""
        pass
    
    def translate_state(self, game_state) -> UIState:
        """Convert CatanDuel state to UI format"""
        pass
    
    def translate_action(self, ui_action) -> Action:
        """Convert UI action to CatanDuel format"""
        pass
    
    def execute_action(self, ui_action) -> Tuple[UIState, List[UIEvent]]:
        """Execute action and return new state + events"""
        pass
```

### Step 2.3: Implement State Translation
1. Map CatanDuel hex types to rlcatan format
2. Convert player resources to UI format
3. Translate building positions
4. Convert valid actions to UI action list
5. Generate appropriate UI messages

### Step 2.4: Test Adapter with Unit Tests
Create `tests/test_ui_adapter.py`:
```python
def test_state_translation():
    # Test each component of state translation
    pass

def test_action_translation():
    # Test each action type conversion
    pass

def test_coordinate_mapping():
    # Verify colonist.io coordinates map correctly
    pass
```

## Phase 3: Flask Server Integration (Days 6-8)

### Step 3.1: Create Basic Flask Server
Implement `ui/server.py`:
```python
from flask import Flask, render_template, jsonify, request
from adapter import CatanDuelAdapter

app = Flask(__name__)
adapter = CatanDuelAdapter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    # Initialize new game
    pass

@app.route('/api/game_state', methods=['GET'])
def get_state():
    # Return current game state
    pass

@app.route('/api/action', methods=['POST'])
def execute_action():
    # Execute player action
    pass
```

### Step 3.2: Create Minimal HTML Template
Create `ui/templates/index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>CatanDuel</title>
    <link rel="stylesheet" href="/static/css/game.css">
</head>
<body>
    <div id="game-container">
        <div id="board-container">
            <!-- SVG board will be inserted here -->
        </div>
        <div id="player-info">
            <!-- Player stats -->
        </div>
        <div id="action-panel">
            <!-- Action buttons -->
        </div>
    </div>
    <script src="/static/js/api.js"></script>
    <script src="/static/js/board.js"></script>
    <script src="/static/js/game.js"></script>
</body>
</html>
```

### Step 3.3: Implement API Communication
Create `ui/static/js/api.js`:
```javascript
class GameAPI {
    async newGame(config) {
        // POST to /api/new_game
    }
    
    async getState() {
        // GET from /api/game_state
    }
    
    async executeAction(action) {
        // POST to /api/action
    }
}
```

### Step 3.4: Test Basic Server
1. Start Flask server
2. Verify routes work
3. Test new game creation
4. Check state retrieval

## Phase 4: Board Rendering (Days 9-12)

### Step 4.1: Copy and Adapt Board Rendering
1. Copy `board.js` from rlcatan
2. Update coordinate system to use colonist.io IDs
3. Implement hex rendering:
   ```javascript
   function renderHex(hexId, hexType, number) {
       // Use colonist_map coordinates
       const position = getHexPosition(hexId);
       // Create SVG elements
   }
   ```

### Step 4.2: Implement Building Rendering
```javascript
function renderSettlement(cornerId, playerColor) {
    const position = getCornerPosition(cornerId);
    // Create settlement SVG
}

function renderCity(cornerId, playerColor) {
    // Render city at corner
}

function renderRoad(edgeId, playerColor) {
    const [corner1, corner2] = getEdgeCorners(edgeId);
    // Draw road between corners
}
```

### Step 4.3: Create Coordinate Mapping
Create `ui/static/js/coordinates.js`:
```javascript
// Map colonist.io IDs to pixel positions
const HEX_POSITIONS = {
    0: {x: 200, y: 100},
    1: {x: 150, y: 180},
    // ... all 19 hexes
};

const CORNER_POSITIONS = {
    0: {x: 200, y: 70},
    // ... all 54 corners
};

function getEdgePosition(edgeId) {
    // Calculate edge midpoint from corners
}
```

### Step 4.4: Test Board Rendering
1. Render empty board
2. Place test buildings
3. Verify all positions correct
4. Test robber placement

## Phase 5: Game Flow Implementation (Days 13-18)

### Step 5.1: Setup Phase
1. Implement initial settlement placement:
   ```javascript
   function handleSetupClick(cornerId) {
       if (validSetupSpots.includes(cornerId)) {
           api.executeAction({
               type: 'BUILD_INITIAL_SETTLEMENT',
               corner: cornerId
           });
       }
   }
   ```
2. Handle road placement after settlement
3. Show valid placement locations
4. Implement turn order display

### Step 5.2: Dice Rolling
```javascript
function rollDice() {
    api.executeAction({type: 'ROLL'});
}

function animateDice(die1, die2) {
    // Show dice animation
    // Display result
}
```

### Step 5.3: Building Actions
1. Show build menu when appropriate
2. Highlight valid building spots
3. Handle build clicks:
   ```javascript
   function buildSettlement(cornerId) {
       api.executeAction({
           type: 'BUILD_SETTLEMENT',
           corner: cornerId
       });
   }
   ```

### Step 5.4: Resource Management
1. Display player resources
2. Update on state changes
3. Animate resource gains/losses
4. Show resource production on dice rolls

### Step 5.5: Development Cards
```javascript
function buyDevCard() {
    api.executeAction({type: 'BUY_DEVELOPMENT_CARD'});
}

function playDevCard(cardType) {
    switch(cardType) {
        case 'KNIGHT':
            // Trigger robber movement
            break;
        case 'YEAR_OF_PLENTY':
            // Show resource selection
            break;
        // ... other cards
    }
}
```

## Phase 6: Special Actions (Days 19-22)

### Step 6.1: Discard Handling
```javascript
function showDiscardDialog(requiredCount) {
    // Show resource selection UI
    // Track selected resources
    // Submit when count matches
}

function submitDiscard(resources) {
    api.executeAction({
        type: 'DISCARD',
        resources: resources
    });
}
```

### Step 6.2: Robber Movement
```javascript
function moveRobber(hexId) {
    if (hexId !== currentRobberHex) {
        const victims = getPlayersOnHex(hexId);
        if (victims.length > 0) {
            showStealDialog(hexId, victims);
        } else {
            api.executeAction({
                type: 'MOVE_ROBBER',
                hex: hexId,
                victim: null
            });
        }
    }
}
```

### Step 6.3: Maritime Trading
```javascript
function showTradeDialog() {
    const availableRatios = getPlayerTradeRatios();
    // Show trade interface
}

function executeTrade(giveResource, giveAmount, getResource) {
    api.executeAction({
        type: 'MARITIME_TRADE',
        give: giveResource,
        amount: giveAmount,
        receive: getResource
    });
}
```

### Step 6.4: Development Card Actions
1. Year of Plenty resource selection
2. Monopoly resource choice
3. Road Building (place 2 roads)
4. Knight card (move robber)

## Phase 7: AI Integration (Days 23-25)

### Step 7.1: AI Selection UI
```html
<select id="ai-type">
    <option value="random">Random AI</option>
    <option value="greedy">Greedy AI</option>
    <option value="minimax">Minimax AI</option>
    <option value="mcts">MCTS AI</option>
</select>
<button onclick="startGame()">Start Game</button>
```

### Step 7.2: AI Configuration
```javascript
function getAIConfig() {
    const aiType = document.getElementById('ai-type').value;
    const config = {type: aiType};
    
    if (aiType === 'minimax') {
        config.depth = parseInt(document.getElementById('minimax-depth').value);
    } else if (aiType === 'mcts') {
        config.timeLimit = parseFloat(document.getElementById('mcts-time').value);
    }
    
    return config;
}
```

### Step 7.3: AI Move Handling
```python
# In server.py
@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    if game.current_player == AI_PLAYER_ID:
        action = game.players[AI_PLAYER_ID].decide(game, valid_actions)
        # Add thinking delay for UX
        time.sleep(0.5)
        return execute_action_internal(action)
```

### Step 7.4: AI Thinking Indicator
```javascript
function showAIThinking() {
    document.getElementById('ai-thinking').style.display = 'block';
}

function hideAIThinking() {
    document.getElementById('ai-thinking').style.display = 'none';
}
```

## Phase 8: Polish and Features (Days 26-30)

### Step 8.1: Visual Enhancements
1. Smooth animations for all actions
2. Hover effects on interactive elements
3. Better color scheme
4. Victory animation

### Step 8.2: Game Information
```javascript
function updateGameLog(action, player) {
    const log = document.getElementById('game-log');
    const entry = createLogEntry(action, player);
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function updateStatistics() {
    // Update VP display
    // Show longest road owner
    // Display largest army
    // Resource counts
}
```

### Step 8.3: Settings Menu
1. Animation speed control
2. Sound effects toggle
3. Board zoom level
4. Color customization

### Step 8.4: Save/Load Functionality
```python
@app.route('/api/save_game', methods=['POST'])
def save_game():
    game_state = adapter.serialize_game()
    # Save to file or database
    return jsonify({'id': game_id})

@app.route('/api/load_game/<game_id>', methods=['GET'])
def load_game(game_id):
    # Load and restore game state
    pass
```

## Phase 9: Testing and Debugging (Days 31-35)

### Step 9.1: Comprehensive Testing
1. **Setup Phase Tests**:
   - [ ] All valid settlement spots clickable
   - [ ] Road must connect to settlement
   - [ ] Resources distributed correctly
   - [ ] Turn order correct (0-1-1-0)

2. **Main Game Tests**:
   - [ ] All actions work correctly
   - [ ] Invalid actions prevented
   - [ ] State updates properly
   - [ ] No desync between UI and engine

3. **Special Case Tests**:
   - [ ] 7 roll with no discards
   - [ ] 7 roll with one player discard
   - [ ] 7 roll with both players discard
   - [ ] Robber on hex with no players
   - [ ] Friendly robber rule

4. **End Game Tests**:
   - [ ] Victory detection
   - [ ] Final score display
   - [ ] Restart game option

### Step 9.2: Performance Testing
```javascript
function measurePerformance() {
    console.time('render');
    renderBoard(gameState);
    console.timeEnd('render');
    
    console.time('action');
    api.executeAction(testAction);
    console.timeEnd('action');
}
```

### Step 9.3: Cross-Browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

### Step 9.4: Debug Tools
```javascript
// Add debug panel
function createDebugPanel() {
    const panel = document.createElement('div');
    panel.id = 'debug-panel';
    panel.innerHTML = `
        <button onclick="showGameState()">Show State</button>
        <button onclick="showValidActions()">Valid Actions</button>
        <button onclick="forceWin(0)">P0 Win</button>
        <button onclick="forceWin(1)">P1 Win</button>
    `;
}
```

## Phase 10: Documentation and Deployment (Days 36-40)

### Step 10.1: User Documentation
Create `ui/USER_GUIDE.md`:
1. How to start a game
2. Basic controls
3. Game rules reminder
4. AI difficulty levels
5. Keyboard shortcuts

### Step 10.2: Developer Documentation
Create `ui/DEVELOPER_GUIDE.md`:
1. Architecture overview
2. Adding new AI types
3. Modifying UI elements
4. Debugging common issues
5. Performance optimization tips

### Step 10.3: API Documentation
```python
"""
API Endpoints:

POST /api/new_game
  Body: {
    player_types: ['human', 'minimax'],
    ai_config: {depth: 3}
  }
  Response: {game_id: string, state: UIState}

GET /api/game_state
  Response: {state: UIState}

POST /api/action
  Body: {action: UIAction}
  Response: {state: UIState, events: UIEvent[]}
"""
```

### Step 10.4: Deployment Preparation
1. Production configuration
2. Error handling
3. Logging setup
4. Performance optimization
5. Security review

## Validation Checklist

Before considering the UI complete:

### Core Functionality
- [ ] Can play complete game human vs AI
- [ ] All game rules implemented correctly
- [ ] No crashes or hangs
- [ ] State stays synchronized

### UI/UX
- [ ] Intuitive controls
- [ ] Clear visual feedback
- [ ] Responsive design
- [ ] Smooth animations

### Features
- [ ] Multiple AI types work
- [ ] Game saves/loads correctly
- [ ] Statistics track properly
- [ ] Settings persist

### Performance
- [ ] Quick page load
- [ ] Smooth gameplay
- [ ] AI moves in reasonable time
- [ ] No memory leaks

### Compatibility
- [ ] Works in major browsers
- [ ] Mobile responsive
- [ ] Handles slow connections
- [ ] Graceful error handling

## Troubleshooting Guide

Common issues and solutions:

1. **Coordinate mismatch**: Check colonist_map.py mappings
2. **State desync**: Verify adapter translation
3. **Invalid actions**: Check action validation
4. **Performance issues**: Profile rendering code
5. **AI not moving**: Check async handling

## Success Metrics

The implementation is successful when:
1. Can play 100 games without errors
2. UI responds in <100ms
3. AI moves complete in <2s
4. No visual glitches
5. Players understand how to play immediately