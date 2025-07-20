"""
Pure functions for manipulating game state.

These functions take a GameState and modify it in place. They handle
all the game logic for building, trading, playing cards, etc.

Based on catanatron's state_functions.py but simplified for 2 players.
"""

import random
from typing import List, Optional, Tuple, Set

from models.enums import (
    # Resources
    WOOD, BRICK, SHEEP, WHEAT, ORE, RESOURCES,
    # Development cards
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    # Building types and costs
    SETTLEMENT, CITY, ROAD,
    ROAD_COST, SETTLEMENT_COST, CITY_COST, DEV_CARD_COST,
    # Game constants
    HAND_LIMIT, MIN_LARGEST_ARMY, MIN_LONGEST_ROAD,
    # Actions
    ActionPrompt,
    # Players
    PLAYER_0, PLAYER_1,
    # Board
    HEX_TYPE_DESERT
)
from state import GameState, PlayerState
from colonist_map import (
    HEX_TO_CORNERS, get_corner_hexes, PORT_CORNERS,
    PORT_TYPE_3_1, PORT_TYPE_WOOD, PORT_TYPE_BRICK,
    PORT_TYPE_SHEEP, PORT_TYPE_WHEAT, PORT_TYPE_ORE
)


# ===== Resource Management =====

def give_resources(state: GameState, player_id: int, resources: List[int]):
    """Give resources to a player from the bank."""
    player = state.players[player_id]
    for i in range(5):
        amount = resources[i]
        if amount > 0:
            # Check bank has enough
            if state.resource_bank[i] < amount:
                amount = state.resource_bank[i]  # Give what's available
            
            player.resources[i] += amount
            state.resource_bank[i] -= amount


def take_resources(state: GameState, player_id: int, resources: List[int]):
    """Take resources from a player to the bank."""
    player = state.players[player_id]
    for i in range(5):
        amount = resources[i]
        if amount > 0:
            # Ensure player has enough
            if player.resources[i] < amount:
                raise ValueError(f"Player doesn't have enough {RESOURCES[i]}")
            
            player.resources[i] -= amount
            state.resource_bank[i] += amount


def transfer_resources(state: GameState, from_player: int, to_player: int, resources: List[int]):
    """Transfer resources directly between players (for robber stealing)."""
    from_state = state.players[from_player]
    to_state = state.players[to_player]
    
    for i in range(5):
        amount = resources[i]
        if amount > 0:
            if from_state.resources[i] < amount:
                raise ValueError(f"Player doesn't have enough {RESOURCES[i]}")
            
            from_state.resources[i] -= amount
            to_state.resources[i] += amount


def steal_random_resource(state: GameState, thief: int, victim: int) -> Optional[int]:
    """
    Steal a random resource from victim to thief.
    
    Returns:
        The resource type stolen, or None if victim has no resources
    """
    victim_state = state.players[victim]
    
    # Build list of available resources
    available = []
    for i in range(5):
        available.extend([i] * victim_state.resources[i])
    
    if not available:
        return None
    
    # Pick random resource
    stolen_type = random.choice(available)
    
    # Transfer it
    transfer_resources(state, victim, thief, [
        1 if i == stolen_type else 0 for i in range(5)
    ])
    
    return stolen_type


# ===== Building Functions =====

def place_initial_settlement(state: GameState, player_id: int, corner_id: int):
    """Place a settlement during setup phase."""
    # Place on board
    state.board.place_initial_settlement(player_id, corner_id)
    
    # Update player's pieces
    player = state.players[player_id]
    player.settlements_left -= 1
    player.public_vps += 1
    
    # Track setup progress
    state.initial_settlements_placed += 1
    
    # Second settlement gives resources
    settlements_for_player = len(state.board.get_player_buildings(player_id)[SETTLEMENT])
    if settlements_for_player == 2:
        # Collect resources from adjacent hexes
        resources_to_give = [0, 0, 0, 0, 0]
        
        for hex_id in get_corner_hexes(corner_id):
            if state.hex_types[hex_id] != HEX_TYPE_DESERT:
                resource_type = state.hex_types[hex_id] - 1  # Convert to 0-4 index
                resources_to_give[resource_type] += 1
        
        give_resources(state, player_id, resources_to_give)


def place_initial_road(state: GameState, player_id: int, edge_id: int):
    """Place a road during setup phase."""
    # Place on board
    state.board.place_initial_road(player_id, edge_id)
    
    # Update player's pieces
    player = state.players[player_id]
    player.roads_left -= 1


