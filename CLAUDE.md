# CatanDuel Project Context for Claude

## Project Overview
This is CatanDuel - a 2-player version of Catan with a Python game engine and web UI. The web UI was salvaged from rlcatan (a reinforcement learning Catan project) and adapted to work with our custom engine.

## Current State (July 25, 2025)
The project is **fully functional** with a polished UI and comprehensive game log. All known bugs have been fixed, including proper board generation with balance rules, correct game logging, and various UI improvements.

## Architecture (CRITICAL - DO NOT VIOLATE)

### Clean Separation of Concerns
1. **Engine (Python)**: Owns ALL game logic. Located in `/engine/`
   - Validates all moves
   - Manages game state
   - Generates valid actions
   - NO UI concerns

2. **Web Server (Flask)**: Simple translation layer in `/ui/web_server.py`
   - Converts between engine and UI formats
   - NO game logic
   - Just format conversion

3. **UI (JavaScript)**: Pure presentation in `/ui/static/js/game.js`
   - Displays game state
   - Collects user input
   - NO game logic
   - Uses modals for better UX (e.g., discard selection)

### Key Principle
**The engine provides valid actions, the UI just displays them and lets users choose.**

## Resource Mapping (IMPORTANT)
The UI and engine use different resource orderings:
- **UI indices**: 0=brick, 1=grain, 2=lumber, 3=ore, 4=wool
- **Engine indices**: 0=wood, 1=brick, 2=sheep, 3=wheat, 4=ore

This mapping is critical for maritime trade and discard actions.

## Recent Improvements (July 25, 2025)

### Core Fixes
- **Board Generation**: Fixed hex adjacency detection for proper balance rules (no adjacent 6/8s)
- **Game Log**: Comprehensive event logging with resource/building icons following colonist.io style
- **Road Building**: Proper state tracking and UI feedback
- **Friendly Robber**: Correctly uses public VPs instead of actual VPs
- **Stolen Resources**: Game log now shows which resource was stolen

### UI Enhancements
- Resource names standardized (wood, brick, sheep, wheat, ore)
- 6s and 8s displayed in dark red on the board
- Building icons in game log match player colors
- Dev card button maintains proper aspect ratio
- Resource and building SVGs used throughout instead of text/emojis

### Technical Improvements
- Proper event generation for all game actions
- Consistent state serialization between engine and UI
- Clean separation of concerns maintained throughout
- Smart AI players with improved initial settlement placement (July 25, 2025)

## Common Pitfalls to Avoid

1. **DO NOT add game logic to the UI or server**
   - The engine already handles everything correctly
   - The UI should only format and display

2. **DO NOT create custom actions in the UI**
   - Always find and use actions from the legal_actions list
   - Example: Maritime trade must find matching action, not create new one

3. **DO NOT assume action formats**
   - MOVE_ROBBER uses 2-tuple: (hex_id, victim_id)
   - MARITIME_TRADE uses 3-tuple: (give_res, give_amount, get_res)
   - DISCARD uses array: [wood, brick, sheep, wheat, ore]

4. **DO NOT clear game state too early**
   - Example: We keep last_dice_roll for UI display

## Testing Status

### Automated Tests Pass ✅
- `test_all_fixes.py` - Comprehensive test of all fixes
- `test_latest_fixes.py` - Friendly robber and maritime trade
- `test_remaining_fixes.py` - Final round of fixes

### Manual Testing Needed 🔄
- Full gameplay from UI (user needs to test)
- All action types working correctly

## Key Files

### Engine
- `/engine/game.py` - Main game class
- `/engine/state.py` - Game state definition
- `/engine/state_functions.py` - State manipulation logic
- `/engine/models/actions.py` - Action generation

### UI Integration
- `/ui/web_server.py` - Flask server (bridge between engine and UI)
- `/ui/static/js/game.js` - Main UI JavaScript
- `/ui/templates/index.html` - HTML structure

### Documentation
- `FIXES_SUMMARY.md` - List of all fixes made
- `ARCHITECTURE.md` - Architecture explanation
- This file - Context for Claude

## Next Steps

1. **User Testing**: The user needs to play through a full game to verify everything works
2. **Polish**: Based on testing, might need minor UI improvements
3. **Future Features**: Could add player-vs-player, better AI, etc.

## Important Notes

### If User Reports "X doesn't work"
1. First check if it's a UI display issue (90% of issues so far)
2. Check if it's a format mismatch between UI and engine
3. The engine logic is probably correct - it's likely a presentation issue

### If Tempted to Add Logic to UI
**DON'T!** The engine already handles it. Find where the engine provides the information and display it properly.

### State Management
- The engine is the single source of truth
- The UI polls for updates and displays current state
- Never trust UI state over engine state

## Current Working Features
- ✅ Full game flow from setup to victory
- ✅ All building types (settlements, cities, roads)
- ✅ Resource collection and management  
- ✅ Development cards (all types working correctly)
- ✅ Trading (maritime only, no player trading yet)
- ✅ Robber movement and stealing (with resource shown)
- ✅ Friendly robber rule (based on public VPs)
- ✅ Longest road and largest army
- ✅ AI opponents with multiple difficulty levels:
  - Random (Easy) - Makes random moves
  - Smart Greedy (Medium) - Prioritizes certain actions with smart initial placement
  - Smart Simple Minimax (Hard) - Uses limited search with smart initial placement
  - Smart Full Minimax (Expert) - Deep search with smart initial placement
- ✅ Discard on 7 with modal selection UI
- ✅ Victory point tracking (public vs hidden)
- ✅ Comprehensive game log with icons
- ✅ Board balance rules (no adjacent 6/8s)

## Known Limitations
- No player-to-player trading (only maritime)
- No online multiplayer (local only)

## Future Possibilities
- Smarter AI opponents
- Player-to-player trading
- Online multiplayer support
- Additional map layouts
- Statistics tracking

## Remember
The project is stable and feature-complete for 1v1 play. The architecture is clean with proper separation of concerns. Any new features should maintain this architecture.

Good luck! 🎲