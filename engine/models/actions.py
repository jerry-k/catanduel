"""
Action generation and validation for CatanDuel.

This module contains all the functions that generate valid actions
based on the current game state. It's the core of the game's move
generation system.

Based on catanatron's actions.py but simplified for 2 players.
"""

from typing import List, Set, Optional
import random

from engine.models.enums import (
    # Actions
    Action, ActionType, ActionPrompt,
    # Resources
    WOOD, BRICK, SHEEP, WHEAT, ORE, RESOURCES,
    # Development cards
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    # Building costs
    ROAD_COST, SETTLEMENT_COST, CITY_COST, DEV_CARD_COST,
    # Building types
    SETTLEMENT, CITY, ROAD,
    # Game constants
    HAND_LIMIT, MIN_LARGEST_ARMY, MIN_LONGEST_ROAD,
    # Players
    PLAYER_0, PLAYER_1,
    # Board
    HEX_TYPE_DESERT,
    # Port types
    PORT_TYPE_3_1, PORT_TYPE_WOOD, PORT_TYPE_BRICK,
    PORT_TYPE_SHEEP, PORT_TYPE_WHEAT, PORT_TYPE_ORE
)
from engine.colonist_map import (
    HEX_TO_CORNERS, HEX_TO_EDGES, EDGE_TO_CORNERS,
    get_corner_hexes, get_connected_edges, get_adjacent_corners,
    PORT_CORNERS
)
from engine.state import GameState


def generate_actions(state: GameState) -> List[Action]:
    """
    Generate all valid actions for the current game state.
    
    This is the main entry point for action generation. It delegates
    to specific functions based on the current action prompt.
    """
    # Use cached actions if available
    if state._valid_actions_cache is not None:
        return state._valid_actions_cache
    
    # Generate based on current prompt
    prompt = state.current_prompt
    
    if prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
        actions = generate_initial_settlement_actions(state)
    elif prompt == ActionPrompt.BUILD_INITIAL_ROAD:
        actions = generate_initial_road_actions(state)
    elif prompt == ActionPrompt.PLAY_TURN:
        actions = generate_play_turn_actions(state)
    elif prompt == ActionPrompt.DISCARD:
        actions = generate_discard_actions(state)
    elif prompt == ActionPrompt.MOVE_ROBBER:
        actions = generate_move_robber_actions(state)
    else:
        actions = []
    
    # Cache and return
    state._valid_actions_cache = actions
    return actions


def generate_initial_settlement_actions(state: GameState) -> List[Action]:
    """Generate valid initial settlement placement actions."""
    # Determine which player is placing
    player_id = state.setup_phase_player_order()
    
    # Find all valid corners
    valid_corners = []
    occupied = set(state.board.buildings.keys())
    
    # For initial settlements, any unoccupied corner with distance rule is valid
    for corner_id in range(54):  # All corners
        # Check unoccupied
        if corner_id in occupied:
            continue
        
        # Check distance rule
        valid = True
        for adjacent in get_adjacent_corners(corner_id):
            if adjacent in occupied:
                valid = False
                break
        
        if valid:
            valid_corners.append(corner_id)
    
    # Create actions
    return [
        Action(
            action_type=ActionType.BUILD_INITIAL_SETTLEMENT,
            value=corner_id
        )
        for corner_id in valid_corners
    ]


def generate_initial_road_actions(state: GameState) -> List[Action]:
    """Generate valid initial road placement actions."""
    # Determine which player is placing
    player_id = state.setup_phase_player_order()
    
    # Find the player's most recent settlement
    # Initial roads must connect to the settlement just placed
    player_buildings = state.board.get_player_buildings(player_id)
    settlements = player_buildings[SETTLEMENT]
    
    if not settlements:
        return []  # No settlement to connect to
    
    # Get the most recent settlement (last in list)
    settlement_corner = settlements[-1]
    
    # Find all edges connected to this corner
    valid_edges = []
    for edge_id in get_connected_edges(settlement_corner):
        if edge_id not in state.board.roads:
            valid_edges.append(edge_id)
    
    # Create actions
    return [
        Action(
            action_type=ActionType.BUILD_INITIAL_ROAD,
            value=edge_id
        )
        for edge_id in valid_edges
    ]


def generate_play_turn_actions(state: GameState) -> List[Action]:
    """Generate valid actions during normal play turn."""
    actions = []
    player_id = state.current_player
    player = state.current_player_state()
    
    # Check if dice have been rolled
    if not state.dice_rolled:
        # Can play development cards before rolling
        actions.extend(generate_dev_card_actions(state))
        
        # Always allow rolling at start of turn
        actions.append(Action(action_type=ActionType.ROLL, value=None))
    else:
        # After rolling, can build, trade, play cards, or end turn
        actions.extend(generate_build_actions(state))
        actions.extend(generate_trade_actions(state))
        actions.extend(generate_dev_card_actions(state))
        
        # Can always end turn after rolling
        actions.append(Action(action_type=ActionType.END_TURN, value=None))
    
    return actions


