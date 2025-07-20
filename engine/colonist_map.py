"""
Colonist.io coordinate mappings for CatanDuel.

This module defines the exact coordinate system used by colonist.io:
- 19 hexes (0-18) arranged in a specific pattern
- 54 corners (0-53) where settlements/cities can be built
- 72 edges (0-71) where roads can be built

The coordinate mappings here should match the Excel files provided.
"""

from typing import Dict, List, Set, Tuple, Optional
from engine.models.enums import (
    HEX_TYPE_DESERT, HEX_TYPE_WOOD, HEX_TYPE_BRICK, 
    HEX_TYPE_SHEEP, HEX_TYPE_WHEAT, HEX_TYPE_ORE,
    PORT_TYPE_3_1, PORT_TYPE_WOOD, PORT_TYPE_BRICK,
    PORT_TYPE_SHEEP, PORT_TYPE_WHEAT, PORT_TYPE_ORE
)

# Hex arrangement in rows (counter-clockwise spiral from top-left)
# Row 1: 3 hexes, Row 2: 4 hexes, Row 3: 5 hexes, Row 4: 4 hexes, Row 5: 3 hexes
HEX_ROWS = [
    [0, 11, 10],         # Row 1 (top)
    [1, 12, 17, 9],      # Row 2
    [2, 13, 18, 16, 8],  # Row 3 (middle)
    [3, 14, 15, 7],      # Row 4
    [4, 5, 6]            # Row 5 (bottom)
]

# Flattened list of all hex IDs
ALL_HEX_IDS = list(range(19))

# Each hex has 6 corners (clockwise from top point)
HEX_TO_CORNERS: Dict[int, List[int]] = {
    0: [0, 1, 2, 3, 4, 5],
    1: [4, 3, 6, 7, 8, 9],
    2: [8, 7, 10, 11, 12, 13],
    3: [10, 14, 15, 16, 17, 11],
    4: [15, 18, 19, 20, 21, 16],
    5: [22, 23, 24, 25, 19, 18],
    6: [26, 27, 28, 29, 24, 23],
    7: [30, 31, 32, 27, 26, 33],
    8: [34, 35, 36, 31, 30, 37],
    9: [38, 39, 34, 37, 40, 41],
    10: [42, 43, 38, 41, 44, 45],
    11: [46, 45, 44, 47, 2, 1],
    12: [2, 27, 48, 49, 6, 3],
    13: [6, 49, 50, 14, 10, 7],
    14: [50, 51, 22, 18, 15, 14],
    15: [52, 33, 26, 23, 22, 51],
    16: [40, 37, 30, 33, 52, 53],
    17: [44, 41, 40, 53, 48, 47],
    18: [48, 53, 52, 51, 50, 49],
}

# Each hex has 6 edges (clockwise from top-right edge)
HEX_TO_EDGES: Dict[int, List[int]] = {
    0: [0, 1, 2, 3, 4, 5],
    1: [3, 6, 7, 8, 9, 10],
    2: [8, 11, 12, 13, 14, 15],
    3: [16, 17, 18, 19, 20, 12],
    4: [21, 22, 23, 24, 25, 18],
    5: [26, 27, 28, 29, 22, 30],
    6: [31, 32, 33, 34, 27, 35],
    7: [36, 37, 38, 31, 39, 40],
    8: [41, 42, 43, 36, 44, 45],
    9: [46, 47, 45, 48, 49, 50],
    10: [51, 52, 50, 53, 54, 55],
    11: [56, 54, 57, 58, 1, 59],
    12: [58, 60, 61, 62, 6, 2],
    13: [62, 63, 64, 16, 11, 7],
    14: [65, 66, 30, 21, 17, 64],
    15: [67, 39, 35, 26, 66, 68],
    16: [48, 44, 40, 67, 68, 70],
    17: [53, 49, 70, 71, 60, 57],
    18: [71, 69, 68, 65, 63, 61],
}

# Reverse mappings for quick lookups
CORNER_TO_HEXES: Dict[int, List[int]] = {}
EDGE_TO_HEXES: Dict[int, List[int]] = {}

# Adjacent corners for each corner (for road connectivity)
CORNER_ADJACENCY: Dict[int, List[int]] = {
    0: [1, 5],
    1: [0, 2, 46],
    2: [1, 3, 27, 47],
    3: [2, 4, 6],
    4: [3, 5, 9],
    5: [0, 4],
    6: [3, 7, 49],
    7: [6, 8, 10],
    8: [7, 9, 13],
    9: [4, 8],
    10: [7, 11, 14],
    11: [10, 12, 17],
    12: [11, 13],
    13: [8, 12],
    14: [10, 15, 50],
    15: [14, 16, 18],
    16: [15, 17, 21],
    17: [11, 16],
    18: [15, 19, 22],
    19: [18, 20, 25],
    20: [19, 21],
    21: [16, 20],
    22: [18, 23, 51],
    23: [22, 24, 26],
    24: [23, 25, 29],
    25: [19, 24],
    26: [23, 27, 33],
    27: [2, 26, 28, 32, 48],
    28: [27, 29],
    29: [24, 28],
    30: [31, 33, 37],
    31: [30, 32, 36],
    32: [27, 31],
    33: [26, 30, 52],
    34: [35, 37, 39],
    35: [34, 36],
    36: [31, 35],
    37: [30, 34, 40],
    38: [39, 41, 43],
    39: [34, 38],
    40: [37, 41, 53],
    41: [38, 40, 44],
    42: [43, 45],
    43: [38, 42],
    44: [41, 45, 47],
    45: [42, 44, 46],
    46: [1, 45],
    47: [2, 44, 48],
    48: [27, 47, 49, 53],
    49: [6, 48, 50],
    50: [14, 49, 51],
    51: [22, 50, 52],
    52: [33, 51, 53],
    53: [40, 48, 52],
}

