# Development Card UI Investigation

## Overview
This document tracks the investigation into development card UI issues, specifically the monopoly card 400 error and verification of other dev card types.

Created: July 22, 2025

## Background
From the initial bug report, we identified that:
1. Dev cards bought this turn are incorrectly shown as playable (root cause found)
2. Monopoly card returns 400 error when played
3. Road Building and Year of Plenty cards haven't been tested

## Investigation Focus

### 1. Monopoly Card 400 Error
**Status:** 🟡 Cause Identified

**What we know:**
- Engine expects a single integer (0-4) for resource type
- Server returns 400 error due to format mismatch
- UI shows proper resource selection modal
- UI sends `resource` field instead of `value` field

**Root Cause:**
The UI sends:
```javascript
{
  player: 0,
  resource: 0,    // Wrong field name!
  type: "PLAY_MONOPOLY"
}
```

But server expects:
```javascript
{
  type: "PLAY_MONOPOLY",
  value: 0        // Should be 'value'
}
```

**Fix Required:**
- Find where monopoly action is created in UI
- Change `resource` field to `value` field

### 2. Road Building Card
**Status:** 🔴 Not Tested

**Expected behavior:**
- Player clicks Road Building card
- Can place 2 free roads
- Should see placement mode for roads

**To investigate:**
- [ ] Test if card is clickable
- [ ] Verify if it triggers road placement mode
- [ ] Check if 2 free roads are properly tracked
- [ ] Confirm action format matches server expectations

### 3. Year of Plenty Card
**Status:** 🔴 Not Tested

**Expected behavior:**
- Player clicks Year of Plenty card
- Resource selection dialog appears
- Player selects 2 resources (can be same type)
- Resources are added to player's hand

**To investigate:**
- [ ] Test if card is clickable
- [ ] Check for resource selection UI
- [ ] Verify action format (should be tuple of 2 resources)
- [ ] Confirm resources are properly added

## Technical Details

### Server Expectations
From the engine code (actions.py and state_functions.py):

1. **PLAY_MONOPOLY**: 
   - Type: ActionType.PLAY_MONOPOLY
   - Value: Single integer (0-4) representing resource type

2. **PLAY_ROAD_BUILDING**:
   - Type: ActionType.PLAY_ROAD_BUILDING
   - Value: None (roads placed separately)

3. **PLAY_YEAR_OF_PLENTY**:
   - Type: ActionType.PLAY_YEAR_OF_PLENTY
   - Value: Tuple (resource1, resource2) where each is 0-4

### UI Integration Points to Check

1. **Dev card display** - How are dev cards shown and made clickable?
2. **Click handlers** - What happens when a dev card is clicked?
3. **Resource selection** - Is there a modal or selection UI for monopoly/year of plenty?
4. **Action formatting** - How are dev card actions formatted before sending?
5. **API calls** - What's the exact format sent to the server?

## Next Steps

1. Search for dev card UI code more thoroughly
2. Test each dev card type systematically
3. Use browser developer tools to inspect network requests
4. Document exact error messages and request/response payloads
5. Create minimal test cases for each card type

## Additional Findings

### Knight Card
**Status:** ✅ Working
- Properly triggers robber movement when played
- No issues found

### Victory Point Display
**Status:** 🟟 Minor Issue
- Hidden VPs should show as "5 (6)" to the owner but just "5" to opponents
- Currently showing total to both players

### AI Player Quality
**Status:** 🟟 Not a bug, but worth noting
- Current RandomPlayer AI makes poor decisions
- Always settles in same spots
- Only builds roads, rarely other structures
- This is expected behavior for RandomPlayer (picks first valid action)

## Summary

**Bugs with identified causes:**
1. Monopoly card - Wrong field name in UI (`resource` vs `value`)
2. Forced dev card play - Engine not checking `bought_this_turn`

**Still need testing:**
1. Road Building card
2. Year of Plenty card

**Working correctly:**
1. Knight card
2. Dev card UI modals (for monopoly at least)

## Notes

- The UI was adapted from rlcatan, so dev card handling might use different patterns
- The monopoly modal works perfectly, just sends wrong field name
- Knight card implementation proves the basic dev card system works