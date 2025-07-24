#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import uuid
import os
import logging
import sys

# Add parent directory to path to import engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.state import GameState, PlayerState
from engine.models.player import Player, RandomPlayer

app = Flask(__name__)
app.secret_key = 'catanduel-secret-key'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store game instances
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('static/assets', filename)

@app.route('/api/new_game', methods=['POST'])
def new_game():
    try:
        data = request.json or {}
        game_id = str(uuid.uuid4())
        seed = data.get('seed')
        
        # Create new game with two players
        # Using RandomPlayer for both for now - the UI will handle human moves
        player1 = RandomPlayer(0, "Human")
        player2 = RandomPlayer(1, "AI")
        game = Game([player1, player2], seed=seed)
        
        games[game_id] = game
        
        # Get initial legal actions
        legal_actions = []
        # Determine the actual acting player
        acting_player = game.state.setup_phase_player_order() if game.state.is_setup_phase() else game.state.current_player
        
        for action in game.get_valid_actions():
            action_data = {
                'type': action.action_type.name,
                'player': acting_player
            }
            if action.value is not None:
                if action.action_type.name in ['BUILD_SETTLEMENT', 'BUILD_INITIAL_SETTLEMENT', 'BUILD_CITY']:
                    action_data['corner'] = action.value
                elif action.action_type.name in ['BUILD_ROAD', 'BUILD_INITIAL_ROAD']:
                    action_data['edge'] = action.value
                else:
                    action_data['value'] = action.value
            legal_actions.append(action_data)
        
        return jsonify({
            'game_id': game_id,
            'state': serialize_state(game),
            'legal_actions': legal_actions
        })
    except Exception as e:
        logger.error(f"Error creating new game: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/game_state/<game_id>')
def get_game_state(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    # Handle AI turns
    events = []
    # Get the actual acting player
    acting_player = game.state.setup_phase_player_order() if game.state.is_setup_phase() else game.state.current_player
    
    # Limit iterations to prevent infinite loops
    max_ai_actions = 50
    ai_action_count = 0
    
    # Log initial state
    logger.info(f"Initial state: acting_player={acting_player}, prompt={game.state.current_prompt}, is_moving_robber={game.state.is_moving_robber}")
    
    while acting_player == 1 and not game.is_over() and ai_action_count < max_ai_actions:
        # AI's turn
        ai_actions = game.get_valid_actions()
        if not ai_actions:
            logger.warning(f"AI has no valid actions. Current prompt: {game.state.current_prompt}")
            break
            
        # Simple AI: pick first valid action
        ai_action = ai_actions[0]
        logger.info(f"AI executing: {ai_action.action_type.name}")
        success = game.execute(ai_action)
        
        if success:
            events.append({
                'type': 'AI_ACTION',
                'message': f'AI played {ai_action.action_type.name}'
            })
            # Always update acting player from game state
            acting_player = game.state.setup_phase_player_order() if game.state.is_setup_phase() else game.state.current_player
            
            # Log state after action
            logger.info(f"After {ai_action.action_type.name}: current_player={game.state.current_player}, prompt={game.state.current_prompt}")
        else:
            logger.error(f"AI action failed: {ai_action}")
            break
            
        ai_action_count += 1
    
    if ai_action_count >= max_ai_actions:
        logger.error("AI action limit reached - possible infinite loop")
    
    # Get legal actions in rlcatan format
    legal_actions = []
    # Determine the actual acting player
    acting_player = game.state.setup_phase_player_order() if game.state.is_setup_phase() else game.state.current_player
    
    for action in game.get_valid_actions():
        action_data = {
            'type': action.action_type.name,
            'player': acting_player
        }
        if action.value is not None:
            if isinstance(action.value, tuple):
                # Handle tuple values
                if action.action_type.name == 'MOVE_ROBBER' and len(action.value) == 2:
                    action_data['hex'] = action.value[0]
                    action_data['victim'] = action.value[1]
                else:
                    # For other tuples (like MARITIME_TRADE), keep as value
                    action_data['value'] = action.value
            else:
                # Handle single values
                if action.action_type.name in ['BUILD_SETTLEMENT', 'BUILD_INITIAL_SETTLEMENT', 'BUILD_CITY']:
                    action_data['corner'] = action.value
                elif action.action_type.name in ['BUILD_ROAD', 'BUILD_INITIAL_ROAD']:
                    action_data['edge'] = action.value
                else:
                    action_data['value'] = action.value
        legal_actions.append(action_data)
    
    # Check game over
    game_over = game.is_over()
    winner = game.state.get_winner() if game_over else None
    
    return jsonify({
        'state': serialize_state(game),
        'legal_actions': legal_actions,
        'events': events,
        'game_over': game_over,
        'winner': winner,
        'ai_thinking': acting_player == 1  # AI is player 1
    })

@app.route('/api/execute_action/<game_id>', methods=['POST'])
def execute_action(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    action_data = request.json
    
    # Convert from rlcatan format to engine Action
    from engine.models.enums import Action, ActionType
    
    try:
        action_type = ActionType[action_data['type']]
        
        # Extract value based on action type
        value = None
        if 'corner' in action_data:
            value = action_data['corner']
        elif 'edge' in action_data:
            value = action_data['edge']
        elif 'hex' in action_data and 'victim' in action_data:
            value = (action_data['hex'], action_data['victim'])
        elif 'resource' in action_data:
            # Handle monopoly card - UI sends 'resource' instead of 'value'
            value = action_data['resource']
        elif 'resources' in action_data:
            # Handle year of plenty - UI sends 'resources' array instead of 'value'
            value = tuple(action_data['resources'])
        elif 'value' in action_data:
            value = action_data['value']
            # Convert list to tuple for MARITIME_TRADE
            if action_type == ActionType.MARITIME_TRADE and isinstance(value, list):
                value = tuple(value)
            
        action = Action(action_type, value)
        
        # Store state before monopoly action to calculate resources taken
        opponent_resources_before = None
        if action_type == ActionType.PLAY_MONOPOLY:
            acting_player = game.state.current_player
            opponent_id = 1 - acting_player
            opponent_resources_before = game.state.players[opponent_id].resources[value]
        
        # Execute the action
        success = game.execute(action)
        
        if not success:
            return jsonify({'error': 'Invalid action'}), 400
            
        # Generate events based on action type
        events = []
        player = action_data.get('player', 0)
        
        if action_type == ActionType.PLAY_YEAR_OF_PLENTY:
            # Count resources taken
            resources_taken = {}
            resource_names = ['lumber', 'brick', 'wool', 'grain', 'ore']
            for res_idx in value:
                res_name = resource_names[res_idx]
                resources_taken[res_name] = resources_taken.get(res_name, 0) + 1
            
            events.append({
                'type': 'YEAR_OF_PLENTY_PLAYED',
                'player': player,
                'resources': resources_taken
            })
        elif action_type == ActionType.PLAY_MONOPOLY:
            # Calculate total taken from other players
            resource_names = ['lumber', 'brick', 'wool', 'grain', 'ore']
            total_taken = opponent_resources_before if opponent_resources_before is not None else 0
            events.append({
                'type': 'MONOPOLY_PLAYED',
                'player': player,
                'resource': resource_names[value],
                'total_taken': total_taken
            })
        elif action_type == ActionType.PLAY_KNIGHT_CARD:
            events.append({
                'type': 'KNIGHT_PLAYED',
                'player': player
            })
        elif action_type == ActionType.PLAY_ROAD_BUILDING:
            events.append({
                'type': 'ROAD_BUILDING_PLAYED',
                'player': player
            })
            
        # Get updated state
        legal_actions = []
        # Determine the actual acting player
        acting_player = game.state.setup_phase_player_order() if game.state.is_setup_phase() else game.state.current_player
        
        for action in game.get_valid_actions():
            action_dict = {
                'type': action.action_type.name,
                'player': acting_player
            }
            if action.value is not None:
                if isinstance(action.value, tuple):
                    if action.action_type.name == 'MOVE_ROBBER' and len(action.value) == 2:
                        action_dict['hex'] = action.value[0]
                        action_dict['victim'] = action.value[1]
                    else:
                        # For other tuples (like MARITIME_TRADE), keep as value
                        action_dict['value'] = action.value
                else:
                    if action.action_type.name in ['BUILD_SETTLEMENT', 'BUILD_INITIAL_SETTLEMENT', 'BUILD_CITY']:
                        action_dict['corner'] = action.value
                    elif action.action_type.name in ['BUILD_ROAD', 'BUILD_INITIAL_ROAD']:
                        action_dict['edge'] = action.value
                    else:
                        action_dict['value'] = action.value
            legal_actions.append(action_dict)
        
        game_over = game.is_over()
        winner = game.state.get_winner() if game_over else None
        
        return jsonify({
            'success': True,
            'state': serialize_state(game),
            'legal_actions': legal_actions,
            'events': events,
            'game_over': game_over,
            'winner': winner,
            'ai_thinking': acting_player == 1
        })
        
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return jsonify({'error': str(e)}), 500

def serialize_state(game):
    """Convert game state to rlcatan format using real game data."""
    state = game.state
    
    # Map resource types to UI names
    resource_map = {
        0: 'desert',  # DESERT
        1: 'lumber',  # WOOD
        2: 'brick',   # BRICK
        3: 'wool',    # SHEEP
        4: 'grain',   # WHEAT
        5: 'ore'      # ORE
    }
    
    # Convert hexes from game state
    hexes = {}
    for i in range(19):
        hex_type = state.hex_types[i]
        hex_number = state.hex_numbers[i]
        
        hexes[str(i)] = {
            'resource': resource_map[hex_type],
            'number': hex_number if hex_type != 0 else None  # No number on desert (0 is desert)
        }
    
    # Convert ports from game state
    port_type_map = {
        1: '3:1',    # PORT_TYPE_3_1
        2: 'lumber', # PORT_TYPE_WOOD
        3: 'brick',  # PORT_TYPE_BRICK
        4: 'wool',   # PORT_TYPE_SHEEP
        5: 'grain',  # PORT_TYPE_WHEAT
        6: 'ore'     # PORT_TYPE_ORE
    }
    
    ports = {}
    for edge_id, port_type in state.port_edges.items():
        ports[str(edge_id)] = port_type_map.get(port_type, '3:1')
    
    # Convert resources - no mapping needed since UI now uses engine order
    resources = {}
    for player_id in range(2):
        player_res = state.players[player_id].resources
        resources[str(player_id)] = {
            '0': player_res[0],  # WOOD
            '1': player_res[1],  # BRICK
            '2': player_res[2],  # SHEEP
            '3': player_res[3],  # WHEAT
            '4': player_res[4]   # ORE
        }
    
    # Convert buildings to corners format
    corners = {str(i): None for i in range(54)}
    for corner_id, (player_id, building_type) in state.board.buildings.items():
        corners[str(corner_id)] = {
            'player': player_id,
            'type': 'SETTLEMENT' if building_type == 1 else 'CITY'
        }
    
    # Convert roads to edges format
    edges = {}
    for edge_id, player_id in state.board.roads.items():
        edges[edge_id] = player_id
    
    # Dev cards
    dev_cards = {}
    dev_cards_detail = {'0': {}, '1': {}}
    for player_id in range(2):
        player = state.players[player_id]
        # Count total dev cards (including bought this turn)
        dev_cards[str(player_id)] = sum(player.dev_cards) + sum(player.dev_cards_bought_this_turn)
        
        # For human player, show details including cards bought this turn
        if player_id == 0:
            dev_card_names = ['KNIGHT', 'YEAR_OF_PLENTY', 'MONOPOLY', 'ROAD_BUILDING', 'VICTORY_POINT']
            # Show playable cards
            for i, count in enumerate(player.dev_cards):
                if count > 0:
                    dev_cards_detail['0'][dev_card_names[i]] = count
            # Also show cards bought this turn (not playable yet)
            for i, count in enumerate(player.dev_cards_bought_this_turn):
                if count > 0:
                    card_name = dev_card_names[i] + '_NEW'
                    dev_cards_detail['0'][card_name] = count
    
    # Determine the actual current player
    current_player = state.setup_phase_player_order() if state.is_setup_phase() else state.current_player
    
    return {
        'current_player': current_player,
        'turn_number': state.turn_number,
        'setup_phase': state.is_setup_phase(),
        'setup_round': 1 if state.initial_phase else 2,
        'setup_settlement_placed': False,  # rlcatan UI will track this from valid actions
        'setup_road_placed': False,  # rlcatan UI will track this from valid actions  
        'last_placed_settlement': None,  # rlcatan UI will track this from board state
        'turn_state': 'NORMAL',
        'action_state': 'WAITING_FOR_ACTION',
        'hexes': hexes,
        'ports': ports,
        'resources': resources,
        'victory_points': {
            '0': state.players[0].public_vps,
            '1': state.players[1].public_vps
        },
        'hidden_vps': {
            '0': state.players[0].hidden_vps,  # Human player can see their own hidden VPs
            '1': 0  # AI's hidden VPs are not revealed to human player
        },
        'robber_tile': state.board.robber_hex,
        'dice_rolled': state.last_dice_roll if state.last_dice_roll else False,
        'edges': edges,
        'corners': corners,
        'dev_cards': dev_cards,
        'dev_cards_detail': dev_cards_detail,
        'longest_road_player': 0 if state.players[0].has_longest_road else (1 if state.players[1].has_longest_road else None),
        'largest_army_player': 0 if state.players[0].has_largest_army else (1 if state.players[1].has_largest_army else None),
        'knights_played': {
            '0': state.players[0].knights_played,
            '1': state.players[1].knights_played
        },
        'road_lengths': {
            '0': state.board.get_player_road_length(0),
            '1': state.board.get_player_road_length(1)
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)