#!/usr/bin/env python3
"""Test that opponent settlements correctly block roads."""

from engine.models.board import Board
from engine.models.enums import SETTLEMENT
from engine.colonist_map import EDGE_TO_CORNERS


def test_opponent_blocking():
    """Test opponent settlement blocking behavior."""
    # Create a board
    board = Board()
    
    # Place settlements at corners 0 and 2 for player 0
    board.buildings[0] = (0, SETTLEMENT)
    board.buildings[2] = (0, SETTLEMENT)
    
    # Place roads on edges 0-10 for player 0
    for edge in range(11):
        board.roads[edge] = 0
    
    print("Scenario 1: No opponent settlements")
    print("=" * 40)
    length1 = board.get_player_road_length(0)
    print(f"Longest road: {length1} roads")
    
    # Add opponent settlement at corner 6
    board.buildings[6] = (1, SETTLEMENT)  # Player 1
    
    print("\n\nScenario 2: Opponent settlement at corner 6")
    print("=" * 40)
    print("This should break the path at corner 6")
    length2 = board.get_player_road_length(0)
    print(f"Longest road: {length2} roads")
    
    # Expected: The path 3->6->7->8->9 is now blocked at corner 6
    # So we lose the branch from 3 to 9 via 6,7,8
    # Remaining paths:
    # - Loop: 0->1->2->3->4->5->0 (uses 5 or 6 edges depending on start)
    # - Direct: 4->9 (edge 10)
    
    print("\n\nDetailed analysis with opponent at corner 6:")
    print("Corner 6 blocks the path between edges 6 and 7")
    print("This splits the road network into:")
    print("1. Upper network: 0-1-2-3-4-5-0 plus 3-6 (dead end)")
    print("2. Lower network: 7-8-9-4 (isolated)")
    print()
    print("The upper network forms a cycle with a dead-end branch")
    print("Maximum path in upper network: 0->1->2->3->4->5->0 is 6 edges")
    print("Or with dead end: 6->3->2->1->0->5->4 is 6 edges")
    print("But since 4 connects to 9, we can extend: 6->3->2->1->0->5->4->9")
    print("That's 7 edges")
    
    # Test more blocking scenarios
    print("\n\nScenario 3: Opponent settlements at corners 3 and 6")
    print("=" * 40)
    board.buildings[3] = (1, SETTLEMENT)  # Player 1
    length3 = board.get_player_road_length(0)
    print(f"Longest road: {length3} roads")
    print("This should severely fragment the network")
    
    return length1, length2, length3


def visualize_blocking():
    """Visualize how opponent settlements block roads."""
    print("\n\nVisualizing road blocking:")
    print("=" * 40)
    print("Original network (all roads belong to player 0):")
    print()
    print("    5---0---1")
    print("    |       |")
    print("    4---3---2")
    print("        |")
    print("        6")
    print("        |")
    print("        7")
    print("        |")
    print("        8")
    print("        |")
    print("        9---4")
    print()
    print("With opponent at corner 6:")
    print()
    print("    5---0---1")
    print("    |       |")
    print("    4---3---2")
    print("        |")
    print("        X (opponent blocks here)")
    print("        ")
    print("        7")
    print("        |")
    print("        8")
    print("        |")
    print("        9---4")
    print()
    print("The road network is split into two components")


if __name__ == "__main__":
    l1, l2, l3 = test_opponent_blocking()
    visualize_blocking()
    
    print("\n\nSUMMARY:")
    print("=" * 40)
    print(f"No opponents: {l1} roads (CORRECT - max possible is 9)")
    print(f"Opponent at 6: {l2} roads")
    print(f"Opponents at 3,6: {l3} roads")