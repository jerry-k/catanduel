/**
 * Board rendering functions for CatanDuel.
 * Handles SVG rendering of the game board.
 */

// Board dimensions
const BOARD_WIDTH = 800;
const BOARD_HEIGHT = 700;
const HEX_SIZE = 60;
const HEX_WIDTH = HEX_SIZE * Math.sqrt(3);
const HEX_HEIGHT = HEX_SIZE * 2;

// Hex positions based on colonist.io layout
const HEX_POSITIONS = {
    // Row 1 (top)
    0:  {x: 296, y: 170},
    11: {x: 400, y: 170},
    10: {x: 504, y: 170},
    
    // Row 2
    1:  {x: 244, y: 260},
    12: {x: 348, y: 260},
    17: {x: 452, y: 260},
    9:  {x: 556, y: 260},
    
    // Row 3 (middle)
    2:  {x: 192, y: 350},
    13: {x: 296, y: 350},
    18: {x: 400, y: 350},  // Center hex
    16: {x: 504, y: 350},
    8:  {x: 608, y: 350},
    
    // Row 4
    3:  {x: 244, y: 440},
    14: {x: 348, y: 440},
    15: {x: 452, y: 440},
    7:  {x: 556, y: 440},
    
    // Row 5 (bottom)
    4:  {x: 296, y: 530},
    5:  {x: 400, y: 530},
    6:  {x: 504, y: 530},
};

// Hex type colors
const HEX_COLORS = {
    'forest': '#228B22',
    'hills': '#BC4A3C',
    'pasture': '#90EE90',
    'fields': '#F4A460',
    'mountains': '#696969',
    'desert': '#F4E4C1'
};

// Resource emojis
const RESOURCE_EMOJI = {
    'forest': '🪵',
    'hills': '🧱',
    'pasture': '🐑',
    'fields': '🌾',
    'mountains': '⛰️'
};

// Main board rendering function
function renderBoard() {
    if (!gameState || !gameState.board) return;
    
    const board = gameState.board;
    
    // Clear existing board
    clearBoard();
    
    // Draw hexes
    drawHexes(board.hexes);
    
    // Draw ports
    drawPorts(board.ports);
    
    // Draw edges (for roads)
    drawEdges();
    
    // Draw corners (for settlements/cities)
    drawCorners();
    
    // Draw buildings
    drawBuildings(board.buildings);
    
    // Draw robber
    drawRobber(board.robber_hex);
    
    // Draw numbers
    drawNumbers(board.hexes);
}

// Clear all board elements
function clearBoard() {
    document.getElementById('hexes').innerHTML = '';
    document.getElementById('edges').innerHTML = '';
    document.getElementById('corners').innerHTML = '';
    document.getElementById('buildings').innerHTML = '';
    document.getElementById('robber').innerHTML = '';
    document.getElementById('numbers').innerHTML = '';
    document.getElementById('ports').innerHTML = '';
}

// Draw hexagon tiles
function drawHexes(hexes) {
    const hexGroup = document.getElementById('hexes');
    
    for (const hex of hexes) {
        const pos = HEX_POSITIONS[hex.id];
        if (!pos) continue;
        
        const hexElement = createHexagon(pos.x, pos.y, HEX_SIZE, HEX_COLORS[hex.type]);
        hexElement.setAttribute('data-hex-id', hex.id);
        hexElement.onclick = () => handleHexClick(hex.id);
        
        hexGroup.appendChild(hexElement);
    }
}

// Create hexagon SVG element
function createHexagon(cx, cy, size, color) {
    const points = [];
    for (let i = 0; i < 6; i++) {
        const angle = (Math.PI / 3) * i;
        const x = cx + size * Math.cos(angle);
        const y = cy + size * Math.sin(angle);
        points.push(`${x},${y}`);
    }
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', points.join(' '));
    polygon.setAttribute('fill', color);
    polygon.setAttribute('stroke', '#000');
    polygon.setAttribute('stroke-width', '2');
    polygon.classList.add('hex');
    
    return polygon;
}

