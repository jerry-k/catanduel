#!/usr/bin/env python3
"""Test the longest road calculation for a specific scenario."""

from engine.models.board import Board
from engine.models.enums import SETTLEMENT, CITY
from engine.models.player import Player


def test_longest_road_scenario():
    """Test longest road calculation with settlements at corners 0,2 and roads on edges 0-10."""
    # Create a board
    board = Board()
    
    # Create a simple player
    player = Player(0, "TestPlayer")
    
    # Place settlements at corners 0 and 2 for player 0
    board.buildings[0] = (0, SETTLEMENT)  # (player_id, building_type)
    board.buildings[2] = (0, SETTLEMENT)  # (player_id, building_type)
    
    # Place roads on edges 0-10 for player 0
    for edge in range(11):
        board.roads[edge] = 0
    
    # Calculate longest road
    road_length = board.get_player_road_length(0)
    
    print(f"Test Scenario:")
    print(f"- Player 0 has settlements at corners 0 and 2")
    print(f"- Player 0 has roads on edges 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
    print(f"- Calculated longest road length: {road_length}")
    
    # Let's also trace the path to understand the calculation
    print("\nEdge connections:")
    from engine.colonist_map import EDGE_TO_CORNERS
    for edge in range(11):
        corners = EDGE_TO_CORNERS.get(edge, (-1, -1))
        print(f"  Edge {edge}: connects corners {corners[0]} and {corners[1]}")
    
    print("\nPossible paths:")
    print("  Path 1: 7→8→9→10→3→2→1→0→5→4 (10 roads)")
    print("  Path 2: 4→5→0→1→2→3→10→9→8→7 (10 roads)")
    
    # Let's also check what happens if there's an opponent settlement at corner 6
    print("\n\nTest with opponent settlement at corner 6:")
    board.buildings[6] = (1, SETTLEMENT)  # Player 1 (opponent)
    
    road_length_with_opponent = board.get_player_road_length(0)
    print(f"- With opponent settlement at corner 6: longest road = {road_length_with_opponent}")
    
    # Check the actual paths by examining the road network
    print("\nDetailed analysis:")
    print("- Settlements act as endpoints for road paths")
    print("- The path should be: 0(settlement)→1→2(settlement) + 2(settlement)→3→4→5→0(settlement)")
    print("- Plus the branch: 4→10→9→8→7→6")
    
    return road_length, road_length_with_opponent


if __name__ == "__main__":
    length_without_opponent, length_with_opponent = test_longest_road_scenario()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Without opponent at corner 6: {length_without_opponent} roads")
    print(f"With opponent at corner 6: {length_with_opponent} roads")
    print("Expected: 10 roads")
    
    if length_without_opponent == 10:
        print("✅ Longest road calculation is CORRECT!")
    else:
        print("❌ Longest road calculation is INCORRECT!")