def generate_build_actions(state: GameState) -> List[Action]:
    """Generate all valid build actions."""
    actions = []
    player_id = state.current_player
    player = state.current_player_state()
    
    # Check for free roads from Road Building
    free_roads = getattr(state, '_free_roads', 0)
    
    # Build settlement
    if player.settlements_left > 0 and (free_roads == 0):
        if state.can_afford(player_id, SETTLEMENT_COST):
            for corner_id in range(54):
                if state.board.can_build_settlement(player_id, corner_id):
                    actions.append(Action(
                        action_type=ActionType.BUILD_SETTLEMENT,
                        value=corner_id
                    ))
    
    # Build city
    if player.cities_left > 0 and (free_roads == 0):
        if state.can_afford(player_id, CITY_COST):
            player_buildings = state.board.get_player_buildings(player_id)
            for corner_id in player_buildings[SETTLEMENT]:
                actions.append(Action(
                    action_type=ActionType.BUILD_CITY,
                    value=corner_id
                ))
    
    # Build road (or free road)
    if player.roads_left > 0:
        if free_roads > 0 or state.can_afford(player_id, ROAD_COST):
            for edge_id in range(72):
                if state.board.can_build_road(player_id, edge_id):
                    actions.append(Action(
                        action_type=ActionType.BUILD_ROAD,
                        value=edge_id
                    ))
    
    # Buy development card
    if state.dev_card_deck and (free_roads == 0):
        if state.can_afford(player_id, DEV_CARD_COST):
            actions.append(Action(action_type=ActionType.BUY_DEVELOPMENT_CARD, value=None))
    
    return actions


def generate_trade_actions(state: GameState) -> List[Action]:
    """Generate all valid maritime trade actions."""
    actions = []
    player_id = state.current_player
    player = state.current_player_state()
    
    # Get player's available trade ratios
    ratios = get_trade_ratios(state, player_id)
    
    # For each resource the player has
    for give_res in range(5):
        if player.resources[give_res] >= min(ratios[give_res]):
            # For each possible ratio
            for ratio in ratios[give_res]:
                if player.resources[give_res] >= ratio:
                    # For each resource they could get
                    for get_res in range(5):
                        if get_res != give_res and state.resource_bank[get_res] > 0:
                            actions.append(Action(
                                action_type=ActionType.MARITIME_TRADE,
                                value=(give_res, ratio, get_res)
                            ))
    
    return actions


def get_trade_ratios(state: GameState, player_id: int) -> List[List[int]]:
    """
    Get available trade ratios for each resource.
    
    Returns:
        List where index is resource type, value is list of valid ratios
    """
    # Start with 4:1 for all resources
    ratios = [[4] for _ in range(5)]
    
    # Check ports - build port corners from game state instead of using global
    from engine.colonist_map import EDGE_TO_CORNERS
    port_corners = {}
    for edge_id, port_type in state.port_edges.items():
        if edge_id in EDGE_TO_CORNERS:
            corner1, corner2 = EDGE_TO_CORNERS[edge_id]
            port_corners[corner1] = port_type
            port_corners[corner2] = port_type
    
    player_buildings = state.board.get_player_buildings(player_id)
    all_corners = player_buildings[SETTLEMENT] + player_buildings[CITY]
    
    for corner_id in all_corners:
        if corner_id in port_corners:
            port_type = port_corners[corner_id]
            
            if port_type == PORT_TYPE_3_1:
                # 3:1 port - all resources can use 3:1
                for i in range(5):
                    if 3 not in ratios[i]:
                        ratios[i].append(3)
            else:
                # 2:1 specific resource port
                resource_map = {
                    PORT_TYPE_WOOD: WOOD,
                    PORT_TYPE_BRICK: BRICK,
                    PORT_TYPE_SHEEP: SHEEP,
                    PORT_TYPE_WHEAT: WHEAT,
                    PORT_TYPE_ORE: ORE
                }
                if port_type in resource_map:
                    res_type = resource_map[port_type]
                    if 2 not in ratios[res_type]:
                        ratios[res_type].append(2)
    
    # Sort ratios (best first)
    for i in range(5):
        ratios[i].sort()
    
    return ratios


