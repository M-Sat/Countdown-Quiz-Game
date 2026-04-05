import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt5.QtGui import QIcon, QFont, QCursor, QPainter, QColor, QPen, QLinearGradient, QPixmap
PROGRAMS = [
    {
        "file":        "numbersgame.py",        
        "title":       "NUMBERS GAME",
        "subtitle":    "Countdown",
        "description": "Draw 6 numbers and reach\nthe target using arithmetic.",
        "icon":        "images/num.png",
        "color":       "#3498db",
        "hover":       "#66bbff",
    },
    {
        "file":        "lettersgame.py",         
        "title":       "LETTERS GAME",
        "subtitle":    "Countdown",
        "description": "Draw 9 letters and find\nthe longest word you can.",
        "icon":        "images/let.png",
        "color":       "#e67e22",
        "hover":       "#f39c12",
    },
]
class GameCard(QFrame):
    """A styled clickable card for each game."""
    def __init__(self, program: dict, parent=None):
        super().__init__(parent)
        self.program = program
        self.base_color = program["color"]
        self.hover_color = program["hover"]
        self._is_hovered = False
        self.setFixedSize(500, 580)  # BIGGER CARDS
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("gameCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 55, 45, 55)  # more internal padding
        layout.setSpacing(20)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(QPixmap(program["icon"]).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # bigger icon
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 72px; background: transparent;")
        layout.addWidget(icon_lbl)
        sub_lbl = QLabel(program["subtitle"].upper())
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(
            f"color: {program['color']}; font-size: 16px; font-weight: bold;"  
            "letter-spacing: 6px; background: transparent;"
        )
        layout.addWidget(sub_lbl)
        title_lbl = QLabel(program["title"])
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet(
            "color: #f1c40f; font-size: 36px; font-weight: 900;"  
            "letter-spacing: 2px; background: transparent;"
        )
        layout.addWidget(title_lbl)
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"background-color: {program['color']}; border: none;")
        layout.addWidget(line)
        desc_lbl = QLabel(program["description"])
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            "color: #95a5a6; font-size: 18px; line-height: 1.6; background: transparent;"  # bigger desc
        )
        layout.addWidget(desc_lbl)
        layout.addStretch()
        self.play_btn = QPushButton("▶  PLAY")
        self.play_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.play_btn.setFixedHeight(60)  # taller button
        self.play_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {program['color']};
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                letter-spacing: 3px;
            }}
            QPushButton:hover {{
                background-color: {program['hover']};
            }}
            QPushButton:pressed {{
                background-color: #1a252f;
            }}
            """
        )
        self.play_btn.clicked.connect(self.launch)
        layout.addWidget(self.play_btn)
        self._update_style()
    def _update_style(self):
        border_color = self.hover_color if self._is_hovered else "#3d5166"
        bg = "#1e2e3e" if self._is_hovered else "#1a252f"
        self.setStyleSheet(
            f"""
            QFrame#gameCard {{
                background-color: {bg};
                border: 2px solid {border_color};
                border-radius: 16px;
            }}
            """
        )
    def enterEvent(self, event):
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)
    def leaveEvent(self, event):
        self._is_hovered = False
        self._update_style()
        super().leaveEvent(event)
    def launch(self):
        try:
            subprocess.Popen([sys.executable, self.program["file"]])
        except FileNotFoundError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "File Not Found",
                f"Could not launch '{self.program['file']}'.\n"
                "Make sure all game files are in the same directory as main.py."
            )
            
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Countdown")
        self.setWindowIcon(QIcon("images/icon.jpg"))
        self._bg_pixmap = QPixmap("images/icon.jpg")  # load background image
        self.setStyleSheet(
            """
            QWidget {
                background-color: transparent;
                color: #ecf0f1;
                font-family: 'Segoe UI', sans-serif;
            }
            """
        )
        self._build_ui()

    def paintEvent(self, event):
        """Draw dark base first, then background image at low opacity on top."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        painter.setOpacity(1.0)
        painter.fillRect(self.rect(), QColor("#2c3e50"))

        if not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.setOpacity(0.3)
            painter.drawPixmap(x, y, scaled)

        painter.end()
        super().paintEvent(event)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 50, 60, 50)
        root.setSpacing(0)
        header = QVBoxLayout()
        header.setSpacing(8)
        title = QLabel("COUNTDOWN")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 140px; font-weight: 900; color: #f1c40f;"
            "letter-spacing: 10px; background: transparent;"
        )
        header.addWidget(title)
        root.addLayout(header)
        root.addSpacing(80)  
        cards_row = QHBoxLayout()
        cards_row.setSpacing(60)  
        cards_row.addStretch()
        for prog in PROGRAMS:
            card = GameCard(prog)
            cards_row.addWidget(card)
        cards_row.addStretch()
        root.addLayout(cards_row)
        root.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home = HomePage()
    home.showMaximized()
    home.show()
    sys.exit(app.exec_())