// Draw number tokens
function drawNumbers(hexes) {
    const numberGroup = document.getElementById('numbers');
    
    for (const hex of hexes) {
        if (hex.number && hex.type !== 'desert') {
            const pos = HEX_POSITIONS[hex.id];
            if (!pos) continue;
            
            // Background circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x);
            circle.setAttribute('cy', pos.y);
            circle.setAttribute('r', '20');
            circle.setAttribute('fill', '#FFF');
            circle.setAttribute('stroke', '#000');
            circle.setAttribute('stroke-width', '2');
            
            // Number text
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', pos.x);
            text.setAttribute('y', pos.y + 7);
            text.setAttribute('text-anchor', 'middle');
            text.classList.add('hex-number');
            if (hex.number === 6 || hex.number === 8) {
                text.classList.add('red-number');
            }
            text.textContent = hex.number;
            
            numberGroup.appendChild(circle);
            numberGroup.appendChild(text);
        }
    }
}

// Draw edges for road placement
function drawEdges() {
    const edgeGroup = document.getElementById('edges');
    
    // For now, create invisible clickable areas for edges
    // In a full implementation, we'd calculate all 72 edge positions
    // based on the colonist.io coordinate system
}

// Draw corners for settlement/city placement
function drawCorners() {
    const cornerGroup = document.getElementById('corners');
    
    // For now, create invisible clickable areas for corners
    // In a full implementation, we'd calculate all 54 corner positions
    // based on the colonist.io coordinate system
}

// Draw buildings (settlements, cities, roads)
function drawBuildings(buildings) {
    const buildingGroup = document.getElementById('buildings');
    
    for (const building of buildings) {
        if (building.type === 'settlement') {
            drawSettlement(building.location, building.player);
        } else if (building.type === 'city') {
            drawCity(building.location, building.player);
        } else if (building.type === 'road') {
            drawRoad(building.location, building.player);
        }
    }
}

// Draw settlement
function drawSettlement(cornerId, playerId) {
    const buildingGroup = document.getElementById('buildings');
    
    // Calculate position based on corner ID
    // For now, use a simple offset from center
    const pos = getCornerPosition(cornerId);
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('transform', `translate(${pos.x}, ${pos.y})`);
    
    // House shape
    const house = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    house.setAttribute('points', '-10,5 0,-10 10,5 10,15 -10,15');
    house.setAttribute('fill', playerId === 0 ? '#CC0000' : '#0066CC');
    house.setAttribute('stroke', '#000');
    house.setAttribute('stroke-width', '2');
    
    g.appendChild(house);
    buildingGroup.appendChild(g);
}

// Draw city
function drawCity(cornerId, playerId) {
    const buildingGroup = document.getElementById('buildings');
    
    const pos = getCornerPosition(cornerId);
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('transform', `translate(${pos.x}, ${pos.y})`);
    
    // City shape (larger house)
    const city = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    city.setAttribute('points', '-15,8 0,-15 15,8 15,20 -15,20');
    city.setAttribute('fill', playerId === 0 ? '#CC0000' : '#0066CC');
    city.setAttribute('stroke', '#000');
    city.setAttribute('stroke-width', '2');
    
    g.appendChild(city);
    buildingGroup.appendChild(g);
}

// Draw road
function drawRoad(edgeId, playerId) {
    const buildingGroup = document.getElementById('buildings');
    
    // Calculate position based on edge ID
    const pos = getEdgePosition(edgeId);
    
    const road = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    road.setAttribute('x', pos.x - 20);
    road.setAttribute('y', pos.y - 4);
    road.setAttribute('width', '40');
    road.setAttribute('height', '8');
    road.setAttribute('fill', playerId === 0 ? '#CC0000' : '#0066CC');
    road.setAttribute('stroke', '#000');
    road.setAttribute('stroke-width', '1');
    road.setAttribute('rx', '4');
    
    buildingGroup.appendChild(road);
}

// Draw robber
function drawRobber(hexId) {
    const robberGroup = document.getElementById('robber');
    const pos = HEX_POSITIONS[hexId];
    if (!pos) return;
    
    const robber = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    robber.setAttribute('cx', pos.x);
    robber.setAttribute('cy', pos.y);
    robber.setAttribute('r', '25');
    robber.setAttribute('fill', '#000');
    robber.setAttribute('opacity', '0.7');
    
    robberGroup.appendChild(robber);
}

