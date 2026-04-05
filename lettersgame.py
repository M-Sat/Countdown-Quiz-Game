import sys
import random
from collections import Counter
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGridLayout, QMessageBox,
                             QTextEdit, QLCDNumber)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QIcon, QTextCursor

FREQ = {
    'A': 7.8, 'B': 2.0, 'C': 4.0, 'D': 3.8, 'E': 11.0,
    'F': 1.4, 'G': 3.0, 'H': 2.3, 'I': 8.6, 'J': 0.25,
    'K': 0.97, 'L': 5.3, 'M': 2.7, 'N': 7.2, 'O': 6.1,
    'P': 2.8, 'Q': 0.19, 'R': 7.3, 'S': 8.7, 'T': 6.7,
    'U': 3.3, 'V': 1.0, 'W': 0.91, 'X': 0.27, 'Y': 1.6, 'Z': 0.44
}

VOWELS = ['A', 'E', 'I', 'O', 'U']
CONSONANTS = [l for l in FREQ if l not in VOWELS]

def _normalize(group):
    total = sum(FREQ[l] for l in group)
    return [FREQ[l] / total for l in group]

VOWEL_WEIGHTS = _normalize(VOWELS)
CONSONANT_WEIGHTS = _normalize(CONSONANTS)

def calculate_score(word):
    return 18 if len(word) == 9 else len(word)

def find_best_words(letters, word_set):
    """Return all longest valid words formable from 'letters'."""
    available = Counter(letters)
    best_len = 0
    best_words = []

    for word in word_set:
        w = word.upper()
        if len(w) < 2:
            continue
        wc = Counter(w)
        if all(wc[ch] <= available[ch] for ch in wc):
            if len(w) > best_len:
                best_len = len(w)
                best_words = [w]
            elif len(w) == best_len:
                best_words.append(w)

    return best_len, sorted(best_words)

