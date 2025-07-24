#!/usr/bin/env python3
"""
Test script to debug port detection in CatanDuel.

This script:
1. Creates a game instance
2. Prints out the port_edges from the game state
3. Prints out the PORT_CORNERS dictionary
4. Places settlements and checks port access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.game import Game
from engine.models.player import Player
from engine.colonist_map import PORT_CORNERS, PORT_EDGES, EDGE_TO_CORNERS
from engine.models.enums import (
    PORT_TYPE_3_1, PORT_TYPE_WOOD, PORT_TYPE_BRICK,
    PORT_TYPE_SHEEP, PORT_TYPE_WHEAT, PORT_TYPE_ORE,
    SETTLEMENT
)

def port_type_to_string(port_type):
    """Convert port type number to string."""
    port_names = {
        PORT_TYPE_3_1: "3:1 Generic",
        PORT_TYPE_WOOD: "2:1 Wood",
        PORT_TYPE_BRICK: "2:1 Brick", 
        PORT_TYPE_SHEEP: "2:1 Sheep",
        PORT_TYPE_WHEAT: "2:1 Wheat",
        PORT_TYPE_ORE: "2:1 Ore"
    }
    return port_names.get(port_type, f"Unknown ({port_type})")

def main():
    print("=== CatanDuel Port Debug Script ===\n")
    
    # Create a game instance
    print("1. Creating game instance...")
    player1 = Player(0)
    player2 = Player(1)
    game = Game([player1, player2])
    state = game.state
    
    # Print port edges from the static map definition
    print("\n2. PORT_EDGES from colonist_map.py:")
    print(f"   Total port edges defined: {len(PORT_EDGES)}")
    for edge_id, port_type in sorted(PORT_EDGES.items()):
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        print(f"   Edge {edge_id} -> {port_type_to_string(port_type)} (corners {corner1}, {corner2})")
    
    # Print port edges from game state
    print("\n3. port_edges from game state:")
    if hasattr(state, 'port_edges') and state.port_edges:
        print(f"   Total port edges in state: {len(state.port_edges)}")
        for edge_id, port_type in sorted(state.port_edges.items()):
            corner1, corner2 = EDGE_TO_CORNERS[edge_id]
            print(f"   Edge {edge_id} -> {port_type_to_string(port_type)} (corners {corner1}, {corner2})")
    else:
        print("   No port_edges found in game state!")
    
    # Print PORT_CORNERS dictionary
    print("\n4. PORT_CORNERS dictionary:")
    print(f"   Total corners with ports: {len(PORT_CORNERS)}")
    if PORT_CORNERS:
        for corner_id, port_type in sorted(PORT_CORNERS.items()):
            print(f"   Corner {corner_id} -> {port_type_to_string(port_type)}")
    else:
        print("   PORT_CORNERS is empty!")
    
    # Test placing settlements and checking port access
    print("\n5. Testing port detection with settlements:")
    
    # Find corners that should have ports
    expected_port_corners = set()
    for edge_id in PORT_EDGES:
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        expected_port_corners.add(corner1)
        expected_port_corners.add(corner2)
    
    print(f"   Expected corners with ports: {sorted(expected_port_corners)}")
    
    # Test a few specific corners
    test_corners = [0, 5, 20, 21, 25, 19]  # These should have ports based on PORT_EDGES
    print("\n6. Testing specific corners:")
    for corner in test_corners:
        has_port = corner in PORT_CORNERS
        port_type = PORT_CORNERS.get(corner, None)
        print(f"   Corner {corner}: {'HAS PORT' if has_port else 'NO PORT'}", end="")
        if has_port:
            print(f" - {port_type_to_string(port_type)}")
        else:
            print()
    
    # Check which edges connect to these corners
    print("\n7. Checking edge connections for test corners:")
    for corner in test_corners:
        print(f"   Corner {corner} is connected to edges:", end="")
        connected_edges = []
        for edge_id, (c1, c2) in EDGE_TO_CORNERS.items():
            if corner == c1 or corner == c2:
                connected_edges.append(edge_id)
        print(f" {connected_edges}")
        
        # Check if any of these edges are port edges
        port_edges = [e for e in connected_edges if e in PORT_EDGES]
        if port_edges:
            print(f"      Port edges: {port_edges}")
            for pe in port_edges:
                print(f"        Edge {pe} -> {port_type_to_string(PORT_EDGES[pe])}")

    # Place a settlement and check if it has port access
    print("\n8. Simulating settlement placement:")
    
    # Try to place a settlement on a corner that should have a port
    if expected_port_corners:
        test_corner = list(expected_port_corners)[0]
        print(f"   Placing settlement for Player 0 at corner {test_corner}")
        
        try:
            # Place initial settlement (no validation during setup)
            state.board.place_initial_settlement(0, test_corner)
            
            # Check if the game recognizes this corner has a port
            # Check port access directly
            buildings = state.board.get_player_buildings(0)
            settlement_corners = buildings[SETTLEMENT]
            print(f"   Player 0's settlements: {settlement_corners}")
            
            player_ports = []
            for corner in settlement_corners:
                if corner in PORT_CORNERS:
                    player_ports.append(PORT_CORNERS[corner])
            
            print(f"   Player 0's port access: {[port_type_to_string(pt) for pt in set(player_ports)]}")
            
            # Also check what the state thinks about ports
            print(f"   Direct check - Corner {test_corner} in PORT_CORNERS: {test_corner in PORT_CORNERS}")
            if test_corner in PORT_CORNERS:
                print(f"   Port type at corner {test_corner}: {port_type_to_string(PORT_CORNERS[test_corner])}")
            
        except Exception as e:
            print(f"   Error placing settlement: {e}")
    
    # Test maritime trade
    print("\n9. Checking if PORT_CORNERS gets updated after game generation:")
    
    # The issue might be that PORT_CORNERS still has the static values
    # Let's check if it matches the game state's port_edges
    
    print("   Comparing PORT_CORNERS with game state port_edges:")
    
    # Rebuild PORT_CORNERS based on game state
    expected_port_corners = {}
    for edge_id, port_type in state.port_edges.items():
        if edge_id in EDGE_TO_CORNERS:
            corner1, corner2 = EDGE_TO_CORNERS[edge_id]
            expected_port_corners[corner1] = port_type
            expected_port_corners[corner2] = port_type
    
    # Check if they match
    mismatches = []
    for corner, expected_type in expected_port_corners.items():
        actual_type = PORT_CORNERS.get(corner)
        if actual_type != expected_type:
            mismatches.append((corner, actual_type, expected_type))
    
    if mismatches:
        print(f"   Found {len(mismatches)} mismatches!")
        for corner, actual, expected in mismatches[:5]:
            print(f"     Corner {corner}: PORT_CORNERS has {port_type_to_string(actual)}, game state has {port_type_to_string(expected)}")
    else:
        print("   PORT_CORNERS matches game state port_edges perfectly!")
    
    # The real issue is likely that PORT_CORNERS is not being updated after game generation
    print("\n10. Recommendation:")
    print("   The PORT_CORNERS dictionary is initialized from the static PORT_EDGES")
    print("   but when a game is created, port types are randomized.")
    print("   The game should update PORT_CORNERS after board generation.")
    print("   This update is likely missing in the game initialization.")

if __name__ == "__main__":
    main()