def build_settlement(state: GameState, player_id: int, corner_id: int):
    """Build a settlement during normal play."""
    player = state.players[player_id]
    
    # Check resources
    if not state.can_afford(player_id, SETTLEMENT_COST):
        raise ValueError("Cannot afford settlement")
    
    # Check pieces
    if player.settlements_left <= 0:
        raise ValueError("No settlements left")
    
    # Build it
    state.board.build_settlement(player_id, corner_id)
    
    # Pay cost
    take_resources(state, player_id, SETTLEMENT_COST)
    
    # Update player
    player.settlements_left -= 1
    player.public_vps += 1


def build_city(state: GameState, player_id: int, corner_id: int):
    """Upgrade a settlement to a city."""
    player = state.players[player_id]
    
    # Check resources
    if not state.can_afford(player_id, CITY_COST):
        raise ValueError("Cannot afford city")
    
    # Check pieces
    if player.cities_left <= 0:
        raise ValueError("No cities left")
    
    # Build it
    state.board.build_city(player_id, corner_id)
    
    # Pay cost
    take_resources(state, player_id, CITY_COST)
    
    # Update player
    player.cities_left -= 1
    player.settlements_left += 1  # Get settlement back
    player.public_vps += 1  # City worth 2, settlement was 1


def build_road(state: GameState, player_id: int, edge_id: int):
    """Build a road."""
    player = state.players[player_id]
    
    # Check resources (unless free road from Road Building)
    road_building_active = (state.current_prompt == ActionPrompt.PLAY_TURN and 
                           hasattr(state, '_free_roads') and state._free_roads > 0)
    
    if not road_building_active and not state.can_afford(player_id, ROAD_COST):
        raise ValueError("Cannot afford road")
    
    # Check pieces
    if player.roads_left <= 0:
        raise ValueError("No roads left")
    
    # Build it
    state.board.build_road(player_id, edge_id)
    
    # Pay cost
    if not road_building_active:
        take_resources(state, player_id, ROAD_COST)
    else:
        state._free_roads -= 1
    
    # Update player
    player.roads_left -= 1
    
    # Check longest road
    update_longest_road(state)


# ===== Development Cards =====

def buy_development_card(state: GameState, player_id: int) -> int:
    """
    Buy a development card.
    
    Returns:
        The card type bought
    """
    player = state.players[player_id]
    
    # Check resources
    if not state.can_afford(player_id, DEV_CARD_COST):
        raise ValueError("Cannot afford development card")
    
    # Check deck
    if not state.dev_card_deck:
        raise ValueError("No development cards left")
    
    # Pay cost
    take_resources(state, player_id, DEV_CARD_COST)
    
    # Draw card
    card_type = state.dev_card_deck.pop()
    
    # Add to player's hand (bought this turn)
    player.dev_cards_bought_this_turn[card_type] += 1
    
    # Victory points are immediately counted (but hidden)
    if card_type == VICTORY_POINT:
        player.hidden_vps += 1
    
    return card_type


def play_knight(state: GameState, player_id: int):
    """Play a knight card."""
    player = state.players[player_id]
    
    # Check card availability
    if player.dev_cards[KNIGHT] <= 0:
        raise ValueError("No knight cards to play")
    
    # Check already played this turn
    if player.has_played_dev_card:
        raise ValueError("Already played a development card this turn")
    
    # Play the card
    player.dev_cards[KNIGHT] -= 1
    player.knights_played += 1
    player.has_played_dev_card = True
    
    # Update largest army
    update_largest_army(state)
    
    # Robber will be moved as a separate action
    state.current_prompt = ActionPrompt.MOVE_ROBBER
    state.is_moving_robber = True


def play_year_of_plenty(state: GameState, player_id: int, resource1: int, resource2: int):
    """Play Year of Plenty card to gain 2 resources."""
    player = state.players[player_id]
    
    # Check card availability
    if player.dev_cards[YEAR_OF_PLENTY] <= 0:
        raise ValueError("No Year of Plenty cards to play")
    
    # Check already played this turn
    if player.has_played_dev_card:
        raise ValueError("Already played a development card this turn")
    
    # Build resource array
    resources_to_take = [0, 0, 0, 0, 0]
    resources_to_take[resource1] += 1
    resources_to_take[resource2] += 1
    
    # Check bank has resources
    if not state.bank_has_resources(resources_to_take):
        raise ValueError("Bank doesn't have those resources")
    
    # Play the card
    player.dev_cards[YEAR_OF_PLENTY] -= 1
    player.has_played_dev_card = True
    
    # Give resources
    give_resources(state, player_id, resources_to_take)


