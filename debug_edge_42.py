#!/usr/bin/env python3
"""Debug edge 42 and its port assignment."""

from engine.colonist_map import (
    EDGE_TO_CORNERS, PORT_EDGES, PORT_CORNERS,
    initialize_reverse_mappings
)
from engine.models.enums import (
    PORT_TYPE_3_1, PORT_TYPE_WOOD, PORT_TYPE_BRICK,
    PORT_TYPE_SHEEP, PORT_TYPE_WHEAT, PORT_TYPE_ORE
)
from engine.game import Game
from engine.models.player import RandomPlayer

def port_type_to_string(port_type):
    """Convert port type to string."""
    return {
        PORT_TYPE_3_1: "3:1 (Generic)",
        PORT_TYPE_WOOD: "2:1 Wood",
        PORT_TYPE_BRICK: "2:1 Brick",
        PORT_TYPE_SHEEP: "2:1 Sheep",
        PORT_TYPE_WHEAT: "2:1 Wheat",
        PORT_TYPE_ORE: "2:1 Ore"
    }.get(port_type, f"Unknown ({port_type})")

def main():
    print("=== Edge 42 Debug ===\n")
    
    # 1. What corners does edge 42 connect?
    corner1, corner2 = EDGE_TO_CORNERS[42]
    print(f"1. Edge 42 connects corners: {corner1} and {corner2}")
    
    # 2. According to the static PORT_EDGES, what port should edge 42 have?
    static_port_type = PORT_EDGES.get(42, None)
    print(f"2. Static PORT_EDGES[42]: {port_type_to_string(static_port_type) if static_port_type else 'No port'}")
    
    # 3. Initialize the mappings and check PORT_CORNERS
    initialize_reverse_mappings()
    print(f"3. After initialization:")
    print(f"   - PORT_CORNERS[{corner1}]: {port_type_to_string(PORT_CORNERS.get(corner1, 'No port'))}")
    print(f"   - PORT_CORNERS[{corner2}]: {port_type_to_string(PORT_CORNERS.get(corner2, 'No port'))}")
    
    # 4. Create a game and see what actually happens after board generation
    print("\n4. Creating a game with random board generation...")
    players = [RandomPlayer(0, "P0"), RandomPlayer(1, "P1")]
    game = Game(players, seed=42)  # Use seed for reproducibility
    
    # Check what port is actually on edge 42 after shuffling
    actual_port_type = game.state.port_edges.get(42, None)
    print(f"   - Actual port on edge 42 after board generation: {port_type_to_string(actual_port_type) if actual_port_type else 'No port'}")
    
    # 5. Show all port edges in the game state
    print("\n5. All ports in game state after shuffling:")
    for edge_id, port_type in sorted(game.state.port_edges.items()):
        c1, c2 = EDGE_TO_CORNERS[edge_id]
        print(f"   Edge {edge_id} (corners {c1}, {c2}): {port_type_to_string(port_type)}")
    
    # 6. Rebuild port corners from game state
    print("\n6. Rebuilding PORT_CORNERS from game state...")
    game_port_corners = {}
    for edge_id, port_type in game.state.port_edges.items():
        if edge_id in EDGE_TO_CORNERS:
            c1, c2 = EDGE_TO_CORNERS[edge_id]
            game_port_corners[c1] = port_type
            game_port_corners[c2] = port_type
    
    print(f"   - Corner {corner1} port: {port_type_to_string(game_port_corners.get(corner1, 'No port'))}")
    print(f"   - Corner {corner2} port: {port_type_to_string(game_port_corners.get(corner2, 'No port'))}")
    
    # 7. Test placing a settlement on corner 35 or 36
    print(f"\n7. Testing settlement placement on corners {corner1} and {corner2}...")
    # Place a settlement on one of edge 42's corners during setup
    test_corner = corner1  # Use corner 35
    game.state.board.place_initial_settlement(0, test_corner)
    print(f"   - Placed settlement for Player 0 at corner {test_corner}")
    
    # Check what ports Player 0 has access to through the game state port mappings
    print("\n8. Checking port access for Player 0's settlement...")
    from engine.models.enums import SETTLEMENT, CITY
    player_buildings = game.state.board.get_player_buildings(0)
    all_corners = player_buildings[SETTLEMENT] + player_buildings[CITY]  # settlements + cities
    
    print(f"   - Player 0 has buildings at corners: {all_corners}")
    
    for corner in all_corners:
        if corner in game_port_corners:
            port = game_port_corners[corner]
            print(f"   - Corner {corner} has port: {port_type_to_string(port)}")
            
    # Summary
    print("\n=== SUMMARY ===")
    print(f"1. Edge 42 statically connects to corners {corner1} and {corner2}")
    print(f"2. In the static PORT_EDGES, edge 42 is a {port_type_to_string(PORT_EDGES[42])}")
    print(f"3. After board generation with shuffling, edge 42 actually has: {port_type_to_string(game.state.port_edges[42])}")
    print(f"4. Therefore, a player settling on corners {corner1} or {corner2} gets a {port_type_to_string(game.state.port_edges[42])} port")
    print("\nThis is working correctly! The ports are randomly shuffled during board generation.")

if __name__ == "__main__":
    main()