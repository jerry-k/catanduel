# Coordinate Mapping Documentation

## Overview
This document details the mapping between colonist.io coordinate IDs and pixel positions for SVG rendering.

## Hex Layout

Colonist.io hex arrangement (19 hexes):
```
      0   11   10
    1  12  17   9
  2  13  18  16  8  
    3  14  15  7
      4   5   6
```

## SVG Coordinate System

- Origin: Top-left corner (0, 0)
- Board center: (400, 350) for 800x700 viewport
- Hex size: 60px from center to vertex
- Hex spacing: 104px horizontal, 90px vertical

## Hex Pixel Positions

Based on a hex size of 60px and board center at (400, 350):

```python
HEX_POSITIONS = {
    # Row 1 (top)
    0:  {'x': 296, 'y': 170},
    11: {'x': 400, 'y': 170},
    10: {'x': 504, 'y': 170},
    
    # Row 2
    1:  {'x': 244, 'y': 260},
    12: {'x': 348, 'y': 260},
    17: {'x': 452, 'y': 260},
    9:  {'x': 556, 'y': 260},
    
    # Row 3 (middle)
    2:  {'x': 192, 'y': 350},
    13: {'x': 296, 'y': 350},
    18: {'x': 400, 'y': 350},  # Center hex
    16: {'x': 504, 'y': 350},
    8:  {'x': 608, 'y': 350},
    
    # Row 4
    3:  {'x': 244, 'y': 440},
    14: {'x': 348, 'y': 440},
    15: {'x': 452, 'y': 440},
    7:  {'x': 556, 'y': 440},
    
    # Row 5 (bottom)
    4:  {'x': 296, 'y': 530},
    5:  {'x': 400, 'y': 530},
    6:  {'x': 504, 'y': 530},
}
```

## Corner Positions

Corners are the vertices of hexagons. Each hex has 6 corners (clockwise from top):
- Top: (x, y - 60)
- Top-right: (x + 52, y - 30)
- Bottom-right: (x + 52, y + 30)
- Bottom: (x, y + 60)
- Bottom-left: (x - 52, y + 30)
- Top-left: (x - 52, y - 30)

## Edge Positions

Edges connect two corners. Position is the midpoint between the two corners.

## Port Locations

Ports are positioned on coastal edges:

```python
PORT_EDGE_POSITIONS = {
    5: {'x': 244, 'y': 110},   # Top-left 3:1
    9: {'x': 140, 'y': 290},   # Left wheat
    20: {'x': 140, 'y': 470},  # Left ore
    24: {'x': 296, 'y': 590},  # Bottom wood
    28: {'x': 504, 'y': 590},  # Bottom brick
    38: {'x': 660, 'y': 470},  # Right 3:1
    42: {'x': 660, 'y': 290},  # Right sheep
    46: {'x': 556, 'y': 110},  # Top-right 3:1
    56: {'x': 400, 'y': 110},  # Top 3:1
}
```

## Number Token Positions

Number tokens are centered on hexes:
- 6 and 8: Red color (#CC0000)
- Others: Black color (#000000)
- Font size: 24px
- Background: White circle with 20px radius

## Building Placement

### Settlements/Cities
- Placed at corner positions
- Size: 20x20px for settlements, 24x24px for cities
- Centered on corner point

### Roads
- Drawn as lines between corner positions
- Width: 8px
- Length: Calculated from corner distance
- Rotation: Calculated from corner angle

## Robber
- Size: 30x40px
- Placed at hex center
- Black color with slight transparency

## Conversion Functions

```javascript
// Get pixel position for a hex
function getHexPosition(hexId) {
    return HEX_POSITIONS[hexId];
}

// Get pixel position for a corner
function getCornerPosition(cornerId) {
    // Use colonist_map.py HEX_TO_CORNERS to find hex
    // Calculate based on hex position and corner index
}

// Get pixel position for an edge
function getEdgePosition(edgeId) {
    // Use colonist_map.py EDGE_TO_CORNERS
    // Return midpoint between two corners
}
```

## Click Detection

For detecting clicks on board elements:
1. Hexes: Point-in-hexagon test
2. Corners: Distance < 15px from corner position
3. Edges: Distance < 10px from edge line

## Animation Coordinates

For smooth animations:
- Resource collection: From hex center to player panel
- Building placement: Fade in at position
- Robber movement: Slide from old hex to new hex
- Dice roll: Center of board

## Responsive Scaling

For different screen sizes:
- Calculate scale factor: `min(width/800, height/700)`
- Apply to all positions and sizes
- Maintain aspect ratio