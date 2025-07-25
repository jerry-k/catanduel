# Probabilistic Expansion Implementation Plan for CatanDuel Engine

## Executive Summary

This document outlines a plan to add probabilistic expansion support to the CatanDuel engine, enabling AI players to properly evaluate actions with random outcomes. This enhancement would allow for true expectimax search and bring our AI capabilities in line with catanatron's implementation.

## Current Limitations

Our engine currently only supports **deterministic execution** of random actions:
- When rolling dice, we get one random outcome
- When buying a dev card, we get one random card
- When stealing with the robber, we get one random resource

AI players cannot explore "what-if" scenarios for different outcomes, limiting their ability to make optimal decisions.

## Proposed Solution

Add **hypothetical execution** support that allows AI to explore all possible outcomes of random actions with their associated probabilities.

## Implementation Plan

### Phase 1: Action Structure Enhancement

**1.1 Modify Action Class**
```python
# Current
Action = namedtuple("Action", ["action_type", "value"])

# Proposed
@dataclass
class Action:
    action_type: ActionType
    value: Any = None
    forced_outcome: Optional[Any] = None  # For hypothetical execution
```

**1.2 Action Value Semantics**
- For ROLL: `forced_outcome = (dice1, dice2)`
- For BUY_DEVELOPMENT_CARD: `forced_outcome = card_type`
- For MOVE_ROBBER with stealing: `forced_outcome = (hex_id, victim_id, resource_stolen)`

### Phase 2: Core Engine Modifications

**2.1 Add Hypothetical Execution to Game.execute()**

```python
def execute(self, action: Action, validate: bool = True) -> bool:
    """Execute an action, optionally with forced outcome."""
    if action.action_type == ActionType.ROLL:
        if action.forced_outcome:
            dice1, dice2 = action.forced_outcome
            self._execute_roll_with_outcome(dice1, dice2)
        else:
            self._execute_roll_random()
    # Similar for other probabilistic actions
```

**2.2 Implement Probabilistic Expansion Functions**

Create new module `engine/probabilistic_expansion.py`:

```python
def expand_spectrum(game: Game, actions: List[Action]) -> Dict[Action, List[Tuple[Game, float]]]:
    """Expand all actions into their possible outcomes with probabilities."""
    results = {}
    for action in actions:
        results[action] = execute_spectrum(game, action)
    return results

def execute_spectrum(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Execute one action expanding all possible outcomes."""
    if action.action_type == ActionType.ROLL:
        return expand_roll(game, action)
    elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
        return expand_dev_card(game, action)
    elif action.action_type == ActionType.MOVE_ROBBER:
        return expand_robber(game, action)
    else:
        # Deterministic action
        return [(execute_copy(game, action), 1.0)]
```

**2.3 Specific Expansion Implementations**

```python
DICE_PROBABILITIES = {
    2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
    7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
}

def expand_roll(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Expand dice roll into all 11 possible outcomes."""
    results = []
    for total in range(2, 13):
        # Generate all ways to get this total
        for dice1 in range(1, 7):
            dice2 = total - dice1
            if 1 <= dice2 <= 6:
                game_copy = game.copy()
                forced_action = Action(
                    action_type=ActionType.ROLL,
                    value=None,
                    forced_outcome=(dice1, dice2)
                )
                if game_copy.execute(forced_action, validate=False):
                    results.append((game_copy, DICE_PROBABILITIES[total]))
                break  # Only need one way to get each total
    return results
```

### Phase 3: State Management Enhancements

**3.1 Optimize Game Copying**
- Implement efficient deep copy for GameState
- Consider copy-on-write for large structures
- Profile and optimize copy performance

**3.2 Development Card Deck Tracking**
```python
@dataclass
class DevelopmentDeck:
    cards: List[DevelopmentCard]
    
    def get_probabilities(self) -> Dict[DevelopmentCard, float]:
        """Get probability of drawing each card type."""
        total = len(self.cards)
        if total == 0:
            return {}
        counts = Counter(self.cards)
        return {card: count/total for card, count in counts.items()}
```

### Phase 4: Hidden Information Handling

**4.1 Track Unknown Cards**
- When opponents buy dev cards, track them as "unknown"
- When calculating probabilities, include these unknown cards
- Model opponent's hand for robber stealing probabilities

**4.2 Robber Stealing Enhancement**
```python
def expand_robber(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Expand robber movement with all possible stealing outcomes."""
    hex_id, victim_id = action.value
    
    if victim_id is None:
        # No stealing, deterministic
        return [(execute_copy(game, action), 1.0)]
    
    # Get victim's resources
    victim_resources = game.state.players[victim_id].resources
    total_resources = sum(victim_resources)
    
    if total_resources == 0:
        return [(execute_copy(game, action), 1.0)]
    
    results = []
    for resource_type in range(5):
        if victim_resources[resource_type] > 0:
            probability = victim_resources[resource_type] / total_resources
            game_copy = game.copy()
            forced_action = Action(
                action_type=ActionType.MOVE_ROBBER,
                value=(hex_id, victim_id),
                forced_outcome=resource_type
            )
            if game_copy.execute(forced_action, validate=False):
                results.append((game_copy, probability))
    
    return results
```

### Phase 5: AI Player Integration

**5.1 Update AI Base Class**
```python
class Player:
    def use_probabilistic_expansion(self) -> bool:
        """Override to enable probabilistic expansion."""
        return False
```

**5.2 Update Minimax/AlphaBeta Players**
- Modify search algorithms to use `expand_spectrum` when available
- Calculate expected values across all outcomes
- Update CatanatronAlphaBetaPlayer to use new functionality

## Impact Analysis

### Backward Compatibility
- Existing code continues to work with `forced_outcome=None`
- Default behavior remains random execution
- Only AI players that opt-in use probabilistic expansion

### Performance Considerations
- Game copying needs to be efficient (target: <1ms per copy)
- Dice roll expansion: 11 copies per ROLL action
- Dev card expansion: up to 5 copies per BUY action
- Search depth may need adjustment due to increased branching

### Testing Requirements
1. Unit tests for each expansion function
2. Verify probability calculations
3. Performance benchmarks for game copying
4. Integration tests with AI players
5. Regression tests for existing functionality

## Implementation Timeline

1. **Week 1**: Action structure enhancement and basic forced execution
2. **Week 2**: Implement expansion functions for all action types
3. **Week 3**: Optimize game copying and add hidden information tracking
4. **Week 4**: Integrate with AI players and testing

## Success Metrics

1. CatanatronAlphaBetaPlayer properly evaluates dev card purchases
2. AI can calculate expected value of rolling vs other actions
3. Performance: <100ms overhead per turn for probabilistic AI
4. No regression in existing functionality

## Open Questions

1. Should we support partial probability trees (e.g., only expand top 3 most likely outcomes)?
2. How to handle very deep trees (3+ levels with full expansion)?
3. Should we add caching for repeated game state evaluations?
4. Do we need to support custom probability distributions (e.g., for loaded dice variants)?

## Conclusion

Adding probabilistic expansion support would significantly enhance our AI capabilities, allowing for sophisticated decision-making that considers all possible outcomes. While the implementation requires careful attention to performance and correctness, the modular design allows for incremental development and testing.