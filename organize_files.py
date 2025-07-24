#!/usr/bin/env python3
"""Script to help organize the CatanDuel codebase files."""

import os
import shutil
from pathlib import Path

# Define file categories and their destinations
FILE_MOVES = {
    # Test files from root to tests/
    'tests/unit': [
        'test_board_graph.py',
        'test_dev_card_fix.py',
        'test_game_over_flow.py',
        'test_longest_road_calculation.py',
        'test_maritime_trade_fix.py',
        'test_opponent_blocking.py',
        'test_settlement_building.py',
        'test_trade_then_settle.py',
        'test_turn_sequence.py',
        'test_winner_edge_cases.py',
        'test_winner_serialization.py',
        'direct_test_longest_road.py',
        'exact_board_test.py',
    ],
    'tests/integration': [
        'test_manual_server.py',
        'test_port_debug.py',
        'test_port_flow.py',
        'test_port_ui.py',
        'test_ports.py',
    ],
    # Debug scripts to scripts/debug/
    'scripts/debug/longest_road': [
        'analyze_all_edges.py',
        'analyze_edge_6.py',
        'analyze_longest_path.py',
        'analyze_road_network.py',
        'debug_longest_road.py',
        'debug_algorithm_path.py',
        'debug_dfs_edges.py',
        'debug_dfs_path.py',
        'trace_algorithm.py',
        'trace_blocking.py',
        'trace_edge_paths.py',
        'trace_longest_path.py',
        'trace_road_path.py',
        'find_11_path.py',
        'verify_road_count.py',
        'check_cycle_detection.py',
        'detailed_trace.py',
        'final_debug.py',
        'simple_debug.py',
        'longest_road_summary.py',
    ],
    'scripts/debug/settlements': [
        'debug_settlement_blocking.py',
        'debug_settlement_issue.py',
        'check_specific_settlement.py',
        'check_valid_corners.py',
        'check_corner_connections.py',
        'dump_adjacency_data.py',
        'fix_corner_adjacency.py',
        'verify_corner_adjacency.py',
        'visualize_corner_27_area.py',
    ],
    'scripts/debug/hexes': [
        'check_all_hex_edges.py',
        'verify_hex_12.py',
        'debug_edge_42.py',
    ],
}

# Files from subdirectories
SUBDIR_MOVES = {
    'tests/unit': [
        ('engine/test_ai_players.py', 'test_ai_players.py'),
        ('engine/test_ai_simple.py', 'test_ai_simple.py'),
        ('engine/test_basic.py', 'test_engine_basic.py'),
        ('engine/test_comprehensive.py', 'test_engine_comprehensive.py'),
    ],
    'tests/ui': [
        ('ui/test_ai_seven_roll.py', 'test_ai_seven_roll.py'),
        ('ui/test_ai_turns.py', 'test_ai_turns.py'),
        ('ui/test_all_fixes.py', 'test_all_fixes.py'),
        ('ui/test_board_fix.py', 'test_board_fix.py'),
        ('ui/test_fixes_verification.py', 'test_fixes_verification.py'),
        ('ui/test_integration.py', 'test_ui_integration.py'),
        ('ui/test_latest_fixes.py', 'test_latest_fixes.py'),
        ('ui/test_remaining_fixes.py', 'test_remaining_fixes.py'),
        ('ui/test_robber_issues.py', 'test_robber_issues.py'),
        ('ui/test_setup_phase.py', 'test_setup_phase.py'),
        ('ui/test_ui_fixes.py', 'test_ui_fixes.py'),
        ('ui/test_ui_separation.py', 'test_ui_separation.py'),
        ('ui/test_vp_display.py', 'test_vp_display.py'),
        ('ui/test_web_server_fix.py', 'test_web_server_fix.py'),
    ],
}

# Files to potentially remove (after manual verification)
POTENTIALLY_OBSOLETE = [
    'engine/hexes.xlsx',
    'engine/ports.xlsx',
    'ui/debug_placement.html',
    'ui/test_ui_actions.html',
    'longest_road_analysis_summary.md',  # Likely superseded by debug scripts
]

def main():
    """Main function to organize files."""
    print("CatanDuel File Organization Script")
    print("=================================\n")
    
    # Create report of what would be done
    print("This script would perform the following actions:\n")
    
    # Report root file moves
    print("1. Move test files from root to tests/ directory:")
    for dest, files in FILE_MOVES.items():
        if dest.startswith('tests/'):
            print(f"\n   To {dest}:")
            for f in files:
                if os.path.exists(f):
                    print(f"     - {f}")
    
    # Report subdirectory moves
    print("\n2. Move test files from subdirectories to tests/:")
    for dest, moves in SUBDIR_MOVES.items():
        print(f"\n   To {dest}:")
        for src, dst in moves:
            if os.path.exists(src):
                print(f"     - {src} -> {dst}")
    
    # Report debug script moves
    print("\n3. Move debug scripts to scripts/debug/:")
    for dest, files in FILE_MOVES.items():
        if dest.startswith('scripts/'):
            print(f"\n   To {dest}:")
            for f in files:
                if os.path.exists(f):
                    print(f"     - {f}")
    
    # Report potentially obsolete files
    print("\n4. Potentially obsolete files (verify before removing):")
    for f in POTENTIALLY_OBSOLETE:
        if os.path.exists(f):
            print(f"   - {f}")
    
    print("\n" + "="*50)
    print("\nTo execute these moves, run with --execute flag")
    print("To create directories only, run with --create-dirs flag")
    
    # Check for command line arguments
    import sys
    if '--create-dirs' in sys.argv:
        create_directories()
    elif '--execute' in sys.argv:
        response = input("\nAre you sure you want to reorganize files? (yes/no): ")
        if response.lower() == 'yes':
            execute_moves()
        else:
            print("Operation cancelled.")

def create_directories():
    """Create the directory structure."""
    dirs_to_create = [
        'tests/unit',
        'tests/integration',
        'tests/ui',
        'tests/ai',
        'scripts/debug/longest_road',
        'scripts/debug/settlements',
        'scripts/debug/hexes',
        'scripts/debug/ports',
        'scripts/analysis/board_analysis',
    ]
    
    print("\nCreating directory structure...")
    for d in dirs_to_create:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"Created: {d}")
        
        # Create __init__.py for test directories
        if d.startswith('tests/'):
            init_file = Path(d) / '__init__.py'
            if not init_file.exists():
                init_file.write_text('')
                print(f"Created: {init_file}")

def execute_moves():
    """Execute the file moves."""
    # First create directories
    create_directories()
    
    print("\nMoving files...")
    
    # Move root files
    for dest, files in FILE_MOVES.items():
        for f in files:
            if os.path.exists(f):
                dest_path = Path(dest) / f
                print(f"Moving {f} to {dest_path}")
                shutil.move(f, dest_path)
    
    # Move subdirectory files
    for dest, moves in SUBDIR_MOVES.items():
        for src, dst in moves:
            if os.path.exists(src):
                dest_path = Path(dest) / dst
                print(f"Moving {src} to {dest_path}")
                shutil.move(src, dest_path)
    
    print("\nFile organization complete!")
    print("\nRemember to:")
    print("1. Update any imports in moved files")
    print("2. Update any references to moved files")
    print("3. Run tests to ensure everything still works")
    print("4. Manually review and remove obsolete files")

if __name__ == '__main__':
    main()
