# Colonist to CatanDuel Log Conversion Plan

## Overview

This document outlines the plan for converting Colonist.io's verbose JSON log format to CatanDuel's minimal action-based format. The goal is to extract only the essential game actions while discarding redundant state information.

## Format Comparison

### Colonist Format (Verbose)
```json
{
  "data": {
    "eventHistory": {
      "events": [
        {
          "deltaS": 1.5,
          "stateChange": {
            "mapState": {...},
            "gameLogState": {...},
            "diceState": {...}
          }
        }
      ]
    },
    "initialState": {...},
    "endGameState": {...}
  }
}
```
- **Structure**: Deeply nested with state tracking
- **Size**: ~500+ lines for a short game
- **Content**: Full state changes, UI events, timing data
- **Redundancy**: Same information stored multiple ways

### CatanDuel Format (Minimal)
```json
[
  [0, "BUILD_INITIAL_SETTLEMENT", 41],
  [0, "BUILD_INITIAL_ROAD", 53],
  [1, "ROLL", [6, 3]],
  [0, "END_TURN", null]
]
```
- **Structure**: Simple array of [player_id, action_type, value]
- **Size**: ~50 lines for same game
- **Content**: Only player actions
- **Efficiency**: State inferred from action sequence

## Key Mappings

### Resource Types
| Resource | CatanDuel | Colonist |
|----------|-----------|----------|
| Wood     | 0         | 2        |
| Brick    | 1         | 1        |
| Sheep    | 2         | 5        |
| Wheat    | 3         | 4        |
| Ore      | 4         | 3        |
| Desert   | 5         | 0        |

### Player Colors
| Player   | CatanDuel | Colonist |
|----------|-----------|----------|
| Player 0 | Red (0)   | Red (1)  |
| Player 1 | Black (1) | Blue (5) |

### Event Types (Colonist → CatanDuel)
| Colonist Type | Colonist Code | CatanDuel Action |
|---------------|---------------|------------------|
| Roll Dice     | 10           | ROLL             |
| Build Road    | 4 (piece=0)  | BUILD_ROAD       |
| Build Settlement | 4 (piece=2) | BUILD_SETTLEMENT |
| Build City    | 5            | BUILD_CITY       |
| Buy Dev Card  | 1            | BUY_DEVELOPMENT_CARD |
| End Turn      | 44           | END_TURN         |
| Move Robber   | 11           | MOVE_ROBBER      |
| Discard       | 113          | DISCARD          |
| Trade Bank    | 116          | MARITIME_TRADE   |

## Conversion Strategy

### Extract From Colonist
1. **Player Actions Only**
   - Build actions (settlements, roads, cities)
   - Dice rolls with values
   - Development card purchases/plays
   - Resource trades
   - Robber movements
   - Turn endings

2. **Special Cases**
   - Initial settlement phase (4 placements)
   - Development card plays (knight, monopoly, etc.)
   - Maritime trades (port ratios)

### Discard From Colonist
1. **State Changes**
   - Resource production events
   - Victory point updates
   - Bank state changes

2. **UI/Meta Information**
   - Time deltas (deltaS)
   - Animation states
   - Log text formatting

3. **Redundant Events**
   - Resource gain notifications (inferred from dice)
   - Longest road/largest army updates
   - Turn state transitions

## Implementation Approach

### Phase 1: Core Converter
```python
class ColonistToCatanDuelConverter:
    """Convert Colonist logs to CatanDuel format."""
    
    def __init__(self, colonist_json: str):
        self.data = json.loads(colonist_json)
        self.events = self._extract_events()
        
    def convert(self) -> List[List]:
        """Main conversion method."""
        actions = []
        
        for event in self.events:
            action = self._parse_event(event)
            if action:
                actions.append(action)
                
        return actions
```

### Phase 2: Event Parsing
```python
def _parse_event(self, event) -> Optional[List]:
    """Parse single colonist event to CatanDuel action."""
    
    # Extract game log entries
    log_entries = event.get("stateChange", {}).get("gameLogState", {})
    
    for log_entry in log_entries.values():
        action = self._extract_action(log_entry)
        if action:
            return action
            
    # Check for other state changes (builds, etc.)
    return self._extract_from_state_change(event)
```

### Phase 3: Coordinate Mapping
Since both systems use the same coordinate system (0-53 corners, 0-71 edges), we can use direct mapping. However, we need to verify this assumption with test games.

### Phase 4: Validation
1. Convert a colonist log
2. Replay in CatanDuel engine
3. Compare final states:
   - Building counts
   - Victory points
   - Resource counts
   - Special achievements

## Example Conversion

### Colonist Event (Verbose)
```json
{
  "deltaS": 1.5,
  "stateChange": {
    "mapState": {
      "tileCornerStates": {
        "41": {
          "owner": 1,
          "buildingType": 1
        }
      }
    },
    "gameLogState": {
      "0": {
        "from": 1,
        "text": {
          "type": 4,
          "pieceEnum": 2,
          "playerColor": 1
        }
      }
    }
  }
}
```

### CatanDuel Action (Minimal)
```json
[0, "BUILD_INITIAL_SETTLEMENT", 41]
```

## Testing Strategy

1. **Unit Tests**
   - Test each event type conversion
   - Verify coordinate mappings
   - Check resource/player mappings

2. **Integration Tests**
   - Convert full game logs
   - Replay in engine
   - Validate outcomes

3. **Edge Cases**
   - Games with all dev card types
   - Various trade scenarios
   - Robber movements
   - Different victory conditions