class LettersGame(QWidget):
    def __init__(self):
        super().__init__()
        try:
            with open('words.txt') as f:
                self.word_set = set(line.strip().upper() for line in f if line.strip())
        except FileNotFoundError:
            QMessageBox.critical(None, "Error", "words.txt not found in the working directory.")
            sys.exit(1)

        self.drawn_letters = []
        self.vowel_count = 0
        self.consonant_count = 0
        self.points_history = []
        self.current_word = []      
        self.button_history = []    
        self.letter_buttons = []   

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.time_left = 30

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Countdown Letters Game')
        self.setWindowIcon(QIcon('images/let.png'))
        self.setStyleSheet("""
            QWidget { background-color: #2c3e50; color: #ecf0f1; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #34495e; border: 1px solid #7f8c8d; padding: 10px; border-radius: 5px; font-size: 18px; }
            QPushButton:hover { background-color: #66bbff; }

            QPushButton#vowelBtn  { background-color: #3498db; }
            QPushButton#vowelBtn:hover  { background-color: #66bbff; }
            QPushButton#consonantBtn { background-color: #3498db; }
            QPushButton#consonantBtn:hover { background-color: #66bbff; }
                           
            QPushButton#letBtn { background-color: #3498db; }
            QPushButton#letBtn:hover { background-color: #66bbff; }

            QPushButton#playAgainBtn:enabled { background-color: #27ae60; color: white; font-weight: bold; }
            QPushButton#playAgainBtn:hover:enabled { background-color: #2ecc71; }
            QPushButton#homeBtn:enabled { background-color: #27ae60; color: white; font-weight: bold; }
            QPushButton#homeBtn:hover:enabled { background-color: #2ecc71; }

            QPushButton#drawBtn:enabled { background-color: #3498db; color: white; font-weight: bold; }
            QPushButton#drawBtn:hover:enabled { background-color: #66bbff; }

            QPushButton#untimedBtn { background-color: #34495e; color: white; font-size: 14px; margin-top: 5px; }
            QPushButton#untimedBtn:disabled { background-color: #7f8c8d; opacity: 0.5; }

            QPushButton:disabled { background-color: #7f8c8d; color: #95a5a6; border: 1px solid #7f8c8d; }

            QLabel#gameTitle { font-size: 88px; font-weight: bold; color: #f1c40f; margin-top: 10px; }

            QLCDNumber#timerLCD { background-color: black; border: 2px solid #333; border-radius: 5px; color: #00FF00; }

            QLabel#lettersDisplay { font-size: 64px; font-weight: bold; color: #f1c40f; letter-spacing: 12px; }

            QLabel#historyLabel { font-size: 20px; color: #ecf0f1; line-height: 1.5; }

            QLabel#wordDisplay { font-size: 36px; font-weight: bold; color: #f1c40f; background-color: #1a252f; border: 2px solid #3498db; border-radius: 8px; padding: 10px 16px; min-height: 70px; letter-spacing: 6px; }

            QTextEdit#solverArea { background-color: #1a252f; color: #2ecc71; font-family: 'Consolas', monospace; font-size: 15px; border: none; padding: 15px; }
        """)

        self.main_layout = QHBoxLayout(self)

        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)

        self.title_label = QLabel("COUNTDOWN: LETTERS GAME")
        self.title_label.setObjectName("gameTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.title_label)

        self.timer_lcd = QLCDNumber()
        self.timer_lcd.setObjectName("timerLCD")
        self.timer_lcd.setDigitCount(2)
        self.timer_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.timer_lcd.setFixedSize(150, 80)
        self.timer_lcd.display(30)
        self.left_layout.addWidget(self.timer_lcd, alignment=Qt.AlignCenter)

        self.btn_untimed = QPushButton("STOP THE CLOCK")
        self.btn_untimed.setObjectName("untimedBtn")
        self.btn_untimed.setFixedWidth(160)
        self.btn_untimed.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_untimed.setEnabled(False)
        self.btn_untimed.clicked.connect(self.stop_timer_manually)
        self.left_layout.addWidget(self.btn_untimed, alignment=Qt.AlignCenter)

        self.header_layout = QHBoxLayout()
        self.nav_layout = QVBoxLayout()

        self.btn_home = QPushButton("Home")
        self.btn_home.setObjectName("homeBtn")
        self.btn_home.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_home.clicked.connect(QApplication.instance().quit)

        self.btn_play_again = QPushButton("Play Again")
        self.btn_play_again.setObjectName("playAgainBtn")
        self.btn_play_again.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_play_again.setEnabled(False)
        self.btn_play_again.clicked.connect(self.reset_game)

        self.nav_layout.addWidget(self.btn_home)
        self.nav_layout.addWidget(self.btn_play_again)
        self.header_layout.addLayout(self.nav_layout)
        self.header_layout.addStretch()

        self.score_container = QVBoxLayout()
        self.score_container.addWidget(QLabel("SCORE HISTORY"), alignment=Qt.AlignRight)
        self.history_label = QLabel("")
        self.history_label.setObjectName("historyLabel")
        self.history_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.score_container.addWidget(self.history_label)
        self.header_layout.addLayout(self.score_container)
        self.left_layout.addLayout(self.header_layout)

        self.letters_label = QLabel("")
        self.letters_label.setObjectName("lettersDisplay")
        self.letters_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.letters_label)

        self.word_display = QLabel("Pick 9 letters to start")
        self.word_display.setObjectName("wordDisplay")
        self.word_display.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.word_display)

        self.setup_area = QHBoxLayout()
        self.btn_vowel = QPushButton("Draw VOWEL")
        self.btn_consonant = QPushButton("Draw CONSONANT")
        self.btn_vowel.setObjectName("drawBtn")
        self.btn_consonant.setObjectName("drawBtn")
        self.btn_vowel.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_consonant.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_vowel.clicked.connect(lambda: self.draw_letter('V'))
        self.btn_consonant.clicked.connect(lambda: self.draw_letter('C'))
        self.setup_area.addWidget(self.btn_vowel)
        self.setup_area.addWidget(self.btn_consonant)
        self.left_layout.addLayout(self.setup_area)

        self.grid = QGridLayout()
        self.left_layout.addLayout(self.grid)

        self.action_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_submit = QPushButton("SUBMIT WORD")
        self.btn_submit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_clear.clicked.connect(self.clear_word)
        self.btn_undo.clicked.connect(self.undo_letter)
        self.btn_submit.clicked.connect(self.evaluate_result)
        self.action_layout.addWidget(self.btn_clear)
        self.action_layout.addWidget(self.btn_undo)
        self.action_layout.addWidget(self.btn_submit)
        self.left_layout.addLayout(self.action_layout)

        self.toggle_game_buttons(False)

        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.addWidget(QLabel("COMPUTER'S ANALYSIS"))
        self.solver_display = QTextEdit()
        self.solver_display.setObjectName("solverArea")
        self.solver_display.setReadOnly(True)
        self.right_layout.addWidget(self.solver_display)

        self.main_layout.addWidget(self.left_container, 75)
        self.main_layout.addWidget(self.right_container, 25)

    def draw_letter(self, mode):
        if len(self.drawn_letters) >= 9:
            return

        if mode == 'V':
            if self.vowel_count >= 5:
                self.status_label.setText("Maximum vowels (5) already drawn!")
                return
            letter = random.choices(VOWELS, weights=VOWEL_WEIGHTS)[0]
            self.vowel_count += 1
        else:
            if self.consonant_count >= 6:
                self.status_label.setText("Maximum consonants (6) already drawn!")
                return
            letter = random.choices(CONSONANTS, weights=CONSONANT_WEIGHTS)[0]
            self.consonant_count += 1

        self.drawn_letters.append(letter)
        self.letters_label.setText("  ".join(self.drawn_letters))

        remaining = 9 - len(self.drawn_letters)

        if self.vowel_count == 5 and remaining > 0:
            self.word_display.setText(f"Max vowels → auto-drawing {remaining} consonant(s)…")
            for _ in range(remaining):
                c = random.choices(CONSONANTS, weights=CONSONANT_WEIGHTS)[0]
                self.drawn_letters.append(c)
                self.consonant_count += 1
            self.letters_label.setText("  ".join(self.drawn_letters))

        elif self.consonant_count == 6 and remaining > 0:
            self.word_display.setText(f"Max consonants → auto-drawing {remaining} vowel(s)…")
            for _ in range(remaining):
                v = random.choices(VOWELS, weights=VOWEL_WEIGHTS)[0]
                self.drawn_letters.append(v)
                self.vowel_count += 1
            self.letters_label.setText("  ".join(self.drawn_letters))

        if len(self.drawn_letters) == 9:
            self.btn_vowel.setEnabled(False)
            self.btn_consonant.setEnabled(False)
            self.start_game()
        else:
            drawn_so_far = len(self.drawn_letters)
            slots = 9 - drawn_so_far
            hints = []
            if self.vowel_count == 5:
                hints.append("no more vowels")
            if self.consonant_count == 6:
                hints.append("no more consonants")
            extra = f"  ({', '.join(hints)})" if hints else ""
            self.word_display.setText(
                f"Drawn: {drawn_so_far}/9 — {slots} slot(s) left{extra}"
            )

    def start_game(self):
        self.toggle_game_buttons(True)
        self.create_letter_tiles()
        self.solver_display.clear()

        self.time_left = 30
        self.timer_lcd.display(self.time_left)
        self.btn_untimed.setEnabled(True)
        self.countdown_timer.start(1000)

        self.current_word = []
        self.button_history = []
        self.update_word_display()

    def stop_timer_manually(self):
        self.countdown_timer.stop()
        self.btn_untimed.setEnabled(False)
        self.btn_untimed.setText("UNTIMED ACTIVE")

    def update_countdown(self):
        self.time_left -= 1
        if self.time_left >= 0:
            self.timer_lcd.display(self.time_left)

        if self.time_left == 0:
            self.countdown_timer.stop()
            self.btn_untimed.setEnabled(False)
            QMessageBox.critical(self, "Time's Up!", "You didn't submit in time! Score: 0")
            self.points_history.append(0)
            self.history_label.setText("\n".join(map(str, self.points_history[-7:])))
            self.finalize_turn()

    def finalize_turn(self):
        self.btn_play_again.setEnabled(True)
        self.btn_untimed.setEnabled(False)
        self.toggle_game_buttons(False)
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setEnabled(False)
        self.run_solver()

    def toggle_game_buttons(self, state):
        self.btn_submit.setEnabled(state)
        self.btn_clear.setEnabled(state)
        self.btn_undo.setEnabled(state)

    def create_letter_tiles(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        self.letter_buttons = []
        for i, letter in enumerate(self.drawn_letters):
            btn = QPushButton(letter)
            btn.setObjectName("letBtn")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedSize(70, 70)
            btn.setStyleSheet("font-size: 28px; font-weight: bold;")
            btn.clicked.connect(lambda ch, b=btn, l=letter: self.add_letter(l, b))
            self.grid.addWidget(btn, 0, i)
            self.letter_buttons.append(btn)

    def add_letter(self, letter, button):
        self.current_word.append(letter)
        self.button_history.append(button)
        button.setEnabled(False)
        self.update_word_display()

    def undo_letter(self):
        if self.current_word:
            self.current_word.pop()
            btn = self.button_history.pop()
            btn.setEnabled(True)
            self.update_word_display()

    def clear_word(self):
        self.current_word = []
        self.button_history = []
        for btn in self.letter_buttons:
            btn.setEnabled(True)
        self.update_word_display()

    def update_word_display(self):
        text = " ".join(self.current_word)
        self.word_display.setText(text if text else "Build your word…")

    def evaluate_result(self):
        self.countdown_timer.stop()
        self.btn_untimed.setEnabled(False)

        word = "".join(self.current_word)

        if not word:
            QMessageBox.warning(self, "No Word", "Click some letters to build a word first.")
            if self.btn_untimed.text() != "UNTIMED ACTIVE":
                self.countdown_timer.start(1000)
                self.btn_untimed.setEnabled(True)
            return

        if word not in self.word_set:
            QMessageBox.warning(self, "Not a Word",
                                f"'{word}' is not in the word list. Score: 0")
            self.points_history.append(0)
            self.history_label.setText("\n".join(map(str, self.points_history[-7:])))
            self.finalize_turn()
            return

        points = calculate_score(word)
        self.points_history.append(points)
        self.history_label.setText("\n".join(map(str, self.points_history[-7:])))

        msg = f"Word: {word}\nLength: {len(word)}\nPoints: {points}"
        if len(word) == 9:
            msg += "\n\n🎉 NINE LETTERS! MAXIMUM SCORE!"
        QMessageBox.information(self, "Result", msg)
        self.finalize_turn()

    def run_solver(self):
        self.solver_display.setText("Computing best words…")
        QApplication.processEvents()

        best_len, best_words = find_best_words(self.drawn_letters, self.word_set)

        self.solver_display.clear()
        if not best_words:
            self.solver_display.append("No valid words found.")
            return

        header = (f"NINE-LETTER PERFECTION!" if best_len == 9
                  else f"Best length: {best_len} letters")
        self.solver_display.append(f"{header}\n" + "=" * 25)
        for w in best_words[:20]:
            score = calculate_score(w)
            self.solver_display.append(f"• {w}  ({score} pts)")

        self.solver_display.moveCursor(QTextCursor.Start)

    def reset_game(self):
        self.drawn_letters = []
        self.vowel_count = 0
        self.consonant_count = 0
        self.current_word = []
        self.button_history = []
        self.letter_buttons = []
        self.countdown_timer.stop()

        self.letters_label.setText("")
        self.word_display.setText("Pick 9 letters to start")
        self.timer_lcd.display(30)

        self.btn_untimed.setEnabled(False)
        self.btn_untimed.setText("STOP THE CLOCK")
        self.btn_vowel.setEnabled(True)
        self.btn_consonant.setEnabled(True)
        self.btn_play_again.setEnabled(False)

        self.solver_display.clear()
        self.toggle_game_buttons(False)

        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = LettersGame()
    game.showMaximized()
    sys.exit(app.exec_())