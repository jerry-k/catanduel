# CatanDuel UI Implementation Plan

## Overview

This document outlines a comprehensive plan to salvage and adapt the rlcatan web UI for use with the CatanDuel engine. The rlcatan UI provides a polished web-based interface with SVG board rendering, but was abandoned due to engine bugs. By combining rlcatan's UI with CatanDuel's robust engine (based on catanatron), we can create a complete, playable game.

## Goals

1. **Salvage rlcatan's web UI** - Reuse the Flask server, HTML/CSS/JS frontend, and SVG assets
2. **Adapt to CatanDuel engine** - Create adapter layer to translate between UI and engine
3. **Maintain 2-player focus** - Simplify UI elements for 1v1 gameplay
4. **Fix coordinate system** - Ensure colonist.io coordinate mapping works correctly
5. **Add improvements** - Better AI selection, game history, statistics

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Browser       │────▶│   Flask Server   │────▶│ CatanDuel Engine│
│ (HTML/JS/SVG UI)   │◀────│   (Adapter)      │◀────│   (Pure Logic)  │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
         │                           │                         │
         ▼                           ▼                         ▼
    User Actions               State Translation          Game State
    Click Events               Action Mapping             AI Players
    Visual Updates             Event Generation           Validation
```

## Implementation Phases

### Phase 1: Core Infrastructure Setup

1. **Copy UI files from rlcatan**
   - `web_server.py` → Adapt to use CatanDuel engine
   - `templates/index.html` → Simplify for 2 players
   - `static/js/game.js` → Update action handling
   - `static/css/game.css` → Maintain styling
   - `assets/` → Copy all SVG assets

2. **Create adapter layer** (`catanduel/ui/adapter.py`)
   - Translate CatanDuel state to rlcatan UI format
   - Map CatanDuel actions to UI action format
   - Handle coordinate system translation
   - Generate UI events from engine changes

3. **Update Flask server**
   - Import CatanDuel engine instead of rlcatan
   - Use adapter for all state/action translation
   - Add AI player selection endpoints
   - Improve error handling and logging

### Phase 2: Coordinate System Integration

1. **Implement coordinate mapping**
   - Use colonist_map.py for hex/corner/edge IDs
   - Update SVG rendering to use colonist coordinates
   - Ensure building placement uses correct IDs
   - Test all 19 hexes, 54 corners, 72 edges

2. **Update board rendering**
   - Modify hex layout to match colonist.io arrangement
   - Update port positions to match colonist edges
   - Ensure robber placement works correctly
   - Fix number token positions

### Phase 3: Game Flow Adaptation

1. **Setup phase handling**
   - Show valid settlement spots during setup
   - Enforce road placement after settlement
   - Handle resource distribution from second settlement
   - Proper turn order (0-1-1-0)

2. **Main game mechanics**
   - Dice rolling animation
   - Resource distribution visualization
   - Discard handling (sequential, not simultaneous)
   - Robber movement and stealing
   - Development card playing

3. **Trading system**
   - Remove player-to-player trading UI
   - Maritime trade interface
   - Port bonus visualization
   - 4:1 trade always available

### Phase 4: AI Integration

1. **AI player selection**
   - Dropdown to choose AI type:
     - RandomPlayer
     - GreedyPlayer
     - MinimaxPlayer (with depth setting)
     - MCTSPlayer (with time limit setting)
   - Difficulty presets (Easy/Medium/Hard)
   - AI thinking indicator

2. **AI move visualization**
   - Smooth animations for AI actions
   - Configurable AI move delay
   - Show AI "thinking" during computation
   - Highlight AI's last action

### Phase 5: UI Enhancements

1. **Visual improvements**
   - Player color customization (keep red/blue default)
   - Board zoom/pan controls
   - Fullscreen mode
   - Mobile responsive design

2. **Game information**
   - Detailed action log with timestamps
   - Resource/building statistics
   - Victory point breakdown
   - Longest road/largest army indicators

3. **Quality of life**
   - Undo last action (single player only)
   - Save/load game state
   - Replay game from history
   - Export game log

### Phase 6: Additional Features

1. **Statistics tracking**
   - Win/loss record vs each AI type
   - Average game length
   - Resource collection stats
   - Building patterns

2. **Tutorial mode**
   - Highlight available actions
   - Explain game rules
   - Strategy tips
   - AI move explanations

3. **Debug mode**
   - Show all game state
   - Manual state manipulation
   - Action probability display
   - Performance metrics

## Technical Details

### State Translation (adapter.py)

```python
def translate_state(catanduel_state) -> dict:
    """Convert CatanDuel GameState to rlcatan UI format"""
    return {
        'current_player': catanduel_state.current_player,
        'phase': 'setup' if catanduel_state.is_setup_phase() else 'main',
        'board': translate_board(catanduel_state.board),
        'players': translate_players(catanduel_state.players),
        'dice': catanduel_state.last_dice_roll,
        'robber_hex': catanduel_state.board.robber_hex,
        # ... etc
    }
