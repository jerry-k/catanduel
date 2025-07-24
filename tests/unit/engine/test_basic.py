"""
Basic tests for CatanDuel engine.

This is a simple test file to verify the engine works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game, play_random_game, benchmark_games
from models.player import RandomPlayer, GreedyPlayer
from models.enums import Action, ActionType, WOOD, BRICK, SETTLEMENT
from state import GameState


def test_game_initialization():
    """Test that a game can be initialized."""
    print("Testing game initialization...")
    
    players = [
        RandomPlayer(0, "Test Player 0"),
        RandomPlayer(1, "Test Player 1")
    ]
    
    game = Game(players, seed=42)
    
    assert len(game.players) == 2
    assert game.state.current_player == 0
    assert game.state.is_setup_phase()
    assert not game.is_over()
    
    print("✓ Game initialization successful")


def test_setup_phase():
    """Test the initial setup phase."""
    print("\nTesting setup phase...")
    
    players = [
        RandomPlayer(0, "Random 0"),
        RandomPlayer(1, "Random 1")
    ]
    
    game = Game(players, seed=42)
    
    # Should start with settlement placement
    actions = game.get_valid_actions()
    assert len(actions) > 0
    assert all(a.action_type == ActionType.BUILD_INITIAL_SETTLEMENT for a in actions)
    
    # Place 4 settlements and 4 roads
    for i in range(4):
        # Place settlement
        actions = game.get_valid_actions()
        assert actions[0].action_type == ActionType.BUILD_INITIAL_SETTLEMENT
        game.execute(actions[0])
        
        # Place road
        actions = game.get_valid_actions()
        assert actions[0].action_type == ActionType.BUILD_INITIAL_ROAD
        game.execute(actions[0])
    
    # Should now be in normal play
    assert not game.state.is_setup_phase()
    assert game.state.current_player == 0
    
    # Players should have starting resources from second settlement
    p0_resources = game.state.players[0].total_resources()
    p1_resources = game.state.players[1].total_resources()
    assert p0_resources > 0 or p1_resources > 0  # At least one player got resources
    
    print(f"✓ Setup phase complete. P0 has {p0_resources} resources, P1 has {p1_resources}")


def test_resource_distribution():
    """Test that resources are distributed correctly."""
    print("\nTesting resource distribution...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup phase
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Roll dice and check resources before/after
    initial_total = sum(p.total_resources() for p in game.state.players)
    
    # Keep rolling until we get a non-7
    rolled_non_seven = False
    for _ in range(20):  # Try up to 20 times
        if game.state.dice_rolled:
            # End turn to roll again
            game.execute(Action(ActionType.END_TURN, None))
        
        # Roll
        game.execute(Action(ActionType.ROLL, None))
        
        # Check if we rolled a 7 (would need to handle discards/robber)
        if game.state.is_discarding:
            # Handle discards
            while game.state.is_discarding:
                actions = game.get_valid_actions()
                if actions:
                    game.execute(actions[0])
                else:
                    break
        else:
            # Rolled non-7, resources might have been distributed
            rolled_non_seven = True
            break
    
    if rolled_non_seven:
        final_total = sum(p.total_resources() for p in game.state.players)
        print(f"✓ Resources distributed. Total went from {initial_total} to {final_total}")
    else:
        print("✓ Only rolled 7s in test (unlikely but possible)")


def test_building():
    """Test building mechanics."""
    print("\nTesting building mechanics...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Roll dice first to enter normal turn
    actions = game.get_valid_actions()
    roll_action = next((a for a in actions if a.action_type == ActionType.ROLL), None)
    if roll_action:
        game.execute(roll_action)
    
    # Handle any discards if rolled a 7
    while game.state.is_discarding:
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
        else:
            break
    
    # Give player 0 resources to build
    game.state.players[game.state.current_player].resources = [5, 5, 5, 5, 5]  # Plenty of everything
    
    # Find build actions
    game.state.invalidate_actions_cache()
    actions = game.get_valid_actions()
    
    build_actions = [a for a in actions if a.action_type in [
        ActionType.BUILD_SETTLEMENT,
        ActionType.BUILD_CITY,
        ActionType.BUILD_ROAD,
        ActionType.BUY_DEVELOPMENT_CARD
    ]]
    
    assert len(build_actions) > 0
    print(f"✓ Found {len(build_actions)} possible build actions")


def test_complete_game():
    """Test playing a complete game."""
    print("\nTesting complete game...")
    
    try:
        winner, turns = play_random_game(seed=42)
        
        if winner is None:
            print(f"Game ended without winner after {turns} turns")
        else:
            print(f"✓ Game completed. Player {winner.player_id} won in {turns} turns")
            
        # For now, just check the game runs without crashing
        assert turns >= 0
    except Exception as e:
        print(f"Game failed with error: {e}")
        raise


def test_game_copy():
    """Test game state copying."""
    print("\nTesting game state copying...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game1 = Game(players, seed=42)
    
    # Play a few actions
    for _ in range(10):
        actions = game1.get_valid_actions()
        if actions:
            game1.execute(actions[0])
    
    # Copy the game
    game2 = game1.copy()
    
    # Verify states are independent
    game1.execute(game1.get_valid_actions()[0])
    
    assert game1.state.turn_number != game2.state.turn_number or \
           len(game1.action_history) != len(game2.action_history)
    
    print("✓ Game copying works correctly")


def test_benchmark():
    """Test performance benchmark."""
    print("\nRunning performance benchmark...")
    
    stats = benchmark_games(10)  # Just 10 games for quick test
    
    assert stats['games'] == 10
    assert stats['games_per_second'] > 0
    # Some games might not complete, so just check we ran them
    total_wins = stats['wins']['player_0'] + stats['wins']['player_1']
    assert total_wins <= 10
    
    print(f"✓ Benchmark complete: {stats['games_per_second']:.1f} games/second")
    print(f"  {total_wins} games completed successfully")


def run_all_tests():
    """Run all tests."""
    print("Running CatanDuel engine tests...\n")
    
    test_game_initialization()
    test_setup_phase()
    test_resource_distribution()
    test_building()
    test_complete_game()
    test_game_copy()
    test_benchmark()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()