def play_monopoly(state: GameState, player_id: int, resource_type: int):
    """Play Monopoly card to take all of one resource from opponents."""
    player = state.players[player_id]
    
    # Check card availability
    if player.dev_cards[MONOPOLY] <= 0:
        raise ValueError("No Monopoly cards to play")
    
    # Check already played this turn
    if player.has_played_dev_card:
        raise ValueError("Already played a development card this turn")
    
    # Play the card
    player.dev_cards[MONOPOLY] -= 1
    player.has_played_dev_card = True
    
    # Take resources from opponent
    opponent_id = 1 - player_id
    opponent = state.players[opponent_id]
    amount = opponent.resources[resource_type]
    
    if amount > 0:
        transfer_resources(state, opponent_id, player_id, [
            amount if i == resource_type else 0 for i in range(5)
        ])


def play_road_building(state: GameState, player_id: int):
    """Play Road Building card to build 2 free roads."""
    player = state.players[player_id]
    
    # Check card availability
    if player.dev_cards[ROAD_BUILDING] <= 0:
        raise ValueError("No Road Building cards to play")
    
    # Check already played this turn
    if player.has_played_dev_card:
        raise ValueError("Already played a development card this turn")
    
    # Play the card
    player.dev_cards[ROAD_BUILDING] -= 1
    player.has_played_dev_card = True
    
    # Set up free roads (actual building happens through normal build_road)
    state._free_roads = min(2, player.roads_left)


# ===== Dice and Robber =====

def roll_dice(state: GameState) -> Tuple[int, int]:
    """
    Roll dice and distribute resources.
    
    Returns:
        The two dice values
    """
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2
    
    state.dice_rolled = True
    
    if total == 7:
        # Save whose turn it is
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
        else:
            # No one needs to discard, move to robber
            state.is_moving_robber = True
            check_friendly_robber(state)
    else:
        # Distribute resources
        distribute_resources(state, total)
    
    return die1, die2


def distribute_resources(state: GameState, dice_total: int):
    """Distribute resources for a dice roll."""
    # Find all hexes with this number
    for hex_id in range(19):
        if state.hex_numbers[hex_id] == dice_total and state.board.robber_hex != hex_id:
            resource_type = state.hex_types[hex_id] - 1  # Convert to 0-4 index
            
            if resource_type >= 0:  # Not desert
                # Count buildings on this hex
                for corner_id in HEX_TO_CORNERS[hex_id]:
                    if corner_id in state.board.buildings:
                        owner, building_type = state.board.buildings[corner_id]
                        amount = 1 if building_type == SETTLEMENT else 2
                        
                        # Give resources if bank has them
                        resources = [0, 0, 0, 0, 0]
                        resources[resource_type] = amount
                        
                        if state.bank_has_resources(resources):
                            give_resources(state, owner, resources)


def check_friendly_robber(state: GameState):
    """Check if friendly robber rule applies and set prompt."""
    # Friendly robber: Can't move robber if no one has 3+ points
    has_enough_points = any(p.public_vps >= 3 for p in state.players)
    
    if has_enough_points:
        state.current_prompt = ActionPrompt.MOVE_ROBBER
    else:
        # Robber doesn't activate, return to normal play
        state.current_prompt = ActionPrompt.PLAY_TURN
        state.is_moving_robber = False


def move_robber(state: GameState, hex_id: int, victim_id: Optional[int]) -> Optional[int]:
    """
    Move the robber and potentially steal a resource.
    
    Returns:
        The resource type stolen, or None
    """
    # Move robber
    state.board.move_robber(hex_id)
    
    # Steal if victim specified (current_turn_player is the thief)
    stolen = None
    if victim_id is not None:
        stolen = steal_random_resource(state, state.current_turn_player, victim_id)
    
    # Return to normal play
    state.current_prompt = ActionPrompt.PLAY_TURN
    state.is_moving_robber = False
    
    return stolen


def discard_resources(state: GameState, player_id: int, resources: List[int]):
    """Discard resources when over hand limit."""
    player = state.players[player_id]
    
    # Calculate how many to discard
    num_cards = player.total_resources()
    num_to_discard = num_cards // 2
    
    # Validate discard amount
    total_discard = sum(resources)
    if total_discard != num_to_discard:
        raise ValueError(f"Must discard exactly {num_to_discard} cards")
    
    # Validate player has resources
    for i in range(5):
        if resources[i] > player.resources[i]:
            raise ValueError(f"Don't have enough {RESOURCES[i]} to discard")
    
    # Discard
    take_resources(state, player_id, resources)
    
    # Check if other player needs to discard
    other_player = 1 - player_id
    if state.players[other_player].total_resources() > HAND_LIMIT:
        # Other player needs to discard
        state.current_player = other_player
        # Stay in DISCARD prompt
    else:
        # All discards done, move to robber
        state.current_player = state.current_turn_player  # Restore turn player
        state.is_discarding = False
        state.is_moving_robber = True
        check_friendly_robber(state)


