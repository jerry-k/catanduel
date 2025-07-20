/**
 * UI update functions for CatanDuel.
 * Handles updating the DOM based on game state.
 */

// Update player information panels
function updatePlayerInfo() {
    if (!gameState) return;
    
    for (let i = 0; i < gameState.players.length; i++) {
        const player = gameState.players[i];
        const playerSection = document.getElementById(`player-${i}-info`);
        
        // Update active state
        if (player.is_active) {
            playerSection.classList.add('active');
        } else {
            playerSection.classList.remove('active');
        }
        
        // Update name
        playerSection.querySelector('.player-name').textContent = player.name;
        
        // Update resources
        const resourcesDiv = document.getElementById(`player-${i}-resources`);
        resourcesDiv.innerHTML = `
            <div class="resource-item">
                <span class="resource-icon">🪵</span>
                <span class="resource-count">${player.resources.wood}</span>
            </div>
            <div class="resource-item">
                <span class="resource-icon">🧱</span>
                <span class="resource-count">${player.resources.brick}</span>
            </div>
            <div class="resource-item">
                <span class="resource-icon">🐑</span>
                <span class="resource-count">${player.resources.sheep}</span>
            </div>
            <div class="resource-item">
                <span class="resource-icon">🌾</span>
                <span class="resource-count">${player.resources.wheat}</span>
            </div>
            <div class="resource-item">
                <span class="resource-icon">⛰️</span>
                <span class="resource-count">${player.resources.ore}</span>
            </div>
        `;
        
        // Update stats
        document.getElementById(`player-${i}-vps`).textContent = player.public_vps;
        document.getElementById(`player-${i}-knights`).textContent = player.knights_played;
        
        // Update dev cards count
        const devCardCount = player.dev_cards.knight + player.dev_cards.victory_point +
                           player.dev_cards.road_building + player.dev_cards.year_of_plenty +
                           player.dev_cards.monopoly;
        document.getElementById(`player-${i}-dev-cards`).textContent = devCardCount;
        
        // Add badges for longest road / largest army
        let badges = '';
        if (player.has_longest_road) {
            badges += ' 🛤️';
        }
        if (player.has_largest_army) {
            badges += ' ⚔️';
        }
        if (badges) {
            playerSection.querySelector('.player-name').textContent += badges;
        }
    }
    
    // Update game info
    document.getElementById('turn-number').textContent = gameState.turn_number;
    document.getElementById('game-phase').textContent = gameState.phase.charAt(0).toUpperCase() + gameState.phase.slice(1);
}

// Update action buttons based on valid actions
function updateActionButtons() {
    if (!gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player];
    const isHumanTurn = currentPlayer.is_human;
    
    // Hide all buttons first
    document.getElementById('roll-button').style.display = 'none';
    document.getElementById('end-turn-button').style.display = 'none';
    document.getElementById('buy-dev-card-button').style.display = 'none';
    document.getElementById('build-actions').style.display = 'none';
    document.getElementById('dev-card-actions').style.display = 'none';
    document.getElementById('trade-actions').style.display = 'none';
    
    if (!isHumanTurn) {
        // AI turn - no buttons
        return;
    }
    
    // Show buttons based on valid actions
    const validActionTypes = gameState.valid_actions.map(a => a.type);
    
    if (validActionTypes.includes('ROLL')) {
        document.getElementById('roll-button').style.display = 'block';
    }
    
    if (validActionTypes.includes('END_TURN')) {
        document.getElementById('end-turn-button').style.display = 'block';
    }
    
    if (validActionTypes.includes('BUY_DEVELOPMENT_CARD')) {
        document.getElementById('buy-dev-card-button').style.display = 'block';
    }
    
    // Building actions
    const hasBuildActions = validActionTypes.some(type => 
        type === 'BUILD_ROAD' || type === 'BUILD_SETTLEMENT' || type === 'BUILD_CITY' ||
        type === 'BUILD_INITIAL_ROAD' || type === 'BUILD_INITIAL_SETTLEMENT'
    );
    
    if (hasBuildActions || gameState.phase === 'setup') {
        document.getElementById('build-actions').style.display = 'block';
        updateBuildButtons();
    }
    
    // Dev card actions
    if (currentPlayer.dev_cards.knight > 0 || currentPlayer.dev_cards.road_building > 0 ||
        currentPlayer.dev_cards.year_of_plenty > 0 || currentPlayer.dev_cards.monopoly > 0) {
        updateDevCardButtons();
        document.getElementById('dev-card-actions').style.display = 'block';
    }
    
    // Trade actions
    if (gameState.phase === 'main' && gameState.dice_rolled) {
        document.getElementById('trade-actions').style.display = 'block';
    }
    
    // Special phase handling
    if (gameState.phase === 'setup') {
        // Auto-start building mode for setup
        const validActions = gameState.valid_actions;
        if (validActions.length > 0) {
            const firstAction = validActions[0];
            if (firstAction.type === 'BUILD_INITIAL_SETTLEMENT') {
                startBuildingMode('settlement');
            } else if (firstAction.type === 'BUILD_INITIAL_ROAD') {
                startBuildingMode('road');
            }
        }
    }
}