# The two corners that each edge connects
EDGE_TO_CORNERS: Dict[int, Tuple[int, int]] = {
    0: (0, 1),
    1: (1, 2),
    2: (2, 3),
    3: (3, 4),
    4: (4, 5),
    5: (5, 0),
    6: (3, 6),
    7: (6, 7),
    8: (7, 8),
    9: (8, 9),
    10: (9, 4),
    11: (7, 10),
    12: (10, 11),
    13: (11, 12),
    14: (12, 13),
    15: (13, 8),
    16: (10, 14),
    17: (14, 15),
    18: (15, 16),
    19: (16, 17),
    20: (17, 11),
    21: (15, 18),
    22: (18, 19),
    23: (19, 20),
    24: (20, 21),
    25: (21, 16),
    26: (22, 23),
    27: (23, 24),
    28: (24, 25),
    29: (25, 19),
    30: (18, 22),
    31: (26, 27),
    32: (27, 28),
    33: (28, 29),
    34: (29, 24),
    35: (23, 26),
    36: (30, 31),
    37: (31, 32),
    38: (32, 27),
    39: (26, 33),
    40: (33, 30),
    41: (34, 35),
    42: (35, 36),
    43: (36, 31),
    44: (30, 37),
    45: (37, 34),
    46: (38, 39),
    47: (39, 34),
    48: (37, 40),
    49: (40, 41),
    50: (41, 38),
    51: (42, 43),
    52: (43, 38),
    53: (41, 44),
    54: (44, 45),
    55: (45, 42),
    56: (46, 45),
    57: (44, 47),
    58: (47, 2),
    59: (1, 46),
    60: (27, 48),
    61: (48, 49),
    62: (49, 6),
    63: (49, 50),
    64: (50, 14),
    65: (50, 51),
    66: (51, 22),
    67: (52, 33),
    68: (51, 52),
    69: (53, 52),
    70: (53, 40),
    71: (53, 48),
}

# Edges that connect to each corner (derived from EDGE_TO_CORNERS)
CORNER_TO_EDGES: Dict[int, List[int]] = {}

# Port locations and types
# Edge ID -> Port Type mapping
# Standard Catan has 4x 3:1 ports and 1 of each resource port (2:1)
# We need to map the 9 ports from Excel to the correct types
# Assuming standard distribution:
PORT_EDGES: Dict[int, int] = {
    5: PORT_TYPE_3_1,      # Generic 3:1 port
    24: PORT_TYPE_WOOD,    # 2:1 Wood port
    28: PORT_TYPE_BRICK,   # 2:1 Brick port  
    42: PORT_TYPE_SHEEP,   # 2:1 Sheep port
    9: PORT_TYPE_WHEAT,    # 2:1 Wheat port
    20: PORT_TYPE_ORE,     # 2:1 Ore port
    38: PORT_TYPE_3_1,     # Generic 3:1 port
    56: PORT_TYPE_3_1,     # Generic 3:1 port
    46: PORT_TYPE_3_1,     # Generic 3:1 port
}

# Corners affected by each port (derived from PORT_EDGES and EDGE_TO_CORNERS)
PORT_CORNERS: Dict[int, int] = {}  # Will be computed from PORT_EDGES

# Standard board number arrangement (can be randomized)
# 18 numbers for non-desert hexes
STANDARD_NUMBERS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

# Standard resource distribution
# 4 wood, 3 brick, 4 sheep, 4 wheat, 3 ore, 1 desert
STANDARD_RESOURCES = [
    HEX_TYPE_WOOD, HEX_TYPE_WOOD, HEX_TYPE_WOOD, HEX_TYPE_WOOD,
    HEX_TYPE_BRICK, HEX_TYPE_BRICK, HEX_TYPE_BRICK,
    HEX_TYPE_SHEEP, HEX_TYPE_SHEEP, HEX_TYPE_SHEEP, HEX_TYPE_SHEEP,
    HEX_TYPE_WHEAT, HEX_TYPE_WHEAT, HEX_TYPE_WHEAT, HEX_TYPE_WHEAT,
    HEX_TYPE_ORE, HEX_TYPE_ORE, HEX_TYPE_ORE,
    HEX_TYPE_DESERT
]

# Standard port distribution
# 4 x 3:1 ports, 1 of each 2:1 resource port
STANDARD_PORTS = [
    PORT_TYPE_3_1, PORT_TYPE_3_1, PORT_TYPE_3_1, PORT_TYPE_3_1,
    PORT_TYPE_WOOD, PORT_TYPE_BRICK, PORT_TYPE_SHEEP, 
    PORT_TYPE_WHEAT, PORT_TYPE_ORE
]


