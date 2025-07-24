# CatanDuel Current Bugs and Issues

## Overview
This document tracks bugs discovered during manual playtesting of CatanDuel. Each bug includes a description, expected behavior, investigation status, and potential causes.

Last updated: July 24, 2025 (2:45 PM)

## Bug List

### 1. Game Log Only Shows "AI_ACTION" Messages
**Status:** 🟡 Cause Identified

**Description:** The game log only displays generic "AI_ACTION" messages without any detail about what actually happened.

**Expected Behavior:** 
- Display dice roll numbers (e.g., "Player rolled 6+2=8")
- Show resources gained from dice rolls
- Log building actions (roads, settlements, cities)
- Log development card usage
- Display trading actions

**Root Cause:**
- Events are only being generated for AI actions in `web_server.py` (line 113-116)
- No event generation for human player actions, dice rolls, or other game events
- The log system exists but only tracks basic AI actions

**Fix Required:**
- Add comprehensive event generation for all action types
- Include dice roll results and resource collection
- Add events for human player actions in the execute_action endpoint

### 2. Longest Road Indicator Shows 0 Until 5+ Roads
**Status:** ✅ Fixed

**Description:** The UI showed road length as 0 for all players until someone achieved the longest road card (5+ roads).

**Expected Behavior:** Display actual road lengths (1, 2, 3, 4) for each player before anyone achieves longest road.

**Root Cause:**
- Server was only sending road length if player had the longest road card
- Missing method to calculate road length independent of longest road ownership

**Fix Applied:**
- Added `get_player_road_length()` method to Board class
- Updated adapter.py to include actual road lengths in UI state
- Modified web_server.py to send actual road lengths instead of 0

### 3. Largest Army Not Golden at 3 Knights
**Status:** ✅ Fixed

**Description:** The largest army indicator wasn't turning golden when a player played 3 knights.

**Expected Behavior:** Largest army should be highlighted golden when a player has played 3+ knights.

**Root Cause:**
- UI was missing highlighting logic for largest army (only had knight count display)
- Server was returning boolean values instead of player indices for largest_army_player