// Draw ports
function drawPorts(ports) {
    const portGroup = document.getElementById('ports');
    
    for (const port of ports) {
        // Draw port indicator at edge position
        const pos = getEdgePosition(port.edge_id);
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', '15');
        circle.setAttribute('fill', '#FFD700');
        circle.setAttribute('stroke', '#000');
        circle.setAttribute('stroke-width', '2');
        
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pos.x);
        text.setAttribute('y', pos.y + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '12');
        text.textContent = port.type;
        
        portGroup.appendChild(circle);
        portGroup.appendChild(text);
    }
}

// Position calculation functions (simplified for now)
function getCornerPosition(cornerId) {
    // This should use the actual colonist.io coordinate mappings
    // For now, return a position based on corner ID
    const angle = (cornerId / 54) * Math.PI * 2;
    const radius = 200;
    return {
        x: 400 + radius * Math.cos(angle),
        y: 350 + radius * Math.sin(angle)
    };
}

function getEdgePosition(edgeId) {
    // This should use the actual colonist.io coordinate mappings
    // For now, return a position based on edge ID
    const angle = (edgeId / 72) * Math.PI * 2;
    const radius = 250;
    return {
        x: 400 + radius * Math.cos(angle),
        y: 350 + radius * Math.sin(angle)
    };
}

// Highlight functions for building mode
function highlightValidSettlementSpots() {
    // Highlight corners where settlements can be built
    clearHighlights();
    
    const validActions = gameState.valid_actions.filter(a => 
        a.type === 'BUILD_SETTLEMENT' || a.type === 'BUILD_INITIAL_SETTLEMENT'
    );
    
    for (const action of validActions) {
        if (action.data.corner !== undefined) {
            highlightCorner(action.data.corner);
        }
    }
}

function highlightValidRoadSpots() {
    // Highlight edges where roads can be built
    clearHighlights();
    
    const validActions = gameState.valid_actions.filter(a => 
        a.type === 'BUILD_ROAD' || a.type === 'BUILD_INITIAL_ROAD'
    );
    
    for (const action of validActions) {
        if (action.data.edge !== undefined) {
            highlightEdge(action.data.edge);
        }
    }
}

function highlightValidCitySpots() {
    // Highlight corners where cities can be built
    clearHighlights();
    
    const validActions = gameState.valid_actions.filter(a => a.type === 'BUILD_CITY');
    
    for (const action of validActions) {
        if (action.data.corner !== undefined) {
            highlightCorner(action.data.corner);
        }
    }
}

function highlightCorner(cornerId) {
    const cornerGroup = document.getElementById('corners');
    const pos = getCornerPosition(cornerId);
    
    const highlight = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    highlight.setAttribute('cx', pos.x);
    highlight.setAttribute('cy', pos.y);
    highlight.setAttribute('r', '15');
    highlight.setAttribute('fill', '#FFD700');
    highlight.setAttribute('opacity', '0.5');
    highlight.classList.add('building', 'valid-spot');
    highlight.onclick = () => handleBoardClick('corner', cornerId);
    
    cornerGroup.appendChild(highlight);
}

function highlightEdge(edgeId) {
    const edgeGroup = document.getElementById('edges');
    const pos = getEdgePosition(edgeId);
    
    const highlight = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    highlight.setAttribute('x', pos.x - 25);
    highlight.setAttribute('y', pos.y - 10);
    highlight.setAttribute('width', '50');
    highlight.setAttribute('height', '20');
    highlight.setAttribute('fill', '#FFD700');
    highlight.setAttribute('opacity', '0.5');
    highlight.classList.add('building', 'valid-spot');
    highlight.onclick = () => handleBoardClick('edge', edgeId);
    
    edgeGroup.appendChild(highlight);
}

function clearHighlights() {
    // Remove all highlight elements
    const highlights = document.querySelectorAll('.valid-spot');
    highlights.forEach(h => h.remove());
}

// Click handlers
function handleHexClick(hexId) {
    if (gameState.phase === 'robber') {
        handleRobberPlacement(hexId);
    }
}

// Get players on a hex
function getPlayersOnHex(hexId) {
    const players = [];
    const buildings = gameState.board.buildings;
    
    // Check each building to see if it's on this hex
    // This requires the full coordinate mapping implementation
    
    return players;
}