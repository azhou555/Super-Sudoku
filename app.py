import sys
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QRect, Qt
from square import Cell
from PyQt6.QtWidgets import *
from sudoku import Sudoku
from model import SudokuAI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._sudoku = Sudoku(3).difficulty(0.1)
        self._solution = self._sudoku.solve()
        self.selected_cell = None
        self.cells = []
        self.ai = None  # Initialize AI lazily
        self.interface_init()
        self.sudoku_widget = QWidget()
        self.grid = QGridLayout()
        self.display_sudoku()
        self.ai_widget = self.create_ai_widget()
        main_layout = QHBoxLayout()
        main_widget = QWidget()
        main_layout.addWidget(self.sudoku_widget)
        main_layout.addWidget(self.ai_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Make sure window can receive keyboard events
        self.sudoku_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        # Clear existing cells
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)
        self.cells = []
        
        # Store original puzzle state to distinguish given numbers (only on first call)
        if not hasattr(self, '_original_board'):
            self._original_board = [row[:] for row in self._sudoku.board]
        
        # Create new cells
        for i in range(9):
            row = []
            for j in range(9):
                original_val = self._original_board[i][j]
                is_given = original_val is not None and original_val != 0
                current_val = self._sudoku.board[i][j]
                # Convert None to 0 for display
                display_val = current_val if current_val is not None else 0
                cell = Cell(display_val, i, j, is_given)
                cell.cellSelected.connect(self.on_cell_selected)
                self.grid.addWidget(cell, i, j)
                row.append(cell)
            self.cells.append(row)
        
        # Set grid spacing and styling - no spacing for tight grid
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(5, 5, 5, 5)
        self.sudoku_widget.setLayout(self.grid)
        self.sudoku_widget.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 3px solid #333;
            }
        """)
        self.sudoku_widget.setFixedSize(510, 510)
    
    def on_cell_selected(self, row, col):
        # Deselect previous cell
        if self.selected_cell:
            old_row, old_col = self.selected_cell
            self.cells[old_row][old_col].set_selected(False)
        
        # Select new cell
        self.selected_cell = (row, col)
        self.cells[row][col].set_selected(True)
        
        # Ensure main window has focus for keyboard input
        self.setFocus()
    
    def keyPressEvent(self, event):
        if self.selected_cell:
            row, col = self.selected_cell
            key = event.key()
            
            print(f"Key pressed: {key}, Selected cell: {row}, {col}")  # Debug
            print(f"Original board value at {row}, {col}: {self._original_board[row][col]}")  # Debug
            print(f"Current board value at {row}, {col}: {self._sudoku.board[row][col]}")  # Debug
            
            # Don't allow editing given numbers (handle both None and 0 as empty)
            original_value = self._original_board[row][col]
            if original_value is not None and original_value != 0:
                print(f"Cannot edit given number at {row}, {col}")  # Debug
                super().keyPressEvent(event)
                return
            
            # Handle number keys 1-9
            if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
                number = key - Qt.Key.Key_1 + 1
                print(f"Setting {number} at {row}, {col}")  # Debug
                self._sudoku.board[row][col] = number
                self.cells[row][col].set_value(number, is_user_input=True)
            
            # Handle delete/backspace
            elif key in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace, Qt.Key.Key_0]:
                print(f"Clearing cell at {row}, {col}")  # Debug
                # Set to None to match sudoku library format
                self._sudoku.board[row][col] = None
                self.cells[row][col].set_value(0, is_user_input=True)
        else:
            print("No cell selected")  # Debug
        
        super().keyPressEvent(event)
    
    def create_ai_widget(self):
        """Create the AI assistant panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # AI Assistant label
        ai_label = QLabel("AI Assistant")
        ai_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(ai_label)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        layout.addWidget(self.chat_display)
        
        # Chat input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask the AI assistant...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        layout.addWidget(self.chat_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.hint_button = QPushButton("Get Hint")
        self.hint_button.clicked.connect(self.get_hint)
        button_layout.addWidget(self.hint_button)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_chat_message)
        button_layout.addWidget(send_button)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.ai_status = QLabel("AI not initialized")
        self.ai_status.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.ai_status)
        
        widget.setLayout(layout)
        widget.setFixedWidth(300)
        return widget
    
    def initialize_ai(self):
        """Initialize AI model (lazy loading)"""
        if not self.ai:
            try:
                self.ai_status.setText("Initializing AI...")
                self.ai = SudokuAI()
                self.ai_status.setText("AI ready")
                self.ai_status.setStyleSheet("color: green; font-size: 10px;")
            except Exception as e:
                self.ai_status.setText(f"AI Error: {str(e)}")
                self.ai_status.setStyleSheet("color: red; font-size: 10px;")
    
    def get_hint(self):
        """Get a hint from the AI"""
        self.initialize_ai()
        if not self.ai:
            return
            
        try:
            self.hint_button.setText("Getting hint...")
            self.hint_button.setEnabled(False)
            
            hint = self.ai.get_hint(self._sudoku.board, self._solution.board)
            self.chat_display.append(f"<b>AI Hint:</b> {hint}")
            
        except Exception as e:
            self.chat_display.append(f"<b>Error:</b> {str(e)}")
        finally:
            self.hint_button.setText("Get Hint")
            self.hint_button.setEnabled(True)
    
    def send_chat_message(self):
        """Send a chat message to the AI"""
        message = self.chat_input.text().strip()
        if not message:
            return
            
        self.initialize_ai()
        if not self.ai:
            return
            
        try:
            self.chat_display.append(f"<b>You:</b> {message}")
            self.chat_input.clear()
            
            response = self.ai.chat(message, self._sudoku.board, self._solution.board)
            self.chat_display.append(f"<b>AI:</b> {response}")
            
        except Exception as e:
            self.chat_display.append(f"<b>Error:</b> {str(e)}")
    def easy_generate(self):
        self._sudoku = Sudoku(3).difficulty(0.2)
        self._solution = self._sudoku.solve()
        self.selected_cell = None
        if hasattr(self, '_original_board'):
            delattr(self, '_original_board')
        self.display_sudoku()
    def medium_generate(self):
        self._sudoku = Sudoku(3).difficulty(0.4)
        self._solution = self._sudoku.solve()
        self.selected_cell = None
        if hasattr(self, '_original_board'):
            delattr(self, '_original_board')
        self.display_sudoku()
    def difficult_generate(self):
        self._sudoku = Sudoku(3).difficulty(0.8)
        self._solution = self._sudoku.solve()
        self.selected_cell = None
        if hasattr(self, '_original_board'):
            delattr(self, '_original_board')
        self.display_sudoku()
    def custom_generate(self, num):
        self._sudoku = Sudoku(3).difficulty(num)
        self._solution = self._sudoku.solve()
        self.selected_cell = None
        if hasattr(self, '_original_board'):
            delattr(self, '_original_board')
        self.display_sudoku()
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
