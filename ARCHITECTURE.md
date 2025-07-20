# CatanDuel UI Architecture

## Clean Separation of Concerns

### Game Engine (Python)
- **Owns ALL game logic**: rules, valid moves, state management
- **Provides legal actions**: list of all valid moves for current state
- **Validates actions**: ensures moves are legal before executing
- **Examples**:
  - Friendly robber rule: engine filters which hexes robber can be placed on
  - Discard: engine generates all valid discard combinations
  - Trade: engine determines available trade ratios based on ports

### Web Server (Flask)
- **Simple bridge**: translates between engine and UI formats
- **No game logic**: just format conversion
- **State serialization**: converts engine state to UI-friendly JSON

### UI (JavaScript)
- **Pure presentation**: displays game state and available actions
- **User interaction**: converts user clicks/selections into actions
- **No game logic**: doesn't know rules, just shows what engine says
- **UI enhancements**:
  - Modal for card selection (better UX than showing 100+ discard combinations)
  - Visual placement guides for settlements/roads
  - Card grouping and counting

## Example: Discard Flow

1. **Engine**: "Player needs to discard 4 cards. Here are all 35 valid combinations"
2. **UI**: Shows modal saying "Select 4 cards to discard" (better UX)
3. **User**: Clicks cards to select
4. **UI**: Sends selected combination as DISCARD action
5. **Engine**: Validates it's one of the 35 valid combinations
6. **Engine**: Executes discard if valid, rejects if not

## Key Points

- Engine has ALL game logic
- UI is just a pretty interface to display state and collect input
- Web server is a thin translation layer
- UI can provide better UX (modals, drag-drop, etc.) without implementing game logic