#!/usr/bin/env python3
"""
Test script to verify the latest fixes for friendly robber and maritime trade.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import Game
from engine.models.player import RandomPlayer
from engine.models.enums import Action, ActionType, ActionPrompt, WOOD, BRICK, SHEEP, WHEAT, ORE
import engine.state_functions as sf

def test_friendly_robber_fix():
    """Test that friendly robber now allows movement but restricts placement."""
    print("Testing fixed friendly robber rule...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Give players different VP amounts
    game.state.players[0].public_vps = 3  # Above threshold
    game.state.players[1].public_vps = 2  # At or below threshold
    
    # Place some buildings for testing
    # Place AI settlements at corners 5 and 15
    game.state.board.buildings[5] = (1, 1)  # AI settlement at corner 5
    game.state.board.buildings[15] = (1, 1) # AI settlement at corner 15
    
    # Force a 7 roll scenario
    game.state.current_player = 0
    game.state.current_turn_player = 0
    game.state.is_moving_robber = True
    game.state.current_prompt = ActionPrompt.MOVE_ROBBER
    game.state.invalidate_actions_cache()
    
    # Get robber movement actions
    actions = game.get_valid_actions()
    robber_actions = [a for a in actions if a.action_type == ActionType.MOVE_ROBBER]
    
    print(f"\nTotal robber movement actions: {len(robber_actions)}")
    
    # Check which hexes are allowed
    from engine.colonist_map import get_corner_hexes
    
    # Get hexes adjacent to AI's settlements (should be blocked)
    ai_hexes = set()
    for corner_id in [5, 15]:
        ai_hexes.update(get_corner_hexes(corner_id))
    
    print(f"Hexes adjacent to AI settlements (VP=2): {ai_hexes}")
    
    # Check if these hexes are blocked
    allowed_hexes = set()
    blocked_hexes = set()
    
    for action in robber_actions:
        hex_id = action.value[0] if isinstance(action.value, tuple) else action.value
        if hex_id in ai_hexes:
            blocked_hexes.add(hex_id)
        else:
            allowed_hexes.add(hex_id)
    
    print(f"Blocked hexes: {blocked_hexes}")
    print(f"Allowed hexes: {allowed_hexes}")
    
    if blocked_hexes:
        print("❌ Friendly robber is still blocking hexes with low VP opponents!")
        return False
    else:
        print("✅ Friendly robber fixed - can move to any hex since opponent has ≤2 VP")
        return True

def test_maritime_trade_fix():
    """Test that maritime trade now works with the tuple conversion."""
    print("\n\nTesting maritime trade fix...")
    
    player1 = RandomPlayer(0, "Human")
    player2 = RandomPlayer(1, "AI")
    game = Game([player1, player2])
    
    # Complete setup
    while game.state.is_setup_phase():
        actions = game.get_valid_actions()
        if actions:
            game.execute(actions[0])
    
    # Give player resources for trading
    game.state.players[0].resources = [8, 0, 0, 0, 0]  # 8 wood
    
    # Set up for trade
    game.state.current_player = 0
    game.state.dice_rolled = True
    game.state.invalidate_actions_cache()
    
    # Look for maritime trade actions
    actions = game.get_valid_actions()
    trade_actions = [a for a in actions if a.action_type == ActionType.MARITIME_TRADE]
    
    if trade_actions:
        print(f"Found {len(trade_actions)} maritime trade actions")
        
        # Try a 4:1 trade
        for action in trade_actions:
            give_res, give_amount, get_res = action.value
            if give_res == WOOD and give_amount == 4:
                print(f"Executing 4:1 trade: 4 wood for 1 {['wood','brick','sheep','wheat','ore'][get_res]}")
                
                # Check resources before
                wood_before = game.state.players[0].resources[WOOD]
                get_before = game.state.players[0].resources[get_res]
                
                # Execute trade
                success = game.execute(action)
                
                if success:
                    wood_after = game.state.players[0].resources[WOOD]
                    get_after = game.state.players[0].resources[get_res]
                    
                    if wood_after == wood_before - 4 and get_after == get_before + 1:
                        print("✅ Maritime trade executed successfully!")
                        return True
                    else:
                        print("❌ Trade executed but resources incorrect")
                        return False
                else:
                    print("❌ Trade execution failed")
                    return False
    else:
        print("❌ No maritime trade actions available")
        return False

def test_robber_with_different_vp_scenarios():
    """Test robber placement with various VP scenarios."""
    print("\n\nTesting robber with various VP scenarios...")
    
    scenarios = [
        (1, 1, "Both players have 1 VP"),
        (2, 2, "Both players have 2 VP"), 
        (3, 2, "Current player 3 VP, opponent 2 VP"),
        (2, 3, "Current player 2 VP, opponent 3 VP"),
        (4, 5, "Both players above threshold")
    ]
    
    for p0_vp, p1_vp, desc in scenarios:
        print(f"\n{desc}:")
        
        player1 = RandomPlayer(0, "Human")
        player2 = RandomPlayer(1, "AI")
        game = Game([player1, player2])
        
        # Complete setup
        while game.state.is_setup_phase():
            actions = game.get_valid_actions()
            if actions:
                game.execute(actions[0])
        
        # Set VPs
        game.state.players[0].public_vps = p0_vp
        game.state.players[1].public_vps = p1_vp
        
        # Place opponent settlement
        game.state.board.buildings[10] = (1, 1)
        
        # Set up robber scenario for player 0
        game.state.current_player = 0
        game.state.current_turn_player = 0
        game.state.is_moving_robber = True
        game.state.current_prompt = ActionPrompt.MOVE_ROBBER
        game.state.invalidate_actions_cache()
        
        # Get actions
        actions = game.get_valid_actions()
        robber_actions = [a for a in actions if a.action_type == ActionType.MOVE_ROBBER]
        
        # Check if opponent's hex is blocked
        from engine.colonist_map import get_corner_hexes
        opponent_hexes = set(get_corner_hexes(10))
        
        can_place_on_opponent = False
        for action in robber_actions:
            hex_id = action.value[0] if isinstance(action.value, tuple) else action.value
            if hex_id in opponent_hexes:
                can_place_on_opponent = True
                break
        
        expected = p1_vp > 2  # Can place on opponent if they have >2 VP
        if can_place_on_opponent == expected:
            print(f"  ✅ Correct: Can place on opponent hex = {can_place_on_opponent}")
        else:
            print(f"  ❌ Wrong: Can place on opponent hex = {can_place_on_opponent}, expected {expected}")

if __name__ == "__main__":
    print("=== Testing Latest Fixes ===\n")
    
    all_passed = True
    all_passed &= test_friendly_robber_fix()
    all_passed &= test_maritime_trade_fix()
    test_robber_with_different_vp_scenarios()
    
    if all_passed:
        print("\n\n🎉 All fixes verified!")
    else:
        print("\n\n⚠️ Some issues remain")