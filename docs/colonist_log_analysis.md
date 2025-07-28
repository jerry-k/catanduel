# Colonist Log Format Analysis

## Overview
The colonist.io log format is a comprehensive JSON structure that captures every aspect of a game from start to finish. This document reverse-engineers the format based on `examplelog.json`.

## Top-Level Structure
```json
{
  "data": {
    "eventHistory": {
      "events": [...],
      "version": 0,
      "startTime": "2025-07-14T20:06:13.496Z",
      "botUserNames": {},
      "endGameState": {...},
      "initialState": {...},
      "eventsPerspectives": [1, 5]
    },
    "playerUserStates": [...],
    "playOrder": [1, 5],
    "gameDetails": {...},
    "gameSettings": {...},
    "databaseGameId": "168643344",
    "playerPerspective": 5
  }
}
```

## Event Structure
Each event in the `events` array contains:
```json
{
  "input": {
    "deltaS": 51.2  // Time since last event in seconds
  },
  "stateChange": {
    // Various state updates
  }
}
```

## State Change Types

### 1. mapState
Board modifications:
- `tileCornerStates`: Settlement/city placements (corners 0-53)
- `tileEdgeStates`: Road placements (edges 0-71)
- `tileHexStates`: Hex definitions (0-18)

### 2. currentState
Game flow control:
- `startTime`: Timestamp
- `turnState`: Current phase
- `actionState`: Current action type
- `allocatedTime`: Time limit in seconds
- `completedTurns`: Turn counter
- `currentTurnPlayerColor`: Active player

### 3. gameLogState
Text log entries with type codes:
```json
{
  "2": {
    "from": 1,
    "text": {
      "type": 4,
      "pieceEnum": 2,
      "playerColor": 1
    }
  }
}
```

### 4. playerStates
Player-specific data:
- `resourceCards`: Current hand
- `victoryPointsState`: VP breakdown
- `isTakingAction`: Action status

### 5. bankState
Bank resources remaining

### 6. diceState
Dice roll information

### 7. Various mechanicXState
Game mechanics tracking (roads, settlements, dev cards, etc.)

## Type Code Mappings

### Log Entry Types
| Type | Meaning | Additional Fields |
|------|---------|-------------------|
| 0 | Player reconnected | playerColor |
| 1 | Buy development card | playerColor |
| 4 | Build piece (setup) | pieceEnum (0=road, 2=settlement), playerColor |
| 5 | Build piece (game) | pieceEnum (0=road, 2=settlement, 3=city), playerColor, isVp |
| 10 | Roll dice | firstDice, secondDice, playerColor |
| 11 | Move robber | tileInfo (location), pieceEnum=5, playerColor |
| 14 | Steal card (to victim) | cardEnums, playerColor |
| 15 | Steal card (to thief) | cardEnums, playerColor |
| 20 | Play dev card | cardEnum, playerColor |
| 24 | Player disconnected | playerColor |
| 44 | End turn | - |
| 45 | Turn started | playerColor |
| 47 | Resource distribution | cardsToBroadcast, distributionType (0=setup, 1=dice) |
| 49 | Robber blocks | tileInfo |
| 60 | Seven rolled | all (discard all?) |
| 66 | Achievement | achievementEnum (1=largest army) |
| 74 | Robber moved | - |
| 112 | Discard phase | playerColor |
| 116 | Maritime trade | givenCardEnums, receivedCardEnums |
| 130 | Timer warning | count |

### Resource Mappings
| ID | Resource | CatanDuel Mapping |
|----|----------|-------------------|
| 0 | Desert | 5 |
| 1 | Brick | 1 |
| 2 | Wood | 0 |
| 3 | Ore | 4 |
| 4 | Wheat | 3 |
| 5 | Sheep | 2 |

### Player Color Mappings
| ID | Color | CatanDuel Mapping |
|----|-------|-------------------|
| 1 | Red | 0 |
| 5 | Blue | 1 |

### Development Card Mappings
| ID | Card Type |
|----|-----------|
| 10 | Unknown (in bank) |
| 11 | Knight |
| 12 | Victory Point |
| 13 | Monopoly (probable) |
| 14 | Year of Plenty (probable) |
| 15 | Road Building |

## Initial State
Contains complete board setup:
- `mapState`: All hex types, numbers, port locations
- `bankState`: Starting resources (19 each)
- `playerStates`: Empty hands, 0 VPs
- `mechanicXState`: Starting piece counts

## End Game State
Contains final statistics:
- Player rankings and VPs
- Resource income/loss breakdown
- Dice roll distribution
- Development card stats
- Game duration

## Key Insights for Conversion

1. **Redundancy**: Same information appears in multiple places (e.g., building in mapState and gameLogState)
2. **Timing**: deltaS provides exact timing but not needed for game logic
3. **Hidden Info**: Dev cards shown when bought/played
4. **State Tracking**: Full state after each event, not just deltas
5. **Coordinate System**: Same as CatanDuel (0-53 corners, 0-71 edges)

## Extractable Actions for ML
From this format, we can extract:
1. Board state at each decision point
2. Available actions (inferred from game rules)
3. Chosen action
4. Hidden information (what player knew vs didn't know)
5. Game outcome for reward assignment