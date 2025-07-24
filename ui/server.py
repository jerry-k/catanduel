"""
Flask server for CatanDuel UI.

Provides REST API endpoints for game interaction and serves the web interface.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import uuid
import logging
from typing import Dict, Optional
import time

from ui.adapter import CatanDuelAdapter
from ui.adapter_types import UIAction, UIActionType, UIPhase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'catanduel-secret-key'
CORS(app)  # Enable CORS for development

# Store game instances globally with game_id
games: Dict[str, CatanDuelAdapter] = {}


@app.route('/')
def index():
    """Serve the main game page."""
    return render_template('index.html')


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets."""
    return send_from_directory('static/assets', filename)


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """
    Create a new game.
    
    Request body:
    {
        "seed": "optional_seed",
        "ai_difficulty": "minimax|random"
    }
    """
    try:
        data = request.json or {}
        game_id = str(uuid.uuid4())
        seed = data.get('seed')
        
        # Create new game adapter
        adapter = CatanDuelAdapter()
        
        # Configure players for rlcatan-style UI
        player1_config = {"type": "human", "name": "Red Player"}
        player2_config = {"type": "random", "name": "Blue Player"}  # Default to random AI
        
        logger.info(f"Creating new game {game_id} with seed: {seed}")
        
        # Initialize game
        ui_state = adapter.new_game(player1_config, player2_config, seed=seed)
        
        # Store game
        games[game_id] = adapter
        
        # Get legal actions in rlcatan format
        legal_actions = []
        for action in ui_state.valid_actions:
            legal_actions.append({
                'type': action.type.value,
                'player': 0,  # Human player
                **action.data
            })
        
        # Convert to dict and return in rlcatan format
        return jsonify({
            'game_id': game_id,
            'state': serialize_state(adapter),
            'legal_actions': legal_actions
        })
        
    except Exception as e:
        logger.error(f"Error creating new game: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/game_state/<game_id>')
def get_game_state(game_id):
    """Get current game state and handle AI turns."""
    try:
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        adapter = games[game_id]
        events = []
        
        # Handle AI turns (similar to rlcatan)
        game_over = False
        winner = None
        
        ui_state = adapter.translate_state()
        
        # If it's AI's turn (player 1), let AI play
        ai_turn_count = 0
        max_ai_turns = 10  # Prevent infinite loops
        
        while ui_state.current_player == 1 and not game_over and ai_turn_count < max_ai_turns:
            ai_turn_count += 1
            logger.info(f"Taking AI turn #{ai_turn_count}...")
            
            time.sleep(0.3)  # Brief delay to simulate thinking
            
            ai_action = adapter.get_ai_action()
            if not ai_action:
                logger.info("No AI action available, breaking")
                break
            
            logger.info(f"AI chose action: {ai_action.type}")
            
            # Execute AI action
            try:
                ui_state, ai_events = adapter.execute_action(ai_action)
                events.extend(ai_events)
                
                # Check for game over
                if ui_state.phase == 'game_over':
                    game_over = True
                    winner = ui_state.winner
                    break
                    
            except Exception as e:
                logger.error(f"AI action failed: {e}")
                break
        
        # Check if we hit the turn limit
        if ai_turn_count >= max_ai_turns:
            logger.warning(f"AI hit max turn limit ({max_ai_turns}), stopping to prevent infinite loop")
        
        ai_thinking = ui_state.current_player == 1
        
        # Get legal actions in rlcatan format
        legal_actions = []
        for action in ui_state.valid_actions:
            legal_actions.append({
                'type': action.type.value,
                'player': ui_state.current_player,
                **action.data
            })
        
        return jsonify({
            'state': serialize_state(adapter),
            'legal_actions': legal_actions,
            'events': [{'type': e.type, 'message': e.message} for e in events],
            'game_over': game_over,
            'winner': winner,
            'ai_thinking': ai_thinking
        })
        
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/execute_action/<game_id>', methods=['POST'])
def execute_action(game_id):
    """
    Execute a player action.
    
    Request body:
    {
        "type": "BUILD_SETTLEMENT",
        "player": 0,
        "corner": 23
    }
    """
    try:
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        adapter = games[game_id]
        
        action = request.json
        if not action or 'type' not in action:
            return jsonify({'error': 'No action data provided'}), 400
        
        logger.info(f"Executing action: {action}")
        
        # Convert rlcatan action format to our UIAction format
        action_type = UIActionType(action['type'])
        action_data = {k: v for k, v in action.items() if k not in ['type', 'player']}
        ui_action = UIAction(type=action_type, data=action_data)
        
        # Execute action
        ui_state, events = adapter.execute_action(ui_action)
        
        # Check for game over
        game_over = ui_state.phase == 'game_over'
        winner = ui_state.winner if game_over else None
        
        # AI turns are now handled in get_game_state endpoint via polling
        ai_thinking = ui_state.current_player == 1
        
        # Get legal actions in rlcatan format
        legal_actions = []
        for action in ui_state.valid_actions:
            legal_actions.append({
                'type': action.type.value,
                'player': ui_state.current_player,
                **action.data
            })
        
        return jsonify({
            'success': True,
            'state': serialize_state(adapter),
            'legal_actions': legal_actions,
            'events': [{'type': e.type, 'message': e.message} for e in events],
            'game_over': game_over,
            'winner': winner,
            'ai_thinking': ai_thinking
        })
        
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return jsonify({'error': str(e)}), 500


def serialize_state(adapter: CatanDuelAdapter):
    """Convert CatanDuel state to rlcatan UI format."""
    ui_state = adapter.translate_state()
    
    # Convert hexes to rlcatan format
    hexes = {}
    for hex_tile in ui_state.board.hexes:
        hexes[str(hex_tile.id)] = {
            'resource': hex_tile.type,
            'number': hex_tile.number
        }
    
    # Convert corners to rlcatan format - build from buildings list
    corners = {}
    edges = {}
    
    for building in ui_state.board.buildings:
        if building.type in ['settlement', 'city']:
            corners[str(building.location)] = {
                'player': building.player,
                'type': building.type.upper()  # SETTLEMENT, CITY
            }
        elif building.type == 'road':
            # Roads are stored in edges dict
            edges[building.location] = building.player
    
    # Fill in None for empty corners
    for corner_id in range(54):  # Colonist.io has 54 corners
        if str(corner_id) not in corners:
            corners[str(corner_id)] = None
    
    # Convert ports to rlcatan format
    ports = {}
    for port in ui_state.board.ports:
        ports[str(port.edge_id)] = port.type
    
    # Convert resources to rlcatan format
    resources = {}
    for player in ui_state.players:
        resources[str(player.id)] = {
            '0': player.resources.brick,   # BRICK = 0
            '1': player.resources.wheat,   # GRAIN/WHEAT = 1  
            '2': player.resources.wood,    # LUMBER/WOOD = 2
            '3': player.resources.ore,     # ORE = 3
            '4': player.resources.sheep    # WOOL/SHEEP = 4
        }
    
    # Convert dev cards to rlcatan format
    dev_cards = {}
    dev_cards_detail = {'0': {}, '1': {}}
    
    for player in ui_state.players:
        # Count total unplayed dev cards
        dev_cards[str(player.id)] = player.dev_cards.total()
        
        # For human player (0), send detailed card info
        if player.id == 0:
            dev_cards_detail[str(player.id)] = {
                'KNIGHT': player.dev_cards.knight,
                'VICTORY_POINT': player.dev_cards.victory_point,
                'ROAD_BUILDING': player.dev_cards.road_building,
                'YEAR_OF_PLENTY': player.dev_cards.year_of_plenty,
                'MONOPOLY': player.dev_cards.monopoly
            }
    
    return {
        'current_player': ui_state.current_player,
        'turn_number': ui_state.turn_number,
        'setup_phase': ui_state.phase in [UIPhase.SETUP_INITIAL, UIPhase.SETUP_SECOND],
        'setup_round': 1 if ui_state.phase == UIPhase.SETUP_INITIAL else 2,
        'setup_settlement_placed': getattr(ui_state, 'setup_settlement_placed', False),
        'setup_road_placed': getattr(ui_state, 'setup_road_placed', False),
        'last_placed_settlement': getattr(ui_state, 'last_placed_settlement', None),
        'turn_state': 'NORMAL',  # Simplified for now
        'action_state': 'WAITING_FOR_ACTION',  # Simplified for now
        'hexes': hexes,
        'ports': ports,
        'resources': resources,
        'victory_points': {
            '0': ui_state.players[0].public_vps,
            '1': ui_state.players[1].public_vps
        },
        'robber_tile': ui_state.board.robber_hex,
        'dice_rolled': ui_state.dice_rolled,
        'edges': edges,
        'corners': corners,
        'dev_cards': dev_cards,
        'dev_cards_detail': dev_cards_detail,
        'longest_road_player': 0 if ui_state.players[0].has_longest_road else (1 if ui_state.players[1].has_longest_road else None),
        'largest_army_player': 0 if ui_state.players[0].has_largest_army else (1 if ui_state.players[1].has_largest_army else None),
        'knights_played': {
            '0': ui_state.players[0].knights_played,
            '1': ui_state.players[1].knights_played
        },
        'road_lengths': {
            '0': ui_state.players[0].longest_road_length,
            '1': ui_state.players[1].longest_road_length
        }
    }


# Error handlers
@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({'error': str(e)}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    import traceback
    traceback.print_exc()
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Run development server
    import socket
    
    # Find an available port
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    # Try ports 5001-5010, then find a random free port
    for port in range(5001, 5011):
        try:
            app.run(debug=True, port=port, host='0.0.0.0')
            break
        except OSError:
            continue
    else:
        # If all preferred ports are taken, use a random free port
        free_port = find_free_port()
        print(f"Using port {free_port}")
        app.run(debug=True, port=free_port, host='0.0.0.0')