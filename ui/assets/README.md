# Game Assets

This directory contains SVG assets for the CatanDuel UI.

## Asset Categories

### /cards/
Development card images:
- knight.svg - Knight card
- victory_point.svg - Victory point card
- road_building.svg - Road building card
- year_of_plenty.svg - Year of plenty card
- monopoly.svg - Monopoly card

### /buildings/
Building pieces in different colors:
- settlement_red.svg - Red settlement
- settlement_blue.svg - Blue settlement
- city_red.svg - Red city
- city_blue.svg - Blue city
- road_red.svg - Red road
- road_blue.svg - Blue road

### /dice/
Dice faces:
- die_1.svg through die_6.svg

### /icons/
UI and resource icons:
- wood.svg - Wood/lumber resource
- brick.svg - Brick/clay resource
- sheep.svg - Sheep/wool resource
- wheat.svg - Wheat/grain resource
- ore.svg - Ore/stone resource
- robber.svg - Robber piece
- port_3_1.svg - 3:1 port
- port_wood.svg - 2:1 wood port
- port_brick.svg - 2:1 brick port
- port_sheep.svg - 2:1 sheep port
- port_wheat.svg - 2:1 wheat port
- port_ore.svg - 2:1 ore port

## Placeholder Status

Currently these are placeholder references. Actual SVG files need to be:
1. Created from scratch, or
2. Copied from rlcatan (if available), or
3. Generated using an SVG creation tool

## SVG Guidelines

- Use viewBox for scalability
- Keep file sizes small
- Use consistent color scheme:
  - Red: #CC0000
  - Blue: #0066CC
  - Wood: #8B4513
  - Brick: #BC4A3C
  - Sheep: #90EE90
  - Wheat: #F4A460
  - Ore: #696969

## Example SVG Structure

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="#CC0000"/>
</svg>
```