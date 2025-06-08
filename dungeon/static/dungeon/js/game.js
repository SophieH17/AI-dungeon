class DungeonGame {
    constructor() {
        this.setupContainer = document.getElementById('setup-container');
        this.gameInterface = document.getElementById('game-interface');
        this.gameContainer = document.getElementById('game-container');
        this.gameContent = document.getElementById('game-content');
        this.exitGameBtn = document.getElementById('exit-game-btn');
        this.commandForm = document.getElementById('command-form');
        this.commandInput = document.getElementById('command-input');
        this.submitBtn = document.getElementById('submit-btn');
        this.startGameBtn = document.getElementById('start-game-btn');
        this.downloadControls = document.querySelector('.download-controls');
        this.selectedWorld = 'fantasy'; // default world
        this.gameStarted = false;
        this.customWorldDescription = '';
        this.selectedPlayStyle = 'adventure'; // default play style
        
        // Initialize marked with options
        marked.setOptions({
            breaks: false,     // Changed from true to false to prevent automatic <br>
            gfm: true,
            headerIds: false,
            mangle: false,
            sanitize: false
        });
        
        this.initializeEventListeners();
        this.initializeCustomWorldPanel();
        this.initializePlayStyleSelector();
    }

    initializeEventListeners() {
        this.startGameBtn.addEventListener('click', () => this.startGame());
        this.commandForm.addEventListener('submit', (e) => this.handleCommand(e));
        
        // World selection buttons
        document.querySelectorAll('.world-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectWorld(btn));
        });

        document.getElementById('downloadTxt').addEventListener('click', () => this.downloadHistory('txt'));
        document.getElementById('downloadCsv').addEventListener('click', () => this.downloadHistory('csv'));
        this.exitGameBtn.addEventListener('click', () => this.exitToHome());
    }

    initializeCustomWorldPanel() {
        const customWorldBtn = document.getElementById('customWorldBtn');
        const customWorldPanel = document.getElementById('customWorldPanel');
        const saveCustomWorldBtn = document.getElementById('saveCustomWorld');
        const customWorldDescription = document.getElementById('customWorldDescription');

        customWorldBtn.addEventListener('click', () => {
            customWorldPanel.style.display = customWorldPanel.style.display === 'none' ? 'block' : 'none';
        });

        saveCustomWorldBtn.addEventListener('click', () => {
            const description = customWorldDescription.value.trim();
            if (description) {
                this.customWorldDescription = description;
                this.selectWorld(customWorldBtn);
                customWorldPanel.style.display = 'none';
            } else {
                alert('Please provide a description for your custom world.');
            }
        });
    }

    initializePlayStyleSelector() {
        document.querySelectorAll('.playstyle-btn').forEach(btn => {
            btn.addEventListener('click', () => this.selectPlayStyle(btn));
        });
    }

    selectWorld(btn) {
        // Only allow world selection before game starts
        if (this.gameStarted) {
            alert('You cannot change worlds during an active game. Please exit to homepage first.');
            return;
        }
        
        // Remove active class from all buttons
        document.querySelectorAll('.world-btn').forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        btn.classList.add('active');
        this.selectedWorld = btn.dataset.world;
    }

    selectPlayStyle(btn) {
        document.querySelectorAll('.playstyle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.selectedPlayStyle = btn.dataset.style;

        // If game is already started, update the play style
        if (this.gameStarted) {
            this.updatePlayStyle();
        }
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setLoading(isLoading) {
        this.submitBtn.disabled = isLoading;
        this.commandInput.disabled = isLoading;
        this.submitBtn.textContent = isLoading ? 'Processing...' : 'Send';
    }

    displayMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (type === 'user') {
            // User messages don't need markdown parsing
            messageDiv.textContent = `> ${message}`;
        } else {
            // Parse assistant messages as markdown with fallback
            try {
                messageDiv.innerHTML = marked.parse(message);
            } catch (e) {
                console.error('Markdown parsing failed:', e);
                messageDiv.textContent = message;  // Fallback to plain text
            }
        }
        
        this.gameContent.appendChild(messageDiv);
        this.gameContent.scrollTop = this.gameContent.scrollHeight;
    }

    async startGame() {
        this.setupContainer.style.display = 'none';
        this.gameInterface.style.display = 'block';
        
        this.setLoading(true);
        try {
            const worldData = {
                command: 'start',
                world: this.selectedWorld,
                playStyle: this.selectedPlayStyle,
                customWorldDescription: this.selectedWorld === 'custom' ? this.customWorldDescription : null
            };

            const response = await fetch('/dungeon/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(worldData),
            });
            
            const data = await response.json();
            this.displayMessage(data.message, 'assistant');
            this.gameStarted = true;
        } finally {
            this.setLoading(false);
        }
    }

    async handleCommand(e) {
        e.preventDefault();
        const command = this.commandInput.value.trim();
        if (!command) return;

        this.displayMessage(`> ${command}`, 'user');
        
        this.setLoading(true);
        try {
            const response = await fetch('/dungeon/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ 
                    command: command,
                    world: this.selectedWorld,
                    customWorldDescription: this.selectedWorld === 'custom' ? this.customWorldDescription : null
                }),
            });
            
            const data = await response.json();
            this.displayMessage(data.message, 'assistant');
        } finally {
            this.setLoading(false);
            this.commandInput.value = '';
        }
    }

    downloadHistory(format) {
        window.location.href = `/dungeon/download/${format}/`;
    }

    async updatePlayStyle() {
        this.setLoading(true);
        try {
            const response = await fetch('/dungeon/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ 
                    command: 'update_style',
                    world: this.selectedWorld,
                    playStyle: this.selectedPlayStyle,
                    customWorldDescription: this.selectedWorld === 'custom' ? this.customWorldDescription : null
                }),
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            this.displayMessage(data.message, 'assistant');
        } catch (error) {
            console.error('Error:', error);
            this.displayMessage('Error updating play style. Please try again.', 'error');
        }
        this.setLoading(false);
    }

    exitToHome() {
        if (confirm('Are you sure you want to exit? Your current game progress will be lost.')) {
            this.gameStarted = false;
            this.gameInterface.style.display = 'none';
            this.setupContainer.style.display = 'block';
            this.gameContent.innerHTML = '';
            this.game_history = [];
        }
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DungeonGame();
}); 