def generate_dev_card_actions(state: GameState) -> List[Action]:
    """Generate valid development card play actions."""
    actions = []
    player_id = state.current_player
    player = state.current_player_state()
    
    # Can't play if already played this turn
    if player.has_played_dev_card:
        return actions
    
    # Can't play cards bought this turn
    # (Victory points don't need to be played)
    
    # Knight
    # Note: dev_cards only contains playable cards (cards from previous turns)
    # Cards bought this turn are in dev_cards_bought_this_turn (separate array)
    if player.dev_cards[KNIGHT] > 0:
        actions.append(Action(action_type=ActionType.PLAY_KNIGHT_CARD, value=None))
    
    # Year of Plenty
    if player.dev_cards[YEAR_OF_PLENTY] > 0:
        # Generate all possible resource combinations
        for res1 in range(5):
            if state.resource_bank[res1] > 0:
                for res2 in range(5):
                    # Check if bank has enough (considering we might take 2 of same)
                    if res1 == res2:
                        if state.resource_bank[res1] >= 2:
                            actions.append(Action(
                                action_type=ActionType.PLAY_YEAR_OF_PLENTY,
                                value=(res1, res2)
                            ))
                    else:
                        if state.resource_bank[res2] > 0:
                            actions.append(Action(
                                action_type=ActionType.PLAY_YEAR_OF_PLENTY,
                                value=(res1, res2)
                            ))
    
    # Monopoly
    if player.dev_cards[MONOPOLY] > 0:
        # Can monopolize any resource type
        for res_type in range(5):
            actions.append(Action(
                action_type=ActionType.PLAY_MONOPOLY,
                value=res_type
            ))
    
    # Road Building
    if player.dev_cards[ROAD_BUILDING] > 0 and player.roads_left > 0:
        actions.append(Action(action_type=ActionType.PLAY_ROAD_BUILDING, value=None))
    
    return actions


def generate_discard_actions(state: GameState) -> List[Action]:
    """Generate valid discard actions."""
    # Current player is the one who needs to discard
    player_id = state.current_player
    player = state.players[player_id]
    
    # Calculate how many to discard
    num_cards = player.total_resources()
    num_to_discard = num_cards // 2
    
    if num_to_discard == 0:
        # Edge case - shouldn't happen
        return [Action(
            action_type=ActionType.DISCARD,
            value=[0, 0, 0, 0, 0]
        )]
    
    # Generate all combinations of resources that sum to num_to_discard
    combos = generate_resource_combinations(
        player.resources,
        num_to_discard
    )
    
    # Return actions
    return [
        Action(
            action_type=ActionType.DISCARD,
            value=combo
        )
        for combo in combos
    ]


def generate_resource_combinations(resources: List[int], target: int) -> List[List[int]]:
    """
    Generate all combinations of resources that sum to target.
    
    Args:
        resources: Available resources [wood, brick, sheep, wheat, ore]
        target: Number of resources to discard
        
    Returns:
        List of resource arrays that sum to target
    """
    combinations = []
    
    def backtrack(combo: List[int], remaining: int, start_idx: int):
        if remaining == 0:
            combinations.append(combo.copy())
            return
        
        for i in range(start_idx, 5):
            if combo[i] < resources[i] and remaining > 0:
                combo[i] += 1
                backtrack(combo, remaining - 1, i)
                combo[i] -= 1
    
    backtrack([0, 0, 0, 0, 0], target, 0)
    return combinations


def generate_move_robber_actions(state: GameState) -> List[Action]:
    """Generate valid robber movement actions."""
    player_id = state.current_player
    actions = []
    
    # Get all valid hexes (not current position)
    valid_hexes = state.board.get_valid_robber_hexes()
    
    # Apply friendly robber rule: can't place on hex adjacent to opponent with ≤2 VP
    has_low_vp_opponent = any(p.actual_vps() <= 2 for i, p in enumerate(state.players) if i != player_id)
    
    for hex_id in valid_hexes:
        # Get players on this hex
        players_on_hex = state.board.get_players_on_hex(hex_id)
        
        # Remove current player
        victims = [p for p in players_on_hex if p != player_id]
        
        # Check friendly robber restriction
        if has_low_vp_opponent:
            # Check if any low VP opponent has buildings on this hex
            blocked = False
            for victim_id in victims:
                if state.players[victim_id].actual_vps() <= 2:
                    blocked = True
                    break
            if blocked:
                continue  # Skip this hex
        
        if victims:
            # Can steal from any victim
            has_stealable_victim = False
            for victim_id in victims:
                # Check victim has resources
                if state.players[victim_id].total_resources() > 0:
                    actions.append(Action(
                        action_type=ActionType.MOVE_ROBBER,
                        value=(hex_id, victim_id)
                    ))
                    has_stealable_victim = True
            
            # If no victim has resources, still allow moving robber there
            if not has_stealable_victim:
                actions.append(Action(
                    action_type=ActionType.MOVE_ROBBER,
                    value=(hex_id, None)
                ))
        else:
            # No victims, just move robber
            actions.append(Action(
                action_type=ActionType.MOVE_ROBBER,
                value=(hex_id, None)
            ))
    
    return actions


def filter_actions_by_player(actions: List[Action], player_id: int) -> List[Action]:
    """
    Filter actions to only those available to a specific player.
    
    This is used in games where multiple players might need to act
    in the same phase (e.g., discarding).
    """
    # For now, all actions are for the current player
    # This might change if we add simultaneous discarding
    return actions


def is_action_valid(state: GameState, action: Action) -> bool:
    """
    Check if an action is valid in the current state.
    
    This is useful for validating human input or debugging.
    """
    valid_actions = generate_actions(state)
    return action in valid_actions