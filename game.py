# game.py
import numpy as np

ROWS = 6
COLS = 7

class Connect4Game:
    def __init__(self):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.turn = 1  # 1 for Player 1, 2 for Player 2
        self.game_over = False
        self.winner = None
        self.last_move = None

    def drop_piece(self, col):
        if not (0 <= col < COLS):
            return False
        if self.is_valid_location(col):
            row = self.get_next_open_row(col)
            self.board[row][col] = self.turn
            self.last_move = (row, col)
            self.check_win()
            return True
        return False

    def is_valid_location(self, col):
        if not (0 <= col < COLS):
            return False
        return self.board[0][col] == 0

    def get_next_open_row(self, col):
        for r in reversed(range(ROWS)):
            if self.board[r][col] == 0:
                return r
        return None

    def check_win(self):
        # Horizontal, vertical, diagonal checks for current turn
        for c in range(COLS - 3):
            for r in range(ROWS):
                if self.board[r][c] == self.turn and self.board[r][c+1] == self.turn and \
                   self.board[r][c+2] == self.turn and self.board[r][c+3] == self.turn:
                    self.winner = self.turn
                    self.game_over = True
                    return
        for c in range(COLS):
            for r in range(ROWS - 3):
                if self.board[r][c] == self.turn and self.board[r+1][c] == self.turn and \
                   self.board[r+2][c] == self.turn and self.board[r+3][c] == self.turn:
                    self.winner = self.turn
                    self.game_over = True
                    return
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if self.board[r][c] == self.turn and self.board[r+1][c+1] == self.turn and \
                   self.board[r+2][c+2] == self.turn and self.board[r+3][c+3] == self.turn:
                    self.winner = self.turn
                    self.game_over = True
                    return
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if self.board[r][c] == self.turn and self.board[r-1][c+1] == self.turn and \
                   self.board[r-2][c+2] == self.turn and self.board[r-3][c+3] == self.turn:
                    self.winner = self.turn
                    self.game_over = True
                    return
        if np.all(self.board != 0):
            self.winner = 0  # Draw
            self.game_over = True

    def switch_turn(self):
        self.turn = 1 if self.turn == 2 else 2

    def reset(self):
        self.__init__()
