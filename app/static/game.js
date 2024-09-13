let currentPlayer = 'X';
let gameId = null; 

// DOM elements
const boardElement = document.getElementById('game-board');
const restartButton = document.getElementById('restart-btn');
const statusElement = document.getElementById('status');

// Initialize the game board
function initializeBoard(size = 3) {
    boardElement.innerHTML = '';
    for (let i = 0; i < size * size; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.index = i;
        cell.addEventListener('click', handleCellClick);
        boardElement.appendChild(cell);
    }

    // Adjust board size dynamically
    boardElement.style.gridTemplateColumns = `repeat(${size}, 100px)`;
    boardElement.style.gridTemplateRows = `repeat(${size}, 100px)`;
    statusElement.textContent = ''; // Clear status message
}

// Handle cell click
function handleCellClick(event) {
    const index = event.target.dataset.index;
    if (!gameId || !currentPlayer) return; 
    
    fetch(`/api/puzzle/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            game_id: gameId,
            move_position: [Math.floor(index / 3), index % 3],
            player_id: currentPlayer
        })
    })
    .then(response => response.json())
    .then(data => {
        updateGameUI(data);
    })
    .catch(err => console.error('Error making move:', err));
}

// Polling for game status
let pollingActive = false;

function pollGameStatus() {
    if (!gameId) {
        console.error('Game ID is not defined');
        return;
    }

    if (pollingActive) {
        console.warn('Polling is already active');
        return;
    }

    pollingActive = true;

    // Poll every 3 seconds
    const intervalId = setInterval(() => {
        fetch(`/api/puzzle/status/${gameId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                updateGameUI(data);
            })
            .catch(err => {
                console.error('Error fetching game status:', err);
            });
    }, 3000);

    // Optionally, return intervalId if you need to clear the interval later
    return intervalId;
}

// Example function to stop polling
function stopPolling(intervalId) {
    clearInterval(intervalId);
    pollingActive = false;
}


// Update the UI based on game data
function updateGameUI(data) {
    if (data.board_state) {
        const cells = boardElement.getElementsByClassName('cell');
        data.board_state.forEach((value, index) => {
            cells[index].textContent = value;
        });
    }

    if (data.current_player) {
        currentPlayer = data.current_player;
    }

    if (data.status) {
        statusElement.textContent = data.status;
    }

    // Optionally handle win/draw messages or game completion
    if (data.status === 'COMPLETE') {
        alert(data.message);
    }
}

// Handle form submission to create or join a game
document.getElementById('size-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const size = parseInt(document.getElementById('board-size').value, 10);
    const playerX = document.getElementById('player-x').value.trim();
    const playerO = document.getElementById('player-o').value.trim();
    
    if (size >= 3 && playerX && playerO) {
        fetch('/api/puzzle/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_x: playerX,
                player_o: playerO,
                board_size: size
            })
        })
        .then(response => response.json())
        .then(data => {
            gameId = data.game_id;
            initializeBoard(size);
            pollGameStatus();
            restartButton.style.display = 'inline';
        })
        .catch(err => console.error('Error creating game:', err));
    } else {
        alert('Please enter valid names and board size.');
    }
});

restartButton.addEventListener('click', () => {
    initializeBoard(3); 
    gameId = null;
    currentPlayer = 'X'; 
});
