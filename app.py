import sys
import random
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QRect
from square import Cell
from PyQt6.QtWidgets import *
from sudoku import Sudoku

class MainWindow(QMainWindow):
    curr_sudoku = Sudoku(3).difficulty(0.1)
    def __init__(self):
        super().__init__()
        self.interface_init()
        self.sudoku_widget = QWidget()
        self.display_sudoku()
        filler_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget = QWidget()
        main_layout.addWidget(self.sudoku_widget)
        main_layout.addWidget(filler_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    def interface_init(self):
        self.setWindowTitle("Super Sudoku")
        easy_generate = QAction("Easy", self)
        easy_generate.triggered.connect(self.easy_generate)
        easy_generate.setCheckable(False)
        medium_generate = QAction("Medium", self)
        medium_generate.triggered.connect(self.medium_generate)
        medium_generate.setCheckable(False)
        difficult_generate = QAction("Difficult", self)
        difficult_generate.triggered.connect(self.difficult_generate)
        difficult_generate.setCheckable(False)
        menu = self.menuBar();
        new_menu_item = menu.addMenu("New")
        new_menu_item.addAction(easy_generate)
        new_menu_item.addSeparator()
        new_menu_item.addAction(medium_generate)
        new_menu_item.addSeparator()
        new_menu_item.addAction(difficult_generate)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)
    def display_sudoku(self):
        grid = QGridLayout()
        for i in range(9):
            for j in range(9):
                grid.addWidget(Cell(self.curr_sudoku.board[i][j]), i, j)
        self.sudoku_widget.setLayout(grid)
    def easy_generate(self):
        self.curr_sudoku = Sudoku(3).difficulty(0.2)
        self.display_sudoku()
    def medium_generate(self):
        self.curr_sudoku = Sudoku(3).difficulty(0.4)
        self.display_sudoku()
    def difficult_generate(self):
        self.curr_sudoku = Sudoku(3).difficulty(0.8)
        self.display_sudoku()
    def custom_generate(self, num):
        self.curr_sudoku = Sudoku(3).difficulty(num)
        self.display_sudoku()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
