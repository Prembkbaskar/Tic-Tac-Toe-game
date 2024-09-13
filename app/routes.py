from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
from app.models import Puzzle, db

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/puzzle/create', methods=['POST'])
def create_game():
    data = request.json
    player_x = data.get('player_x')
    player_o = data.get('player_o')
    board_size = data.get('board_size')

    if not player_x or not player_o or not board_size:
        return jsonify({"error":"missing required parameters"}),400

    new_game = Puzzle(
        board_size=board_size,
        board_state=",".join([""] * (board_size ** 2)),
        current_turn=player_x,
        status='NOT_STARTED',
        player_x=player_x,
        player_o=player_o
    )
    db.session.add(new_game)
    db.session.commit()

    return jsonify({
        'game_id': new_game.id,
        'status': new_game.status}),200

@app.route('/api/puzzle/join', methods=['POST'])
def join_game():
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')

    puzzle = Puzzle.query.get(game_id)
    if puzzle:
        if not puzzle.player_x:
            puzzle.player_x = player_id
        elif not puzzle.player_o:
            puzzle.player_o = player_id
            puzzle.set_status('IN_PROGRESS')  # Update status to 'IN_PROGRESS'
        else:
            return jsonify({'error': 'Game already has two players'}), 400

        db.session.commit()
        return jsonify({'status': 'Player joined successfully', 'game_status': puzzle.status})
    return jsonify({'error': 'Game not found'}), 404


@app.route('/api/puzzle/move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('game_id')
    move_position = data.get('move_position')
    player_id = data.get('player_id')

    game = Puzzle.query.get(game_id)
    print("move query ----",game)
    if not game or game.status != 'IN_PROGRESS':  # Ensure game is in progress
        return jsonify({"error": "Game not found or not in progress"}), 400

    board_state = game.board_state.split(",")
    index = move_position[0] * game.board_size + move_position[1]
    if board_state[index]:
        return jsonify({"error": "Cell already taken"}), 400

    board_state[index] = player_id
    game.board_state = ",".join(board_state)
    game.current_turn = game.player_o if player_id == game.player_x else game.player_x
    db.session.commit()
    return jsonify({"status": "IN_PROGRESS", "current_player": game.current_turn, "board_state": board_state})


@app.route('/api/puzzle/status/<int:game_id>', methods=['GET'])
def get_status(game_id):
    game = Puzzle.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    print (jsonify)

    return jsonify({
        'id': game.id,
        'board_size': game.board_size,
        'board_state': game.board_state,
        'current_turn': game.current_turn,
        'status': game.status,
        'player_x': game.player_x,
        'player_o': game.player_o,
        'created_at': game.created_at,
        'last_move_at': game.last_move_at
    })

@app.route('/api/puzzle/result/<int:game_id>', methods=['GET'])
def game_result(game_id):
    puzzle = Puzzle.query.get(game_id)
    if puzzle and puzzle.status == 'COMPLETE':
        return jsonify({'status': puzzle.status, 'board_state': puzzle.board_state})
    return jsonify({'error': 'Game not completed or not found'}), 404

@app.route('/api/puzzle/timeout', methods=['POST'])
def timeout():
    data = request.json
    game_id = data.get('game_id')
    puzzle = Puzzle.query.get(game_id)
    if puzzle and puzzle.status == 'IN_PROGRESS':
        if datetime.utcnow() - puzzle.last_move_at > timedelta(minutes=1):
            puzzle.set_status('TIME_OUT')
            db.session.commit()
            winner = 'O' if puzzle.current_turn == 'X' else 'X'
            return jsonify({'status': 'TIME_OUT', 'winner': winner})
    return jsonify({'error': 'Game not in progress or timeout not triggered'}), 400

def check_winner(board, size):
    # Check rows
    for i in range(size):
        if all(board[i*size + j] == board[i*size] and board[i*size] != '' for j in range(size)):
            return True

    # Check columns
    for i in range(size):
        if all(board[j*size + i] == board[i] and board[i] != '' for j in range(size)):
            return True

    # Check primary diagonal
    if all(board[i*size + i] == board[0] and board[0] != '' for i in range(size)):
        return True

    # Check secondary diagonal
    if all(board[i*size + (size-i-1)] == board[size-1] and board[size-1] != '' for i in range(size)):
        return True

    return False
