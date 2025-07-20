# CatanDuel UI

Web-based user interface for the CatanDuel engine, adapted from rlcatan's UI design.

## Overview

This UI provides a browser-based interface to play CatanDuel against various AI opponents. It features:
- SVG-based board rendering
- Support for all game actions
- Multiple AI difficulty levels
- Game state visualization
- Action history logging

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Browser       │────▶│   Flask Server   │────▶│ CatanDuel Engine│
│ (HTML/JS/SVG UI)   │◀────│   (Adapter)      │◀────│   (Pure Logic)  │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
```

## Components

- **server.py**: Flask web server handling HTTP requests
- **adapter.py**: Translation layer between UI and engine formats
- **adapter_types.py**: Data structure definitions for UI
- **templates/index.html**: Main game interface
- **static/js/**: JavaScript for game logic and rendering
- **static/css/**: Styling
- **assets/**: SVG images for game pieces

## Installation

```bash
pip install flask
```

## Running

```bash
cd catanduel/ui
python server.py
```

Then open http://localhost:5000 in your browser.

## Development Status

Phase 1: Initial Setup ✓
- [x] Directory structure created
- [x] Documentation started
- [x] rlcatan analysis completed
- [ ] Placeholder assets
- [ ] Basic server

Phase 2-10: See UI_IMPLEMENTATION_GUIDE.md

## Coordinate System

Using colonist.io coordinate system:
- Hexes: 0-18 (counter-clockwise spiral)
- Corners: 0-53 (where settlements/cities go)
- Edges: 0-71 (where roads go)

## File Sources

| CatanDuel File | Adapted From | Changes |
|----------------|--------------|---------|
| server.py | rlcatan/web_server.py | Use CatanDuel engine |
| adapter.py | New | Translate between formats |
| index.html | rlcatan/templates/index.html | Simplify for 2 players |
| game.js | rlcatan/static/js/game.js | Update action handling |
| board.js | rlcatan/static/js/board.js | Colonist.io coordinates |

## Known Differences

1. **Coordinate System**: Colonist.io IDs instead of rlcatan's system
2. **Players**: Fixed 2 players instead of 3-4
3. **Trading**: Maritime only, no player-to-player
4. **State Format**: Adapted to match rlcatan's structure
5. **Actions**: Sequential discard instead of simultaneous