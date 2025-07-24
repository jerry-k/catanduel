# Longest Road Debug Scripts

## Retained Scripts:
1. **analyze_longest_path.py** - Most comprehensive analysis of path calculation
2. **debug_longest_road.py** - Main debugging script with visual output
3. **trace_blocking.py** - Analyzes settlement blocking behavior

## Archived/Redundant Scripts:
The following scripts were investigating the same issue (11-edge path calculation) and have been consolidated:
- analyze_all_edges.py - Analyzed why 11 edges can't form single path
- analyze_edge_6.py - Specific edge analysis (covered in main script)
- analyze_road_network.py - Basic network structure (covered in main)
- check_cycle_detection.py - Cycle detection (integrated into main)
- debug_algorithm_path.py - Algorithm path (duplicate of trace)
- debug_dfs_edges.py - DFS edge traversal (covered in main)
- debug_dfs_path.py - DFS path finding (duplicate)
- detailed_trace.py - Detailed tracing (duplicate of trace_algorithm)
- final_debug.py - Final attempts (duplicate)
- find_11_path.py - Finding 11-edge paths (covered in analyze_longest_path)
- simple_debug.py - Simplified version (less comprehensive)
- trace_algorithm.py - Algorithm tracing (duplicate)
- trace_edge_paths.py - Edge path tracing (covered in main)
- trace_longest_path.py - Path tracing (duplicate)
- trace_road_path.py - Road path tracing (duplicate)
- verify_road_count.py - Road counting (covered in main)
- longest_road_summary.py - Summary document (obsolete)

## Key Finding:
The issue was that the longest road algorithm was incorrectly handling the road graph construction by checking for "blocked" corners during graph building.