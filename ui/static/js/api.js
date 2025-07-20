/**
 * API communication layer for CatanDuel.
 * Handles all server communication.
 */

class GameAPI {
    constructor() {
        this.baseUrl = '';  // Use relative URLs
    }

    /**
     * Create a new game
     * @param {Object} config - Game configuration
     * @returns {Promise<Object>} Game state
     */
    async newGame(config) {
        try {
            const response = await fetch(`${this.baseUrl}/api/new_game`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create game');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error creating new game:', error);
            throw error;
        }
    }

    /**
     * Get current game state
     * @returns {Promise<Object>} Game state
     */
    async getState() {
        try {
            const response = await fetch(`${this.baseUrl}/api/game_state`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to get game state');
            }

            const data = await response.json();
            return data.state;
        } catch (error) {
            console.error('Error getting game state:', error);
            throw error;
        }
    }

    /**
     * Execute a game action
     * @param {Object} action - Action to execute
     * @returns {Promise<Object>} New state and events
     */
    async executeAction(action) {
        try {
            const response = await fetch(`${this.baseUrl}/api/action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(action)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to execute action');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error executing action:', error);
            throw error;
        }
    }

    /**
     * Get valid actions for current state
     * @returns {Promise<Array>} List of valid actions
     */
    async getValidActions() {
        try {
            const response = await fetch(`${this.baseUrl}/api/valid_actions`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to get valid actions');
            }

            const data = await response.json();
            return data.actions;
        } catch (error) {
            console.error('Error getting valid actions:', error);
            throw error;
        }
    }

    /**
     * Get AI action without executing
     * @returns {Promise<Object|null>} AI action or null
     */
    async getAIAction() {
        try {
            const response = await fetch(`${this.baseUrl}/api/ai_action`, {
                method: 'POST'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to get AI action');
            }

            const data = await response.json();
            return data.action;
        } catch (error) {
            console.error('Error getting AI action:', error);
            throw error;
        }
    }

    /**
     * Get debug state information
     * @returns {Promise<Object>} Debug info
     */
    async getDebugState() {
        try {
            const response = await fetch(`${this.baseUrl}/api/debug/state`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to get debug state');
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting debug state:', error);
            throw error;
        }
    }
}

// Create global API instance
const gameAPI = new GameAPI();