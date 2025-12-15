# gui.py
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QKeyEvent
from PySide6.QtCore import Qt, QTimer, QRect

from game import Connect4Game, ROWS, COLS
from levels import AIController
import random
import os

class BoardWidget(QWidget):
    def __init__(self, game, margin=40):
        super().__init__()
        self.game = game
        self.margin = margin
        base = "assets/images/"

        def load(path):
            pm = QPixmap(path) if os.path.exists(path) else QPixmap()
            return pm if not pm.isNull() else None

        # تحميل الصور
        self.bg_img = load(base + "background.png")
        self.board_img = load(base + "board.png")
        self.red_img = load(base + "red.png")
        self.yellow_img = load(base + "yellow.png")
        self.hl_img = load(base + "highlight.png")

        # متغيرات ديناميكية
        self.cell_size = 0
        self.board_rect = QRect(0, 0, 0, 0)

        # كاش للصور المعالجة
        self._cache = {
            "bg": None,
            "board": None,
            "red": None,
            "yellow": None,
            "hl": None,
            "size": (0, 0)
        }

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        if (w, h) != self._cache["size"]:
            self._cache["size"] = (w, h)
            self._cache.update({k: None for k in ["bg", "board", "red", "yellow", "hl"]})
        super().resizeEvent(event)

    def compute_layout(self):
        avail_w = max(0, self.width() - 2 * self.margin)
        avail_h = max(0, self.height() - 2 * self.margin)

        self.cell_size = min(avail_w // COLS if COLS else 0, avail_h // ROWS if ROWS else 0)
        if self.cell_size <= 0:
            self.cell_size = 1

        board_w = self.cell_size * COLS
        board_h = self.cell_size * ROWS

        x = (self.width() - board_w) // 2
        y = (self.height() - board_h) // 2
        self.board_rect = QRect(x, y, board_w, board_h)

    def _get_scaled(self, key, pixmap, target_w, target_h):
        cached = self._cache.get(key)
        if cached is None:
            if pixmap is None:
                return None
            scaled = pixmap.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._cache[key] = scaled
            return scaled
        return cached

    def paintEvent(self, event):
        self.compute_layout()
        painter = QPainter(self)

        # 1) الخلفية
        if self.bg_img:
            bg = self._get_scaled("bg", self.bg_img, self.width(), self.height())
            if bg:
                scaled = self.bg_img.scaled(
                    self.size(), 
                    Qt.KeepAspectRatioByExpanding, 
                    Qt.SmoothTransformation
                )
                x = (scaled.width() - self.width()) // 2
                y = (scaled.height() - self.height()) // 2
                painter.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
        else:
            painter.fillRect(self.rect(), QColor(18, 18, 25))

        # 2) صورة البورد
        if self.board_img:
            board_scaled = self._get_scaled("board", self.board_img, 
                                           self.board_rect.width(), self.board_rect.height())
            if board_scaled:
                bx = self.board_rect.x() + (self.board_rect.width() - board_scaled.width()) // 2
                by = self.board_rect.y() + (self.board_rect.height() - board_scaled.height()) // 2
                painter.drawPixmap(bx, by, board_scaled)
        else:
            painter.fillRect(self.board_rect, QColor(40, 40, 60))
        
        # 3) رسم القطع
        origin_x = self.board_rect.x()
        origin_y = self.board_rect.y()
        token_w = token_h = self.cell_size
        
        red_token = self._get_scaled("red", self.red_img, token_w, token_h) if self.red_img else None
        yellow_token = self._get_scaled("yellow", self.yellow_img, token_w, token_h) if self.yellow_img else None
        hl_token = self._get_scaled("hl", self.hl_img, token_w, token_h) if self.hl_img else None

        for r in range(ROWS):
            for c in range(COLS):
                piece = self.game.board[r][c]
                x = origin_x + c * self.cell_size
                y = origin_y + r * self.cell_size

                if piece == 1:
                    if red_token:
                        painter.drawPixmap(x, y, red_token)
                    else:
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setBrush(QBrush(QColor(220, 40, 40)))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(x + 4, y + 4, self.cell_size - 8, self.cell_size - 8)
                elif piece == 2:
                    if yellow_token:
                        painter.drawPixmap(x, y, yellow_token)
                    else:
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setBrush(QBrush(QColor(230, 200, 40)))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(x + 4, y + 4, self.cell_size - 8, self.cell_size - 8)

        # 4) إبراز آخر حركة
        if self.game.last_move:
            r, c = self.game.last_move
            x = origin_x + c * self.cell_size
            y = origin_y + r * self.cell_size
            if hl_token:
                painter.drawPixmap(x, y, hl_token)
            else:
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(Qt.NoBrush)
                pen = painter.pen()
                pen.setWidth(4)
                pen.setColor(QColor(180, 255, 180, 200))
                painter.setPen(pen)
                painter.drawEllipse(x + 6, y + 6, self.cell_size - 12, self.cell_size - 12)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        if not self.board_rect.contains(event.pos()):
            return
        col = (event.pos().x() - self.board_rect.x()) // self.cell_size
        parent = self.parent()
        if hasattr(parent, "on_board_click"):
            parent.on_board_click(col)

class GameWindow(QWidget):
    def __init__(self, mode='pvai', parent_menu=None, difficulty='medium'):
        super().__init__()
        self.setWindowTitle(f"Connect 4 - {difficulty.capitalize()} Difficulty")
        self.mode = mode
        self.parent_menu = parent_menu
        self.difficulty = difficulty

        self.game = Connect4Game()
        self.board_widget = BoardWidget(self.game)
        
        self.ai_player = 2
        self.ai = AIController.create_ai(difficulty, self.ai_player)

        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.run_ai_turn)

        self.init_ui()
        self.showFullScreen()

        if self.mode == "aivai":
            QTimer.singleShot(300, lambda: self.ai_timer.start(500))

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # العنوان
        title_text = f"Connect 4 - {self.difficulty.capitalize()} Difficulty"
        if self.mode == 'pvp':
            title_text = "Connect 4 - Player vs Player"
        elif self.mode == 'aivai':
            title_text = "Connect 4 - AI vs AI"
            
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22pt; 
            font-weight: bold; 
            color: white;
            background-color: rgba(0, 0, 0, 120);
            padding: 10px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 50);
        """)
        layout.addWidget(title)

        # مؤشر الدور
        self.turn_label = QLabel()
        self.update_turn_indicator()
        self.turn_label.setAlignment(Qt.AlignCenter)
        self.turn_label.setStyleSheet("""
            font-size: 14pt; 
            font-weight: bold; 
            color: #FFD700;
            background-color: rgba(0, 0, 0, 80);
            padding: 8px;
            border-radius: 5px;
        """)
        layout.addWidget(self.turn_label)

        # البورد
        board_container = QHBoxLayout()
        board_container.addStretch(1)
        board_container.addWidget(self.board_widget, 10)
        board_container.addStretch(1)
        layout.addLayout(board_container)

        # أزرار التحكم
        btn_layout = QHBoxLayout()
        restart_btn = QPushButton("🔄 Restart")
        menu_btn = QPushButton("🏠 Menu")
        fullscreen_btn = QPushButton("📺 Toggle Fullscreen")

        for b in (restart_btn, menu_btn, fullscreen_btn):
            b.setFixedHeight(45)
            b.setStyleSheet("""
                QPushButton {
                    font-size: 12pt;
                    font-weight: bold;
                    background-color: rgba(42, 42, 58, 180);
                    color: white;
                    border: 2px solid rgba(100, 100, 150, 150);
                    border-radius: 8px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: rgba(62, 62, 78, 200);
                    border-color: rgba(150, 150, 200, 200);
                }
                QPushButton:pressed {
                    background-color: rgba(32, 32, 48, 180);
                }
            """)

        restart_btn.clicked.connect(self.restart_game)
        menu_btn.clicked.connect(self.back_to_menu)
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        btn_layout.addStretch(1)
        btn_layout.addWidget(restart_btn)
        btn_layout.addWidget(menu_btn)
        btn_layout.addWidget(fullscreen_btn)
        btn_layout.addStretch(1)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.board_widget.setParent(self)

    def update_turn_indicator(self):
        if hasattr(self, 'turn_label'):
            player_text = "🔴 Player 1 (Red)" if self.game.turn == 1 else "🟡 Player 2 (Yellow)"
            if self.mode == 'pvai' and self.game.turn == self.ai_player:
                player_text = f"🤖 AI ({self.difficulty.capitalize()})"
            self.turn_label.setText(f"Current Turn: {player_text}")

    def on_board_click(self, col):
        if not (0 <= col < COLS):
            return
        if self.mode == 'pvp' or (self.mode == 'pvai' and self.game.turn != self.ai_player):
            if self.game.drop_piece(col):
                self.board_widget.update()
                if self.game.game_over:
                    self.show_winner()
                    return
                self.game.switch_turn()
                self.update_turn_indicator()
                if self.mode == 'pvai' and self.game.turn == self.ai_player:
                    QTimer.singleShot(50, self.ai_move)

    def ai_move(self):
        """حركة الذكاء الاصطناعي مع تصحيح"""
        if self.game.game_over:
            return
        
        # طباعة معلومات تصحيح (يمكن إزالتها لاحقاً)
        valid_moves = [c for c in range(COLS) if self.game.is_valid_location(c)]
        print(f"[DEBUG] {self.difficulty.upper()} AI - الحركات المتاحة: {valid_moves}")
        
        move = self.ai.get_best_move(self.game)
        print(f"[DEBUG] {self.difficulty.upper()} AI اختار: العمود {move}")
        
        if move is None or not self.game.is_valid_location(move):
            print(f"[DEBUG] حركة غير صالحة، اختيار عشوائي")
            if valid_moves:
                move = random.choice(valid_moves)
            else:
                return
        
        self.game.drop_piece(move)
        self.board_widget.update()
        
        if self.game.game_over:
            self.show_winner()
        else:
            self.game.switch_turn()
            self.update_turn_indicator()

    def run_ai_turn(self):
        if self.game.game_over:
            return
        
        move = self.ai.get_best_move(self.game)
        
        if move is None or not self.game.is_valid_location(move):
            valid = [c for c in range(COLS) if self.game.is_valid_location(c)]
            if not valid:
                return
            move = random.choice(valid)
        
        self.game.drop_piece(move)
        self.board_widget.update()
        if self.game.game_over:
            self.ai_timer.stop()
            self.show_winner()
        else:
            self.game.switch_turn()
            self.update_turn_indicator()

    def show_winner(self):
        if self.ai_timer.isActive():
            self.ai_timer.stop()
        
        msg = QMessageBox(self)
        msg.setWindowTitle("🎮 Game Over!")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgba(20, 20, 30, 220);
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14pt;
            }
            QPushButton {
                background-color: rgba(42, 42, 58, 180);
                color: white;
                border: 2px solid rgba(100, 100, 150, 150);
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(62, 62, 78, 200);
            }
        """)
        
        if self.game.winner == 0:
            msg.setText("🤝 It's a Draw!")
            msg.setInformativeText("The board is full with no winner.")
        else:
            winner_text = ""
            if self.mode == 'pvai' and self.game.winner == self.ai_player:
                winner_text = f"🏆 AI ({self.difficulty.capitalize()}) Wins!"
            else:
                winner_text = f"🏆 Player {self.game.winner} Wins!"
            
            msg.setText(winner_text)
            color = "🔴 Red" if self.game.winner == 1 else "🟡 Yellow"
            msg.setInformativeText(f"{color} player connected 4 pieces!")
        
        msg.addButton("🔄 Play Again", QMessageBox.AcceptRole)
        msg.addButton("🏠 Main Menu", QMessageBox.RejectRole)
        
        result = msg.exec()
        
        if result == QMessageBox.AcceptRole:
            self.restart_game()
        elif result == QMessageBox.RejectRole:
            self.back_to_menu()

    def restart_game(self):
        if self.ai_timer.isActive():
            self.ai_timer.stop()
        
        self.game.reset()
        self.board_widget.update()
        self.update_turn_indicator()
        self.ai = AIController.create_ai(self.difficulty, self.ai_player)
        
        if self.mode == "aivai":
            QTimer.singleShot(200, lambda: self.ai_timer.start(500))

    def back_to_menu(self):
        if self.ai_timer.isActive():
            self.ai_timer.stop()
        self.close()
        if self.parent_menu:
            self.parent_menu.showFullScreen()
            self.parent_menu.show()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_R:
            self.restart_game()
        elif event.key() == Qt.Key_M:
            self.back_to_menu()
        elif event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)