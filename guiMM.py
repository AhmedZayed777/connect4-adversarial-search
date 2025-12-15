from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QComboBox,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QKeyEvent
from PySide6.QtCore import Qt
import os

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect 4 - Main Menu")
        self.background_img = None
        self.load_background()
        self.init_ui()

    def load_background(self):
        """تحميل صورة خلفية Main Menu"""
        base = "assets/images/"
        bg_path = base + "backgroundM.png"
        
        if os.path.exists(bg_path):
            self.background_img = QPixmap(bg_path)
        else:
            print(f"⚠️  تحذير: ملف الخلفية غير موجود: {bg_path}")
            self.background_img = None

    def paintEvent(self, event):
        """رسم الخلفية لتغطية كامل الشاشة"""
        if self.background_img and not self.background_img.isNull():
            painter = QPainter(self)
            
            # حساب الأبعاد لتغطية كامل الشاشة مع الحفاظ على نسبة العرض
            widget_size = self.size()
            img_size = self.background_img.size()
            
            # Scale the image to fill the widget while preserving aspect ratio
            scaled = self.background_img.scaled(
                widget_size, 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            # Calculate position to center the image
            x = (scaled.width() - widget_size.width()) // 2
            y = (scaled.height() - widget_size.height()) // 2
            
            # Draw the image
            painter.drawPixmap(0, 0, scaled, x, y, widget_size.width(), widget_size.height())
        else:
            # Fallback: solid color background
            super().paintEvent(event)
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(18, 18, 25))

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        # Title
        title = QLabel("Connect 4 - Minimax AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32pt; 
            font-weight: bold; 
            color: white;
            background-color: rgba(0, 0, 0, 120);
            border-radius: 10px;
            padding: 20px;
            border: 2px solid rgba(255, 255, 255, 50);
        """)
        layout.addWidget(title)

        # Difficulty selection
        difficulty_label = QLabel("Select Difficulty:")
        difficulty_label.setStyleSheet("""
            font-size: 16pt; 
            color: white;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 100);
            padding: 10px;
            border-radius: 8px;
        """)
        difficulty_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(difficulty_label)
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setCurrentText("Medium")
        self.difficulty_combo.setFixedHeight(50)
        self.difficulty_combo.setStyleSheet("""
            QComboBox {
                font-size: 14pt;
                padding: 10px;
                background-color: rgba(42, 42, 58, 200);
                color: white;
                border: 2px solid rgba(100, 100, 150, 150);
                border-radius: 8px;
                selection-background-color: rgba(80, 80, 120, 200);
            }
            QComboBox:hover {
                border-color: rgba(150, 150, 200, 200);
                background-color: rgba(52, 52, 68, 200);
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-top: 8px solid white;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(42, 42, 58, 200);
                color: white;
                selection-background-color: rgba(80, 80, 120, 200);
                border: 1px solid rgba(100, 100, 150, 150);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.difficulty_combo)

        # Difficulty description
        self.difficulty_desc = QLabel("Medium: Balanced performance and speed")
        self.difficulty_desc.setAlignment(Qt.AlignCenter)
        self.difficulty_desc.setStyleSheet("""
            font-size: 12pt; 
            color: rgba(200, 200, 255, 200); 
            font-style: italic;
            background-color: rgba(0, 0, 0, 80);
            padding: 8px;
            border-radius: 5px;
        """)
        self.difficulty_desc.setWordWrap(True)
        layout.addWidget(self.difficulty_desc)
        
        # Update description when difficulty changes
        self.difficulty_combo.currentTextChanged.connect(self.update_difficulty_desc)

        # Buttons
        pvp_btn = QPushButton("🎮 Player vs Player")
        pvai_btn = QPushButton("🤖 Player vs AI")
        aivai_btn = QPushButton("⚔️ AI vs AI")
        exit_btn = QPushButton("🚪 Exit")

        # Button styling
        button_style = """
            QPushButton {
                font-size: 16pt;
                font-weight: bold;
                background-color: rgba(42, 42, 58, 200);
                color: white;
                border: 2px solid rgba(100, 100, 150, 150);
                border-radius: 12px;
                padding: 15px;
                min-height: 60px;
            }
            QPushButton:hover {
                background-color: rgba(62, 62, 78, 220);
                border-color: rgba(150, 150, 200, 200);
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(32, 32, 48, 200);
                border-color: rgba(80, 80, 130, 200);
            }
        """
        
        for b in (pvp_btn, pvai_btn, aivai_btn, exit_btn):
            b.setFixedHeight(60)
            b.setStyleSheet(button_style)

        # Connect buttons - GameWindow will be imported dynamically
        pvp_btn.clicked.connect(lambda: self.start_game('pvp'))
        pvai_btn.clicked.connect(lambda: self.start_game('pvai'))
        aivai_btn.clicked.connect(lambda: self.start_game('aivai'))
        exit_btn.clicked.connect(self.close)

        # Add vertical spacing
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(pvp_btn)
        layout.addWidget(pvai_btn)
        layout.addWidget(aivai_btn)
        layout.addWidget(exit_btn)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Keyboard shortcuts info
        shortcuts_label = QLabel("Shortcuts: F11 - Fullscreen | Esc - Exit Fullscreen")
        shortcuts_label.setAlignment(Qt.AlignCenter)
        shortcuts_label.setStyleSheet("""
            font-size: 10pt; 
            color: rgba(150, 150, 200, 150);
            background-color: rgba(0, 0, 0, 80);
            padding: 5px;
            border-radius: 3px;
        """)
        layout.addWidget(shortcuts_label)

        self.setLayout(layout)

    def update_difficulty_desc(self, difficulty):
        """تحديث وصف مستوى الصعوبة"""
        descriptions = {
            "Easy": "🤖 Easy - Shallow search with some randomness",
            "Medium": "⚡ Medium - Balanced performance and speed",
            "Hard": "🧠 Hard - Advanced search with Alpha-Beta pruning"
        }
        self.difficulty_desc.setText(descriptions.get(difficulty, ""))

    def start_game(self, mode):
        """بدء اللعبة مع الوضع المختار"""
        self.hide()
        difficulty = self.difficulty_combo.currentText().lower()
        
        # استيراد GameWindow بشكل ديناميكي لتجنب استيرادات دائرية
        from gui import GameWindow
        self.game_window = GameWindow(mode, parent_menu=self, difficulty=difficulty)
        self.game_window.show()

    def keyPressEvent(self, event: QKeyEvent):
        """معالجة أحداث لوحة المفاتيح"""
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)