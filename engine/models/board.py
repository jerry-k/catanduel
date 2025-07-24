"""
Board state management for CatanDuel.

Adapted from catanatron's board.py but using colonist.io coordinate system.
Tracks buildings, roads, and robber position.
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import random

from engine.models.enums import (
    SETTLEMENT, CITY, ROAD,
    PLAYER_0, PLAYER_1,
    HEX_TYPE_DESERT
)
from engine.colonist_map import (
    HEX_TO_CORNERS, HEX_TO_EDGES,
    CORNER_ADJACENCY, EDGE_TO_CORNERS,
    get_corner_hexes, get_connected_edges,
    can_build_settlement as map_can_build_settlement,
    can_build_road as map_can_build_road,
    is_edge_on_coast, get_adjacent_hexes,
    ALL_HEX_IDS
)


class Board:
    """
    Manages the physical board state.
    
    Tracks:
    - Buildings (settlements and cities)
    - Roads
    - Robber position
    - Longest road calculation
    """
    
    def __init__(self):
        """Initialize an empty board."""
        # Buildings: corner_id -> (player_id, building_type)
        self.buildings: Dict[int, Tuple[int, int]] = {}
        
        # Roads: edge_id -> player_id
        self.roads: Dict[int, int] = {}
        
        # Robber position (hex_id)
        self.robber_hex: int = 0  # Will be set to desert during board generation
        
        # Cache for longest road calculation
        # player_id -> List[Set[corner_ids]] (connected components)
        self.connected_components: Dict[int, List[Set[int]]] = {
            PLAYER_0: [],
            PLAYER_1: []
        }
        
        # Longest road tracking
        self.longest_road_player: Optional[int] = None
        self.longest_road_length: int = 0
        
    def copy(self):
        """Create a deep copy of the board state."""
        new_board = Board()
        new_board.buildings = self.buildings.copy()
        new_board.roads = self.roads.copy()
        new_board.robber_hex = self.robber_hex
        
        # Deep copy connected components
        new_board.connected_components = {
            player: [component.copy() for component in components]
            for player, components in self.connected_components.items()
        }
        
        new_board.longest_road_player = self.longest_road_player
        new_board.longest_road_length = self.longest_road_length
        
        return new_board
    
    def place_initial_settlement(self, player_id: int, corner_id: int):
        """
        Place a settlement during initial setup phase.
        
        No distance or connectivity checks during setup.
        """
        if corner_id in self.buildings:
            raise ValueError(f"Corner {corner_id} already occupied")
        
        self.buildings[corner_id] = (player_id, SETTLEMENT)
        
    def place_initial_road(self, player_id: int, edge_id: int):
        """
        Place a road during initial setup phase.
        
        Must connect to player's most recently placed settlement.
        """
        if edge_id in self.roads:
            raise ValueError(f"Edge {edge_id} already has a road")
        
        # Check connection to a settlement
        corner1, corner2 = EDGE_TO_CORNERS[edge_id]
        connected = False
        
        for corner in [corner1, corner2]:
            if corner in self.buildings:
                building_player, building_type = self.buildings[corner]
                if building_player == player_id:
                    connected = True
                    break
        
        if not connected:
            raise ValueError(f"Road at edge {edge_id} must connect to your settlement")
        
        self.roads[edge_id] = player_id
        self._update_longest_road()
    
    def can_build_settlement(self, player_id: int, corner_id: int) -> bool:
        """
        Check if a settlement can be built at this corner.
        
        Requirements:
        - Corner is unoccupied
        - No adjacent settlements (distance rule)
        - Connected to player's road network
        """
        # Check basic map constraints
        if not map_can_build_settlement(corner_id, set(self.buildings.keys())):
            return False
        
        # Check road connection
        for edge_id in get_connected_edges(corner_id):
            if edge_id in self.roads and self.roads[edge_id] == player_id:
                return True
        
        return False
    
    def build_settlement(self, player_id: int, corner_id: int):
        """Build a settlement (after initial phase)."""
        if not self.can_build_settlement(player_id, corner_id):
            raise ValueError(f"Cannot build settlement at corner {corner_id}")
        
        self.buildings[corner_id] = (player_id, SETTLEMENT)
        self._update_longest_road()  # Settlements can break opponent's roads
    
    def can_build_city(self, player_id: int, corner_id: int) -> bool:
        """Check if a city can be built at this corner."""
        if corner_id not in self.buildings:
            return False
        
        building_player, building_type = self.buildings[corner_id]
        return building_player == player_id and building_type == SETTLEMENT
    
    def build_city(self, player_id: int, corner_id: int):
        """Upgrade a settlement to a city."""
        if not self.can_build_city(player_id, corner_id):
            raise ValueError(f"Cannot build city at corner {corner_id}")
        
        self.buildings[corner_id] = (player_id, CITY)
    
    def can_build_road(self, player_id: int, edge_id: int) -> bool:
        """
        Check if a road can be built on this edge.
        
        Requirements:
        - Edge is unoccupied
        - Connects to player's road network or building
        - Cannot pass through opponent's settlements/cities
        """
        if edge_id in self.roads:
            return False
        
        # Get player's buildings and roads
        player_buildings = {
            corner for corner, (p, _) in self.buildings.items()
            if p == player_id
        }
        player_roads = {
            edge for edge, p in self.roads.items()
            if p == player_id
        }
        
        return map_can_build_road(edge_id, player_roads, player_buildings, self.buildings)
    
    def build_road(self, player_id: int, edge_id: int):
        """Build a road."""
        if not self.can_build_road(player_id, edge_id):
            raise ValueError(f"Cannot build road at edge {edge_id}")
        
        self.roads[edge_id] = player_id
        self._update_longest_road()
    
    def move_robber(self, hex_id: int):
        """Move the robber to a new hex."""
        if hex_id == self.robber_hex:
            raise ValueError("Must move robber to a different hex")
        
        self.robber_hex = hex_id
    
    def get_buildings_on_hex(self, hex_id: int) -> List[Tuple[int, int, int]]:
        """
        Get all buildings on a hex.
        
        Returns:
            List of (corner_id, player_id, building_type)
        """
        buildings = []
        for corner_id in HEX_TO_CORNERS[hex_id]:
            if corner_id in self.buildings:
                player_id, building_type = self.buildings[corner_id]
                buildings.append((corner_id, player_id, building_type))
        return buildings
    
    def get_players_on_hex(self, hex_id: int) -> Set[int]:
        """Get all players with buildings on a hex."""
        players = set()
        for _, player_id, _ in self.get_buildings_on_hex(hex_id):
            players.add(player_id)
        return players
    
    def get_player_buildings(self, player_id: int) -> Dict[int, List[int]]:
        """
        Get all buildings owned by a player.
        
        Returns:
            Dict mapping building_type to list of corner_ids
        """
        settlements = []
        cities = []
        
        for corner_id, (owner, building_type) in self.buildings.items():
            if owner == player_id:
                if building_type == SETTLEMENT:
                    settlements.append(corner_id)
                else:  # CITY
                    cities.append(corner_id)
        
        return {
            SETTLEMENT: settlements,
            CITY: cities
        }
    
    def get_player_roads(self, player_id: int) -> List[int]:
        """Get all roads owned by a player."""
        return [edge_id for edge_id, owner in self.roads.items() if owner == player_id]
    
    def get_player_road_length(self, player_id: int) -> int:
        """
        Calculate the longest road length for a specific player.
        
        Args:
            player_id: The player ID (0 or 1)
            
        Returns:
            The length of the player's longest road
        """
        # Build adjacency graph for this player's roads
        road_graph = defaultdict(set)
        player_roads = self.get_player_roads(player_id)
        
        for edge_id in player_roads:
            corner1, corner2 = EDGE_TO_CORNERS[edge_id]
            
            # Check if path is blocked by opponent's building
            # Player's own settlements do NOT block their roads
            blocked1 = self._is_corner_blocked(corner1, player_id)
            blocked2 = self._is_corner_blocked(corner2, player_id)
            
            # Always add bidirectional connections for the player's own roads
            # Opponent settlements block the path at that corner
            if not blocked1 and not blocked2:
                # Both corners are free or have player's own buildings
                road_graph[corner1].add(corner2)
                road_graph[corner2].add(corner1)
            elif not blocked1 and blocked2:
                # corner2 is blocked by opponent, so it's a dead end
                road_graph[corner1].add(corner2)
                # Note: we don't add the reverse connection from corner2
            elif blocked1 and not blocked2:
                # corner1 is blocked by opponent, so it's a dead end
                road_graph[corner2].add(corner1)
                # Note: we don't add the reverse connection from corner1
            # If both blocked by opponents, road doesn't contribute
        
        # Find longest path in the graph
        return self._find_longest_path(road_graph)
    
    def _update_longest_road(self):
        """
        Recalculate longest road for both players.
        
        This uses a graph traversal approach to find the longest
        path in each player's road network.
        """
        for player_id in [PLAYER_0, PLAYER_1]:
            # Get longest path for this player
            longest = self.get_player_road_length(player_id)
            
            # Update longest road if this player has 5+ and is longest
            if longest >= 5:
                if (self.longest_road_player is None or 
                    longest > self.longest_road_length or
                    (longest == self.longest_road_length and self.longest_road_player != player_id)):
                    self.longest_road_player = player_id
                    self.longest_road_length = longest
    
    def _is_corner_blocked(self, corner_id: int, player_id: int) -> bool:
        """Check if a corner blocks road continuation for a player."""
        if corner_id not in self.buildings:
            return False
        
        building_player, _ = self.buildings[corner_id]
        return building_player != player_id
    
    def _find_longest_path(self, graph: Dict[int, Set[int]]) -> int:
        """
        Find the longest path in an undirected graph.
        
        In Catan, the longest road allows revisiting corners but not edges.
        Uses DFS tracking visited edges instead of visited nodes.
        """
        if not graph:
            return 0
        
        def dfs(node: int, visited_edges: Set[Tuple[int, int]]) -> int:
            """DFS that tracks visited edges instead of nodes."""
            max_length = 0
            
            for neighbor in graph[node]:
                # Create edge tuple (smaller_id, larger_id) for consistency
                edge = (min(node, neighbor), max(node, neighbor))
                
                if edge not in visited_edges:
                    visited_edges.add(edge)
                    length = 1 + dfs(neighbor, visited_edges)
                    max_length = max(max_length, length)
                    visited_edges.remove(edge)
            
            return max_length
        
        # Try starting from each node
        max_path = 0
        for start_node in list(graph.keys()):
            path_length = dfs(start_node, set())
            max_path = max(max_path, path_length)
        
        return max_path
    
    def get_valid_robber_hexes(self) -> List[int]:
        """Get all hexes where the robber can be placed (not current position)."""
        return [hex_id for hex_id in ALL_HEX_IDS if hex_id != self.robber_hex]
    
    def get_coast_corners(self) -> List[int]:
        """Get all corners on the coast (for initial settlement placement)."""
        coast_corners = []
        for corner_id in range(54):  # All corners
            hex_count = len(get_corner_hexes(corner_id))
            if hex_count < 3:  # Coast corners touch fewer than 3 hexes
                coast_corners.append(corner_id)
        return coast_corners