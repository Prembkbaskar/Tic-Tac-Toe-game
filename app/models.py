from datetime import datetime
from app import db

class Puzzle(db.Model):
    __tablename__ = 'puzzle'
    id = db.Column(db.Integer, primary_key=True)
    board_size = db.Column(db.Integer, nullable=False)
    board_state = db.Column(db.Text, nullable=False)  # Board state as a string
    current_turn = db.Column(db.String(1), nullable=False)  # 'X' or 'O'
    status = db.Column(db.String(20), nullable=False, default='NOT_STARTED')  # Game status
    player_x = db.Column(db.String(100), nullable=True)  # Player X ID
    player_o = db.Column(db.String(100), nullable=True)  # Player O ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_move_at = db.Column(db.DateTime, default=datetime.utcnow)

    def update_last_move(self):
        self.last_move_at = datetime.utcnow()

    def set_status(self, status):
        self.status = status
        db.session.commit()
