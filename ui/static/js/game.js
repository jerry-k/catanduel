// Game constants
const GAME_CONSTANTS = {
    CARDS_BEFORE_DISCARD: 8,
    VICTORY_POINTS_TO_WIN: 10,
    RESOURCE_PATHS: {
        '0': '/assets/card_brick.5950ea07a7ea01bc54a5.svg',
        '1': '/assets/card_grain.09c9d82146a64bce69b5.svg',
        '2': '/assets/card_lumber.cf22f8083cf89c2a29e7.svg',
        '3': '/assets/card_ore.117f64dab28e1c987958.svg',
        '4': '/assets/card_wool.17a6dea8d559949f0ccc.svg'
    },
    BUILDING_ASSETS: {
        settlement: {
            '0': '/assets/settlement_red.22949197b57f9cfd968b.svg',
            '1': '/assets/settlement_blue.bad4cdb43d65c329deda.svg'
        },
        city: {
            '0': '/assets/city_red.991ae0c7a0b95da9811d.svg',
            '1': '/assets/city_black.7d1ff2a9a5057982225b.svg'
        },
        road: {
            '0': '/assets/road_red.41c6cbd9278108542715.svg',
            '1': '/assets/road_blue.3301e2eed15cae5a6a05.svg'
        }
    }
};

// Game state variables
let gameId = null;
let gameState = null;
let legalActions = [];
let selectedAction = null;

// Hex layout constants
const HEX_SIZE = 55;
const BOARD_CENTER_X = 450;
const BOARD_CENTER_Y = 325;

// Hex positions using colonist.io coordinate system (3,4,5,4,3 rows)
const HEX_POSITIONS = {
    // Top row (3 hexes)
    0: {x: 0, y: -2},     // 0
    11: {x: 1, y: -2},    // 11  
    10: {x: 2, y: -2},    // 10
    
    // Second row (4 hexes)
    1: {x: -1, y: -1},    // 1
    12: {x: 0, y: -1},    // 12
    17: {x: 1, y: -1},    // 17
    9: {x: 2, y: -1},     // 9
    
    // Middle row (5 hexes)
    2: {x: -2, y: 0},     // 2
    13: {x: -1, y: 0},    // 13
    18: {x: 0, y: 0},     // 18 (center)
    16: {x: 1, y: 0},     // 16
    8: {x: 2, y: 0},      // 8
    
    // Fourth row (4 hexes)
    3: {x: -2, y: 1},     // 3
    14: {x: -1, y: 1},    // 14
    15: {x: 0, y: 1},     // 15
    7: {x: 1, y: 1},      // 7
    
    // Bottom row (3 hexes)
    4: {x: -2, y: 2},     // 4
    5: {x: -1, y: 2},     // 5
    6: {x: 0, y: 2}       // 6
};

// Convert hex coordinates to pixel coordinates for pointy-top hexagons
function hexToPixel(hexX, hexY) {
    // For pointy-top hexagons in axial coordinates:
    // - Convert axial (x,y) to pixel coordinates with proper offset
    // - Horizontal spacing is sqrt(3) * size
    // - Vertical spacing is 1.5 * size
    // - Offset every other row by half the horizontal spacing
    const x = HEX_SIZE * Math.sqrt(3) * (hexX + hexY / 2);
    const y = HEX_SIZE * 1.5 * hexY;
    return {
        x: BOARD_CENTER_X + x,
        y: BOARD_CENTER_Y + y
    };
}

// Get hex corners for drawing (pointy-top orientation)
function getHexCorners(centerX, centerY) {
    const corners = [];
    for (let i = 0; i < 6; i++) {
        // Start at top point (-90 degrees) and go clockwise
        const angle = -Math.PI / 2 + (Math.PI / 3 * i);
        corners.push({
            x: centerX + HEX_SIZE * Math.cos(angle),
            y: centerY + HEX_SIZE * Math.sin(angle)
        });
    }
    return corners;
}

// Get the 6 edge IDs for a hex based on colonist.io coordinate system
function getHexEdges(hexId) {
    const edgeMap = {
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
        18: [71, 69, 68, 65, 63, 61]
    };
    return edgeMap[hexId] || [];
}

// Get the 6 corner IDs for a hex based on colonist.io coordinate system
function getHexCornerIds(hexId) {
    const cornerMap = {
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
        12: [2, 47, 48, 49, 6, 3],
        13: [6, 49, 50, 14, 10, 7],
        14: [50, 51, 22, 18, 15, 14],
        15: [52, 33, 26, 23, 22, 51],
        16: [40, 37, 30, 33, 52, 53],
        17: [44, 41, 40, 53, 48, 47],
        18: [48, 53, 52, 51, 50, 49]
    };
    return cornerMap[hexId] || [];
}

// Get position of a specific edge
function getEdgePosition(edgeId) {
    // Find which hexes share this edge
    const hexesWithEdge = [];
    for (let hexId = 0; hexId < 19; hexId++) {
        const edges = getHexEdges(hexId);
        const edgeIndex = edges.indexOf(edgeId);
        if (edgeIndex !== -1) {
            hexesWithEdge.push({hexId, edgeIndex});
        }
    }
    
    if (hexesWithEdge.length === 0) return null;
    
    // Calculate edge position from hex corner positions
    const hex = hexesWithEdge[0];
    const pos = HEX_POSITIONS[hex.hexId];
    const pixel = hexToPixel(pos.x, pos.y);
    const corners = getHexCorners(pixel.x, pixel.y);
    
    // Edge is between two consecutive corners
    const corner1 = corners[hex.edgeIndex];
    const corner2 = corners[(hex.edgeIndex + 1) % 6];
    
    return {
        x1: corner1.x,
        y1: corner1.y,
        x2: corner2.x,
        y2: corner2.y,
        midX: (corner1.x + corner2.x) / 2,
        midY: (corner1.y + corner2.y) / 2
    };
}


// Initialize the game
async function initGame() {
    // Show modal on page load
    document.getElementById('game-modal').style.display = 'block';
    
    // Set up event listeners
    document.getElementById('start-game').addEventListener('click', startNewGame);
    
    // Add action button click handlers will be set up dynamically
}

// Start a new game
async function startNewGame() {
    const gameMode = document.getElementById('game-mode').value;
    const seed = document.getElementById('game-seed').value || null;
    
    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                seed: seed,
                game_mode: gameMode
            })
        });
        
        const data = await response.json();
        gameId = data.game_id;
        gameState = data.state;
        
        // Hide modal
        document.getElementById('game-modal').style.display = 'none';
        
        // Update player names based on game mode
        if (gameMode === 'pve') {
            document.querySelector('#player-0-stats .player-name').textContent = 'You';
            document.querySelector('#player-1-stats .player-name').textContent = 'AI (Minimax)';
        } else if (gameMode === 'eve') {
            document.querySelector('#player-0-stats .player-name').textContent = 'AI 1 (Minimax)';
            document.querySelector('#player-1-stats .player-name').textContent = 'AI 2 (Minimax)';
        }
        
        // Initial game update
        updateGame();
        
        // Get legal actions
        await fetchLegalActions();
        
        // If AI vs AI, start the game
        if (gameMode === 'eve') {
            setTimeout(() => triggerAIMove(), 1000);
        }
        
    } catch (error) {
        console.error('Failed to start game:', error);
        alert('Failed to start game. Please try again.');
    }
}

// Fetch current game state and legal actions
async function fetchLegalActions() {
    try {
        console.log('Fetching legal actions...');
        const response = await fetch(`/api/game_state/${gameId}`);
        const data = await response.json();
        
        gameState = data.state;
        legalActions = data.legal_actions;
        
        console.log('Game state updated - current_player:', data.state.current_player, 'ai_thinking:', data.ai_thinking);
        console.log('Legal actions received:', data.legal_actions.map(a => ({type: a.type, player: a.player})));
        
        // Log events if any (from AI actions)
        if (data.events && data.events.length > 0) {
            console.log('Processing', data.events.length, 'events from AI actions');
            data.events.forEach(event => logEvent(event));
        }
        
        updateGame();
        updateActionButtons();
        
        // Check for game over
        if (data.game_over) {
            const winner = data.winner;
            const winnerName = winner === 0 ? 'You' : 'AI';
            alert(`Game Over! ${winnerName} won!`);
            return;
        }
        
        // If AI is still thinking, continue polling
        if (data.ai_thinking) {
            console.log('AI still thinking, continuing to poll...');
            setTimeout(() => fetchLegalActions(), 1500);
        }
        
    } catch (error) {
        console.error('Failed to fetch game state:', error);
    }
}

