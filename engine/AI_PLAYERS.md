# CatanDuel AI Players

This document describes the AI player implementations available in CatanDuel.

## Overview

CatanDuel includes several AI player implementations with varying levels of sophistication:

1. **RandomPlayer** - Baseline that chooses actions uniformly at random
2. **GreedyPlayer** - Simple heuristic-based player with action priorities  
3. **MinimaxPlayer** - Minimax search with alpha-beta pruning
4. **MCTSPlayer** - Monte Carlo Tree Search with UCT selection

## Player Descriptions

### RandomPlayer
- **Strength**: Weakest (baseline)
- **Speed**: Fastest
- **Use case**: Testing, baseline comparison
- Selects actions uniformly at random from valid moves

### GreedyPlayer
- **Strength**: Weak
- **Speed**: Very fast
- **Use case**: Quick games, weak opponent
- Uses simple priority rules:
  1. Build city (if possible)
  2. Build settlement (if possible)
  3. Buy development card
  4. Build road
  5. Play development cards
  6. Trade at ports
  7. Everything else

### SimpleMinimaxPlayer
- **Strength**: Medium
- **Speed**: Fast
- **Parameters**: 
  - Search depth: 2
  - Time limit: 1 second
- Simplified evaluation function focusing on victory points

### MinimaxPlayer
- **Strength**: Strong
- **Speed**: Medium
- **Parameters**:
  - Search depth: 3 (configurable)
  - Time limit: 2 seconds (configurable)
- Features:
  - Alpha-beta pruning for efficiency
  - Comprehensive evaluation function
  - Action pruning heuristics
- Evaluation considers:
  - Victory points (weighted 100)
  - Development cards and knights
  - Resource count and diversity
  - Building potential
  - Longest road and largest army
  - Port access

### FastMCTSPlayer
- **Strength**: Medium-Strong
- **Speed**: Fast
- **Parameters**:
  - Time limit: 0.5 seconds
  - Exploration constant: 1.0
  - Simulation depth: 20
- Faster MCTS variant for real-time play

### MCTSPlayer
- **Strength**: Strong
- **Speed**: Medium
- **Parameters**:
  - Time limit: 2 seconds (configurable)
  - Exploration constant: 1.414 (configurable)
  - Simulation depth: 50 (configurable)
- Features:
  - UCT (UCB1) selection policy
  - Weighted action selection in simulations
  - Handles high branching factor well
  - Improves with more computation time

### StrongMCTSPlayer
- **Strength**: Very Strong
- **Speed**: Slow
- **Parameters**:
  - Time limit: 5 seconds
  - Exploration constant: 1.414
  - Simulation depth: 100
- Enhanced heuristics for action selection
- Best for finding optimal play

## Usage Examples

```python
from game import Game
from models import MinimaxPlayer, MCTSPlayer

# Create a game with AI players
players = [
    MinimaxPlayer(0, max_depth=3, time_limit=2.0),
    MCTSPlayer(1, time_limit=1.0)
]

game = Game(players)

# Play the game
while not game.is_over():
    actions = game.get_valid_actions()
    current_player = game._get_acting_player()
    action = game.players[current_player].decide(game, actions)
    game.execute(action)

winner = game.state.get_winner()
print(f"Player {winner} wins!")
```

## Performance Characteristics

Based on testing, the expected strength ranking is:

1. **StrongMCTSPlayer** - Best overall performance
2. **MCTSPlayer / MinimaxPlayer** - Strong play, good balance
3. **FastMCTSPlayer / SimpleMinimaxPlayer** - Decent play, very fast
4. **GreedyPlayer** - Weak but consistent
5. **RandomPlayer** - Baseline only

### Choosing an AI Player

- **For strongest play**: Use StrongMCTSPlayer or tune MCTSPlayer with more time
- **For balanced games**: Use MinimaxPlayer or MCTSPlayer with default settings
- **For fast games**: Use FastMCTSPlayer or SimpleMinimaxPlayer
- **For testing**: Use RandomPlayer as baseline or GreedyPlayer for consistency

### Algorithm Comparison

**Minimax with Alpha-Beta**:
- ✅ Deterministic and consistent
- ✅ Good tactical play
- ✅ Efficient with pruning
- ❌ Limited by search depth
- ❌ Requires good evaluation function

**Monte Carlo Tree Search**:
- ✅ Handles uncertainty well
- ✅ Scales with computation time
- ✅ No evaluation function needed
- ✅ Good for strategic play
- ❌ Non-deterministic
- ❌ Slower to find forced wins

## Customization

All AI players can be customized:

```python
# Custom Minimax player
minimax = MinimaxPlayer(
    player_id=0,
    name="CustomMM",
    max_depth=4,      # Deeper search
    time_limit=3.0    # More time
)

# Custom MCTS player  
mcts = MCTSPlayer(
    player_id=1,
    name="CustomMCTS",
    time_limit=5.0,           # More thinking time
    exploration_constant=2.0,  # More exploration
    simulation_depth=100      # Deeper simulations
)
```

## Future Improvements

Potential enhancements for even stronger AI:

1. **Neural network evaluation** - Train value/policy networks on game data
2. **Opening book** - Precomputed optimal setup placements
3. **Endgame tables** - Perfect play in simplified positions
4. **Opponent modeling** - Adapt to opponent's playstyle
5. **Parallel search** - Use multiple threads for deeper search
6. **Learning** - Self-play reinforcement learning

## Implementation Notes

- All AI players inherit from the base `Player` class
- The `decide()` method is the main interface
- Players receive a read-only game state to prevent cheating
- Action validation is handled by the game engine
- Players should handle time limits gracefully