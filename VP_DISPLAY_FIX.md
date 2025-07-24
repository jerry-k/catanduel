# Victory Point Display Fix

## Problem
The UI was only showing visible victory points, not indicating when players have hidden VP cards from development cards. The user requested the display format "visible (total)" where visible is public VPs and total includes hidden VP cards.

## Solution

### 1. Server Changes (ui/web_server.py)
Added `hidden_vps` to the game state sent to the UI:
```python
'hidden_vps': {
    '0': state.players[0].hidden_vps,  # Human player can see their own hidden VPs
    '1': 0  # AI's hidden VPs are not revealed to human player
},
```

### 2. UI Changes (ui/static/js/game.js)
Updated the VP display logic to show "visible (total)" format:
```javascript
// Update VP - show as "visible (total)" if there are hidden VPs
const visibleVPs = gameState.victory_points[playerKey] || 0;
const hiddenVPs = gameState.hidden_vps ? (gameState.hidden_vps[playerKey] || 0) : 0;
const totalVPs = visibleVPs + hiddenVPs;

// Display format: "visible (total)" if hidden VPs exist, otherwise just "visible"
const vpDisplay = hiddenVPs > 0 ? `${visibleVPs} (${totalVPs})` : `${visibleVPs}`;
statsDiv.querySelector('[data-stat="vp"]').textContent = vpDisplay;
```

## Key Design Decisions

1. **Privacy**: Only the human player (player 0) can see their own hidden VPs. The AI's hidden VPs are kept secret (sent as 0) to maintain game integrity.

2. **Display Format**: 
   - When no hidden VPs: Shows just the number (e.g., "4")
   - When hidden VPs exist: Shows "visible (total)" (e.g., "4 (6)")

3. **Game End**: The existing game-over logic already uses `actual_vps()` which includes hidden VPs, so the game will properly end when any player reaches 10 total VPs.

## Testing
Created test_vp_display.py to verify:
- Server correctly sends hidden VP data
- Human player sees their own hidden VPs
- AI's hidden VPs remain hidden
- Display format works as expected

## Files Modified
- `/Users/jerrykim/repos/catan/catanduel/ui/web_server.py` - Added hidden_vps to game state
- `/Users/jerrykim/repos/catan/catanduel/ui/static/js/game.js` - Updated VP display logic
- `/Users/jerrykim/repos/catan/catanduel/ui/test_vp_display.py` - Created test file