# ===== Trading =====

def maritime_trade(state: GameState, player_id: int, give_resource: int, give_amount: int, get_resource: int):
    """Execute a maritime trade."""
    player = state.players[player_id]
    
    # Check player has resources
    if player.resources[give_resource] < give_amount:
        raise ValueError(f"Don't have {give_amount} {RESOURCES[give_resource]}")
    
    # Check bank has resource
    if state.resource_bank[get_resource] < 1:
        raise ValueError(f"Bank doesn't have {RESOURCES[get_resource]}")
    
    # Validate trade ratio
    valid_ratio = False
    
    # Check 4:1 (always available)
    if give_amount == 4:
        valid_ratio = True
    
    # Check ports
    for building_corner in state.board.get_player_buildings(player_id)[SETTLEMENT] + \
                          state.board.get_player_buildings(player_id)[CITY]:
        if building_corner in PORT_CORNERS:
            port_type = PORT_CORNERS[building_corner]
            
            if port_type == PORT_TYPE_3_1 and give_amount == 3:
                valid_ratio = True
                break
            elif give_amount == 2:
                # Check 2:1 specific resource port
                resource_ports = {
                    PORT_TYPE_WOOD: WOOD,
                    PORT_TYPE_BRICK: BRICK,
                    PORT_TYPE_SHEEP: SHEEP,
                    PORT_TYPE_WHEAT: WHEAT,
                    PORT_TYPE_ORE: ORE
                }
                if port_type in resource_ports and resource_ports[port_type] == give_resource:
                    valid_ratio = True
                    break
    
    if not valid_ratio:
        raise ValueError(f"Invalid trade ratio {give_amount}:1")
    
    # Execute trade
    take_resources(state, player_id, [
        give_amount if i == give_resource else 0 for i in range(5)
    ])
    give_resources(state, player_id, [
        1 if i == get_resource else 0 for i in range(5)
    ])


# ===== Turn Management =====

def start_turn(state: GameState):
    """Start a new turn."""
    # Move bought dev cards to regular hand
    player = state.current_player_state()
    for i in range(5):
        player.dev_cards[i] += player.dev_cards_bought_this_turn[i]
        player.dev_cards_bought_this_turn[i] = 0
    
    # Reset turn state
    player.has_played_dev_card = False
    state.dice_rolled = False
    state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Clear special states
    state.is_discarding = False
    state.is_moving_robber = False
    
    # Clear any free roads
    if hasattr(state, '_free_roads'):
        delattr(state, '_free_roads')


def end_turn(state: GameState):
    """End the current turn."""
    # Switch players
    state.current_player = 1 - state.current_player
    state.current_turn_player = state.current_player
    state.turn_number += 1
    
    # Start new turn
    start_turn(state)


# ===== Special State Updates =====

def update_longest_road(state: GameState):
    """Update longest road ownership."""
    # Board already calculated road lengths
    longest_player = state.board.longest_road_player
    longest_length = state.board.longest_road_length
    
    # Update player states
    for player_id in range(2):
        old_has_road = state.players[player_id].has_longest_road
        new_has_road = (longest_player == player_id and longest_length >= MIN_LONGEST_ROAD)
        
        if old_has_road and not new_has_road:
            state.players[player_id].has_longest_road = False
            state.players[player_id].public_vps -= 2
        elif not old_has_road and new_has_road:
            state.players[player_id].has_longest_road = True
            state.players[player_id].public_vps += 2


def update_largest_army(state: GameState):
    """Update largest army ownership."""
    # Find who has most knights
    knights = [p.knights_played for p in state.players]
    max_knights = max(knights)
    
    if max_knights >= MIN_LARGEST_ARMY:
        # Find current holder
        current_holder = None
        for i in range(2):
            if state.players[i].has_largest_army:
                current_holder = i
                break
        
        # Determine new holder
        if knights[0] > knights[1]:
            new_holder = 0
        elif knights[1] > knights[0]:
            new_holder = 1
        else:
            new_holder = current_holder  # Tie goes to current holder
        
        # Update if changed
        if current_holder != new_holder:
            if current_holder is not None:
                state.players[current_holder].has_largest_army = False
                state.players[current_holder].public_vps -= 2
            
            if new_holder is not None:
                state.players[new_holder].has_largest_army = True
                state.players[new_holder].public_vps += 2


def complete_setup_phase(state: GameState):
    """Complete the initial setup phase."""
    state.initial_phase = False
    state.current_prompt = ActionPrompt.PLAY_TURN
    state.current_player = PLAYER_0  # First player starts
    state.current_turn_player = PLAYER_0
    start_turn(state)