**Fix Applied:**
- Added golden highlighting logic in game.js matching longest road style
- Fixed server.py to return correct player index (0/1) or None for largest_army_player
- Now highlights with gold color (#f39c12), bold text, and "Largest Army" tooltip

### 4. Monopoly Card Action Log Inaccuracy
**Status:** ✅ Fixed

**Description:** Action log showed "took 0 wood" when monopoly card actually took resources from opponent.

**Expected Behavior:** Action log should show correct resource count taken.

**Root Cause:**
- The `total_taken` field in monopoly event was hardcoded to 0 in web_server.py
- Server wasn't tracking how many resources were taken during monopoly execution

**Fix Applied:**
- Modified web_server.py to capture opponent's resource count before monopoly execution
- Updated event generation to use actual resources taken instead of hardcoded 0
- Now correctly displays "took 1 cards", "took 3 cards", etc.

### 5. Victory Point Card Display
**Status:** ✅ Fixed

**Description:** Victory point dev cards were not shown in player's VP display in parenthetical format.

**Expected Behavior:** Show visible VPs with total in parentheses: "2 (3)" if player has 1 hidden VP card.

**Root Cause:**
- Server wasn't sending hidden VP counts to the UI
- UI wasn't displaying total VPs including hidden cards

**Fix Applied:**
- Added `hidden_vps` field to game state in web_server.py
- Human player can see their own hidden VPs; AI's remain secret
- Updated game.js to display "visible (total)" format when hidden VPs exist
- Shows just visible count when no hidden VPs (cleaner display)

### 6. Road Building UI Indicators Too Faint
**Status:** ✅ Fixed

**Description:** Legal road positions shown with very faint yellow indicators during road building.

**Expected Behavior:** Clear, visible indicators for legal road building positions.

**Root Cause:**
- Road indicators had low opacity (0.5) and narrow stroke width (8px)
- Yellow color was not bright enough against the game board

**Fix Applied:**
- Changed color from 'yellow' to '#FFD700' (brighter gold)
- Increased stroke width from 8px to 10px
- Increased opacity from 0.5 to 0.85
- Road building indicators are now much more prominent and easier to see

## Summary

**Fixed in this session (14 issues):**
- ✅ Longest road indicator now shows actual road lengths (1, 2, 3, 4) instead of 0
- ✅ Largest army indicator turns golden when player has 3+ knights
- ✅ Monopoly card action log now shows correct resource count taken
- ✅ Victory point cards display in "visible (total)" format  
- ✅ Road building indicators are now more visible (brighter gold, higher opacity)
- ✅ Game no longer crashes when reaching 10 VP (fixed JSON serialization error)
- ✅ Robber hex indicators now use correct pointy-top orientation
- ✅ Road building indicators changed from gold to purple
- ✅ Building piece counters added as badges on build buttons (properly tracks initial placements)
- ✅ Build buttons made larger for better usability
- ✅ Friendly robber rule now correctly checks total VPs including hidden cards
- ✅ Roads can no longer be built through opponent settlements
- ✅ Build button counters now update correctly during gameplay
- ✅ Fixed UI layout shift with new fixed-height card containers

**Still pending:**
- 🟡 Game log only shows "AI_ACTION" messages (cause identified, fix not implemented)

### 12. Longest Road Miscalculation
**Status:** 🔴 Confirmed Bug

**Description:** Longest road calculation is incorrect for certain road configurations.

**Test Case:**
- Player has settlements at corners 0,2 and roads on edges 0-10
- Manual calculation shows longest path: 0→1→2→3→6→7→8→9→4→5 (9 roads)
- Engine calculates only 8 roads

**Root Cause:** 
The `get_player_road_length` method incorrectly handles the road graph construction. It's checking for "blocked" corners during graph building, which prevents proper edge connections. The algorithm should:
1. Build the complete road network graph without considering settlements
2. Then find the longest path

**Current Impact:** Longest road lengths may be undercounted by 1-2 roads in complex networks.

### 13. UI Layout Shift with Resources
**Status:** ✅ Fixed

**Description:** UI elements (scoreboard, action log) get squashed when player collects 4+ resources.

**Expected Behavior:** UI layout should remain stable regardless of card count.

**Root Cause:**
- Resource and dev card containers had dynamic height
- Cards would push down other UI elements as collection grew

**Fix Applied:**
- Implemented fixed-height containers (60px) for both resource and dev cards
- Made cards 40% smaller (48x60px)
- Only display cards with count > 0
- Added clean count badges in bottom-right corner
- Removed overlapping behavior for cleaner appearance

### 7. Game Crashes on Victory (JSON Serialization Error)
**Status:** ✅ Fixed

**Description:** When a player reaches 10 VP, the game crashes with "Object of type RandomPlayer is not JSON serializable" error.

**Expected Behavior:** Game should properly end and display winner when a player reaches 10 VP.

**Root Cause:**
- `game.get_winner()` returns a Player object which is not JSON serializable
- Both get_game_state and execute_action endpoints were trying to serialize Player objects

**Fix Applied:**
- Changed `game.get_winner()` to `game.state.get_winner()` in both endpoints
- Now returns player ID (0 or 1) instead of Player object
- UI already expected player ID format, so no frontend changes needed

### 8. QOL Improvements (Session 2)
**Status:** ✅ Fixed

**Changes Made:**
1. **Robber hex orientation** - Fixed red hex indicators to use pointy-top orientation matching game board
2. **Road building color** - Changed from gold (#FFD700) to purple (#9370DB) for better visibility
3. **Building piece counters** - Added badge-style counters on build buttons showing remaining pieces:
   - Properly counts pieces already on the board (including initial placements)
   - Shows 15 roads, 5 settlements, 4 cities maximum
   - Updates in real-time as pieces are built
4. **Larger build buttons** - Increased button size, icon size, and font size for better usability

### 9. Friendly Robber Rule Bug
**Status:** ✅ Fixed

**Description:** Could not place robber on hexes with opponent settlements even when opponent had 4 VP (more than the 3 VP threshold).

**Expected Behavior:** Friendly robber rule should only protect players with 2 or fewer VP.

**Root Cause:**
1. Rule was checking `public_vps` instead of `actual_vps()`, missing hidden VP cards
2. Robber placement was blocked entirely when no resources could be stolen

**Fix Applied:**
- Changed to use `actual_vps()` to include hidden VP cards in the check
- Allow robber placement with `victim_id=None` when no victims have resources
- Now correctly protects only players with ≤2 total VPs

### 10. Illegal Road Building Through Opponent Settlements
**Status:** ✅ Fixed

**Description:** Opponents could build roads through user's settlements (e.g., edges 6 and 7 both connecting to corner 6 with user's settlement).

**Expected Behavior:** Roads cannot pass through opponent settlements/cities per Catan rules.

**Root Cause:**
- `can_build_road` function didn't check if connecting corners had opponent buildings
- Allowed continuous road networks through opponent settlements

**Fix Applied:**
- Modified `can_build_road` in colonist_map.py to check for opponent buildings
- Updated Board.can_build_road to pass buildings data
- Roads now correctly blocked from passing through opponent settlements

### 11. Build Button Counters Not Updating
**Status:** ✅ Fixed

**Description:** Build button counters (roads, settlements, cities) were not updating during gameplay.

**Expected Behavior:** Counters should decrement as pieces are built.

**Root Cause:**
- JavaScript expected `gameState.buildings` as object but server sends array
- Player ID comparison mismatch (string vs number)

**Fix Applied:**
- Updated `updateBuildingCounters` to handle both array and object formats
- Fixed player ID comparison to handle both strings and numbers
- Counters now properly track remaining pieces
