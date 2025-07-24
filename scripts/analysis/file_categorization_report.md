# CatanDuel File Organization Report

## Summary
This report categorizes all files in the catanduel codebase and provides recommendations for organization.

## File Categories

### 1. Test Files That Should Be Moved to tests/ Folder

#### Root Directory Test Files:
- `test_board_graph.py` - Tests board graph construction
- `test_dev_card_fix.py` - Tests dev card functionality fixes
- `test_game_over_flow.py` - Tests game over flow
- `test_longest_road_calculation.py` - Tests longest road calculation
- `test_manual_server.py` - Manual server testing
- `test_maritime_trade_fix.py` - Tests maritime trade fixes
- `test_opponent_blocking.py` - Tests opponent blocking behavior
- `test_port_debug.py` - Port functionality debugging tests
- `test_port_flow.py` - Port flow testing
- `test_port_ui.py` - Port UI functionality tests
- `test_ports.py` - General port functionality tests
- `test_settlement_building.py` - Settlement building tests
- `test_trade_then_settle.py` - Trade then settle scenario tests
- `test_turn_sequence.py` - Turn sequence tests
- `test_winner_edge_cases.py` - Winner edge case tests
- `test_winner_serialization.py` - Winner serialization tests
- `direct_test_longest_road.py` - Direct longest road tests
- `exact_board_test.py` - Exact board testing

#### Engine Directory Test Files:
- `engine/test_ai_players.py` - AI player tests
- `engine/test_ai_simple.py` - Simple AI tests
- `engine/test_basic.py` - Basic functionality tests
- `engine/test_comprehensive.py` - Comprehensive game tests

#### UI Directory Test Files:
- `ui/test_ai_seven_roll.py` - AI seven roll tests
- `ui/test_ai_turns.py` - AI turn tests
- `ui/test_all_fixes.py` - All fixes verification
- `ui/test_board_fix.py` - Board fixes tests
- `ui/test_fixes_verification.py` - Fixes verification
- `ui/test_integration.py` - UI integration tests
- `ui/test_latest_fixes.py` - Latest fixes tests
- `ui/test_remaining_fixes.py` - Remaining fixes tests
- `ui/test_robber_issues.py` - Robber issues tests
- `ui/test_setup_phase.py` - Setup phase tests
- `ui/test_ui_fixes.py` - UI fixes tests
- `ui/test_ui_separation.py` - UI separation tests
- `ui/test_vp_display.py` - Victory point display tests
- `ui/test_web_server_fix.py` - Web server fixes tests

### 2. Debug/Diagnostic Scripts (Should Be in a debug/ or scripts/ folder)

#### Longest Road Debug Scripts:
- `analyze_all_edges.py` - Analyzes why all 11 edges can't be used in single path
- `analyze_edge_6.py` - Analyzes edge 6 specifically
- `analyze_longest_path.py` - Analyzes longest path calculation differences
- `analyze_road_network.py` - Analyzes road network structure
- `debug_longest_road.py` - Debugs longest road calculation
- `debug_algorithm_path.py` - Debugs algorithm path finding
- `debug_dfs_edges.py` - Debugs DFS edge traversal
- `debug_dfs_path.py` - Debugs DFS path finding
- `trace_algorithm.py` - Traces algorithm execution
- `trace_blocking.py` - Traces blocking behavior
- `trace_edge_paths.py` - Traces edge paths
- `trace_longest_path.py` - Traces longest path algorithm
- `trace_road_path.py` - Traces road paths
- `find_11_path.py` - Finds 11-edge paths
- `verify_road_count.py` - Verifies road count
- `check_cycle_detection.py` - Checks cycle detection
- `detailed_trace.py` - Detailed algorithm tracing
- `final_debug.py` - Final debugging script
- `simple_debug.py` - Simple debug script
- `longest_road_summary.py` - Longest road analysis summary

#### Settlement/Corner Debug Scripts:
- `debug_settlement_blocking.py` - Debug settlement blocking issues
- `debug_settlement_issue.py` - Debug settlement issues
- `check_specific_settlement.py` - Check specific settlement cases
- `check_valid_corners.py` - Check valid corners for settlement
- `check_corner_connections.py` - Check corner connections
- `dump_adjacency_data.py` - Dump adjacency data
- `fix_corner_adjacency.py` - Fix corner adjacency
- `verify_corner_adjacency.py` - Verify corner adjacency
- `visualize_corner_27_area.py` - Visualize corner 27 area

#### Hex/Edge Debug Scripts:
- `check_all_hex_edges.py` - Check all hex edges
- `verify_hex_12.py` - Verify hex 12 configuration
- `debug_edge_42.py` - Debug edge 42 and port assignment

### 3. Redundant/Obsolete Files

#### Potentially Redundant Debug Scripts:
Many of the debug scripts appear to be addressing the same longest road calculation issue:
- Multiple scripts analyzing the same 11-edge path problem
- Multiple trace scripts doing similar analysis
- Several scripts checking corner adjacency

#### Excel Files (May be obsolete):
- `engine/hexes.xlsx` - Hex configuration data
- `engine/ports.xlsx` - Port configuration data
(These might be reference data that was used to build the map but may no longer be needed)

#### HTML Test Files:
- `ui/debug_placement.html` - Debug placement UI
- `ui/test_ui_actions.html` - Test UI actions
(These appear to be manual testing tools that might be obsolete)

### 4. Duplicate Functionality

#### Longest Road Analysis:
- At least 20+ files dealing with longest road debugging
- Many appear to test the same scenarios with slight variations
- Could be consolidated into a single comprehensive test suite

#### Settlement Building Tests:
- Multiple files testing settlement building from different angles
- Could be consolidated into fewer, more comprehensive test files

#### Port Testing:
- `test_ports.py`, `test_port_ui.py`, `test_port_flow.py`, `test_port_debug.py`
- Significant overlap in port testing functionality

### 5. RLCatan Remnants

Files containing RLCatan references (mostly in documentation/comments):
- `ui/web_server.py` - Contains RLCatan references
- `ui/server.py` - Contains RLCatan references
- `ui/adapter_types.py` - Contains RLCatan references
- `ui/RLCATAN_ANALYSIS.md` - Analysis document about RLCatan
- Various MD files with historical references

### 6. Entry Point Scripts (Should remain in root)
- `run_server.py` - Server entry point
- `run_ui.py` - UI entry point

## Recommendations

### 1. Create Proper Test Structure
```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_board.py
│   ├── test_game.py
│   ├── test_state.py
│   └── test_actions.py
├── integration/
│   ├── __init__.py
│   ├── test_game_flow.py
│   ├── test_ui_adapter.py
│   └── test_server.py
└── ai/
    ├── __init__.py
    ├── test_minimax.py
    ├── test_mcts.py
    └── test_random.py
```

### 2. Create Debug/Scripts Directory
```
scripts/
├── debug/
│   ├── longest_road/
│   ├── settlements/
│   └── ports/
└── analysis/
    └── board_analysis/
```

### 3. Consolidation Suggestions
- Combine all longest road debug scripts into a single comprehensive analysis tool
- Merge port testing files into a single test_ports.py
- Combine settlement building tests
- Remove truly redundant scripts after verification

### 4. Files to Remove (after verification)
- Excel files if data is now hardcoded
- HTML test files if no longer used
- Redundant debug scripts after consolidation

### 5. Documentation Cleanup
- Update MD files to remove obsolete RLCatan references
- Ensure all documentation reflects current CatanDuel implementation