// Execute an action
async function executeAction(actionData) {
    try {
        console.log('Sending action to server:', actionData);
        const response = await fetch(`/api/execute_action/${gameId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(actionData)
        });
        
        console.log('Response status:', response.status);
        if (!response.ok) {
            const text = await response.text();
            console.error('Server error response:', text);
            try {
                const errorData = JSON.parse(text);
                alert(`Action failed: ${errorData.error || 'Unknown error'}`);
            } catch (e) {
                alert(`Server error: ${response.status} - ${text}`);
            }
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            gameState = data.state;
            legalActions = data.legal_actions;
            
            // Log events
            data.events.forEach(event => logEvent(event));
            
            updateGame();
            updateActionButtons();
            
            // Check for game over
            if (data.game_over) {
                const winner = data.winner === 0 ? 'Red' : 'Blue';
                alert(`Game Over! ${winner} wins!`);
            }
            
            // Auto-advance in setup phase after placing road
            if (gameState.setup_phase && gameState.setup_road_placed && gameState.current_player === 0) {
                // Just placed a road, auto end turn
                const endTurnAction = legalActions.find(a => a.type === 'END_TURN');
                if (endTurnAction) {
                    setTimeout(() => executeAction(endTurnAction), 500);
                }
            }
            
            // If AI is thinking, poll for updates
            console.log('Checking ai_thinking:', data.ai_thinking, 'current_player:', data.state.current_player);
            if (data.ai_thinking) {
                console.log('AI is thinking, polling for updates in 1.5s...');
                setTimeout(() => fetchLegalActions(), 1500);
            }
        } else {
            alert(`Action failed: ${data.error}`);
        }
        
    } catch (error) {
        console.error('Failed to execute action:', error);
    }
}

// Update the game display
function updateGame() {
    if (!gameState) {
        console.error('No game state available');
        return;
    }
    
    // Game state is now available
    
    // Update resource bar for human player (player 0 in pve mode)
    updateResourceBar();
    
    // Update player stats
    updatePlayerStats(0);
    updatePlayerStats(1);
    
    // Draw board
    drawBoard();
    
    // Update dice if rolled
    console.log('Checking dice display - dice_rolled:', gameState.dice_rolled);
    if (gameState.dice_rolled && gameState.dice_rolled !== false) {
        const diceAssets = {
            1: '/assets/dice_1.f5a1a69c3529b5b5ffc5.svg',
            2: '/assets/dice_2.859c1a230cf0ab52f238.svg',
            3: '/assets/dice_3.353e115f936308bb6256.svg',
            4: '/assets/dice_4.351f1ed668f38d45da30.svg',
            5: '/assets/dice_5.5eea2c3e3b85be8190bd.svg',
            6: '/assets/dice_6.aea83e2b0e712f5f1fab.svg'
        };
        
        // dice_rolled could be a tuple (die1, die2) or an array [die1, die2]
        const die1 = Array.isArray(gameState.dice_rolled) ? gameState.dice_rolled[0] : gameState.dice_rolled[0];
        const die2 = Array.isArray(gameState.dice_rolled) ? gameState.dice_rolled[1] : gameState.dice_rolled[1];
        
        console.log('Displaying dice:', die1, die2);
        
        document.getElementById('dice1').src = diceAssets[die1];
        document.getElementById('dice2').src = diceAssets[die2];
        
        // Show dice display
        const diceDisplay = document.getElementById('dice-display');
        if (diceDisplay) {
            diceDisplay.style.display = 'flex';
            // Hide after 3 seconds
            setTimeout(() => {
                diceDisplay.style.display = 'none';
            }, 3000);
        }
    }
}

// Update resource bar (shows cards for human player)
function updateResourceBar() {
    // In PvE mode, human is always player 0
    const playerIndex = '0';  // Use string key
    const resources = gameState.resources[playerIndex];
    if (!resources) {
        console.error('No resources for player', playerIndex, gameState.resources);
        return;
    }
    const resourceCardsDiv = document.getElementById('resource-cards');
    resourceCardsDiv.innerHTML = '';
    
    // Use shared resource assets
    const cardAssets = {
        brick: GAME_CONSTANTS.RESOURCE_PATHS['0'],
        grain: GAME_CONSTANTS.RESOURCE_PATHS['1'],
        lumber: GAME_CONSTANTS.RESOURCE_PATHS['2'],
        ore: GAME_CONSTANTS.RESOURCE_PATHS['3'],
        wool: GAME_CONSTANTS.RESOURCE_PATHS['4']
    };
    
    // Only show cards for resources the player has
    for (const [resourceKey, count] of Object.entries(resources)) {
        if (count > 0) {
            // Convert numeric resource key to resource name
            const resourceNames = ['brick', 'grain', 'lumber', 'ore', 'wool'];
            const resource = resourceNames[parseInt(resourceKey)] || resourceKey;
            const cardDiv = document.createElement('div');
            cardDiv.className = 'resource-card';
            cardDiv.dataset.resource = resourceKey; // Add data-resource attribute
            
            // Add click handler if in discard or trade mode
            if (discardModalOpen || tradeModalOpen) {
                cardDiv.classList.add('clickable');
                cardDiv.style.cursor = 'pointer';
                cardDiv.onclick = () => handleResourceCardClick(cardDiv);
            }
            
            const img = document.createElement('img');
            img.src = cardAssets[resource];
            img.alt = resource;
            cardDiv.appendChild(img);
            
            const countSpan = document.createElement('span');
            countSpan.className = 'card-count';
            countSpan.textContent = count;
            cardDiv.appendChild(countSpan);
            
            resourceCardsDiv.appendChild(cardDiv);
        }
    }
    
    // Update dev cards
    const devCardsDiv = document.getElementById('dev-cards');
    devCardsDiv.innerHTML = '';
    
    // Get detailed dev card info for human player
    const devCardDetails = gameState.dev_cards_detail && gameState.dev_cards_detail[playerIndex];
    
    
    if (devCardDetails && Object.keys(devCardDetails).length > 0) {
        // Dev card asset mapping
        const cardAssets = {
            'KNIGHT': '/assets/card_knight.a58573f2154fa93a6319.svg',
            'VICTORY_POINT': '/assets/card_vp.672597308e3a8f1100ae.svg',
            'ROAD_BUILDING': '/assets/card_roadbuilding.994e8f21698ce6c350bd.svg',
            'YEAR_OF_PLENTY': '/assets/card_yearofplenty.3df210b5455b7438db09.svg',
            'MONOPOLY': '/assets/card_monopoly.dfac189aaff62e271093.svg'
        };
        
        // Show each dev card individually
        for (const [cardType, count] of Object.entries(devCardDetails)) {
            // Check if this is a newly bought card
            const isNewCard = cardType.endsWith('_NEW');
            const actualCardType = isNewCard ? cardType.replace('_NEW', '') : cardType;
            
            for (let i = 0; i < count; i++) {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'dev-card';
                if (isNewCard) {
                    cardDiv.classList.add('new-card');
                    cardDiv.title = 'Bought this turn - cannot play yet';
                }
                cardDiv.dataset.cardType = actualCardType;
                
                // Victory point cards and new cards are not playable
                const isPlayable = actualCardType !== 'VICTORY_POINT' && !isNewCard;
                if (isPlayable) {
                    cardDiv.classList.add('playable');
                    cardDiv.style.cursor = 'pointer';
                    cardDiv.onclick = () => handleDevCardClick(actualCardType);
                }
                
                const img = document.createElement('img');
                img.src = cardAssets[actualCardType] || '/assets/card_devcardback.92569a1abd04a8c1c17e.svg';
                img.alt = cardType;
                cardDiv.appendChild(img);
                
                devCardsDiv.appendChild(cardDiv);
            }
        }
    }
}

// Update player statistics panel
function updatePlayerStats(playerIndex) {
    const statsDiv = document.getElementById(`player-${playerIndex}-stats`);
    if (!statsDiv) return;
    
    const playerKey = playerIndex.toString();
    
    // Update VP
    statsDiv.querySelector('[data-stat="vp"]').textContent = gameState.victory_points[playerKey] || 0;
    
    // Count total resources
    const playerResources = gameState.resources[playerKey] || {};
    const totalResources = Object.values(playerResources).reduce((sum, count) => sum + count, 0);
    statsDiv.querySelector('[data-stat="resources"]').textContent = totalResources;
    
    // Update dev cards
    statsDiv.querySelector('[data-stat="dev-cards"]').textContent = gameState.dev_cards[playerKey] || 0;
    
    // Update knights
    statsDiv.querySelector('[data-stat="knights"]').textContent = gameState.knights_played ? gameState.knights_played[playerKey] || 0 : 0;
    
    // Update road length
    const roadLengthElement = statsDiv.querySelector('[data-stat="road-length"]');
    const roadLength = gameState.road_lengths ? gameState.road_lengths[playerKey] || 0 : 0;
    roadLengthElement.textContent = roadLength;
    
    // Highlight if this player has longest road
    if (gameState.longest_road_player === playerIndex) {
        roadLengthElement.style.color = '#f39c12';
        roadLengthElement.style.fontWeight = 'bold';
        roadLengthElement.title = 'Longest Road';
    } else {
        roadLengthElement.style.color = '';
        roadLengthElement.style.fontWeight = '';
        roadLengthElement.title = '';
    }
    
    // Highlight current player
    const nameDiv = statsDiv.querySelector('.player-name');
    if (gameState.current_player === playerIndex) {
        nameDiv.style.textDecoration = 'underline';
        nameDiv.style.textShadow = '0 0 10px rgba(243, 156, 18, 0.5)';
    } else {
        nameDiv.style.textDecoration = 'none';
        nameDiv.style.textShadow = 'none';
    }
}

// Get corner position by ID
function getCornerPosition(cornerId) {
    // Find which hexes contain this corner
    for (let hexId = 0; hexId < 19; hexId++) {
        const corners = getHexCornerIds(hexId);
        const cornerIndex = corners.indexOf(cornerId);
        if (cornerIndex !== -1) {
            const pos = HEX_POSITIONS[hexId];
            const pixel = hexToPixel(pos.x, pos.y);
            const hexCorners = getHexCorners(pixel.x, pixel.y);
            return hexCorners[cornerIndex];
        }
    }
    return null;
}

// Draw the game board
function drawBoard() {
    const svg = document.getElementById('game-board');
    svg.innerHTML = ''; // Clear existing
    
    // Draw ocean background
    const ocean = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    ocean.setAttribute('width', '900');
    ocean.setAttribute('height', '650');
    ocean.setAttribute('fill', '#5dade2');
    svg.appendChild(ocean);
    
    // Create defs section for patterns and clips
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    svg.appendChild(defs);
    
    // Draw hexes
    for (let hexId = 0; hexId < 19; hexId++) {
        drawHex(svg, hexId.toString());
    }
    
    // Draw ports
    drawPorts(svg);
    
    // Draw edge numbers for debugging (comment out in production)
    // drawEdgeNumbers(svg);
    
    // Draw corner numbers for debugging (comment out in production)
    // drawCornerNumbers(svg);
    
    // Draw roads
    for (const [edgeId, playerColor] of Object.entries(gameState.edges)) {
        if (playerColor !== null) {
            drawRoad(svg, parseInt(edgeId), playerColor);
        }
    }
    
    // Draw settlements and cities
    for (const [cornerId, building] of Object.entries(gameState.corners)) {
        if (building) {
            drawBuilding(svg, parseInt(cornerId), building);
        }
    }
    
    // Draw robber
    drawRobber(svg);
}

// Draw a single hex
function drawHex(svg, hexId) {
    const hexData = gameState.hexes[hexId];
    if (!hexData) {
        console.error(`No hex data for hex ${hexId}`, gameState.hexes);
        return;
    }
    
    // Convert string hexId back to number for position lookup
    const hexIdNum = parseInt(hexId);
    const pos = HEX_POSITIONS[hexIdNum];
    const pixel = hexToPixel(pos.x, pos.y);
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.classList.add('hex');
    g.setAttribute('data-hex-id', hexId);
    
    // Create hex path
    const corners = getHexCorners(pixel.x, pixel.y);
    const points = corners.map(c => `${c.x},${c.y}`).join(' ');
    
    // Tile asset mapping
    const tileAssets = {
        'brick': '/assets/tile_brick.3082910583708dd98c82.svg',
        'grain': '/assets/tile_grain.f99882d0014743dba80b.svg',
        'lumber': '/assets/tile_lumber.2f0099b519514f091763.svg',
        'ore': '/assets/tile_ore.0033829cd0573ced9c6f.svg',
        'wool': '/assets/tile_wool.72fafecfd68aa740af09.svg'
    };
    
    if (hexData.resource === 'desert') {
        // Draw solid color for desert
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', points);
        polygon.setAttribute('fill', 'rgb(215, 210, 150)');
        polygon.classList.add('hex-tile');
        g.appendChild(polygon);
    } else if (tileAssets[hexData.resource]) {
        // Create clipping path for hex shape
        const clipId = `hex-clip-${hexId}`;
        const defs = svg.querySelector('defs');
        
        const clipPath = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath');
        clipPath.setAttribute('id', clipId);
        
        const clipPolygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        clipPolygon.setAttribute('points', points);
        clipPath.appendChild(clipPolygon);
        defs.appendChild(clipPath);
        
        // Draw the tile image clipped to hex shape
        const image = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        image.setAttribute('href', tileAssets[hexData.resource]);
        image.setAttribute('x', pixel.x - HEX_SIZE);
        image.setAttribute('y', pixel.y - HEX_SIZE);
        image.setAttribute('width', HEX_SIZE * 2);
        image.setAttribute('height', HEX_SIZE * 2);
        image.setAttribute('clip-path', `url(#${clipId})`);
        g.appendChild(image);
        
        // Add hex border
        const border = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        border.setAttribute('points', points);
        border.setAttribute('fill', 'none');
        border.classList.add('hex-tile');
        g.appendChild(border);
    }
    
    // Add number token if not desert
    if (hexData.number) {
        // Position number token lower (offset by 15 pixels down)
        const numberY = pixel.y + 15;
        
        // Background square
        const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        bgRect.setAttribute('x', pixel.x - 15);
        bgRect.setAttribute('y', numberY - 15);
        bgRect.setAttribute('width', '30');
        bgRect.setAttribute('height', '30');
        bgRect.setAttribute('fill', 'white');
        bgRect.setAttribute('stroke', '#2c3e50');
        bgRect.setAttribute('stroke-width', '1');
        g.appendChild(bgRect);
        
        // Number text in black
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pixel.x);
        text.setAttribute('y', numberY + 5);
        text.classList.add('hex-number');
        text.style.fill = 'black';
        text.textContent = hexData.number;
        
        // Make 6 and 8 bold instead of red
        if (hexData.number === 6 || hexData.number === 8) {
            text.style.fontWeight = '900';
        }
        
        g.appendChild(text);
    }
    
    svg.appendChild(g);
}


// Draw edge numbers for debugging (0-71)
function drawEdgeNumbers(svg) {
    const drawnEdges = new Set();
    
    for (let hexId = 0; hexId < 19; hexId++) {
        const hexEdges = getHexEdges(hexId);
        const pos = HEX_POSITIONS[hexId];
        const pixel = hexToPixel(pos.x, pos.y);
        const corners = getHexCorners(pixel.x, pixel.y);
        
        hexEdges.forEach((edgeId, edgeIndex) => {
            if (edgeId !== null && !drawnEdges.has(edgeId)) {
                drawnEdges.add(edgeId);
                
                // Get the two corners that form this edge
                const corner1 = corners[edgeIndex];
                const corner2 = corners[(edgeIndex + 1) % 6];
                
                // Calculate midpoint of the edge
                const midX = (corner1.x + corner2.x) / 2;
                const midY = (corner1.y + corner2.y) / 2;
                
                // Add background circle for better visibility
                const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                bgCircle.setAttribute('cx', midX);
                bgCircle.setAttribute('cy', midY);
                bgCircle.setAttribute('r', '8');
                bgCircle.style.fill = 'white';
                bgCircle.style.stroke = 'red';
                bgCircle.style.strokeWidth = '1px';
                bgCircle.style.opacity = '0.9';
                svg.appendChild(bgCircle);
                
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', midX);
                text.setAttribute('y', midY);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('dominant-baseline', 'middle');
                text.style.fontSize = '10px';
                text.style.fill = 'red';
                text.style.fontWeight = 'bold';
                text.textContent = edgeId;
                
                svg.appendChild(text);
            }
        });
    }
}

// Draw corner numbers for debugging (0-53)
function drawCornerNumbers(svg) {
    const drawnCorners = new Set();
    
    for (let hexId = 0; hexId < 19; hexId++) {
        const hexCornerIds = getHexCornerIds(hexId);
        const pos = HEX_POSITIONS[hexId];
        const pixel = hexToPixel(pos.x, pos.y);
        const corners = getHexCorners(pixel.x, pixel.y);
        
        hexCornerIds.forEach((cornerId, cornerIndex) => {
            if (cornerId !== null && !drawnCorners.has(cornerId)) {
                drawnCorners.add(cornerId);
                
                const corner = corners[cornerIndex];
                
                // Add background circle for better visibility
                const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                bgCircle.setAttribute('cx', corner.x);
                bgCircle.setAttribute('cy', corner.y);
                bgCircle.setAttribute('r', '10');
                bgCircle.style.fill = 'white';
                bgCircle.style.stroke = 'blue';
                bgCircle.style.strokeWidth = '1px';
                bgCircle.style.opacity = '0.9';
                svg.appendChild(bgCircle);
                
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', corner.x);
                text.setAttribute('y', corner.y);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('dominant-baseline', 'middle');
                text.style.fontSize = '10px';
                text.style.fill = 'blue';
                text.style.fontWeight = 'bold';
                text.textContent = cornerId;
                
                svg.appendChild(text);
            }
        });
    }
}

// Get the two corners that form an edge
function getEdgeCorners(edgeId) {
    const corners = [];
    // Check all hexes to find which corners are at the endpoints of this edge
    for (let hexId = 0; hexId < 19; hexId++) {
        const hexEdges = getHexEdges(hexId);
        const edgeIndex = hexEdges.indexOf(edgeId);
        if (edgeIndex !== -1) {
            const hexCorners = getHexCornerIds(hexId);
            // Edge at index i connects corner i and corner (i+1)%6
            corners.push(hexCorners[edgeIndex]);
            corners.push(hexCorners[(edgeIndex + 1) % 6]);
        }
    }
    // Remove duplicates and return unique corners
    return [...new Set(corners)];
}

// Draw ports
function drawPorts(svg) {
    // Get the actual position of a port based on its edge
    for (const [edgeId, portType] of Object.entries(gameState.ports)) {
        const edgeIdNum = parseInt(edgeId);
        const edgePos = getEdgePosition(edgeIdNum);
        if (!edgePos) continue;
        
        // Get the two corners that form this edge
        const cornerIds = getEdgeCorners(edgeIdNum);
        if (cornerIds.length !== 2) continue;
        
        const corner1Pos = getCornerPosition(cornerIds[0]);
        const corner2Pos = getCornerPosition(cornerIds[1]);
        if (!corner1Pos || !corner2Pos) continue;
        
        // Find which hex this edge belongs to (for coastal edges, it's only one hex)
        let hexCenter = null;
        for (let hexId = 0; hexId < 19; hexId++) {
            const edges = getHexEdges(hexId);
            if (edges.includes(edgeIdNum)) {
                const pos = HEX_POSITIONS[hexId];
                hexCenter = hexToPixel(pos.x, pos.y);
                break;
            }
        }
        
        if (!hexCenter) continue;
        
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.classList.add('port');
        
        // Calculate outward direction from hex center through edge midpoint
        const edgeMidX = (corner1Pos.x + corner2Pos.x) / 2;
        const edgeMidY = (corner1Pos.y + corner2Pos.y) / 2;
        
        const outwardDir = {
            x: edgeMidX - hexCenter.x,
            y: edgeMidY - hexCenter.y
        };
        const outwardLength = Math.sqrt(outwardDir.x * outwardDir.x + outwardDir.y * outwardDir.y);
        outwardDir.x /= outwardLength;
        outwardDir.y /= outwardLength;
        
        // Move the port base outward from the edge
        const portOffset = 40; // Increased offset from edge
        const portBaseX = edgeMidX + outwardDir.x * portOffset;
        const portBaseY = edgeMidY + outwardDir.y * portOffset;
        
        // Calculate pier directions (angled inward toward the port center)
        const pierAngle = Math.PI / 6; // 30 degrees inward
        const pierLength = 25;
        
        // Direction from corner1 to port base (and slightly inward)
        const pier1Dir = {
            x: portBaseX - corner1Pos.x,
            y: portBaseY - corner1Pos.y
        };
        const pier1DirLength = Math.sqrt(pier1Dir.x * pier1Dir.x + pier1Dir.y * pier1Dir.y);
        pier1Dir.x /= pier1DirLength;
        pier1Dir.y /= pier1DirLength;
        
        // Direction from corner2 to port base (and slightly inward)
        const pier2Dir = {
            x: portBaseX - corner2Pos.x,
            y: portBaseY - corner2Pos.y
        };
        const pier2DirLength = Math.sqrt(pier2Dir.x * pier2Dir.x + pier2Dir.y * pier2Dir.y);
        pier2Dir.x /= pier2DirLength;
        pier2Dir.y /= pier2DirLength;
        
        const pier1End = {
            x: corner1Pos.x + pier1Dir.x * pierLength,
            y: corner1Pos.y + pier1Dir.y * pierLength
        };
        const pier2End = {
            x: corner2Pos.x + pier2Dir.x * pierLength,
            y: corner2Pos.y + pier2Dir.y * pierLength
        };
        
        // Draw pier lines
        const pier1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        pier1.setAttribute('x1', corner1Pos.x);
        pier1.setAttribute('y1', corner1Pos.y);
        pier1.setAttribute('x2', pier1End.x);
        pier1.setAttribute('y2', pier1End.y);
        pier1.style.stroke = '#8b6914';
        pier1.style.strokeWidth = '6';
        pier1.style.strokeLinecap = 'round';
        g.appendChild(pier1);
        
        const pier2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        pier2.setAttribute('x1', corner2Pos.x);
        pier2.setAttribute('y1', corner2Pos.y);
        pier2.setAttribute('x2', pier2End.x);
        pier2.setAttribute('y2', pier2End.y);
        pier2.style.stroke = '#8b6914';
        pier2.style.strokeWidth = '6';
        pier2.style.strokeLinecap = 'round';
        g.appendChild(pier2);
        
        // Calculate position for port label (at the port base, further from edge)
        const labelX = portBaseX;
        const labelY = portBaseY;
        
        // Use SVG assets for ports
        const portAssets = {
            '3:1': 'threeport.svg',
            'lumber': 'woodport.svg',
            'wood': 'woodport.svg',
            'brick': 'brickport.svg',
            'wool': 'sheepport.svg',
            'sheep': 'sheepport.svg',
            'grain': 'wheatport.svg',
            'wheat': 'wheatport.svg',
            'ore': 'oreport.svg'
        };
        
        const assetFile = portAssets[portType] || 'threeport.svg';
        
        // Create image element for port SVG
        const portImage = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        portImage.setAttribute('href', `/assets/${assetFile}`);
        portImage.setAttribute('x', labelX - 25);  // Center the 50x50 image
        portImage.setAttribute('y', labelY - 25);
        portImage.setAttribute('width', '50');
        portImage.setAttribute('height', '50');
        portImage.style.pointerEvents = 'none';
        g.appendChild(portImage);
        
        svg.appendChild(g);
    }
}

// Draw roads
function drawRoad(svg, edgeId, playerColor) {
    const edgePos = getEdgePosition(edgeId);
    if (!edgePos) return;
    
    // Calculate road position and angle
    const dx = edgePos.x2 - edgePos.x1;
    const dy = edgePos.y2 - edgePos.y1;
    const centerX = (edgePos.x1 + edgePos.x2) / 2;
    const centerY = (edgePos.y1 + edgePos.y2) / 2;
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;
    const length = Math.sqrt(dx * dx + dy * dy);
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('transform', `translate(${centerX}, ${centerY}) rotate(${angle})`);
    
    // Road assets
    const roadAssets = GAME_CONSTANTS.BUILDING_ASSETS.road;
    
    // Use road asset as an image
    const road = document.createElementNS('http://www.w3.org/2000/svg', 'image');
    road.setAttribute('href', roadAssets[playerColor]);
    road.setAttribute('x', -length/2);
    road.setAttribute('y', -5); // Half height for thinner roads
    road.setAttribute('width', length);
    road.setAttribute('height', '10');
    road.setAttribute('preserveAspectRatio', 'none'); // Stretch to fit
    road.classList.add('road');
    
    g.appendChild(road);
    svg.appendChild(g);
}

// Draw buildings
function drawBuilding(svg, cornerId, building) {
    const cornerPos = getCornerPosition(cornerId);
    if (!cornerPos) return;
    
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.classList.add(building.type);
    
    // Building assets
    const settlementAssets = GAME_CONSTANTS.BUILDING_ASSETS.settlement;
    
    const cityAssets = GAME_CONSTANTS.BUILDING_ASSETS.city;
    
    if (building.type === 'SETTLEMENT') { // Settlement
        const settlement = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        settlement.setAttribute('href', settlementAssets[building.player]);
        settlement.setAttribute('x', cornerPos.x - 20);
        settlement.setAttribute('y', cornerPos.y - 20);
        settlement.setAttribute('width', '40');
        settlement.setAttribute('height', '40');
        settlement.classList.add('settlement');
        g.appendChild(settlement);
    } else { // City
        const city = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        city.setAttribute('href', cityAssets[building.player]);
        city.setAttribute('x', cornerPos.x - 25);
        city.setAttribute('y', cornerPos.y - 25);
        city.setAttribute('width', '50');
        city.setAttribute('height', '50');
        city.classList.add('city');
        g.appendChild(city);
    }
    
    svg.appendChild(g);
}

// Draw robber
function drawRobber(svg) {
    if (gameState.robber_tile === null || gameState.robber_tile === undefined) return;
    
    const pos = HEX_POSITIONS[gameState.robber_tile];
    const pixel = hexToPixel(pos.x, pos.y);
    
    // Position robber to the left to avoid covering the number
    const robberX = pixel.x - 25;
    const robberY = pixel.y;
    
    const robber = document.createElementNS('http://www.w3.org/2000/svg', 'image');
    robber.setAttribute('href', '/assets/icon_robber.d6f984074d0d7ed7d8f2.svg');
    robber.setAttribute('x', robberX - 20);  // Center the image
    robber.setAttribute('y', robberY - 20);   // Center the image
    robber.setAttribute('width', '40');
    robber.setAttribute('height', '40');
    robber.classList.add('robber');
    
    svg.appendChild(robber);
}

// State for interactive placement
let placementMode = null; // 'settlement', 'road', 'robber'
let validPlacements = [];

// Global state for discard/trade
let discardSelection = {};
let tradeGiveSelection = {};
let tradeGetResource = null;
let requiredDiscards = 0;
let selectedDiscards = {};
let selectedTradeGive = {};
let selectedTradeGet = null;
let discardModalOpen = false;
let tradeModalOpen = false;

// Update action buttons
function updateActionButtons() {
    const actionsList = document.getElementById('actions-list');
    actionsList.innerHTML = '';
    
    // Update main action buttons availability
    updateMainActionButtons();
    
    // Don't show action buttons if it's not the human player's turn
    if (gameState && gameState.current_player !== 0) {
        console.log('Not human turn (player', gameState.current_player, '), not showing action buttons');
        return;
    }
    
    // Check if we're in setup phase
    if (gameState && gameState.setup_phase) {
        // During setup, enable interactive placement instead of showing buttons
        enableSetupPlacement();
        return;
    }
    
    // The discard modal will be shown when DISCARD actions are in legal_actions
    // (handled in the action button loop below)
    
    // Check for Road Building state
    if (gameState.action_state === 30 || gameState.action_state === 31) { // ROAD_BUILDING_1 or ROAD_BUILDING_2
        const roadsPlaced = gameState.action_state === 30 ? 0 : 1;
        const roadsRemaining = 2 - roadsPlaced;
        addLogEntry(`Road Building: Place ${roadsRemaining} more road${roadsRemaining > 1 ? 's' : ''} for free`, 'system');
    }
    
    // Filter out building actions - these will be interactive
    const nonBuildingActions = legalActions.filter(action => {
        return action.type !== 'BUILD_SETTLEMENT' && 
               action.type !== 'BUILD_ROAD' && 
               action.type !== 'BUILD_CITY' &&
               action.type !== 'MOVE_ROBBER' &&
               action.type !== 'BUY_DEVELOPMENT_CARD';  // Has its own button
    });
    
    // Check if maritime trade is available
    const maritimeTradeActions = nonBuildingActions.filter(a => a.type === 'MARITIME_TRADE');
    const hasMaritimeTrade = maritimeTradeActions.length > 0;
    console.log('Maritime trade actions available:', maritimeTradeActions);
    
    // Show only essential non-building actions as buttons
    nonBuildingActions.forEach((action, index) => {
        // Skip actions that have dedicated UI elements
        if (action.type === 'MARITIME_TRADE') return; // Has modal
        if (action.type === 'BUY_DEVELOPMENT_CARD') return; // Has bottom button
        if (action.type === 'PLAY_KNIGHT_CARD') return; // Click dev card directly
        if (action.type === 'PLAY_ROAD_BUILDING') return; // Click dev card directly
        if (action.type === 'PLAY_YEAR_OF_PLENTY') return; // Click dev card directly
        if (action.type === 'PLAY_MONOPOLY') return; // Click dev card directly
        
        const button = document.createElement('button');
        button.classList.add('action-button');
        
        // Set button text based on action type
        if (action.type === 'ROLL' || action.type === 'ROLL_DICE') {
            button.textContent = 'Roll Dice';
            button.classList.add('primary');
        } else if (action.type === 'END_TURN') {
            button.textContent = 'End Turn';
            button.classList.add('end-turn');
        } else if (action.type === 'DISCARD') {
            // Skip creating a button - we'll show the modal instead
            showDiscardModal();
            return;
        } else if (action.type === 'STEAL_CARD') {
            button.textContent = `Steal from Player ${action.target_player + 1}`;
        } else if (action.type === 'BUY_DEVELOPMENT_CARD') {
            button.textContent = 'Buy Development Card';
            button.classList.add('primary');
        } else {
            // Default for any other action types
            button.textContent = action.type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
            console.warn('Unknown action type for button:', action.type);
        }
        
        button.addEventListener('click', () => {
            console.log('Action button clicked, action:', action);
            executeAction(action);
        });
        actionsList.appendChild(button);
    });
    
    // Add maritime trade button if available
    if (hasMaritimeTrade) {
        const button = document.createElement('button');
        button.classList.add('action-button', 'trade');
        button.textContent = 'Maritime Trade';
        button.addEventListener('click', () => showTradeModal());
        actionsList.appendChild(button);
    }
    
    // Only show robber placement info if needed
    const canMoveRobber = legalActions.some(a => a.type === 'MOVE_ROBBER');
    if (canMoveRobber) {
        const info = document.createElement('div');
        info.innerHTML = '<strong>Click a hex to move the robber</strong>';
        actionsList.appendChild(info);
        enablePlacementMode('robber');
    }
}

// Enable setup phase placement
function enableSetupPlacement() {
    const actionsList = document.getElementById('actions-list');
    
    // Check what we need to place
    const needsSettlement = legalActions.some(a => a.type === 'BUILD_INITIAL_SETTLEMENT');
    const needsRoad = legalActions.some(a => a.type === 'BUILD_INITIAL_ROAD');
    const canEndTurn = legalActions.some(a => a.type === 'END_TURN');
    
    if (needsSettlement) {
        actionsList.innerHTML = '<div class="setup-info"><strong>Setup Phase:</strong> Click on the map to place your settlement</div>';
        enablePlacementMode('settlement');
    } else if (needsRoad) {
        actionsList.innerHTML = '<div class="setup-info"><strong>Setup Phase:</strong> Click on the map to place your road</div>';
        enablePlacementMode('road');
    } else if (canEndTurn) {
        const button = document.createElement('button');
        button.textContent = 'End Turn';
        button.classList.add('action-button', 'end-turn');
        button.addEventListener('click', () => {
            const endTurnAction = legalActions.find(a => a.type === 'END_TURN');
            if (endTurnAction) executeAction(endTurnAction);
        });
        actionsList.innerHTML = '';
        actionsList.appendChild(button);
    }
}

// Enable placement mode
function enablePlacementMode(mode) {
    console.log('Enabling placement mode:', mode);
    console.log('Legal actions available:', legalActions.length);
    console.log('First few legal actions:', legalActions.slice(0, 3));
    
    placementMode = mode;
    validPlacements = [];
    
    // Get valid placements based on mode
    if (mode === 'settlement') {
        validPlacements = legalActions
            .filter(a => a.type === 'BUILD_SETTLEMENT' || a.type === 'BUILD_INITIAL_SETTLEMENT')
            .map(a => ({ type: 'corner', id: a.corner, action: a }));
    } else if (mode === 'road') {
        validPlacements = legalActions
            .filter(a => a.type === 'BUILD_ROAD' || a.type === 'BUILD_INITIAL_ROAD')
            .map(a => ({ type: 'edge', id: a.edge, action: a }));
    } else if (mode === 'city') {
        validPlacements = legalActions
            .filter(a => a.type === 'BUILD_CITY')
            .map(a => ({ type: 'corner', id: a.corner, action: a }));
    } else if (mode === 'robber') {
        validPlacements = legalActions
            .filter(a => a.type === 'MOVE_ROBBER')
            .map(a => ({ type: 'hex', id: a.hex, action: a }));
    }
    
    console.log('Valid placements found:', validPlacements.length);
    console.log('First few valid placements:', validPlacements.slice(0, 3));
    
    // Highlight valid placements
    highlightValidPlacements();
}

// Highlight valid placements on the board
function highlightValidPlacements() {
    console.log('Highlighting placements. Valid placements:', validPlacements.length);
    const svg = document.getElementById('game-board');
    
    // Remove existing highlights
    const existingHighlights = svg.querySelectorAll('.placement-highlight');
    existingHighlights.forEach(h => h.remove());
    
    // Add new highlights
    validPlacements.forEach(placement => {
        if (placement.type === 'corner') {
            // Highlight valid corners
            const pos = getCornerPosition(placement.id);
            console.log(`Corner ${placement.id} position:`, pos);
            if (pos) {
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', pos.x);
                circle.setAttribute('cy', pos.y);
                circle.setAttribute('r', '15');
                circle.setAttribute('fill', 'yellow');
                circle.setAttribute('fill-opacity', '0.5');
                circle.setAttribute('stroke', 'orange');
                circle.setAttribute('stroke-width', '2');
                circle.classList.add('placement-highlight');
                circle.style.cursor = 'pointer';
                circle.addEventListener('click', () => executeAction(placement.action));
                svg.appendChild(circle);
            } else {
                console.error(`Could not find position for corner ${placement.id}`);
            }
        } else if (placement.type === 'edge') {
            // Highlight valid edges
            const corners = getEdgeCorners(placement.id);
            if (corners) {
                const pos1 = getCornerPosition(corners[0]);
                const pos2 = getCornerPosition(corners[1]);
                if (pos1 && pos2) {
                    // Create a group for the edge highlight
                    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                    group.classList.add('placement-highlight');
                    group.style.cursor = 'pointer';
                    group.addEventListener('click', () => executeAction(placement.action));
                    
                    // Create a thick invisible line for easier clicking
                    const clickLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    clickLine.setAttribute('x1', pos1.x);
                    clickLine.setAttribute('y1', pos1.y);
                    clickLine.setAttribute('x2', pos2.x);
                    clickLine.setAttribute('y2', pos2.y);
                    clickLine.setAttribute('stroke', 'transparent');
                    clickLine.setAttribute('stroke-width', '20');
                    clickLine.style.cursor = 'pointer';
                    
                    // Create the visible highlight line
                    const visualLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    visualLine.setAttribute('x1', pos1.x);
                    visualLine.setAttribute('y1', pos1.y);
                    visualLine.setAttribute('x2', pos2.x);
                    visualLine.setAttribute('y2', pos2.y);
                    visualLine.setAttribute('stroke', 'yellow');
                    visualLine.setAttribute('stroke-width', '8');
                    visualLine.setAttribute('stroke-opacity', '0.5');
                    visualLine.style.pointerEvents = 'none'; // Don't interfere with clicks
                    
                    group.appendChild(clickLine);
                    group.appendChild(visualLine);
                    svg.appendChild(group);
                }
            }
        } else if (placement.type === 'hex') {
            // Highlight valid hexes for robber
            const pos = HEX_POSITIONS[placement.id];
            if (pos) {
                const pixel = hexToPixel(pos.x, pos.y);
                const hex = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                const points = [];
                for (let i = 0; i < 6; i++) {
                    const angle = (Math.PI / 3) * i;
                    const x = pixel.x + HEX_SIZE * Math.cos(angle);
                    const y = pixel.y + HEX_SIZE * Math.sin(angle);
                    points.push(`${x},${y}`);
                }
                hex.setAttribute('points', points.join(' '));
                hex.setAttribute('fill', 'red');
                hex.setAttribute('fill-opacity', '0.3');
                hex.setAttribute('stroke', 'darkred');
                hex.setAttribute('stroke-width', '2');
                hex.classList.add('placement-highlight');
                hex.style.cursor = 'pointer';
                hex.addEventListener('click', () => executeAction(placement.action));
                svg.appendChild(hex);
            }
        }
    });
}

// Add log entry helper function
function addLogEntry(message, type = 'system') {
    const logMessages = document.getElementById('log-messages');
    const entry = document.createElement('div');
    entry.classList.add('log-entry', type);
    entry.textContent = message;
    logMessages.appendChild(entry);
    logMessages.scrollTop = logMessages.scrollHeight;
}

// Log game events
function logEvent(event) {
    const logMessages = document.getElementById('log-messages');
    const entry = document.createElement('div');
    entry.classList.add('log-entry');
    
    let message = '';
    let playerClass = '';
    
    // Define resourceEmojis array once at the top
    const resourceEmojis = ['🧱', '🌾', '🌲', '🪨', '🐑'];
    
    switch (event.type) {
        case 'DICE_ROLLED':
            message = `Rolled ${event.dice[0]} + ${event.dice[1]} = ${event.total}`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'RESOURCES_PRODUCED':
        case 'RESOURCES_GAINED':
            // Create custom HTML for resources with icons
            const resourceNames = ['brick', 'grain', 'lumber', 'ore', 'wool'];
            const resourceEmojis = {
                brick: '🧱',
                grain: '🌾', 
                lumber: '🌲',
                ore: '🪨',
                wool: '🐑'
            };
            
            const resourceEmojisOnly = [];
            for (const [resId, count] of Object.entries(event.resources)) {
                const resName = resourceNames[parseInt(resId)] || resId;
                const emoji = resourceEmojis[resName] || '?';
                // Repeat emoji for the count
                for (let i = 0; i < count; i++) {
                    resourceEmojisOnly.push(emoji);
                }
            }
            
            message = `Gained ${resourceEmojisOnly.join('')}`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'ROAD_BUILT':
            message = `Built road`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'SETTLEMENT_BUILT':
            message = `Built settlement`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'CITY_BUILT':
            message = `Built city`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'ROBBER_MOVED':
            message = `Moved robber to hex ${event.hex_id}`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'CARD_STOLEN':
            const targetName = event.target === 0 ? 'Red' : 'Blue';
            const stolenEmoji = resourceEmojis[event.resource] || '?';
            message = `Stole ${stolenEmoji} from ${targetName}`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'TURN_ENDED':
            message = `Turn ended`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'GAME_OVER':
            message = `Game Over! Player ${event.winner + 1} wins!`;
            playerClass = 'system';
            break;
        case 'DEV_CARD_BOUGHT':
            message = `Bought development card`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'KNIGHT_PLAYED':
            message = `Played Knight card`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'ROAD_BUILDING_PLAYED':
            message = `Played Road Building card`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'YEAR_OF_PLENTY_PLAYED':
            const yopResources = [];
            for (const [res, count] of Object.entries(event.resources || {})) {
                const emoji = resourceEmojis[res] || '?';
                for (let i = 0; i < count; i++) {
                    yopResources.push(emoji);
                }
            }
            message = `Played Year of Plenty: took ${yopResources.join('')}`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        case 'MONOPOLY_PLAYED':
            const monopolyEmoji = resourceEmojis[event.resource] || '?';
            message = `Played Monopoly on ${monopolyEmoji}, took ${event.total_taken || 0} cards`;
            playerClass = event.player === 0 ? 'red' : 'blue';
            break;
        default:
            message = `${event.type}`;
            playerClass = 'system';
    }
    
    entry.classList.add(playerClass);
    entry.textContent = message;
    logMessages.appendChild(entry);
    
    // Auto-scroll to bottom
    logMessages.scrollTop = logMessages.scrollHeight;
}

// Trigger AI move (for AI vs AI games)
async function triggerAIMove() {
    if (!gameId) return;
    
    try {
        const response = await fetch(`/api/ai_move/${gameId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        gameState = data.state;
        legalActions = data.legal_actions;
        
        updateGame();
        updateActionButtons();
        
        if (data.game_over) {
            const winner = data.winner === 0 ? 'Red' : 'Blue';
            alert(`Game Over! ${winner} wins!`);
        } else {
            // Continue AI vs AI game
            setTimeout(() => fetchLegalActions(), 1000);
        }
        
    } catch (error) {
        console.error('Failed to trigger AI move:', error);
    }
}

// Update main action buttons (buy dev card, road, settlement, city)
function updateMainActionButtons() {
    console.log('Updating main action buttons...');
    console.log('Current player:', gameState?.current_player);
    console.log('Legal actions:', legalActions);
    
    const buyDevCard = document.getElementById('buy-dev-card');
    const buyRoad = document.getElementById('buy-road');
    const buySettlement = document.getElementById('buy-settlement');
    const buyCity = document.getElementById('buy-city');
    
    // Reset all buttons to disabled
    buyDevCard.disabled = true;
    buyRoad.disabled = true;
    buySettlement.disabled = true;
    buyCity.disabled = true;
    
    // Only enable if it's the human player's turn
    if (!gameState || gameState.current_player !== 0) {
        console.log('Not human player turn, keeping buttons disabled');
        return;
    }
    
    // Check each action in legal actions
    legalActions.forEach(action => {
        switch(action.type) {
            case 'BUY_DEVELOPMENT_CARD':
                console.log('Enabling buy dev card button');
                buyDevCard.disabled = false;
                break;
            case 'BUILD_ROAD':
                console.log('Enabling buy road button');
                buyRoad.disabled = false;
                break;
            case 'BUILD_SETTLEMENT':
                console.log('Enabling buy settlement button');
                buySettlement.disabled = false;
                break;
            case 'BUILD_CITY':
                console.log('Enabling buy city button');
                buyCity.disabled = false;
                break;
        }
    });
}

// Show discard modal
function showDiscardModal() {
    const modal = document.getElementById('discard-modal');
    const discardCount = document.getElementById('discard-count');
    
    // Calculate how many cards to discard
    const totalResources = Object.values(gameState.resources['0']).reduce((a, b) => a + b, 0);
    requiredDiscards = Math.floor(totalResources / 2);
    
    console.log('Discard modal: Total resources:', totalResources, 'Required discards:', requiredDiscards);
    
    // Safety check - should never happen
    if (totalResources < 8) {
        console.error('ERROR: Discard modal shown with less than 8 cards!', gameState.resources['0']);
        modal.style.display = 'none';
        return;
    }
    
    discardCount.textContent = requiredDiscards;
    selectedDiscards = {};
    
    // Set modal open flag first
    discardModalOpen = true;
    
    // Populate available resources in the modal
    const discardResourceCards = document.getElementById('discard-resource-cards');
    discardResourceCards.innerHTML = '';
    
    const resourcePaths = GAME_CONSTANTS.RESOURCE_PATHS;
    
    const resources = gameState.resources['0'];
    for (const [resourceKey, count] of Object.entries(resources)) {
        if (count > 0) {
            for (let i = 0; i < count; i++) {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'modal-resource-card';
                cardDiv.dataset.resource = resourceKey;
                cardDiv.style.cursor = 'pointer';
                
                const img = document.createElement('img');
                img.src = resourcePaths[resourceKey];
                img.style.width = '60px';
                img.style.height = '80px';
                cardDiv.appendChild(img);
                
                cardDiv.onclick = () => {
                    // Move card to selected area - ensure integer key
                    const intKey = parseInt(resourceKey);
                    if (!selectedDiscards[intKey]) selectedDiscards[intKey] = 0;
                    selectedDiscards[intKey]++;
                    cardDiv.style.display = 'none';
                    updateDiscardArea();
                };
                
                discardResourceCards.appendChild(cardDiv);
            }
        }
    }
    
    updateDiscardArea();
    
    modal.style.display = 'block';
}

// Show trade modal
function showTradeModal() {
    const modal = document.getElementById('trade-modal');
    
    selectedTradeGive = {};
    selectedTradeGet = null;
    
    // Set modal open flag first
    tradeModalOpen = true;
    
    // Populate available resources in the modal
    const tradeResourceCards = document.getElementById('trade-resource-cards');
    tradeResourceCards.innerHTML = '';
    
    const resourcePaths = GAME_CONSTANTS.RESOURCE_PATHS;
    
    const resources = gameState.resources['0'];
    for (const [resourceKey, count] of Object.entries(resources)) {
        if (count > 0) {
            for (let i = 0; i < count; i++) {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'modal-resource-card';
                cardDiv.dataset.resource = resourceKey;
                cardDiv.style.cursor = 'pointer';
                
                const img = document.createElement('img');
                img.src = resourcePaths[resourceKey];
                img.style.width = '60px';
                img.style.height = '80px';
                cardDiv.appendChild(img);
                
                cardDiv.onclick = () => {
                    // Move card to selected area - ensure integer key
                    const intKey = parseInt(resourceKey);
                    if (!selectedTradeGive[intKey]) selectedTradeGive[intKey] = 0;
                    selectedTradeGive[intKey]++;
                    cardDiv.style.display = 'none';
                    updateTradeGiveArea();
                    updateTradeConfirmButton();
                };
                
                tradeResourceCards.appendChild(cardDiv);
            }
        }
    }
    
    updateTradeGiveArea();
    updateTradeConfirmButton();
    
    // Reset trade option selection
    document.querySelectorAll('.trade-option').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    modal.style.display = 'block';
}

// Make resource cards clickable for discard/trade
function makeResourceCardsClickable(clickable) {
    const resourceCards = document.querySelectorAll('.resource-card');
    resourceCards.forEach(card => {
        if (clickable) {
            card.classList.add('clickable');
            card.style.cursor = 'pointer';
            card.onclick = () => handleResourceCardClick(card);
        } else {
            card.classList.remove('clickable');
            card.style.cursor = 'default';
            card.onclick = null;
        }
    });
}

// Handle resource card click during discard/trade
function handleResourceCardClick(card) {
    const resourceType = card.dataset.resource;
    const currentCount = parseInt(card.querySelector('.card-count').textContent) || 0;
    
    console.log('Resource card clicked:', resourceType, 'count:', currentCount, 'discardModalOpen:', discardModalOpen, 'tradeModalOpen:', tradeModalOpen);
    
    if (discardModalOpen) {
        // Discard mode
        if (!selectedDiscards[resourceType]) selectedDiscards[resourceType] = 0;
        
        // Check if we can add more to discard
        const totalSelected = Object.values(selectedDiscards).reduce((a, b) => a + b, 0);
        if (totalSelected < requiredDiscards && selectedDiscards[resourceType] < currentCount) {
            selectedDiscards[resourceType]++;
            updateDiscardArea();
        }
    } else if (tradeModalOpen) {
        // Trade mode - ensure we use integer keys
        const intResourceType = parseInt(resourceType);
        if (!selectedTradeGive[intResourceType]) selectedTradeGive[intResourceType] = 0;
        
        // Check if we can add more to trade
        if (selectedTradeGive[intResourceType] < currentCount) {
            selectedTradeGive[intResourceType]++;
            updateTradeGiveArea();
            updateTradeConfirmButton();
        }
    }
}

// Update discard area display
function updateDiscardArea() {
    const discardArea = document.getElementById('selected-discards');
    discardArea.innerHTML = '';
    
    let totalSelected = 0;
    const resourcePaths = GAME_CONSTANTS.RESOURCE_PATHS;
    
    Object.entries(selectedDiscards).forEach(([resource, count]) => {
        for (let i = 0; i < count; i++) {
            const img = document.createElement('img');
            img.src = resourcePaths[resource];
            img.className = 'selected-card';
            img.onclick = () => {
                // Ensure resource is an integer
                const intResource = parseInt(resource);
                selectedDiscards[intResource]--;
                if (selectedDiscards[intResource] === 0) delete selectedDiscards[intResource];
                
                // Re-show the card in available resources
                const availableCards = document.querySelectorAll('#discard-resource-cards .modal-resource-card');
                for (const card of availableCards) {
                    if (parseInt(card.dataset.resource) === intResource && card.style.display === 'none') {
                        card.style.display = '';
                        break;
                    }
                }
                
                updateDiscardArea();
            };
            discardArea.appendChild(img);
            totalSelected++;
        }
    });
    
    // Enable/disable confirm button
    const confirmBtn = document.getElementById('confirm-discard');
    confirmBtn.disabled = totalSelected !== requiredDiscards;
}

// Update trade give area display
function updateTradeGiveArea() {
    const tradeArea = document.getElementById('selected-trade-give');
    tradeArea.innerHTML = '';
    
    const resourcePaths = GAME_CONSTANTS.RESOURCE_PATHS;
    
    Object.entries(selectedTradeGive).forEach(([resource, count]) => {
        for (let i = 0; i < count; i++) {
            const img = document.createElement('img');
            img.src = resourcePaths[resource];
            img.className = 'selected-card';
            img.onclick = () => {
                // Ensure resource is an integer
                const intResource = parseInt(resource);
                selectedTradeGive[intResource]--;
                if (selectedTradeGive[intResource] === 0) delete selectedTradeGive[intResource];
                
                // Re-show the card in available resources
                const availableCards = document.querySelectorAll('#trade-resource-cards .modal-resource-card');
                for (const card of availableCards) {
                    if (parseInt(card.dataset.resource) === intResource && card.style.display === 'none') {
                        card.style.display = '';
                        break;
                    }
                }
                
                updateTradeGiveArea();
                updateTradeConfirmButton();
            };
            tradeArea.appendChild(img);
        }
    });
}

// Update trade confirm button state
function updateTradeConfirmButton() {
    const confirmBtn = document.getElementById('confirm-trade');
    const totalGive = Object.values(selectedTradeGive).reduce((a, b) => a + b, 0);
    
    // Check if valid trade ratio (4:1 bank trade for now)
    // TODO: Check port trades
    confirmBtn.disabled = totalGive < 4 || !selectedTradeGet;
}

// Initialize modal event handlers
function initModalHandlers() {
    console.log('Initializing modal handlers...');
    
    // Discard modal
    const discardModal = document.getElementById('discard-modal');
    const confirmDiscard = document.getElementById('confirm-discard');
    const cancelDiscard = document.getElementById('cancel-discard');
    
    confirmDiscard.onclick = () => {
        console.log('Confirm discard clicked');
        console.log('selectedDiscards:', selectedDiscards);
        
        // Check if any cards are selected
        if (!selectedDiscards || Object.keys(selectedDiscards).length === 0) {
            alert(`Please select ${requiredDiscards} cards to discard.`);
            return;
        }
        
        // Check if we have the right number of cards selected
        const totalSelected = Object.values(selectedDiscards).reduce((a, b) => a + b, 0);
        if (totalSelected !== requiredDiscards) {
            alert(`Please select exactly ${requiredDiscards} cards to discard. You have selected ${totalSelected}.`);
            return;
        }
        
        // Build discard payload - convert to array format [wood, brick, sheep, wheat, ore]
        const discardArray = [0, 0, 0, 0, 0];
        for (const [key, value] of Object.entries(selectedDiscards)) {
            const resourceIndex = parseInt(key);
            // Map UI indices to engine indices
            // UI: 0=brick, 1=grain, 2=lumber, 3=ore, 4=wool
            // Engine: 0=wood, 1=brick, 2=sheep, 3=wheat, 4=ore
            let engineIndex;
            switch(resourceIndex) {
                case 0: engineIndex = 1; break; // brick
                case 1: engineIndex = 3; break; // grain/wheat
                case 2: engineIndex = 0; break; // lumber/wood
                case 3: engineIndex = 4; break; // ore
                case 4: engineIndex = 2; break; // wool/sheep
            }
            discardArray[engineIndex] = value;
        }
        
        const discardPayload = {
            type: 'DISCARD',
            player: 0,
            value: discardArray
        }
        
        console.log('Discard payload:', discardPayload);
        console.log('Total cards to discard:', totalSelected);
        
        // Close modal first to prevent UI freeze
        discardModal.style.display = 'none';
        discardModalOpen = false;
        selectedDiscards = {};
        updateResourceBar(); // Refresh to remove click handlers
        
        // Then execute the action
        executeAction(discardPayload);
    };
    
    if (cancelDiscard) {
        cancelDiscard.onclick = () => {
            console.log('Cancel discard clicked - this should not normally be allowed during forced discard');
            // In Catan, you typically cannot cancel a discard when you have 8+ cards and a 7 is rolled
            // But we'll close the modal to prevent UI freeze
            discardModal.style.display = 'none';
            discardModalOpen = false;
            selectedDiscards = {};
            updateResourceBar(); // Refresh to remove click handlers
        };
    } else {
        console.log('Cancel discard button not found - skipping handler setup');
    }
    
    // Trade modal
    const tradeModal = document.getElementById('trade-modal');
    const confirmTrade = document.getElementById('confirm-trade');
    const cancelTrade = document.getElementById('cancel-trade');
    const tradeOptions = document.querySelectorAll('.trade-option');
    
    tradeOptions.forEach(btn => {
        btn.onclick = () => {
            tradeOptions.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedTradeGet = btn.dataset.resource;
            updateTradeConfirmButton();
        };
    });
    
    confirmTrade.onclick = () => {
        // Find the resource type and count to give
        const giveResource = Object.keys(selectedTradeGive)[0];
        const giveCount = Object.values(selectedTradeGive)[0];
        
        console.log('Maritime trade action:');
        console.log('  Give resource:', giveResource, '(parsed:', parseInt(giveResource), ')');
        console.log('  Give count:', giveCount);
        console.log('  Get resource:', selectedTradeGet, '(parsed:', parseInt(selectedTradeGet), ')');
        
        // Map UI resource indices to engine indices
        // UI: 0=brick, 1=grain, 2=lumber, 3=ore, 4=wool
        // Engine: 0=wood, 1=brick, 2=sheep, 3=wheat, 4=ore
        const uiToEngine = {
            0: 1,  // brick -> brick
            1: 3,  // grain -> wheat
            2: 0,  // lumber -> wood
            3: 4,  // ore -> ore
            4: 2   // wool -> sheep
        };
        
        const engineGiveRes = uiToEngine[parseInt(giveResource)];
        const engineGetRes = uiToEngine[parseInt(selectedTradeGet)];
        
        console.log('Mapped to engine indices:');
        console.log('  Give:', engineGiveRes, 'Count:', giveCount);
        console.log('  Get:', engineGetRes);
        
        // Find the matching maritime trade action from legal actions
        const maritimeActions = legalActions.filter(a => a.type === 'MARITIME_TRADE');
        console.log('Available maritime trade actions:', maritimeActions);
        
        // Find the action that matches our selection
        const matchingAction = maritimeActions.find(action => {
            if (!action.value || action.value.length !== 3) return false;
            const [actionGiveRes, actionGiveCount, actionGetRes] = action.value;
            return actionGiveRes === engineGiveRes && 
                   actionGiveCount === giveCount && 
                   actionGetRes === engineGetRes;
        });
        
        if (matchingAction) {
            console.log('Found matching action:', matchingAction);
            executeAction(matchingAction);
        } else {
            console.error('No matching maritime trade action found!');
            console.log('Looking for:', [parseInt(giveResource), giveCount, parseInt(selectedTradeGet)]);
            alert('This trade is not available. Please select a different trade.');
        }
        
        tradeModal.style.display = 'none';
        tradeModalOpen = false;
        updateResourceBar(); // Refresh to remove click handlers
    };
    
    cancelTrade.onclick = () => {
        tradeModal.style.display = 'none';
        tradeModalOpen = false;
        updateResourceBar(); // Refresh to remove click handlers
    };
    
    // Main action buttons
    const buyDevCardBtn = document.getElementById('buy-dev-card');
    console.log('Setting up buy dev card handler, button found:', !!buyDevCardBtn);
    console.log('Button element:', buyDevCardBtn);
    
    if (buyDevCardBtn) {
        console.log('Attaching click handler to buy dev card button');
        buyDevCardBtn.onclick = () => {
            console.log('Buy dev card clicked!');
            console.log('Legal actions:', legalActions);
            const action = legalActions.find(a => a.type === 'BUY_DEVELOPMENT_CARD');
            console.log('Found BUY_DEVELOPMENT_CARD action:', action);
            if (action) {
                console.log('Executing action:', action);
                executeAction(action);
            } else {
                console.log('No BUY_DEVELOPMENT_CARD action found in legal actions');
            }
        };
        
        // Test with a simple click handler
        buyDevCardBtn.addEventListener('click', function() {
            console.log('Simple click handler fired!');
        });
        
        console.log('Handlers attached successfully');
    } else {
        console.error('Buy dev card button not found!');
    }
    
    document.getElementById('buy-road').onclick = () => {
        console.log('Buy road clicked!');
        enablePlacementMode('road');
    };
    
    document.getElementById('buy-settlement').onclick = () => {
        enablePlacementMode('settlement');
    };
    
    document.getElementById('buy-city').onclick = () => {
        enablePlacementMode('city');
    };
}

// Handle dev card click
function handleDevCardClick(cardType) {
    console.log(`Dev card clicked: ${cardType}`);
    console.log('Current legal actions:', legalActions);
    
    // Check if player can play this dev card
    const canPlayActions = legalActions.filter(a => {
        if (cardType === 'KNIGHT' && a.type === 'PLAY_KNIGHT_CARD') return true;
        if (cardType === 'ROAD_BUILDING' && a.type === 'PLAY_ROAD_BUILDING') return true;
        if (cardType === 'YEAR_OF_PLENTY' && a.type === 'PLAY_YEAR_OF_PLENTY') return true;
        if (cardType === 'MONOPOLY' && a.type === 'PLAY_MONOPOLY') return true;
        return false;
    });
    
    console.log('Can play actions:', canPlayActions);
    
    if (canPlayActions.length > 0) {
        // Check which type of card and show appropriate modal if needed
        if (cardType === 'KNIGHT') {
            // Knight goes directly to robber placement
            executeAction(canPlayActions[0]);
        } else if (cardType === 'ROAD_BUILDING') {
            // Road building enables road placement mode
            executeAction(canPlayActions[0]);
            addLogEntry('Road Building: Place 2 roads for free', 'system');
        } else if (cardType === 'YEAR_OF_PLENTY') {
            // Show year of plenty modal
            showYearOfPlentyModal();
        } else if (cardType === 'MONOPOLY') {
            // Show monopoly modal
            showMonopolyModal();
        }
    } else {
        // Show message that card can't be played now
        console.log(`Cannot play ${cardType} card at this time`);
        // Add visual feedback
        addLogEntry(`Cannot play ${cardType} card yet. Dev cards bought this turn cannot be played until next turn.`, 'system');
    }
}

// Global state for dev card modals
let yopSelectedResources = [];
let monopolySelectedResource = null;

// Show Year of Plenty modal
function showYearOfPlentyModal() {
    const modal = document.getElementById('year-of-plenty-modal');
    
    // Reset state
    yopSelectedResources = [];
    
    // Reset UI
    document.querySelectorAll('.resource-option').forEach(btn => {
        btn.classList.remove('selected');
        btn.style.opacity = '1';
    });
    document.getElementById('yop-count').textContent = '0';
    document.getElementById('yop-selected-resources').innerHTML = '';
    document.getElementById('confirm-yop').disabled = true;
    
    modal.style.display = 'block';
}

// Show Monopoly modal
function showMonopolyModal() {
    const modal = document.getElementById('monopoly-modal');
    
    // Reset state
    monopolySelectedResource = null;
    
    // Reset UI
    document.querySelectorAll('.monopoly-option').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.getElementById('confirm-monopoly').disabled = true;
    
    modal.style.display = 'block';
}

// Initialize Year of Plenty and Monopoly handlers
function initDevCardModals() {
    // Year of Plenty handlers
    const yopModal = document.getElementById('year-of-plenty-modal');
    const yopOptions = document.querySelectorAll('.resource-option');
    const confirmYop = document.getElementById('confirm-yop');
    const cancelYop = document.getElementById('cancel-yop');
    
    yopOptions.forEach(btn => {
        btn.onclick = () => {
            if (yopSelectedResources.length < 2) {
                const resource = parseInt(btn.dataset.resource);
                yopSelectedResources.push(resource);
                
                // Update UI
                const resourceEmojis = ['🧱', '🌾', '🌲', '🪨', '🐑'];
                const selectedDiv = document.getElementById('yop-selected-resources');
                const span = document.createElement('span');
                span.textContent = resourceEmojis[resource];
                selectedDiv.appendChild(span);
                
                document.getElementById('yop-count').textContent = yopSelectedResources.length;
                
                if (yopSelectedResources.length === 2) {
                    confirmYop.disabled = false;
                    yopOptions.forEach(b => b.style.opacity = '0.5');
                }
            }
        };
    });
    
    confirmYop.onclick = () => {
        // Build resources object
        const resources = {};
        yopSelectedResources.forEach(r => {
            resources[r] = (resources[r] || 0) + 1;
        });
        
        executeAction({
            type: 'PLAY_YEAR_OF_PLENTY',
            player: 0,
            resources: resources
        });
        
        yopModal.style.display = 'none';
        yopSelectedResources = [];
    };
    
    cancelYop.onclick = () => {
        yopModal.style.display = 'none';
        yopSelectedResources = [];
    };
    
    // Monopoly handlers
    const monopolyModal = document.getElementById('monopoly-modal');
    const monopolyOptions = document.querySelectorAll('.monopoly-option');
    const confirmMonopoly = document.getElementById('confirm-monopoly');
    const cancelMonopoly = document.getElementById('cancel-monopoly');
    
    monopolyOptions.forEach(btn => {
        btn.onclick = () => {
            monopolyOptions.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            monopolySelectedResource = parseInt(btn.dataset.resource);
            confirmMonopoly.disabled = false;
        };
    });
    
    confirmMonopoly.onclick = () => {
        executeAction({
            type: 'PLAY_MONOPOLY',
            player: 0,
            resource: monopolySelectedResource
        });
        
        monopolyModal.style.display = 'none';
        monopolySelectedResource = null;
    };
    
    cancelMonopoly.onclick = () => {
        monopolyModal.style.display = 'none';
        monopolySelectedResource = null;
    };
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - initializing...');
    initGame();
    initModalHandlers();
    initDevCardModals();
    console.log('All initialization complete');
});