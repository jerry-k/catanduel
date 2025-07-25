# Game Log Events Plan

This document outlines all the events that should be tracked in the game log, following the style of colonist.io.

## Setup Phase Events

1. **Settlement Placement**
   - Format: `{Player} placed a settlement`
   - Example: `Blue placed a settlement`

2. **Road Placement**
   - Format: `{Player} placed a road`
   - Example: `Blue placed a road`

3. **Starting Resources**
   - Format: `{Player} received starting resources {resources}`
   - Example: `Blue received starting resources Ore Ore Brick`
   - Note: Resources should be shown as icons/images in the actual implementation

## Regular Turn Events

4. **Dice Roll**
   - Format: `{Player} rolled {total}`
   - Example: `Red rolled 8`

5. **Resource Production**
   - Format: `{Player} got {resource}`
   - Example: `Blue got Wood`
   - Note: Show resource icon instead of text

7. **Robber Blocking Production**
   - Format: `{Player} rolled {number}. {number} is blocked by robber. No resources produced`
   - Example: `Red rolled 5. 5 is blocked by robber. No resources produced`

## Building Events

8. **Road Building**
   - Format: `{Player} built a road`
   - Example: `Red built a road`
   - Note: Show road icon

9. **Settlement Building**
   - Format: `{Player} built a settlement`
   - Example: `Blue built a settlement`
   - Note: Show settlement icon

10. **City Upgrade**
    - Format: `{Player} built a city`
    - Example: `Red built a city`
    - Note: Show city icon

## Trading Events
- Note: Show the resource icons instead of resource names. So if we have Red gave bank Wheat Wheat Wheat, then it's Red gave bank Wheat_resource_svg Wheat_resource_svg Wheat_resource_svg.

11. **Maritime Trade (4:1)**
    - Format: `{Player} gave bank {resources} and took {resource}`
    - Example: `Red gave bank Wheat Wheat Wheat Wheat and took Brick`

12. **Port Trade (2:1)**
    - Format: `{Player} gave bank {resources} and took {resource}`
    - Example: `Blue gave bank Ore Ore and took Wood`

13. **3:1 Port Trade**
    - Format: `{Player} gave bank {resources} and took {resource}`
    - Example: `Red gave bank Sheep Sheep Sheep for Ore`

## Development Card Events

14. **Buying Dev Card**
    - Format: `{Player} bought {devcard}`
    - Example: `Blue bought devcard`
    - Note: Show devcard icon instead of devcard text.

15. **Playing Knight**
    - Format: `{Player} played Knight`
    - Example: `Red played Knight`

16. **Playing Road Building**
    - Format: `{Player} played Road Building`
    - Example: `Blue played Road Building`

17. **Playing Year of Plenty**
    - Format: `{Player} played Year of Plenty and took {resource} {resource}`
    - Example: `Red played Year of Plenty and took brick brick`
    - Note: The resources are the icons, not text

18. **Playing Monopoly**
    - Format: `{Player} played Monopoly and took {number} {resource}`
    - Example: `Blue played Monopoly and took 3 Wheat`
    - Note: The resource is an icon

## Robber Events

19. **Seven Rolled**
    - Format: `{Player} rolled 7`
    - Example: `Red rolled 7`

20. **Discarding**
    - Format: `{Player} discarded {resources}`
    - Example: `Blue discarded Wheat Wheat Wheat Ore`
    - Note: Use resource icons instead of resource names

21. **Friendly Robber Active**
    - Format: `Friendly robber is active. Tiles available to block are limited`
    - Example: `Friendly robber is active. Tiles available to block are limited`

22. **Moving Robber**
    - Format: `{Player} moved robber`
    - Example: `Red moved robber`

23. **Stealing Resource**
    - Format: `{Player} stole from {Player}`
    - Example: `Blue stole from Red`

24. **No One to Steal From**
    - Format: `No player to steal from`
    - Example: `No player to steal from`

## Achievement Events

25. **Longest Road**
    - Is not included in the game log

26. **Largest Army**
    - Is not included in the game log
## Game End Events

27. **Victory**
    - Format: `{Player} has won!`
    - Example: `Red has won!`

## Implementation Notes

- Resources should be displayed as icons/images, not text
- Buildings (road, settlement, city) should be displayed as icons
- Player names should be colored (Red/Black)
- Each log entry should have appropriate coloring based on the player
- Keep messages concise and consistent with colonist.io style
- No need for "turn started" or "turn ended" messages
- No need to show victory point updates in the log