def initialize_reverse_mappings():
    """Build reverse lookup tables from the forward mappings."""
    global CORNER_TO_HEXES, EDGE_TO_HEXES, PORT_CORNERS, CORNER_TO_EDGES
    
    # Build CORNER_TO_HEXES
    CORNER_TO_HEXES.clear()
    for hex_id, corners in HEX_TO_CORNERS.items():
        for corner in corners:
            if corner not in CORNER_TO_HEXES:
                CORNER_TO_HEXES[corner] = []
            CORNER_TO_HEXES[corner].append(hex_id)
    
    # Build EDGE_TO_HEXES
    EDGE_TO_HEXES.clear()
    for hex_id, edges in HEX_TO_EDGES.items():
        for edge in edges:
            if edge not in EDGE_TO_HEXES:
                EDGE_TO_HEXES[edge] = []
            EDGE_TO_HEXES[edge].append(hex_id)
    
    # Build CORNER_TO_EDGES from EDGE_TO_CORNERS
    CORNER_TO_EDGES.clear()
    for edge_id, (corner1, corner2) in EDGE_TO_CORNERS.items():
        if corner1 not in CORNER_TO_EDGES:
            CORNER_TO_EDGES[corner1] = []
        if corner2 not in CORNER_TO_EDGES:
            CORNER_TO_EDGES[corner2] = []
        CORNER_TO_EDGES[corner1].append(edge_id)
        CORNER_TO_EDGES[corner2].append(edge_id)
    
    # Build PORT_CORNERS from PORT_EDGES
    PORT_CORNERS.clear()
    for edge_id, port_type in PORT_EDGES.items():
        if edge_id in EDGE_TO_CORNERS:
            corner1, corner2 = EDGE_TO_CORNERS[edge_id]
            PORT_CORNERS[corner1] = port_type
            PORT_CORNERS[corner2] = port_type


def get_adjacent_hexes(hex_id: int) -> List[int]:
    """Get all hexes adjacent to the given hex."""
    adjacent = []
    
    # Find hexes that share at least 2 corners with this hex
    my_corners = set(HEX_TO_CORNERS.get(hex_id, []))
    
    for other_hex in ALL_HEX_IDS:
        if other_hex != hex_id:
            other_corners = set(HEX_TO_CORNERS.get(other_hex, []))
            if len(my_corners & other_corners) >= 2:
                adjacent.append(other_hex)
    
    return adjacent


def get_corner_hexes(corner_id: int) -> List[int]:
    """Get all hexes that touch this corner."""
    return CORNER_TO_HEXES.get(corner_id, [])


def get_edge_hexes(edge_id: int) -> List[int]:
    """Get all hexes that touch this edge."""
    return EDGE_TO_HEXES.get(edge_id, [])


def is_corner_on_coast(corner_id: int) -> bool:
    """Check if a corner is on the coast (touches fewer than 3 hexes)."""
    return len(get_corner_hexes(corner_id)) < 3


def is_edge_on_coast(edge_id: int) -> bool:
    """Check if an edge is on the coast (touches only 1 hex)."""
    return len(get_edge_hexes(edge_id)) == 1


def get_connected_edges(corner_id: int) -> List[int]:
    """Get all edges connected to a corner."""
    return CORNER_TO_EDGES.get(corner_id, [])


def get_adjacent_corners(corner_id: int) -> List[int]:
    """Get all corners adjacent to this corner (connected by an edge)."""
    return CORNER_ADJACENCY.get(corner_id, [])


def can_build_settlement(corner_id: int, occupied_corners: Set[int]) -> bool:
    """
    Check if a settlement can be built at this corner.
    
    Rules:
    - Corner must be unoccupied
    - No settlements on adjacent corners (distance rule)
    """
    if corner_id in occupied_corners:
        return False
    
    # Check distance rule
    for adjacent in get_adjacent_corners(corner_id):
        if adjacent in occupied_corners:
            return False
    
    return True


def can_build_road(edge_id: int, player_roads: Set[int], player_buildings: Set[int]) -> bool:
    """
    Check if a road can be built on this edge.
    
    Rules:
    - Edge must be unoccupied
    - Must connect to player's existing road or building
    """
    corner1, corner2 = EDGE_TO_CORNERS.get(edge_id, (-1, -1))
    
    # Check if connected to a building
    if corner1 in player_buildings or corner2 in player_buildings:
        return True
    
    # Check if connected to existing roads
    for corner in [corner1, corner2]:
        for edge in get_connected_edges(corner):
            if edge != edge_id and edge in player_roads:
                return True
    
    return False


def get_port_for_corner(corner_id: int) -> Optional[int]:
    """Get the port type for a corner, if any."""
    return PORT_CORNERS.get(corner_id)


# Initialize reverse mappings when module is imported
# (This will be called after Excel data is loaded)
# initialize_reverse_mappings()

# Initialize all reverse mappings when module loads
initialize_reverse_mappings()