// Update building buttons
function updateBuildButtons() {
    const buildSection = document.getElementById('build-actions');
    buildSection.innerHTML = '<h3>Build</h3>';
    
    const validActionTypes = gameState.valid_actions.map(a => a.type);
    const currentPlayer = gameState.players[gameState.current_player];
    
    // Road button
    if (validActionTypes.includes('BUILD_ROAD') || validActionTypes.includes('BUILD_INITIAL_ROAD')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => startBuildingMode('road');
        
        if (gameState.phase === 'setup') {
            btn.textContent = 'Place Road';
        } else {
            btn.textContent = 'Build Road (1🪵 1🧱)';
            btn.disabled = !canAffordRoad(currentPlayer);
        }
        buildSection.appendChild(btn);
    }
    
    // Settlement button
    if (validActionTypes.includes('BUILD_SETTLEMENT') || validActionTypes.includes('BUILD_INITIAL_SETTLEMENT')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => startBuildingMode('settlement');
        
        if (gameState.phase === 'setup') {
            btn.textContent = 'Place Settlement';
        } else {
            btn.textContent = 'Build Settlement (1🪵 1🧱 1🐑 1🌾)';
            btn.disabled = !canAffordSettlement(currentPlayer);
        }
        buildSection.appendChild(btn);
    }
    
    // City button
    if (validActionTypes.includes('BUILD_CITY')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => startBuildingMode('city');
        btn.textContent = 'Build City (2🌾 3⛰️)';
        btn.disabled = !canAffordCity(currentPlayer);
        buildSection.appendChild(btn);
    }
}

// Update dev card buttons
function updateDevCardButtons() {
    const devCardSection = document.getElementById('dev-card-actions');
    devCardSection.innerHTML = '<h3>Development Cards</h3>';
    
    const currentPlayer = gameState.players[gameState.current_player];
    const validActionTypes = gameState.valid_actions.map(a => a.type);
    
    if (currentPlayer.dev_cards.knight > 0 && validActionTypes.includes('PLAY_KNIGHT')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => playKnight();
        btn.textContent = `Play Knight (${currentPlayer.dev_cards.knight})`;
        devCardSection.appendChild(btn);
    }
    
    if (currentPlayer.dev_cards.road_building > 0 && validActionTypes.includes('PLAY_ROAD_BUILDING')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => playRoadBuilding();
        btn.textContent = `Play Road Building (${currentPlayer.dev_cards.road_building})`;
        devCardSection.appendChild(btn);
    }
    
    if (currentPlayer.dev_cards.year_of_plenty > 0 && validActionTypes.includes('PLAY_YEAR_OF_PLENTY')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => playYearOfPlenty();
        btn.textContent = `Play Year of Plenty (${currentPlayer.dev_cards.year_of_plenty})`;
        devCardSection.appendChild(btn);
    }
    
    if (currentPlayer.dev_cards.monopoly > 0 && validActionTypes.includes('PLAY_MONOPOLY')) {
        const btn = document.createElement('button');
        btn.className = 'action-button';
        btn.onclick = () => playMonopoly();
        btn.textContent = `Play Monopoly (${currentPlayer.dev_cards.monopoly})`;
        devCardSection.appendChild(btn);
    }
}

// Update game message
function updateMessage(message) {
    document.getElementById('message-text').textContent = message || '';
}

// Resource affordability checks
function canAffordRoad(player) {
    return player.resources.wood >= 1 && player.resources.brick >= 1;
}

function canAffordSettlement(player) {
    return player.resources.wood >= 1 && player.resources.brick >= 1 &&
           player.resources.sheep >= 1 && player.resources.wheat >= 1;
}

function canAffordCity(player) {
    return player.resources.wheat >= 2 && player.resources.ore >= 3;
}

function canAffordDevCard(player) {
    return player.resources.sheep >= 1 && player.resources.wheat >= 1 &&
           player.resources.ore >= 1;
}

// Dice animation
function animateDiceRoll(die1, die2) {
    const diceContainer = document.getElementById('dice-container');
    const die1Element = document.getElementById('die1');
    const die2Element = document.getElementById('die2');
    
    diceContainer.style.display = 'flex';
    
    // Animate rolling
    let rolls = 0;
    const rollInterval = setInterval(() => {
        die1Element.textContent = Math.floor(Math.random() * 6) + 1;
        die2Element.textContent = Math.floor(Math.random() * 6) + 1;
        rolls++;
        
        if (rolls > 10) {
            clearInterval(rollInterval);
            die1Element.textContent = die1;
            die2Element.textContent = die2;
            
            // Hide after 2 seconds
            setTimeout(() => {
                diceContainer.style.display = 'none';
            }, 2000);
        }
    }, 100);
}

// Development card actions
async function playKnight() {
    await executeAction({
        type: 'PLAY_KNIGHT',
        data: {}
    });
}

async function playRoadBuilding() {
    await executeAction({
        type: 'PLAY_ROAD_BUILDING',
        data: {}
    });
}

async function playYearOfPlenty() {
    // TODO: Show resource selection dialog
    // For now, just take wood and brick
    await executeAction({
        type: 'PLAY_YEAR_OF_PLENTY',
        data: {
            resource1: 'wood',
            resource2: 'brick'
        }
    });
}

async function playMonopoly() {
    // TODO: Show resource selection dialog
    // For now, just take wood
    await executeAction({
        type: 'PLAY_MONOPOLY',
        data: {
            resource: 'wood'
        }
    });
}