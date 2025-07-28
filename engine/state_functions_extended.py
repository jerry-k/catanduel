"""
Extended state functions that support forced outcomes for probabilistic expansion.

These functions wrap the original state functions and add support for
forcing specific random outcomes, which is needed for AI planning.
"""

import random
from typing import Optional, Tuple, List

from engine.models.enums import (
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    ActionPrompt, HAND_LIMIT
)
from engine.state import GameState
import engine.state_functions as sf


def roll_dice_with_outcome(state: GameState, forced_dice: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
    """
    Roll dice with optional forced outcome.
    
    Args:
        state: Game state to modify
        forced_dice: Optional tuple of (die1, die2) to force specific values
        
    Returns:
        The dice values used
    """
    if forced_dice:
        die1, die2 = forced_dice
        if not (1 <= die1 <= 6 and 1 <= die2 <= 6):
            raise ValueError(f"Invalid dice values: {forced_dice}")
    else:
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
    
    total = die1 + die2
    
    state.dice_rolled = True
    state.last_dice_roll = (die1, die2)
    
    if total == 7:
        # Handle 7 roll - check for discards
        state.current_turn_player = state.current_player
        
        # Check who needs to discard
        discarders = [
            state.players[i].total_resources() > HAND_LIMIT
            for i in range(2)
        ]
        
        if any(discarders):
            # Find first player who needs to discard
            state.current_player = discarders.index(True)
            state.current_prompt = ActionPrompt.DISCARD
            state.is_discarding = True
            state.invalidate_actions_cache()
        else:
            # No one needs to discard, move robber
            state.current_prompt = ActionPrompt.MOVE_ROBBER
            state.is_moving_robber = True
            state.invalidate_actions_cache()
    else:
        # Distribute resources
        sf.distribute_resources(state, total)
    
    return die1, die2


def buy_development_card_with_outcome(state: GameState, player_id: int, 
                                     forced_card: Optional[int] = None) -> int:
    """
    Buy development card with optional forced outcome.
    
    Args:
        state: Game state to modify
        player_id: Player buying the card
        forced_card: Optional card type to force
        
    Returns:
        The card type bought
    """
    player = state.players[player_id]
    
    # Check resources
    if not state.can_afford(player_id, sf.DEV_CARD_COST):
        raise ValueError("Cannot afford development card")
    
    # Check deck
    if not state.dev_card_deck:
        raise ValueError("No development cards left")
    
    # Pay cost
    sf.take_resources(state, player_id, sf.DEV_CARD_COST)
    
    # Draw card
    if forced_card is not None:
        # Verify forced card is in deck
        if forced_card not in state.dev_card_deck:
            raise ValueError(f"Card type {forced_card} not in deck")
        # Remove the specific card
        state.dev_card_deck.remove(forced_card)
        card = forced_card
    else:
        # Random draw
        card = state.dev_card_deck.pop()
    
    # Give card to player (bought this turn)
    player.dev_cards_bought_this_turn[card] += 1
    
    # Track VPs separately (hidden)
    if card == VICTORY_POINT:
        player.hidden_vps += 1
    
    return card


def steal_resource_with_outcome(state: GameState, thief: int, victim: int, 
                               forced_resource: Optional[int] = None) -> Optional[int]:
    """
    Steal resource with optional forced outcome.
    
    Args:
        state: Game state to modify
        thief: Player stealing
        victim: Player being robbed
        forced_resource: Optional resource type to force
        
    Returns:
        Resource type stolen, or None
    """
    victim_state = state.players[victim]
    
    # Build list of available resources
    available_resources = []
    for i in range(5):
        if victim_state.resources[i] > 0:
            available_resources.append(i)
    
    if not available_resources:
        return None
    
    # Choose resource
    if forced_resource is not None:
        if forced_resource not in available_resources:
            raise ValueError(f"Victim doesn't have resource type {forced_resource}")
        stolen = forced_resource
    else:
        # Random selection weighted by count
        resource_list = []
        for i in range(5):
            resource_list.extend([i] * victim_state.resources[i])
        stolen = random.choice(resource_list)
    
    # Transfer resource
    victim_state.resources[stolen] -= 1
    state.players[thief].resources[stolen] += 1
    
    return stolen


def move_robber_with_outcome(state: GameState, hex_id: int, victim_id: Optional[int],
                            forced_resource: Optional[int] = None) -> Optional[int]:
    """
    Move robber with optional forced stealing outcome.
    
    Args:
        state: Game state to modify
        hex_id: Hex to move robber to
        victim_id: Optional player to rob
        forced_resource: Optional resource type to force steal
        
    Returns:
        Resource type stolen, or None
    """
    # Move robber
    state.board.move_robber(hex_id)
    
    # Steal if victim specified
    stolen = None
    if victim_id is not None:
        if forced_resource is not None:
            stolen = steal_resource_with_outcome(state, state.current_turn_player, 
                                               victim_id, forced_resource)
        else:
            stolen = sf.steal_random_resource(state, state.current_turn_player, victim_id)
    
    # Return to normal play
    state.current_prompt = ActionPrompt.PLAY_TURN
    state.is_moving_robber = False
    state.invalidate_actions_cache()
    
    return stolen