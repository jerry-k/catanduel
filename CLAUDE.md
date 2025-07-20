# CatanDuel Project Context for Claude

## Project Overview
This is CatanDuel - a 2-player version of Catan with a Python game engine and web UI. The web UI was salvaged from rlcatan (a reinforcement learning Catan project) and adapted to work with our custom engine.

## Current State (July 20, 2025)
The project is **fully functional** and ready for playtesting. All major UI bugs have been fixed, and the game should be playable from start to finish.

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

## Recent Fixes (All Completed)

### UI Display Issues
- Settlement/city asset mix-up (was showing wrong images)
- Dice not showing after first roll
- Roll dice button missing text
- Buy dev card button not clickable
- Dev cards not showing when bought same turn
- Dice not updating for opponent rolls

### Action Communication Issues
- Maritime trade was sending wrong format (fixed with tuple handling)
- Discard was trying to be random (fixed with proper selection UI)
- Action type mismatches (BUY_DEVELOPMENT_CARD vs BUY_DEV_CARD)

### Game Flow Issues
- AI freezing when rolling 7 (fixed state management)
- Friendly robber preventing all movement (fixed to only restrict placement)

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
- ✅ Development cards (all types)
- ✅ Trading (maritime only, no player trading yet)
- ✅ Robber movement and stealing
- ✅ Friendly robber rule
- ✅ Longest road and largest army
- ✅ AI opponent (simple random AI)
- ✅ Discard on 7 with selection UI
- ✅ Victory point tracking

## Remember
This project is in a good, working state. Most "bugs" are just UI display issues. The engine is solid. Keep the architecture clean and resist the urge to add complexity where it's not needed.

Good luck! 🎲