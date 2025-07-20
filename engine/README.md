# CatanDuel Engine

A simplified 1v1 Catan game engine optimized for AI development, based on the catanatron architecture.

## Overview

CatanDuel is a 2-player variant of Settlers of Catan designed for:
- Fast game simulation (100+ games/second)
- AI agent development and training
- Integration with colonist.io coordinate system
- Simplified rules (no player-to-player trading)

## Architecture

The engine follows catanatron's proven immutable state design:

- **Immutable game states** - States are never modified in place, enabling efficient tree search
- **Pure functions** - All game logic is in pure functions that take a state and return a new state
- **Action-based flow** - Simple action/response pattern instead of complex state machines
- **Efficient copying** - Optimized state copying for Monte Carlo Tree Search

## Key Components

### Core Files
- `game.py` - Main game controller and API
- `state.py` - Immutable game state representation
- `state_functions.py` - Pure functions for state manipulation
- `models/board.py` - Board state and longest road calculation
- `models/actions.py` - Action generation and validation
- `models/player.py` - Player interface and basic AI implementations
- `colonist_map.py` - Colonist.io coordinate mappings

### Game Rules
- 2 players only
- Friendly robber (can't place if no one has 3+ points)
- Maritime trading only (no player-to-player trades)
- Standard Catan building rules and costs
- Victory at 10 points

## Usage

```python
from game import Game
from models.player import RandomPlayer

# Create two players
players = [
    RandomPlayer(0, "Player 0"),
    RandomPlayer(1, "Player 1")
]

# Create and play a game
game = Game(players, seed=42)
winner = game.play()

print(f"Winner: {winner.name}")
```

## Performance

The engine achieves 100+ games/second on modern hardware, making it suitable for:
- Monte Carlo Tree Search
- Reinforcement learning
- Large-scale game analysis

## Next Steps

To build a 1900 ELO AI:
1. Implement MCTS player (models/mcts_player.py)
2. Add position evaluation heuristics
3. Train value/policy networks
4. Optimize with colonist.io game data

## Known Issues

- Some edge cases with discard actions need fixing
- Board generation could use more balance rules
- Missing some colonist.io specific features

## Testing

Run basic tests:
```bash
python3 test_basic.py
```

## Credits

Based on [catanatron](https://github.com/bcollazo/catanatron) by Bryan Collazo.