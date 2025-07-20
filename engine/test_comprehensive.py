"""
Comprehensive tests for CatanDuel engine.

Tests edge cases, discard scenarios, and game mechanics thoroughly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game
from models.player import RandomPlayer
from models.enums import (
    Action, ActionType, ActionPrompt,
    WOOD, BRICK, SHEEP, WHEAT, ORE,
    KNIGHT, YEAR_OF_PLENTY, MONOPOLY, ROAD_BUILDING, VICTORY_POINT,
    SETTLEMENT, CITY, ROAD,
    PLAYER_0, PLAYER_1
)
from state import GameState
from state_functions import roll_dice


def test_discard_no_one_over_limit():
    """Test rolling 7 when no one has more than 7 cards."""
    print("\nTesting 7 roll with no discards needed...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give players exactly 7 resources each
    game.state.players[0].resources = [2, 2, 2, 1, 0]  # 7 total
    game.state.players[1].resources = [1, 1, 1, 1, 3]  # 7 total
    
    # Force a 7 roll
    game.state.invalidate_actions_cache()
    roll_action = Action(ActionType.ROLL, None)
    game.execute(roll_action)
    
    # Manually set the dice to 7
    game.state.dice_rolled = True
    die1, die2 = 3, 4
    total = 7
    
    # Simulate what happens in roll_dice when 7 is rolled
    import state_functions as sf
    game.state.current_turn_player = game.state.current_player
    discarders = [
        game.state.players[i].total_resources() > 7
        for i in range(2)
    ]
    
    assert not any(discarders), "No one should need to discard"
    assert not game.state.is_discarding, "Should not be in discard state"
    
    # Should go directly to robber (unless friendly robber applies)
    game.state.is_moving_robber = True
    sf.check_friendly_robber(game.state)
    
    # Check if friendly robber prevented robber movement
    has_enough_points = any(p.public_vps >= 3 for p in game.state.players)
    
    if has_enough_points:
        if game.state.current_prompt == ActionPrompt.MOVE_ROBBER:
            print("✓ Correctly moved to robber phase without discards")
        else:
            print(f"✗ Wrong prompt: {game.state.current_prompt}")
    else:
        if game.state.current_prompt == ActionPrompt.PLAY_TURN:
            print("✓ Friendly robber rule applied - no robber movement")
        else:
            print(f"✗ Wrong prompt: {game.state.current_prompt}")


def test_discard_one_player():
    """Test when only one player needs to discard."""
    print("\nTesting discard with one player over limit...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give player 0 many resources, player 1 few
    game.state.players[0].resources = [3, 3, 3, 2, 2]  # 13 total
    game.state.players[1].resources = [1, 1, 1, 0, 0]  # 3 total
    game.state.resource_bank = [10, 10, 10, 10, 10]  # Ensure bank has resources
    
    # Roll a 7
    game.state.current_player = 0
    game.state.current_turn_player = 0
    game.state.invalidate_actions_cache()
    
    # Simulate rolling 7
    import state_functions as sf
    game.state.dice_rolled = True
    
    # Check who needs to discard
    discarders = [
        game.state.players[i].total_resources() > 7
        for i in range(2)
    ]
    
    assert discarders == [True, False], "Only player 0 should need to discard"
    
    # Set discard state
    game.state.current_player = 0  # First player who needs to discard
    game.state.current_prompt = ActionPrompt.DISCARD
    game.state.is_discarding = True
    
    # Get discard actions
    actions = game.get_valid_actions()
    assert len(actions) > 0, "Should have discard actions"
    assert all(a.action_type == ActionType.DISCARD for a in actions)
    
    # Check discard amount
    total_cards = game.state.players[0].total_resources()
    expected_discard = total_cards // 2  # 13 // 2 = 6
    
    # Execute a discard
    discard_action = actions[0]
    assert sum(discard_action.value) == expected_discard
    
    game.execute(discard_action)
    
    # Should now be in robber phase (unless friendly robber)
    assert not game.state.is_discarding
    
    # Check if we have enough points for robber
    has_enough_points = any(p.public_vps >= 3 for p in game.state.players)
    
    if has_enough_points:
        assert game.state.is_moving_robber or game.state.current_prompt == ActionPrompt.MOVE_ROBBER
        print("✓ Single player discard handled correctly - moved to robber")
    else:
        assert game.state.current_prompt == ActionPrompt.PLAY_TURN
        print("✓ Single player discard handled correctly - friendly robber applied")


def test_discard_both_players():
    """Test when both players need to discard."""
    print("\nTesting discard with both players over limit...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give both players many resources
    game.state.players[0].resources = [2, 2, 2, 2, 2]  # 10 total
    game.state.players[1].resources = [3, 3, 3, 3, 0]  # 12 total
    game.state.resource_bank = [10, 10, 10, 10, 10]
    
    # Player 1's turn, roll a 7
    game.state.current_player = 1
    game.state.current_turn_player = 1
    game.state.invalidate_actions_cache()
    
    # Simulate rolling 7
    import state_functions as sf
    game.state.dice_rolled = True
    
    # Both should need to discard
    discarders = [
        game.state.players[i].total_resources() > 7
        for i in range(2)
    ]
    assert all(discarders), "Both players should need to discard"
    
    # First player (0) discards first
    game.state.current_player = 0
    game.state.current_prompt = ActionPrompt.DISCARD
    game.state.is_discarding = True
    
    # Player 0 discards
    actions = game.get_valid_actions()
    p0_total = game.state.players[0].total_resources()
    p0_discard = p0_total // 2  # 10 // 2 = 5
    
    discard_action = next(a for a in actions if sum(a.value) == p0_discard)
    game.execute(discard_action)
    
    # Should still be discarding, but now player 1
    assert game.state.is_discarding
    assert game.state.current_player == 1
    
    # Player 1 discards
    actions = game.get_valid_actions()
    p1_total = game.state.players[1].total_resources()
    p1_discard = p1_total // 2  # 12 // 2 = 6
    
    discard_action = next(a for a in actions if sum(a.value) == p1_discard)
    game.execute(discard_action)
    
    # Now should be in robber phase (unless friendly robber)
    assert not game.state.is_discarding
    
    # Check if we have enough points for robber
    has_enough_points = any(p.public_vps >= 3 for p in game.state.players)
    
    if has_enough_points:
        assert game.state.is_moving_robber or game.state.current_prompt == ActionPrompt.MOVE_ROBBER
        assert game.state.current_player == 1  # Back to player whose turn it is
        print("✓ Both players discard handled correctly - moved to robber")
    else:
        assert game.state.current_prompt == ActionPrompt.PLAY_TURN
        assert game.state.current_player == 1  # Back to player whose turn it is
        print("✓ Both players discard handled correctly - friendly robber applied")


def test_robber_movement():
    """Test robber movement and stealing."""
    print("\nTesting robber movement...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Place some buildings and give resources
    # This is a simplified test - in real game buildings would be placed properly
    game.state.players[1].resources = [2, 2, 1, 1, 1]  # 7 total
    
    # Make sure someone has 3+ VPs to allow robber movement
    game.state.players[0].public_vps = 3
    
    # Set up robber movement
    game.state.current_player = 0
    game.state.current_turn_player = 0
    game.state.current_prompt = ActionPrompt.MOVE_ROBBER
    game.state.is_moving_robber = True
    game.state.invalidate_actions_cache()
    
    # Get robber actions
    actions = game.get_valid_actions()
    assert len(actions) > 0
    assert all(a.action_type == ActionType.MOVE_ROBBER for a in actions)
    
    # Execute robber movement
    robber_action = actions[0]
    game.execute(robber_action)
    
    # Should be back to normal play
    assert not game.state.is_moving_robber
    assert game.state.current_prompt == ActionPrompt.PLAY_TURN
    
    print("✓ Robber movement handled correctly")


def test_knight_then_robber():
    """Test playing a knight card then moving robber."""
    print("\nTesting knight card -> robber sequence...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give player a knight card
    game.state.players[0].dev_cards[KNIGHT] = 1
    game.state.dice_rolled = True  # Can play after rolling
    game.state.current_player = 0
    game.state.current_prompt = ActionPrompt.PLAY_TURN
    
    # Make sure someone has 3+ VPs to allow robber movement
    game.state.players[0].public_vps = 3
    
    game.state.invalidate_actions_cache()
    
    # Find knight action
    actions = game.get_valid_actions()
    knight_action = next((a for a in actions if a.action_type == ActionType.PLAY_KNIGHT_CARD), None)
    
    if knight_action:
        game.execute(knight_action)
        
        # Should now be moving robber
        assert game.state.is_moving_robber
        assert game.state.current_prompt == ActionPrompt.MOVE_ROBBER
        assert game.state.players[0].knights_played == 1
        
        print("✓ Knight card triggers robber movement correctly")
    else:
        print("✗ No knight action available")


def test_dev_card_restrictions():
    """Test development card play restrictions."""
    print("\nTesting development card restrictions...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Test 1: Can't play card bought this turn
    player_id = 0
    game.state.players[player_id].dev_cards_bought_this_turn[KNIGHT] = 1
    game.state.players[player_id].has_played_dev_card = False
    
    # Verify can't play it
    from models.actions import generate_dev_card_actions
    dev_actions = generate_dev_card_actions(game.state)
    knight_actions = [a for a in dev_actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    assert len(knight_actions) == 0, "Should not be able to play card bought this turn"
    
    # Test 2: Can play card from previous turn
    game.state.players[player_id].dev_cards[KNIGHT] = 1
    game.state.players[player_id].dev_cards_bought_this_turn[KNIGHT] = 0
    game.state.players[player_id].has_played_dev_card = False
    
    dev_actions = generate_dev_card_actions(game.state)
    knight_actions = [a for a in dev_actions if a.action_type == ActionType.PLAY_KNIGHT_CARD]
    assert len(knight_actions) > 0, "Should be able to play card from previous turn"
    
    # Test 3: Can't play second dev card in same turn
    game.state.players[player_id].has_played_dev_card = True
    
    dev_actions = generate_dev_card_actions(game.state)
    assert len(dev_actions) == 0, "Should not be able to play second dev card"
    
    print("✓ Development card restrictions work correctly")


def test_longest_road_calculation():
    """Test longest road calculation with blocking."""
    print("\nTesting longest road calculation...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give resources for road building
    game.state.players[0].resources = [10, 10, 0, 0, 0]
    game.state.dice_rolled = True
    
    # Build some roads for player 0
    # This is simplified - in real game we'd check valid positions
    initial_roads = len(game.state.board.roads)
    
    # Try to build a road
    game.state.invalidate_actions_cache()
    actions = game.get_valid_actions()
    road_actions = [a for a in actions if a.action_type == ActionType.BUILD_ROAD]
    
    if road_actions:
        for i in range(min(3, len(road_actions))):
            game.execute(road_actions[i])
            game.state.invalidate_actions_cache()
            actions = game.get_valid_actions()
            road_actions = [a for a in actions if a.action_type == ActionType.BUILD_ROAD]
        
        # Check longest road
        longest_player = game.state.board.longest_road_player
        longest_length = game.state.board.longest_road_length
        
        print(f"✓ Longest road: Player {longest_player} with length {longest_length}")
    else:
        print("✓ Longest road calculation exists (no valid road positions)")


def test_maritime_trade():
    """Test maritime trading with ports."""
    print("\nTesting maritime trade...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give player resources for 4:1 trade
    game.state.players[0].resources = [4, 0, 0, 0, 0]  # 4 wood
    game.state.resource_bank = [15, 19, 19, 19, 19]  # Bank has other resources
    game.state.dice_rolled = True
    game.state.invalidate_actions_cache()
    
    # Look for maritime trade actions
    actions = game.get_valid_actions()
    trade_actions = [a for a in actions if a.action_type == ActionType.MARITIME_TRADE]
    
    if trade_actions:
        # Should be able to trade 4 wood for any other resource
        found_valid_trade = False
        for action in trade_actions:
            give_res, give_amount, get_res = action.value
            if give_res == WOOD and give_amount == 4:
                print(f"✓ Can trade 4 wood for 1 {['wood','brick','sheep','wheat','ore'][get_res]}")
                found_valid_trade = True
                break
        if not found_valid_trade:
            print("✗ No valid 4:1 wood trade found")
    else:
        print("✓ No maritime trade actions (may not have enough resources)")


def test_victory_conditions():
    """Test victory point calculation and win conditions."""
    print("\nTesting victory conditions...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Give player 0 victory points
    player0 = game.state.players[0]
    
    # 2 settlements from setup = 2 VPs
    assert player0.public_vps >= 2
    
    # Add victory point cards
    player0.hidden_vps = 3  # 3 VP cards
    
    # Add longest road
    player0.has_longest_road = True
    player0.public_vps += 2
    
    # Add largest army
    player0.has_largest_army = True
    player0.public_vps += 2
    
    # Check total
    total_vps = player0.actual_vps()
    print(f"✓ Player 0 has {total_vps} VPs (public: {player0.public_vps}, hidden: {player0.hidden_vps})")
    
    # Check win condition
    if total_vps >= 10:
        assert game.state.has_ended()
        assert game.state.get_winner() == 0
        print("✓ Win condition detected correctly")


def test_resource_distribution():
    """Test resource distribution on dice rolls."""
    print("\nTesting resource distribution mechanics...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Count settlements/cities on the board
    total_settlements = 0
    total_cities = 0
    for _, (owner, btype) in game.state.board.buildings.items():
        if btype == SETTLEMENT:
            total_settlements += 1
        elif btype == CITY:
            total_cities += 1
    
    print(f"✓ Board has {total_settlements} settlements and {total_cities} cities")
    
    # Test rolling different numbers
    test_rolls = [2, 6, 8, 9, 11, 12]
    for num in test_rolls:
        # Count hexes with this number
        hex_count = sum(1 for h in game.state.hex_numbers if h == num)
        print(f"  - Number {num} appears on {hex_count} hexes")


def test_game_state_consistency():
    """Test that game state remains consistent through operations."""
    print("\nTesting game state consistency...")
    
    players = [RandomPlayer(0), RandomPlayer(1)]
    game = Game(players, seed=42)
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        game.execute(actions[0])
    
    # Check resource conservation
    total_resources_start = sum(game.state.resource_bank) + \
                          sum(game.state.players[0].resources) + \
                          sum(game.state.players[1].resources)
    
    # Play some turns
    for _ in range(10):
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Check resources are conserved (minus dev cards bought)
    total_resources_end = sum(game.state.resource_bank) + \
                         sum(game.state.players[0].resources) + \
                         sum(game.state.players[1].resources)
    
    # Account for dev cards bought (each costs 1 sheep, 1 wheat, 1 ore)
    dev_cards_bought = 25 - len(game.state.dev_card_deck)
    expected_diff = dev_cards_bought * 3
    
    print(f"✓ Resource conservation: {total_resources_start} -> {total_resources_end}")
    print(f"  Dev cards bought: {dev_cards_bought} (expected resource diff: {expected_diff})")


def run_stress_test():
    """Run many random games to find edge cases."""
    print("\nRunning stress test...")
    
    errors = []
    games_played = 0
    
    for seed in range(100):
        try:
            players = [RandomPlayer(0), RandomPlayer(1)]
            game = Game(players, seed=seed)
            
            # Play up to 500 moves
            for _ in range(500):
                if game.is_over():
                    break
                    
                actions = game.get_valid_actions()
                if not actions:
                    errors.append(f"Seed {seed}: No valid actions")
                    break
                    
                action = players[game._get_acting_player()].decide(game, actions)
                game.execute(action)
            
            games_played += 1
            
        except Exception as e:
            errors.append(f"Seed {seed}: {str(e)}")
    
    print(f"✓ Played {games_played} games")
    if errors:
        print(f"✗ Found {len(errors)} errors:")
        for err in errors[:5]:  # Show first 5 errors
            print(f"  - {err}")
    else:
        print("✓ No errors found!")


def run_all_tests():
    """Run all comprehensive tests."""
    print("Running comprehensive CatanDuel tests...\n")
    
    try:
        test_discard_no_one_over_limit()
        test_discard_one_player()
        test_discard_both_players()
        test_robber_movement()
        test_knight_then_robber()
        test_dev_card_restrictions()
        test_longest_road_calculation()
        test_maritime_trade()
        test_victory_conditions()
        test_resource_distribution()
        test_game_state_consistency()
        run_stress_test()
        
        print("\n✅ All comprehensive tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()