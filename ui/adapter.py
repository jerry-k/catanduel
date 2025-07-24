"""
Adapter layer between CatanDuel engine and UI.

Handles translation between engine state/actions and UI format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import random

from engine.game import Game
from engine.state import GameState
from engine.models.player import Player, RandomPlayer, GreedyPlayer
from engine.models.minimax_player import MinimaxPlayer, SimpleMinimaxPlayer
from engine.models.mcts_player import MCTSPlayer, FastMCTSPlayer, StrongMCTSPlayer
from engine.models.enums import (
    Action, ActionType, ActionPrompt,
    PLAYER_0, PLAYER_1,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    SETTLEMENT, CITY, ROAD,
    HEX_TYPE_DESERT
)
from engine.colonist_map import PORT_EDGES

from ui.adapter_types import (
    UIGameState, UIBoard, UIPlayer, UIHex, UIBuilding, UIPort,
    UIResources, UIDevCards, UIAction, UIEvent,
    UIPhase, UIActionType,
    HEX_TYPE_TO_UI, UI_TO_HEX_TYPE,
    PORT_TYPE_TO_UI, UI_TO_PORT_TYPE,
    RESOURCE_NAMES
)


class CatanDuelAdapter:
    """Adapter between CatanDuel engine and UI."""
    
    def __init__(self):
        self.game: Optional[Game] = None
        self.player_names = ["Player 1", "Player 2"]
        self.player_types = ["human", "human"]
        self.last_dice_roll: Optional[Tuple[int, int]] = None
        self._events: List[UIEvent] = []
    
    def new_game(self, player1_config: Dict, player2_config: Dict, seed: Optional[int] = None) -> UIGameState:
        """
        Initialize a new game with specified players.
        
        Args:
            player1_config: {'type': 'human'|'random'|'greedy'|'minimax'|'mcts', 'name': str, ...}
            player2_config: Same format as player1_config
            seed: Random seed for reproducibility
        
        Returns:
            Initial game state in UI format
        """
        # Create players based on config
        players = []
        configs = [player1_config, player2_config]
        
        for i, config in enumerate(configs):
            player_type = config.get('type', 'human')
            name = config.get('name', f'Player {i+1}')
            
            if player_type == 'human':
                # Human players will have actions chosen by UI
                player = RandomPlayer(i, name)  # Placeholder, actions come from UI
            elif player_type == 'random':
                player = RandomPlayer(i, name)
            elif player_type == 'greedy':
                player = GreedyPlayer(i, name)
            elif player_type == 'minimax':
                depth = config.get('depth', 3)
                player = MinimaxPlayer(i, name, max_depth=depth)
            elif player_type == 'mcts':
                time_limit = config.get('time_limit', 2.0)
                player = MCTSPlayer(i, name, time_limit=time_limit)
            else:
                player = RandomPlayer(i, name)  # Default
            
            players.append(player)
            self.player_names[i] = name
            self.player_types[i] = player_type
        
        # Create new game
        self.game = Game(players, seed=seed)
        self.last_dice_roll = None
        self._events = []
        
        # Return initial state
        return self.translate_state()
    
    def translate_state(self) -> UIGameState:
        """Convert CatanDuel GameState to UI format."""
        if not self.game:
            raise ValueError("No game initialized")
        
        state = self.game.state
        
        # Determine UI phase
        phase = self._get_ui_phase(state)
        
        # Translate board
        board = self._translate_board(state)
        
        # Translate players
        players = self._translate_players(state)
        
        # Get valid actions
        valid_actions = self._translate_valid_actions(state)
        
        # Create message
        message = self._generate_message(state, phase)
        
        # Check if can end turn
        can_end_turn = (
            phase == UIPhase.MAIN and 
            state.dice_rolled and 
            any(a.type == UIActionType.END_TURN for a in valid_actions)
        )
        
        # Handle special states
        discard_required = None
        if state.is_discarding:
            discard_required = {}
            for i in range(2):
                if state.players[i].total_resources() > 7:
                    discard_required[i] = state.players[i].total_resources() // 2
        
        robber_steal_options = None
        if state.is_moving_robber:
            # This will be set when robber is placed on a hex
            robber_steal_options = []
        
        road_building_remaining = getattr(state, '_free_roads', 0)
        
        return UIGameState(
            phase=phase,
            current_player=state.current_player,
            turn_number=state.turn_number,
            board=board,
            players=players,
            dice_rolled=state.dice_rolled,
            last_roll=self.last_dice_roll,
            valid_actions=valid_actions,
            message=message,
            can_end_turn=can_end_turn,
            discard_required=discard_required,
            robber_steal_options=robber_steal_options,
            road_building_remaining=road_building_remaining
        )
    
    def _get_ui_phase(self, state: GameState) -> UIPhase:
        """Determine current UI phase from game state."""
        if state.is_setup_phase():
            return UIPhase.SETUP
        elif state.is_discarding:
            return UIPhase.DISCARD
        elif state.is_moving_robber:
            return UIPhase.ROBBER
        elif getattr(state, '_free_roads', 0) > 0:
            return UIPhase.ROAD_BUILDING
        # TODO: Add year of plenty and monopoly phases when needed
        else:
            return UIPhase.MAIN
    
    def _translate_board(self, state: GameState) -> UIBoard:
        """Translate board state to UI format."""
        # Translate hexes
        hexes = []
        for hex_id in range(19):
            hex_type = HEX_TYPE_TO_UI.get(state.hex_types[hex_id], "desert")
            number = state.hex_numbers[hex_id] if state.hex_types[hex_id] != HEX_TYPE_DESERT else None
            has_robber = (state.board.robber_hex == hex_id)
            
            hexes.append(UIHex(
                id=hex_id,
                type=hex_type,
                number=number,
                has_robber=has_robber
            ))
        
        # Translate buildings
        buildings = []
        
        # Settlements and cities
        for corner_id, (player_id, building_type) in state.board.buildings.items():
            ui_type = "settlement" if building_type == SETTLEMENT else "city"
            buildings.append(UIBuilding(
                type=ui_type,
                player=player_id,
                location=corner_id
            ))
        
        # Roads
        for edge_id, player_id in state.board.roads.items():
            buildings.append(UIBuilding(
                type="road",
                player=player_id,
                location=edge_id
            ))
        
        # Translate ports
        ports = []
        for edge_id, port_type in state.port_edges.items():
            ports.append(UIPort(
                edge_id=edge_id,
                type=PORT_TYPE_TO_UI.get(port_type, "3:1")
            ))
        
        return UIBoard(
            hexes=hexes,
            buildings=buildings,
            ports=ports,
            robber_hex=state.board.robber_hex
        )
    
    def _translate_players(self, state: GameState) -> List[UIPlayer]:
        """Translate player states to UI format."""
        players = []
        
        for i in range(2):
            player_state = state.players[i]
            
            # Convert resources
            resources = UIResources.from_array(player_state.resources)
            
            # Convert dev cards (excluding cards bought this turn from UI view)
            dev_cards = UIDevCards.from_array(player_state.dev_cards)
            
            # Determine if active
            is_active = False
            if state.is_setup_phase():
                is_active = (state.setup_phase_player_order() == i)
            else:
                is_active = (state.current_player == i)
            
            # Calculate road length for this player
            road_length = state.board.get_player_road_length(i)
            
            players.append(UIPlayer(
                id=i,
                name=self.player_names[i],
                color="red" if i == 0 else "blue",
                resources=resources,
                dev_cards=dev_cards,
                settlements_left=player_state.settlements_left,
                cities_left=player_state.cities_left,
                roads_left=player_state.roads_left,
                public_vps=player_state.public_vps,
                has_longest_road=player_state.has_longest_road,
                has_largest_army=player_state.has_largest_army,
                knights_played=player_state.knights_played,
                longest_road_length=road_length,
                is_active=is_active,
                is_human=(self.player_types[i] == 'human')
            ))
        
        return players
    
    def _translate_valid_actions(self, state: GameState) -> List[UIAction]:
        """Translate engine actions to UI format."""
        if not self.game:
            return []
        
        engine_actions = self.game.get_valid_actions()
        ui_actions = []
        
        for action in engine_actions:
            ui_action = self._translate_single_action(action)
            if ui_action:
                ui_actions.append(ui_action)
        
        return ui_actions
    
    def _translate_single_action(self, action: Action) -> Optional[UIAction]:
        """Translate a single engine action to UI format."""
        # Map engine action types to UI action types
        action_map = {
            ActionType.BUILD_INITIAL_SETTLEMENT: UIActionType.BUILD_INITIAL_SETTLEMENT,
            ActionType.BUILD_INITIAL_ROAD: UIActionType.BUILD_INITIAL_ROAD,
            ActionType.ROLL: UIActionType.ROLL,
            ActionType.END_TURN: UIActionType.END_TURN,
            ActionType.BUILD_ROAD: UIActionType.BUILD_ROAD,
            ActionType.BUILD_SETTLEMENT: UIActionType.BUILD_SETTLEMENT,
            ActionType.BUILD_CITY: UIActionType.BUILD_CITY,
            ActionType.BUY_DEVELOPMENT_CARD: UIActionType.BUY_DEVELOPMENT_CARD,
            ActionType.MOVE_ROBBER: UIActionType.MOVE_ROBBER,
            ActionType.DISCARD: UIActionType.DISCARD,
            ActionType.PLAY_KNIGHT_CARD: UIActionType.PLAY_KNIGHT,
            ActionType.PLAY_ROAD_BUILDING: UIActionType.PLAY_ROAD_BUILDING,
            ActionType.PLAY_YEAR_OF_PLENTY: UIActionType.PLAY_YEAR_OF_PLENTY,
            ActionType.PLAY_MONOPOLY: UIActionType.PLAY_MONOPOLY,
            ActionType.MARITIME_TRADE: UIActionType.MARITIME_TRADE,
        }
        
        ui_type = action_map.get(action.action_type)
        if not ui_type:
            return None
        
        # Translate action data
        data = {}
        
        if action.action_type in [ActionType.BUILD_INITIAL_SETTLEMENT, 
                                  ActionType.BUILD_SETTLEMENT,
                                  ActionType.BUILD_CITY]:
            data['corner'] = action.value
            
        elif action.action_type in [ActionType.BUILD_INITIAL_ROAD,
                                    ActionType.BUILD_ROAD]:
            data['edge'] = action.value
            
        elif action.action_type == ActionType.MOVE_ROBBER:
            hex_id, victim = action.value
            data['hex'] = hex_id
            if victim is not None:
                data['victim'] = victim
                
        elif action.action_type == ActionType.DISCARD:
            # Convert array to resource object
            resources = action.value
            data['resources'] = {
                'wood': resources[0],
                'brick': resources[1],
                'sheep': resources[2],
                'wheat': resources[3],
                'ore': resources[4]
            }
            
        elif action.action_type == ActionType.PLAY_YEAR_OF_PLENTY:
            res1, res2 = action.value
            data['resource1'] = RESOURCE_NAMES[res1]
            data['resource2'] = RESOURCE_NAMES[res2]
            
        elif action.action_type == ActionType.PLAY_MONOPOLY:
            data['resource'] = RESOURCE_NAMES[action.value]
            
        elif action.action_type == ActionType.MARITIME_TRADE:
            give_res, give_amount, get_res = action.value
            data['give_resource'] = RESOURCE_NAMES[give_res]
            data['give_amount'] = give_amount
            data['get_resource'] = RESOURCE_NAMES[get_res]
        
        return UIAction(type=ui_type, data=data)
    
    def _generate_message(self, state: GameState, phase: UIPhase) -> str:
        """Generate helpful message for current state."""
        if phase == UIPhase.SETUP:
            if state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
                return "Place your settlement"
            else:
                return "Place your road"
        elif phase == UIPhase.DISCARD:
            return "Select cards to discard"
        elif phase == UIPhase.ROBBER:
            return "Move the robber and steal"
        elif phase == UIPhase.ROAD_BUILDING:
            roads_left = getattr(state, '_free_roads', 0)
            return f"Place {roads_left} free road(s)"
        elif not state.dice_rolled:
            return "Roll the dice or play a development card"
        else:
            return "Take your actions"
    
    def translate_action(self, ui_action: UIAction) -> Action:
        """Convert UI action to CatanDuel engine format."""
        # Map UI action types to engine action types
        action_map = {
            UIActionType.BUILD_INITIAL_SETTLEMENT: ActionType.BUILD_INITIAL_SETTLEMENT,
            UIActionType.BUILD_INITIAL_ROAD: ActionType.BUILD_INITIAL_ROAD,
            UIActionType.ROLL: ActionType.ROLL,
            UIActionType.END_TURN: ActionType.END_TURN,
            UIActionType.BUILD_ROAD: ActionType.BUILD_ROAD,
            UIActionType.BUILD_SETTLEMENT: ActionType.BUILD_SETTLEMENT,
            UIActionType.BUILD_CITY: ActionType.BUILD_CITY,
            UIActionType.BUY_DEVELOPMENT_CARD: ActionType.BUY_DEVELOPMENT_CARD,
            UIActionType.MOVE_ROBBER: ActionType.MOVE_ROBBER,
            UIActionType.DISCARD: ActionType.DISCARD,
            UIActionType.PLAY_KNIGHT: ActionType.PLAY_KNIGHT_CARD,
            UIActionType.PLAY_ROAD_BUILDING: ActionType.PLAY_ROAD_BUILDING,
            UIActionType.PLAY_YEAR_OF_PLENTY: ActionType.PLAY_YEAR_OF_PLENTY,
            UIActionType.PLAY_MONOPOLY: ActionType.PLAY_MONOPOLY,
            UIActionType.MARITIME_TRADE: ActionType.MARITIME_TRADE,
        }
        
        engine_type = action_map.get(ui_action.type)
        if not engine_type:
            raise ValueError(f"Unknown UI action type: {ui_action.type}")
        
        # Translate action value
        value = None
        
        if engine_type in [ActionType.BUILD_INITIAL_SETTLEMENT,
                          ActionType.BUILD_SETTLEMENT,
                          ActionType.BUILD_CITY]:
            value = ui_action.data.get('corner')
            
        elif engine_type in [ActionType.BUILD_INITIAL_ROAD,
                            ActionType.BUILD_ROAD]:
            value = ui_action.data.get('edge')
            
        elif engine_type == ActionType.MOVE_ROBBER:
            hex_id = ui_action.data.get('hex')
            victim = ui_action.data.get('victim')
            value = (hex_id, victim)
            
        elif engine_type == ActionType.DISCARD:
            # Convert resource object to array
            res_obj = ui_action.data.get('resources', {})
            value = [
                res_obj.get('wood', 0),
                res_obj.get('brick', 0),
                res_obj.get('sheep', 0),
                res_obj.get('wheat', 0),
                res_obj.get('ore', 0)
            ]
            
        elif engine_type == ActionType.PLAY_YEAR_OF_PLENTY:
            res1_name = ui_action.data.get('resource1')
            res2_name = ui_action.data.get('resource2')
            res1 = RESOURCE_NAMES.index(res1_name)
            res2 = RESOURCE_NAMES.index(res2_name)
            value = (res1, res2)
            
        elif engine_type == ActionType.PLAY_MONOPOLY:
            res_name = ui_action.data.get('resource')
            value = RESOURCE_NAMES.index(res_name)
            
        elif engine_type == ActionType.MARITIME_TRADE:
            give_name = ui_action.data.get('give_resource')
            give_res = RESOURCE_NAMES.index(give_name)
            give_amount = ui_action.data.get('give_amount')
            get_name = ui_action.data.get('get_resource')
            get_res = RESOURCE_NAMES.index(get_name)
            value = (give_res, give_amount, get_res)
        
        return Action(action_type=engine_type, value=value)
    
    def execute_action(self, ui_action: UIAction) -> Tuple[UIGameState, List[UIEvent]]:
        """
        Execute an action and return new state plus events.
        
        Args:
            ui_action: Action from UI
            
        Returns:
            (new_state, events) tuple
        """
        if not self.game:
            raise ValueError("No game initialized")
        
        # Clear events
        self._events = []
        
        # Get old state for comparison
        old_state = self.game.state.copy()
        
        # Special handling for dice rolls
        if ui_action.type == UIActionType.ROLL:
            # We'll capture the dice roll when it happens
            self.last_dice_roll = None
        
        # Translate and execute action
        engine_action = self.translate_action(ui_action)
        
        # For dice rolls, we need to intercept the result
        if engine_action.action_type == ActionType.ROLL:
            # Import here to avoid circular dependency
            from engine.state_functions import roll_dice
            # Get dice result by simulating the roll
            import random
            die1 = random.randint(1, 6)
            die2 = random.randint(1, 6)
            self.last_dice_roll = (die1, die2)
        
        success = self.game.execute(engine_action, validate=True)
        
        if not success:
            raise ValueError("Invalid action")
        
        # Generate events based on what changed
        self._generate_events(old_state, self.game.state, engine_action)
        
        # Get new UI state
        new_state = self.translate_state()
        
        return new_state, self._events
    
    def _generate_events(self, old_state: GameState, new_state: GameState, action: Action):
        """Generate UI events based on state changes."""
        # Dice rolled
        if action.action_type == ActionType.ROLL and self.last_dice_roll:
            die1, die2 = self.last_dice_roll
            
            self._events.append(UIEvent(
                type="dice_rolled",
                data={"die1": die1, "die2": die2, "total": die1 + die2}
            ))
            
            # Check for resource distribution
            total = die1 + die2
            if total != 7:
                for i in range(2):
                    old_res = old_state.players[i].resources
                    new_res = new_state.players[i].resources
                    gained = [new_res[j] - old_res[j] for j in range(5)]
                    
                    for res_type, amount in enumerate(gained):
                        if amount > 0:
                            self._events.append(UIEvent(
                                type="resource_gained",
                                player=i,
                                data={
                                    "resource": RESOURCE_NAMES[res_type],
                                    "amount": amount
                                }
                            ))
        
        # Building placed
        elif action.action_type in [ActionType.BUILD_SETTLEMENT,
                                   ActionType.BUILD_INITIAL_SETTLEMENT]:
            player = new_state.current_turn_player if hasattr(new_state, 'current_turn_player') else new_state.current_player
            self._events.append(UIEvent(
                type="building_placed",
                player=player,
                data={"type": "settlement", "location": action.value}
            ))
            
        elif action.action_type == ActionType.BUILD_CITY:
            player = new_state.current_turn_player if hasattr(new_state, 'current_turn_player') else new_state.current_player
            self._events.append(UIEvent(
                type="building_placed",
                player=player,
                data={"type": "city", "location": action.value}
            ))
            
        elif action.action_type in [ActionType.BUILD_ROAD,
                                   ActionType.BUILD_INITIAL_ROAD]:
            player = new_state.current_turn_player if hasattr(new_state, 'current_turn_player') else new_state.current_player
            self._events.append(UIEvent(
                type="building_placed",
                player=player,
                data={"type": "road", "location": action.value}
            ))
        
        # Robber moved
        elif action.action_type == ActionType.MOVE_ROBBER:
            hex_id, victim = action.value
            self._events.append(UIEvent(
                type="robber_moved",
                data={"hex": hex_id}
            ))
            
            if victim is not None:
                self._events.append(UIEvent(
                    type="resource_stolen",
                    player=new_state.current_player,
                    data={"victim": victim}
                ))
        
        # Development card bought
        elif action.action_type == ActionType.BUY_DEVELOPMENT_CARD:
            self._events.append(UIEvent(
                type="dev_card_bought",
                player=new_state.current_player
            ))
        
        # Development card played
        elif action.action_type == ActionType.PLAY_KNIGHT_CARD:
            self._events.append(UIEvent(
                type="dev_card_played",
                player=new_state.current_player,
                data={"card": "knight"}
            ))
        
        # Turn ended
        elif action.action_type == ActionType.END_TURN:
            self._events.append(UIEvent(
                type="turn_ended",
                player=old_state.current_player
            ))
    
    def get_ai_action(self) -> Optional[UIAction]:
        """
        Get AI action if it's an AI player's turn.
        
        Returns:
            UI action if AI should move, None if human turn
        """
        if not self.game:
            return None
        
        # Determine actual acting player
        if self.game.state.is_setup_phase():
            current = self.game.state.setup_phase_player_order()
        else:
            current = self.game.state.current_player
            
        if self.player_types[current] == 'human':
            return None
        
        # Get AI decision
        valid_actions = self.game.get_valid_actions()
        if not valid_actions:
            return None
        
        ai_player = self.game.players[current]
        engine_action = ai_player.decide(self.game, valid_actions)
        
        # Translate to UI action
        return self._translate_single_action(engine_action)