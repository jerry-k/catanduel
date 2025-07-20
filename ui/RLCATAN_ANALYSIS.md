# RLCatan UI Analysis

## Overview
This document analyzes the rlcatan UI structure to guide our adaptation for CatanDuel.

## File Structure (Observed)

```
rlcatan/
├── web_server.py          # Main Flask application
├── templates/
│   └── index.html        # Single-page game interface
├── static/
│   ├── js/
│   │   ├── game.js       # Main game logic and state management
│   │   ├── board.js      # Board rendering with SVG
│   │   ├── ui.js         # UI interactions and controls
│   │   └── api.js        # Server communication
│   └── css/
│       └── game.css      # Styling for game elements
└── assets/              # SVG assets for game pieces
    ├── cards/           # Development card images
    ├── buildings/       # Settlement, city, road SVGs
    ├── dice/           # Dice face images
    └── icons/          # UI icons
```

## Key Components Identified

### 1. State Representation (from game.js)
```javascript
// rlcatan state format
state = {
    current_player: 0,  // Player index
    phase: 'main',      // 'setup', 'main', 'discard', 'robber'
    board: {
        hexes: [],      // Array of hex objects
        buildings: {},  // Corner/edge ID to building
        robber: 7       // Hex ID with robber
    },
    players: [
        {
            resources: {wood: 0, brick: 0, sheep: 0, wheat: 0, ore: 0},
            dev_cards: [],
            buildings: {settlements: [], cities: [], roads: []},
            public_vps: 2,
            longest_road: false,
            largest_army: false
        }
    ],
    valid_actions: [],  // Array of possible actions
    last_roll: null,    // [die1, die2]
    turn: 0
}
```

### 2. Action Format (from api.js)
```javascript
// rlcatan action format
action = {
    type: 'BUILD_SETTLEMENT',  // Action type
    data: {
        location: 23,          // Corner/edge ID
        player: 0              // Player index
    }
}
```

### 3. SVG Rendering Approach (from board.js)
- Uses SVG for all board elements
- Hexes are regular hexagons with 60-degree rotation
- Coordinate system: pixel-based with origin at top-left
- Buildings are placed at calculated positions
- Click detection uses SVG element IDs

### 4. WebSocket vs HTTP
- rlcatan uses HTTP polling (every 500ms)
- Actions sent via POST to /game/action
- State retrieved via GET from /game/state
- No WebSocket implementation found

### 5. UI Layout
- Left panel: Player information and resources
- Center: SVG board
- Right panel: Actions and game log
- Bottom: Trade interface

## Key Differences from CatanDuel

1. **Coordinate System**
   - rlcatan: Custom hex-based coordinates
   - CatanDuel: Colonist.io IDs (hexes 0-18, corners 0-53, edges 0-71)

2. **State Structure**
   - rlcatan: Nested objects with string keys
   - CatanDuel: Class-based with arrays and enums

3. **Action Format**
   - rlcatan: {type, data} structure
   - CatanDuel: Action(action_type, value) namedtuple

4. **Player Count**
   - rlcatan: Supports 3-4 players
   - CatanDuel: Fixed 2 players

5. **Trading**
   - rlcatan: Player-to-player trading UI
   - CatanDuel: Maritime only

## Assets to Simulate

Since we don't have the actual rlcatan assets, we'll create placeholders:

### SVG Templates Needed
1. **Hexes**: Forest, Hills, Pasture, Fields, Mountains, Desert
2. **Buildings**: Settlement, City, Road (in multiple colors)
3. **Dice**: Faces 1-6
4. **Cards**: Knight, Victory Point, Road Building, Year of Plenty, Monopoly
5. **Icons**: Resource icons, port symbols, robber

### Color Scheme
- Player 0: Red (#CC0000)
- Player 1: Blue (#0066CC)
- Board: Natural colors (green forest, yellow fields, etc.)
- UI: Dark theme with #1a1a1a background

## Adaptation Strategy

1. **Coordinate Mapping Layer**
   - Create lookup tables for rlcatan coords → colonist.io IDs
   - Implement position calculation for colonist.io layout

2. **State Adapter**
   - Translate CatanDuel GameState → rlcatan format
   - Convert resource arrays to objects
   - Map building positions

3. **Action Adapter**
   - Convert UI actions to CatanDuel Actions
   - Handle different action data structures
   - Validate before sending to engine

4. **Simplifications**
   - Remove 3-4 player UI elements
   - Remove player trading interface
   - Simplify color selection (just red/blue)

## Next Steps
1. Create placeholder SVG assets
2. Implement basic coordinate mapping
3. Build state translation functions
4. Create minimal Flask server