```

### Action Translation

```python
def translate_action(ui_action) -> Action:
    """Convert UI action format to CatanDuel Action"""
    action_type = UI_TO_ENGINE_ACTION_MAP[ui_action['type']]
    value = translate_action_value(ui_action)
    return Action(action_type, value)
```

### Event Generation

```python
def generate_events(old_state, new_state, action) -> List[dict]:
    """Generate UI events from state changes"""
    events = []
    # Check what changed and create appropriate events
    # e.g., RESOURCE_GAINED, BUILDING_PLACED, DICE_ROLLED
    return events
```

## File Structure

```
catanduel/
├── engine/           # Existing engine code
├── ui/              # New UI code
│   ├── __init__.py
│   ├── adapter.py   # Engine-UI translation layer
│   ├── server.py    # Flask web server
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── js/
│   │   │   ├── game.js
│   │   │   ├── board.js
│   │   │   └── ui.js
│   │   └── css/
│   │       └── game.css
│   └── assets/      # SVG assets from rlcatan
│       ├── cards/
│       ├── buildings/
│       ├── dice/
│       └── icons/
└── tests/
    └── test_ui_adapter.py
```

## Testing Strategy

1. **Unit tests**
   - Test adapter translation functions
   - Verify coordinate mappings
   - Check action validation

2. **Integration tests**
   - Full game playthrough via API
   - AI vs AI games
   - Edge cases (7 rolls, dev cards, etc.)

3. **UI tests**
   - Manual testing checklist
   - Screenshot comparisons
   - Performance benchmarks

## Migration Checklist

- [ ] Copy UI files from rlcatan
- [ ] Create adapter.py with basic translation
- [ ] Update server.py to use CatanDuel engine
- [ ] Fix coordinate system mapping
- [ ] Test setup phase completely
- [ ] Test main game mechanics
- [ ] Implement AI player selection
- [ ] Add discard handling UI
- [ ] Test robber and stealing
- [ ] Implement maritime trade UI
- [ ] Add development card interfaces
- [ ] Test victory conditions
- [ ] Add statistics and history
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Documentation

## Known Challenges

1. **Coordinate system differences** - Must carefully map between colonist.io and UI coordinates
2. **State representation** - CatanDuel uses immutable state, rlcatan mutated state
3. **Action format** - Different action representations need translation
4. **Discard mechanism** - CatanDuel uses sequential, rlcatan might expect simultaneous
5. **AI integration** - Need to handle async AI computation gracefully

## Success Criteria

1. **Fully playable game** - Human vs AI with all rules implemented
2. **No engine bugs** - CatanDuel's solid foundation prevents rlcatan's issues
3. **Smooth UI** - Responsive, intuitive interface
4. **AI variety** - Multiple AI opponents with different strengths
5. **Performance** - Quick AI moves, smooth animations
6. **Correctness** - Matches colonist.io rules exactly

## Future Enhancements

1. **Multiplayer support** - WebSocket for real-time play
2. **Tournament mode** - Series of games with ELO tracking  
3. **AI training** - Learn from human games
4. **Board editor** - Custom starting positions
5. **Spectator mode** - Watch AI vs AI games
6. **Analysis tools** - Best move suggestions