#!/usr/bin/env python3
"""
Organize scripts directory by moving test/debug files to subdirectories.
"""

import os
import shutil
from pathlib import Path

def organize_scripts():
    """Organize scripts into logical subdirectories."""
    
    scripts_dir = Path(__file__).parent
    
    # Define categories and their patterns
    categories = {
        'tests': {
            'patterns': ['test_*.py', 'compare_*.py', 'check_*.py'],
            'description': 'Test scripts for various features'
        },
        'debug': {
            'patterns': ['debug_*.py', 'analyze_*.py', 'reproduce_*.py'],
            'description': 'Debug and analysis scripts'
        },
        'archive': {
            'patterns': ['*_9vp_*.py', '*_stalled_*.py', '*_vp_*.py'],
            'description': 'Old scripts from debugging specific issues'
        }
    }
    
    # Files to keep in root
    keep_in_root = [
        'tournament.py',
        'bot_game_log.py',
        'baseline_comparison.py',
        'cleanup_scripts.py',
        'README_CATANATRON_FINDINGS.md'
    ]
    
    print("Scripts Directory Cleanup")
    print("=" * 50)
    
    # Create directories if they don't exist
    for category in categories:
        category_dir = scripts_dir / category
        if not category_dir.exists():
            category_dir.mkdir()
            print(f"Created directory: {category}/")
    
    # Move files to appropriate directories
    moved_files = []
    
    for file in scripts_dir.glob("*.py"):
        if file.name in keep_in_root:
            continue
            
        moved = False
        for category, info in categories.items():
            for pattern in info['patterns']:
                if file.match(pattern) and not moved:
                    dest = scripts_dir / category / file.name
                    if not dest.exists():
                        print(f"Moving {file.name} -> {category}/")
                        shutil.move(str(file), str(dest))
                        moved_files.append((file.name, category))
                        moved = True
                        break
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    print(f"\nMoved {len(moved_files)} files:")
    for category in categories:
        count = len([f for f in moved_files if f[1] == category])
        if count > 0:
            print(f"  {category}/: {count} files")
    
    print(f"\nKept in root: {len(keep_in_root)} files")
    for file in keep_in_root:
        if (scripts_dir / file).exists():
            print(f"  - {file}")
    
    # Create README for organization
    readme_content = """# Scripts Organization

## Main Scripts (in root)
- `tournament.py` - Run tournaments between AI players
- `bot_game_log.py` - Run single games with detailed logging
- `baseline_comparison.py` - Compare all AIs against random baseline

## Subdirectories

### tests/
Test scripts for various features and comparisons.

### debug/
Debug and analysis scripts used during development.

### archive/
Old scripts from debugging specific issues (9VP bug, etc). Kept for reference.

### analysis/
Data analysis and visualization scripts.
"""
    
    with open(scripts_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print("\nCreated README.md with directory structure")
    
    return moved_files


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize scripts directory")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be moved without actually moving")
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN - No files will be moved")
        print("\nFiles that would be moved:")
        
        scripts_dir = Path(__file__).parent
        keep_in_root = ['tournament.py', 'bot_game_log.py', 'baseline_comparison.py', 
                       'cleanup_scripts.py', 'README_CATANATRON_FINDINGS.md']
        
        for file in scripts_dir.glob("*.py"):
            if file.name not in keep_in_root:
                print(f"  - {file.name}")
    else:
        organize_scripts()
        print("\n✓ Cleanup complete!")
        print("\nMain scripts kept in root:")
        print("  - tournament.py (run tournaments)")
        print("  - bot_game_log.py (single games with logging)")
        print("  - baseline_comparison.py (AI performance vs random)")


if __name__ == "__main__":
    main()