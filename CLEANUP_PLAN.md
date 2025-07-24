# CatanDuel Codebase Cleanup Plan

## Overview
This plan outlines the steps to organize and clean up the catanduel codebase, moving from a development state with scattered test/debug files to a well-organized production structure.

## Phase 1: Create Directory Structure (Safe - No File Movement)

Create the following directories:
```
catanduel/
├── tests/
│   ├── unit/           # Unit tests for individual components
│   ├── integration/    # Integration tests
│   ├── ai/            # AI player tests
│   └── ui/            # UI-specific tests
├── scripts/
│   ├── debug/         # Debug scripts
│   │   ├── longest_road/
│   │   ├── settlements/
│   │   ├── hexes/
│   │   └── ports/
│   └── analysis/      # Analysis scripts
└── archive/           # For obsolete files before deletion
```

## Phase 2: Move Test Files (Low Risk)

### Tests to Move:
1. **Root directory tests (17 files)** → `tests/`
   - `test_*.py` files → appropriate subdirectory based on content
   - `direct_test_longest_road.py` → `tests/unit/`
   
2. **Engine tests (4 files)** → `tests/unit/engine/`
   - `engine/test_*.py`
   
3. **UI tests (14 files)** → `tests/ui/`
   - `ui/test_*.py`

## Phase 3: Organize Debug Scripts (Medium Risk)

### Debug Scripts to Move:
1. **Longest road debug (20 files)** → `scripts/debug/longest_road/`
   - Consider consolidating similar scripts
   
2. **Settlement debug (9 files)** → `scripts/debug/settlements/`
   
3. **Hex/edge debug (3 files)** → `scripts/debug/hexes/`

## Phase 4: Consolidate Redundant Files (High Risk)

### Candidates for Consolidation:
1. **Longest road scripts**: Many analyze the same 11-edge issue
   - Keep: `analyze_longest_path.py` (most comprehensive)
   - Archive others after extracting unique insights
   
2. **Port tests**: 4 different test files
   - Consolidate into single comprehensive test

## Phase 5: Clean Up Obsolete Files

### Review and Archive:
1. **Excel files**: `engine/hexes.xlsx`, `engine/ports.xlsx`
   - Verify data is captured in code
   - Archive if no longer needed
   
2. **Manual test HTML**: `ui/debug_placement.html`, `ui/test_ui_actions.html`
   - Archive if automated tests cover functionality
   
3. **RLCatan references**: Update or remove outdated references

## Phase 6: Update References

After moving files:
1. Update all import statements
2. Update any hardcoded file paths
3. Update documentation
4. Run all tests to ensure nothing broke

## Execution Commands

Use the provided `organize_files.py` script:

```bash
# Preview what will be done (safe)
python organize_files.py

# Create directory structure only
python organize_files.py --create-dirs

# Execute the reorganization
python organize_files.py --execute
```

## Priority Order

1. **High Priority**: Move test files (improves development workflow)
2. **Medium Priority**: Organize debug scripts (reduces clutter)
3. **Low Priority**: Archive obsolete files (cleanup)

## Safety Measures

1. Make a backup before major changes
2. Use git to track all movements
3. Run tests after each phase
4. Document any issues encountered

## Expected Benefits

1. **Cleaner root directory**: From 50+ files to ~15
2. **Better test organization**: Easy to find and run specific test types
3. **Reduced redundancy**: Consolidated debug scripts
4. **Improved maintainability**: Clear structure for future development