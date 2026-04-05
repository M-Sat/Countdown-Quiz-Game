import sys
import random
import ast
from itertools import combinations
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGridLayout, QMessageBox, QTextEdit, QLCDNumber)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QIcon, QTextCursor

class NumbersGame(QWidget):
    def __init__(self):
        super().__init__()
        self.big_numbers = [25, 50, 75, 100]
        self.small_numbers = list(range(1, 11)) * 2
        self.drawn_numbers = []
        self.target = 0
        self.current_expression = []
        self.button_history = []
        self.points_history = []
        
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.time_left = 30
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Countdown Numbers Game')
        self.setWindowIcon(QIcon('images/num.png'))  
        self.setStyleSheet("""
            QWidget { background-color: #2c3e50; color: #ecf0f1; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #34495e; border: 1px solid #7f8c8d; padding: 10px; border-radius: 5px; font-size: 18px; }
            QPushButton:hover { background-color: #66bbff; }
            
            QPushButton#opBtn { background-color: #3498db; }
            QPushButton#opBtn:hover { background-color: #66bbff; }
            QPushButton#numBtn { background-color: #3498db; }
            QPushButton#numBtn:hover { background-color: #66bbff; }
                           
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

            QLabel#target { font-size: 80px; font-weight: bold; color: #f1c40f; }
            QLabel#expression { font-size: 36px; font-weight: bold; color: #f1c40f; background-color: #1a252f; border: 2px solid #3498db; border-radius: 8px; padding: 10px 16px; min-height: 70px; letter-spacing: 6px; }
            
            QLabel#historyLabel { font-size: 20px; color: #ecf0f1; line-height: 1.5; }
            
            QTextEdit#solverArea { background-color: #1a252f; color: #2ecc71; font-family: 'Consolas', monospace; font-size: 15px; border: none; padding: 15px; }
        """)

        self.main_layout = QHBoxLayout(self)

        # LEFT SIDE
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        
        self.title_label = QLabel("COUNTDOWN: NUMBERS GAME")
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
        self.btn_untimed.setFixedWidth(150)
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

        self.target_label = QLabel("", self)
        self.target_label.setObjectName("target")
        self.target_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.target_label)

        self.expr_label = QLabel("Pick 6 numbers to start", self)
        self.expr_label.setObjectName("expression")
        self.expr_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.expr_label)

        self.setup_area = QHBoxLayout()
        self.btn_big = QPushButton("Draw BIG numbers")
        self.btn_small = QPushButton("Draw SMALL numbers")
        self.btn_big.setObjectName("drawBtn")
        self.btn_small.setObjectName("drawBtn")
        self.btn_big.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_small.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_big.clicked.connect(lambda: self.draw_number('B'))
        self.btn_small.clicked.connect(lambda: self.draw_number('S'))
        self.setup_area.addWidget(self.btn_big)
        self.setup_area.addWidget(self.btn_small)
        self.left_layout.addLayout(self.setup_area)

        self.grid = QGridLayout()
        self.left_layout.addLayout(self.grid)
        
        self.action_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_submit = QPushButton("SUBMIT SOLUTION")
        self.btn_submit.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_clear.clicked.connect(self.clear_expression)
        self.btn_undo.clicked.connect(self.undo_step)
        self.btn_submit.clicked.connect(self.evaluate_result)
        self.action_layout.addWidget(self.btn_clear)
        self.action_layout.addWidget(self.btn_undo)
        self.action_layout.addWidget(self.btn_submit)
        self.left_layout.addLayout(self.action_layout)

        # RIGHT SIDE
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.addWidget(QLabel("COMPUTER'S ANALYSIS"))
        self.solver_display = QTextEdit()
        self.solver_display.setObjectName("solverArea")
        self.solver_display.setReadOnly(True)
        self.right_layout.addWidget(self.solver_display)

        self.main_layout.addWidget(self.left_container, 75)
        self.main_layout.addWidget(self.right_container, 25)

        self.toggle_game_buttons(False)

    def draw_number(self, mode):
        if len(self.drawn_numbers) < 6:
            if mode == 'B' and self.big_numbers:
                num = random.choice(self.big_numbers)
                self.big_numbers.remove(num)
            elif mode == 'S':
                num = random.choice(self.small_numbers)
                self.small_numbers.remove(num)
            else: return

            self.drawn_numbers.append(num)
            self.expr_label.setText(f"Drawn: {', '.join(map(str, self.drawn_numbers))}")
            
            if len(self.drawn_numbers) == 6:
                self.btn_big.setEnabled(False)
                self.btn_small.setEnabled(False)
                self.start_game()

    def start_game(self):
        self.target = random.randint(100, 999)
        self.target_label.setText(str(self.target))
        self.toggle_game_buttons(True)
        self.create_game_buttons()
        self.solver_display.clear()
        self.update_display()
        
        self.time_left = 30
        self.timer_lcd.display(self.time_left)
        self.btn_untimed.setEnabled(True)
        self.countdown_timer.start(1000)

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
            widget = self.grid.itemAt(i).widget()
            if widget: widget.setEnabled(False)
        self.run_solver()

    def toggle_game_buttons(self, state):
        self.btn_submit.setEnabled(state)
        self.btn_clear.setEnabled(state)
        self.btn_undo.setEnabled(state)

    def create_game_buttons(self):
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget: widget.setParent(None)

        self.num_buttons = []
        for i, num in enumerate(self.drawn_numbers):
            btn = QPushButton(str(num))
            btn.setObjectName("numBtn")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda ch, b=btn, n=num: self.add_to_expr(str(n), b))
            self.grid.addWidget(btn, 0, i)
            self.num_buttons.append(btn)

        ops = ['+', '-', '*', '/', '(', ')']
        for i, op in enumerate(ops):
            btn = QPushButton(op)
            btn.setObjectName("opBtn")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda ch, o=op: self.add_to_expr(o, None))
            self.grid.addWidget(btn, 1, i)

    def add_to_expr(self, char, button):
        self.current_expression.append(char)
        self.button_history.append(button)
        if button: button.setEnabled(False) 
        self.update_display()

    def undo_step(self):
        if self.current_expression:
            self.current_expression.pop()
            btn = self.button_history.pop()
            if btn: btn.setEnabled(True) 
            self.update_display()

    def clear_expression(self):
        self.current_expression = []
        self.button_history = []
        for btn in self.num_buttons: btn.setEnabled(True) 
        self.update_display()

    def update_display(self):
        expr_str = " ".join(self.current_expression)
        self.expr_label.setText(expr_str if expr_str else "Build your equation...")

    def evaluate_result(self):
        self.countdown_timer.stop()
        self.btn_untimed.setEnabled(False)
        equation = "".join(self.current_expression)
        result = self.safe_eval(equation)
        
        if result is None:
            QMessageBox.warning(self, "Invalid Math", "Check your brackets/rules.")
            if self.btn_untimed.text() != "UNTIMED ACTIVE":
                self.countdown_timer.start(1000)
                self.btn_untimed.setEnabled(True)
            return

        diff = abs(self.target - result)
        points = 10 if diff == 0 else 7 if diff <= 5 else 5 if diff <= 10 else 0
        self.points_history.append(points)
        self.history_label.setText("\n".join(map(str, self.points_history[-7:])))
        
        QMessageBox.information(self, "Points", f"Result: {result}\nPoints: {points}")
        self.finalize_turn()

    def safe_eval(self, expr):
        try:
            tree = ast.parse(expr, mode='eval')
            return self.eval_node(tree.body)
        except: return None

    def eval_node(self, node):
        if isinstance(node, ast.BinOp):
            left, right = self.eval_node(node.left), self.eval_node(node.right)
            if left is None or right is None: return None
            if isinstance(node.op, ast.Add): res = left + right
            elif isinstance(node.op, ast.Sub): res = left - right
            elif isinstance(node.op, ast.Mult): res = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0 or left % right != 0: return None
                res = left // right
            return res if res > 0 else None
        elif isinstance(node, ast.Constant): return node.value
        return None

    def run_solver(self):
        self.solver_display.setText("Computing...")
        QApplication.processEvents()
        solutions = {}
        def solve_recursive(nums):
            if not nums: return
            for n, expr, prec in nums:
                if n not in solutions: solutions[n] = set()
                solutions[n].add(expr)
            if len(nums) == 1: return
            for (i, (n1, e1, p1)), (j, (n2, e2, p2)) in combinations(enumerate(nums), 2):
                rem = [nums[k] for k in range(len(nums)) if k != i and k != j]
                solve_recursive(rem + [(n1 + n2, f"{e1} + {e2}", 1)])
                me1, me2 = (f"({e1})" if p1 < 2 else e1), (f"({e2})" if p2 < 2 else e2)
                solve_recursive(rem + [(n1 * n2, f"{me1} * {me2}", 2)])
                if n1 - n2 > 0: solve_recursive(rem + [(n1 - n2, f"{e1} - ({e2})" if p2 <= 1 else f"{e1} - {e2}", 1)])
                elif n2 - n1 > 0: solve_recursive(rem + [(n2 - n1, f"{e2} - ({e1})" if p1 <= 1 else f"{e2} - {e1}", 1)])
                if n2 != 0 and n1 % n2 == 0: solve_recursive(rem + [(n1 // n2, f"{me1} / ({e2})" if p2 <= 2 else f"{me1} / {e2}", 2)])
                elif n1 != 0 and n2 % n1 == 0: solve_recursive(rem + [(n2 // n1, f"{me2} / ({e1})" if p1 <= 2 else f"{me2} / {e1}", 2)])

        solve_recursive([(n, str(n), 3) for n in self.drawn_numbers])
        self.solver_display.clear()
        target_found = self.target in solutions
        display_val = self.target if target_found else min(solutions.keys(), key=lambda x: abs(x - self.target))
        self.solver_display.append(f"{'TARGET ACHIEVED!' if target_found else 'Closest: ' + str(display_val)}\n" + "="*25)
        for sol in sorted(list(solutions[display_val]), key=len)[:15]: 
            self.solver_display.append(f"• {sol}")
        self.solver_display.moveCursor(QTextCursor.Start)

    def reset_game(self):
        self.countdown_timer.stop()
 
        self.big_numbers = [25, 50, 75, 100]
        self.small_numbers = list(range(1, 11)) * 2
        self.drawn_numbers = []
        self.current_expression = []
        self.button_history = []
 
        self.target_label.setText("")
        self.expr_label.setText("Pick 6 numbers to start")
        self.timer_lcd.display(30)
 
        self.btn_untimed.setEnabled(False)
        self.btn_untimed.setText("STOP THE CLOCK")   
        self.btn_big.setEnabled(True)
        self.btn_small.setEnabled(True)
        self.btn_play_again.setEnabled(False)
 
        self.solver_display.clear()
        self.toggle_game_buttons(False)
 
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = NumbersGame()
    game.showMaximized()
    sys.exit(app.exec_())