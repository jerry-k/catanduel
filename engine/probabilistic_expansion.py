"""
Probabilistic expansion support for AI players.

This module provides functions to expand actions into all possible outcomes
with their associated probabilities. It allows AI players to perform
expectimax search by considering all possible results of random actions.

Based on catanatron's tree_search_utils.py approach.
"""

from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import random

from engine.models.enums import (
    Action, ActionType,
    RESOURCES, WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    DEVELOPMENT_CARDS
)
from engine.game import Game
import engine.state_functions as sf
import engine.state_functions_extended as sfe


# Dice probabilities for sums 2-12
DICE_PROBABILITIES = {
    2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
    7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
}

# Actions that don't involve randomness
DETERMINISTIC_ACTIONS = {
    ActionType.END_TURN,
    ActionType.BUILD_SETTLEMENT,
    ActionType.BUILD_ROAD,
    ActionType.BUILD_CITY,
    ActionType.PLAY_KNIGHT_CARD,
    ActionType.PLAY_YEAR_OF_PLENTY,
    ActionType.PLAY_ROAD_BUILDING,
    ActionType.PLAY_MONOPOLY,
    ActionType.MARITIME_TRADE,
    ActionType.DISCARD,  # Treated as deterministic (player chooses optimally)
    ActionType.BUILD_INITIAL_SETTLEMENT,
    ActionType.BUILD_INITIAL_ROAD,
}


def execute_deterministic(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Execute a deterministic action and return single outcome with probability 1.0."""
    game_copy = game.copy()
    try:
        game_copy.execute(action, validate=False)
        return [(game_copy, 1.0)]
    except Exception:
        # Action failed - this can happen in AI search when exploring invalid branches
        # Return empty list to indicate no valid outcomes
        return []


def execute_spectrum(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """
    Execute an action and return all possible outcomes with probabilities.
    
    Args:
        game: Current game state
        action: Action to execute
        
    Returns:
        List of (game_copy, probability) tuples representing all possible outcomes
    """
    if action.action_type in DETERMINISTIC_ACTIONS:
        return execute_deterministic(game, action)
    
    elif action.action_type == ActionType.ROLL:
        return expand_roll(game, action)
    
    elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
        return expand_dev_card(game, action)
    
    elif action.action_type == ActionType.MOVE_ROBBER:
        return expand_robber(game, action)
    
    else:
        # Unknown action type, treat as deterministic
        return execute_deterministic(game, action)


def expand_roll(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Expand dice roll into all 11 possible outcomes (sums 2-12)."""
    results = []
    
    for total in range(2, 13):
        # Use the first valid dice combination for each total
        for die1 in range(1, 7):
            die2 = total - die1
            if 1 <= die2 <= 6:
                # Create a copy and execute with forced dice values
                game_copy = game.copy()
                
                # Execute roll with forced outcome
                sfe.roll_dice_with_outcome(game_copy.state, forced_dice=(die1, die2))
                
                results.append((game_copy, DICE_PROBABILITIES[total]))
                break  # Only need one combination per total
    
    return results


def expand_dev_card(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Expand development card purchase into all possible card outcomes."""
    results = []
    player_id = game.state.current_player
    
    # Get the current development card deck
    deck = game.state.dev_card_deck.copy()
    
    if not deck:
        # No cards left, treat as deterministic failure
        return []
    
    # Count each card type in the deck
    card_counts = defaultdict(int)
    for card in deck:
        card_counts[card] += 1
    
    total_cards = len(deck)
    
    # For each possible card type that could be drawn
    for card_type, count in card_counts.items():
        if count > 0:
            probability = count / total_cards
            
            # Create a game copy and force this specific card to be drawn
            game_copy = game.copy()
            
            try:
                # Buy the development card with forced outcome
                sfe.buy_development_card_with_outcome(game_copy.state, player_id, 
                                                     forced_card=card_type)
                results.append((game_copy, probability))
            except ValueError:
                # This can happen if player can't afford or other validation fails
                # In AI search, we might imagine impossible outcomes
                pass
    
    return results


def expand_robber(game: Game, action: Action) -> List[Tuple[Game, float]]:
    """Expand robber movement with all possible stealing outcomes."""
    hex_id, victim_id = action.value
    
    if victim_id is None:
        # No one to rob, deterministic
        return execute_deterministic(game, action)
    
    # Get victim's resources
    victim_resources = game.state.players[victim_id].resources
    total_resources = sum(victim_resources)
    
    if total_resources == 0:
        # Nothing to steal, deterministic
        return execute_deterministic(game, action)
    
    results = []
    
    # For each resource type the victim has
    for resource_type in range(5):
        if victim_resources[resource_type] > 0:
            # Calculate probability based on victim's hand composition
            probability = victim_resources[resource_type] / total_resources
            
            # Create game copy and execute with forced resource
            game_copy = game.copy()
            
            try:
                # Move robber with forced stealing outcome
                sfe.move_robber_with_outcome(game_copy.state, hex_id, victim_id,
                                           forced_resource=resource_type)
                results.append((game_copy, probability))
            except ValueError:
                # This shouldn't happen but handle gracefully
                pass
    
    return results


def expand_spectrum(game: Game, actions: List[Action]) -> Dict[Action, List[Tuple[Game, float]]]:
    """
    Expand multiple actions into their possible outcomes.
    
    Args:
        game: Current game state
        actions: List of actions to expand
        
    Returns:
        Dictionary mapping each action to its list of (game_copy, probability) outcomes
    """
    results = {}
    for action in actions:
        results[action] = execute_spectrum(game, action)
    return results


def get_expected_value(game: Game, action: Action, value_function) -> float:
    """
    Calculate expected value of an action using a value function.
    
    Args:
        game: Current game state
        action: Action to evaluate
        value_function: Function that takes a game state and returns a value
        
    Returns:
        Expected value across all possible outcomes
    """
    outcomes = execute_spectrum(game, action)
    expected_value = 0.0
    
    for game_outcome, probability in outcomes:
        value = value_function(game_outcome)
        expected_value += probability * value
    
    return expected_value