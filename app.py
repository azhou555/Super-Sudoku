import sys
import re
from PyQt6.QtGui import QAction, QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import QRect, Qt, QThread, pyqtSignal, QTimer
from square import Cell
from PyQt6.QtWidgets import *
from sudoku import Sudoku
from model import SudokuAI
import threading

class SuccessOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.opacity = 0.0
        self.phase = 0  # 0 = fade in, 1 = stay, 2 = fade out
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS for smooth animation
        
        self.phase_timer = QTimer(self)
        self.phase_timer.timeout.connect(self.next_phase)
        self.phase_timer.start(800)  # Stay visible for 800ms
    
    def update_animation(self):
        """Update animation state"""
        if self.phase == 0:  # Fade in
            self.opacity = min(1.0, self.opacity + 0.08)
            if self.opacity >= 1.0:
                self.phase = 1
        elif self.phase == 2:  # Fade out
            self.opacity = max(0.0, self.opacity - 0.06)
            if self.opacity <= 0.0:
                self.close_overlay()
        
        self.update()
    
    def next_phase(self):
        """Move to next phase of animation"""
        if self.phase == 1:
            self.phase = 2
            self.phase_timer.stop()
    
    def paintEvent(self, event):
        if self.opacity <= 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Light green overlay with opacity
        overlay_color = QColor(46, 125, 50, int(40 * self.opacity))
        painter.fillRect(self.rect(), overlay_color)
        
        # Success text with fade
        text_color = QColor(46, 125, 50, int(255 * self.opacity))
        painter.setPen(QPen(text_color, 2))
        font = QFont("Arial", 24, QFont.Weight.Normal)
        painter.setFont(font)
        
        text_rect = QRect(0, self.height() // 2 - 30, self.width(), 60)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Puzzle Completed!")
    
    def close_overlay(self):
        try:
            self.timer.stop()
            if hasattr(self, 'phase_timer'):
                self.phase_timer.stop()
            self.hide()
            self.deleteLater()
        except:
            pass

class FailureOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.opacity = 0.0
        self.phase = 0  # 0 = fade in, 1 = stay, 2 = fade out
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS for smooth animation
        
        self.phase_timer = QTimer(self)
        self.phase_timer.timeout.connect(self.next_phase)
        self.phase_timer.start(1200)  # Stay visible for 1200ms
    
    def update_animation(self):
        """Update animation state"""
        if self.phase == 0:  # Fade in
            self.opacity = min(1.0, self.opacity + 0.08)
            if self.opacity >= 1.0:
                self.phase = 1
        elif self.phase == 2:  # Fade out
            self.opacity = max(0.0, self.opacity - 0.06)
            if self.opacity <= 0.0:
                self.close_overlay()
        
        self.update()
    
    def next_phase(self):
        """Move to next phase of animation"""
        if self.phase == 1:
            self.phase = 2
            self.phase_timer.stop()
    
    def paintEvent(self, event):
        if self.opacity <= 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Light red overlay with opacity
        overlay_color = QColor(198, 40, 40, int(30 * self.opacity))
        painter.fillRect(self.rect(), overlay_color)
        
        # Error text with fade
        text_color = QColor(198, 40, 40, int(255 * self.opacity))
        painter.setPen(QPen(text_color, 2))
        font = QFont("Arial", 20, QFont.Weight.Normal)
        painter.setFont(font)
        
        text_rect = QRect(0, self.height() // 2 - 40, self.width(), 40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Puzzle has errors")
        
        # Subtitle
        font = QFont("Arial", 14, QFont.Weight.Normal)
        painter.setFont(font)
        subtitle_rect = QRect(0, self.height() // 2 + 10, self.width(), 30)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "Please review your entries")
    
    def close_overlay(self):
        try:
            self.timer.stop()
            if hasattr(self, 'phase_timer'):
                self.phase_timer.stop()
            self.hide()
            self.deleteLater()
        except:
            pass

class MainWindow(QMainWindow):
    # Define custom signals for threading
    hint_received = pyqtSignal(object)
    hint_error = pyqtSignal(str)
    chat_response = pyqtSignal(str)
    chat_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._sudoku = Sudoku(3).difficulty(0.1)
        self._solution = self._sudoku.solve()
        self.selected_cell = None
        self.selected_number = None  # For number selection mode
        self.cells = []
        self.ai = None  # Initialize AI lazily
        self.game_mode = "classic"  # "classic" or "autocheck"
        self.hint_cells = set()  # Track cells filled by AI hints
        self.interface_init()
        self.sudoku_widget = QWidget()
        self.grid = QGridLayout()
        self.display_sudoku()
        self.ai_widget = self.create_ai_widget()
        main_layout = QHBoxLayout()
        main_widget = QWidget()
        main_layout.addWidget(self.sudoku_widget, 2)  # Give more space to sudoku
        main_layout.addWidget(self.ai_widget, 1)  # Less space to AI widget
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Set up dynamic sizing
        self.resizeEvent = self.on_window_resize
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Connect signals for threading
        self.hint_received.connect(self.on_hint_received)
        self.hint_error.connect(self.on_hint_error)
        self.chat_response.connect(self.on_chat_response)
        self.chat_error.connect(self.on_chat_error)
        
        # Make sure window can receive keyboard events
        self.sudoku_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Graphics overlay for celebrations
        self.graphics_overlay = None
    
    def on_window_resize(self, event):
        """Handle window resize to adjust grid size"""
        super().resizeEvent(event)
        self.adjust_grid_size()
        
        # Resize graphics overlay if it exists
        if self.graphics_overlay and self.graphics_overlay.isVisible():
            self.graphics_overlay.setGeometry(0, 0, self.width(), self.height())
    
    def adjust_grid_size(self):
        """Adjust grid and cell sizes based on available space"""
        if hasattr(self, 'sudoku_widget') and self.sudoku_widget:
            # Get available space for the sudoku widget (2/3 of width)
            available_width = int(self.width() * 0.6)  # Leave space for AI widget
            available_height = self.height() - 100  # Leave space for menu bar
            
            # Make it square and leave some margin
            grid_size = min(available_width, available_height) - 50
            cell_size = max(40, grid_size // 9)  # Minimum 40px per cell
            
            # Update cell sizes
            if hasattr(self, 'cells') and self.cells:
                for i in range(9):
                    for j in range(9):
                        if i < len(self.cells) and j < len(self.cells[i]):
                            self.cells[i][j].setFixedSize(cell_size, cell_size)
            
            # Update sudoku widget size
            total_size = cell_size * 9 + 10  # Add margin
            self.sudoku_widget.setFixedSize(total_size, total_size)
    
    def markdown_to_html(self, text):
        """Convert basic markdown to HTML for display"""
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Convert *italic* to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Convert bullet points
        text = re.sub(r'^- (.*?)$', r'• \1', text, flags=re.MULTILINE)
        # Convert numbered lists
        text = re.sub(r'^(\d+)\. (.*?)$', r'<b>\1.</b> \2', text, flags=re.MULTILINE)
        # Convert line breaks
        text = text.replace('\n', '<br>')
        return text
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
        
        # Add mode selection menu
        mode_menu = menu.addMenu("Mode")
        classic_mode = QAction("Classic", self)
        classic_mode.triggered.connect(lambda: self.set_mode("classic"))
        classic_mode.setCheckable(True)
        classic_mode.setChecked(True)
        
        autocheck_mode = QAction("Autocheck", self)
        autocheck_mode.triggered.connect(lambda: self.set_mode("autocheck"))
        autocheck_mode.setCheckable(True)
        
        mode_menu.addAction(classic_mode)
        mode_menu.addAction(autocheck_mode)
        
        # Store actions for later reference
        self.classic_action = classic_mode
        self.autocheck_action = autocheck_mode
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
                cell.cellRightClicked.connect(self.on_cell_right_clicked)
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
        # Make grid much larger - will be set dynamically based on available space
        self.adjust_grid_size()  # Initial sizing
    
    def on_cell_selected(self, row, col):
        # If in number selection mode, fill the cell with selected number
        if self.selected_number is not None:
            original_value = self._original_board[row][col]
            if (original_value is None or original_value == 0) and (row, col) not in self.hint_cells:  # Only edit empty, non-hint cells
                self.set_cell_value(row, col, self.selected_number)
            return
        
        # Handle cell selection/deselection
        if self.selected_cell == (row, col):
            # Deselect if clicking the same cell
            self.cells[row][col].set_selected(False)
            self.selected_cell = None
        else:
            # Deselect previous cell
            if self.selected_cell:
                old_row, old_col = self.selected_cell
                self.cells[old_row][old_col].set_selected(False)
            
            # Select new cell
            self.selected_cell = (row, col)
            self.cells[row][col].set_selected(True)
        
        # Clear number highlighting when selecting a cell
        if self.selected_number is not None:
            self.clear_number_selection()
        
        # Ensure main window has focus for keyboard input
        self.setFocus()
    
    def on_cell_right_clicked(self, row, col):
        """Handle right-click on cell to erase it"""
        # Only allow erasing if it's not a given number and not a hint cell
        original_value = self._original_board[row][col]
        if (original_value is None or original_value == 0) and (row, col) not in self.hint_cells:
            self.set_cell_value(row, col, 0)  # Erase the cell
            
            # Clear any selections
            if self.selected_cell == (row, col):
                self.selected_cell = None
            
            # Clear number highlighting if in number selection mode
            if self.selected_number is not None:
                self.clear_number_selection()
    
    def set_mode(self, mode):
        """Set game mode (classic or autocheck)"""
        self.game_mode = mode
        self.classic_action.setChecked(mode == "classic")
        self.autocheck_action.setChecked(mode == "autocheck")
        self.update_all_cells()  # Refresh cells to apply mode changes
    
    def set_cell_value(self, row, col, value):
        """Set a cell value and handle validation"""
        self._sudoku.board[row][col] = value if value != 0 else None
        self.cells[row][col].set_value(value, is_user_input=True)
        
        # In autocheck mode, validate the move
        if self.game_mode == "autocheck" and value != 0:
            if not self.is_valid_move(row, col, value):
                self.cells[row][col].set_error(True)
            else:
                self.cells[row][col].set_error(False)
        elif self.game_mode == "autocheck" and value == 0:
            # Clear error highlighting when cell is emptied
            self.cells[row][col].set_error(False)
        self.cells[row][col].update_style()
        # Check for completion
        self.check_completion()
        
        # Refresh number highlighting if in number selection mode
        if self.selected_number is not None:
            self.set_number_selection(self.selected_number)
    
    def is_valid_move(self, row, col, value):
        """Check if a move is valid according to Sudoku rules"""
        # Check row
        for c in range(9):
            if c != col and self._sudoku.board[row][c] == value:
                return False
        
        # Check column
        for r in range(9):
            if r != row and self._sudoku.board[r][col] == value:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r != row or c != col) and self._sudoku.board[r][c] == value:
                    return False
        
        return True
    
    def update_all_cells(self):
        """Update all cells to reflect current state"""
        for i in range(9):
            for j in range(9):
                current_val = self._sudoku.board[i][j]
                display_val = current_val if current_val is not None else 0
                self.cells[i][j].set_value(display_val, is_user_input=self._original_board[i][j] is None or self._original_board[i][j] == 0)
                
                # Apply error highlighting in autocheck mode
                if self.game_mode == "autocheck" and display_val != 0:
                    if not self.is_valid_move(i, j, display_val):
                        self.cells[i][j].set_error(True)
                    else:
                        self.cells[i][j].set_error(False)
                else:
                    self.cells[i][j].set_error(False)
    
    def keyPressEvent(self, event):
        key = event.key()
        
        # Handle arrow keys for navigation
        if self.selected_cell and key in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
            row, col = self.selected_cell
            new_row, new_col = row, col
            
            if key == Qt.Key.Key_Up and row > 0:
                new_row = row - 1
            elif key == Qt.Key.Key_Down and row < 8:
                new_row = row + 1
            elif key == Qt.Key.Key_Left and col > 0:
                new_col = col - 1
            elif key == Qt.Key.Key_Right and col < 8:
                new_col = col + 1
            
            if (new_row, new_col) != (row, col):
                self.on_cell_selected(new_row, new_col)
            return
        
        # Handle number keys
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            number = key - Qt.Key.Key_1 + 1
            
            if self.selected_cell:
                # Cell is selected - enter number in cell
                row, col = self.selected_cell
                original_value = self._original_board[row][col]
                if (original_value is None or original_value == 0) and (row, col) not in self.hint_cells:  # Only edit empty, non-hint cells
                    self.set_cell_value(row, col, number)
            else:
                # No cell selected - enter number selection mode
                if self.selected_number == number:
                    # Same number pressed - deselect
                    self.clear_number_selection()
                else:
                    # Different number - switch to this number
                    self.set_number_selection(number)
            return
        
        # Handle delete/backspace
        if key in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace, Qt.Key.Key_0]:
            if self.selected_cell:
                row, col = self.selected_cell
                original_value = self._original_board[row][col]
                if (original_value is None or original_value == 0) and (row, col) not in self.hint_cells:  # Only edit empty, non-hint cells
                    self.set_cell_value(row, col, 0)
            return
        
        # Handle Escape key to clear selections
        if key == Qt.Key.Key_Escape:
            if self.selected_number is not None:
                self.clear_number_selection()
            elif self.selected_cell is not None:
                row, col = self.selected_cell
                self.cells[row][col].set_selected(False)
                self.selected_cell = None
            return
        
        super().keyPressEvent(event)
    
    def set_number_selection(self, number):
        """Enter number selection mode"""
        # First clear any existing number highlighting
        self.clear_number_selection()
        
        self.selected_number = number
        
        # Clear cell selection
        if self.selected_cell:
            row, col = self.selected_cell
            self.cells[row][col].set_selected(False)
            self.selected_cell = None
        
        # Highlight all cells with this number
        for i in range(9):
            for j in range(9):
                if self.cells[i][j].value == number:
                    self.cells[i][j].set_highlighted(True)
    
    def clear_number_selection(self):
        """Exit number selection mode"""
        self.selected_number = None
        
        # Clear all highlighting
        for i in range(9):
            for j in range(9):
                self.cells[i][j].set_highlighted(False)
    
    def check_completion(self):
        """Check if puzzle is completed and show appropriate message"""
        # Check if all cells are filled
        for i in range(9):
            for j in range(9):
                if self._sudoku.board[i][j] is None:
                    return  # Not complete yet
        
        # All cells filled - check if solution is correct
        if self.is_solution_correct():
            self.show_completion_message(True)
        else:
            self.show_completion_message(False)
    
    def is_solution_correct(self):
        """Check if the current board state is a valid solution"""
        try:
            for i in range(9):
                for j in range(9):
                    value = self._sudoku.board[i][j]
                    if value is None or not self.is_valid_move(i, j, value):
                        return False
            return True
        except Exception as e:
            print(f"Error checking solution: {e}")
            return False
    
    def show_completion_message(self, is_correct):
        """Show completion message with animated graphics"""
        # Clean up existing overlay
        if self.graphics_overlay:
            try:
                self.graphics_overlay.close()
                self.graphics_overlay.deleteLater()
            except:
                pass
            self.graphics_overlay = None
        
        try:
            if is_correct:
                self.graphics_overlay = SuccessOverlay(self)
            else:
                self.graphics_overlay = FailureOverlay(self)
            
            # Make sure overlay covers the entire window
            self.graphics_overlay.setGeometry(0, 0, self.width(), self.height())
            self.graphics_overlay.show()
            self.graphics_overlay.raise_()  # Bring to front
        except Exception as e:
            print(f"Error showing completion graphics: {e}")
            # Fallback to simple message
            if is_correct:
                print("Puzzle completed successfully!")
            else:
                print("Puzzle has errors - please review.")
    
    def mousePressEvent(self, event):
        """Handle clicks outside the grid to clear number selection"""
        if self.selected_number is not None:
            # Check if click was inside sudoku widget
            if not self.sudoku_widget.geometry().contains(event.pos()):
                self.clear_number_selection()
        super().mousePressEvent(event)
    
    def create_ai_widget(self):
        """Create the Arlo assistant panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Arlo Assistant label
        ai_label = QLabel("Arlo - Your Sudoku Assistant")
        ai_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(ai_label)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(500)
        # Enable markdown-like formatting
        self.chat_display.setHtml("")
        layout.addWidget(self.chat_display)
        
        # Chat input
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Ask Arlo...")
        self.chat_input.setMaximumHeight(100)
        self.chat_input.installEventFilter(self)
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
        self.ai_status = QLabel("Arlo not initialized")
        self.ai_status.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.ai_status)
        
        widget.setLayout(layout)
        widget.setMinimumWidth(400)
        widget.setMaximumWidth(600)
        return widget
    
    def initialize_ai(self):
        """Initialize AI model (lazy loading)"""
        if not self.ai:
            try:
                self.ai_status.setText("Initializing Arlo...")
                self.ai = SudokuAI()
                self.ai_status.setText("Arlo ready")
                self.ai_status.setStyleSheet("color: green; font-size: 10px;")
            except Exception as e:
                self.ai_status.setText(f"Arlo Error: {str(e)}")
                self.ai_status.setStyleSheet("color: red; font-size: 10px;")
    
    def get_hint(self):
        """Get a hint from Arlo"""
        self.initialize_ai()
        if not self.ai:
            return
            
        self.hint_button.setText("Getting hint...")
        self.hint_button.setEnabled(False)
        
        # Add loading message to chat
        self.chat_display.append(f"<i>Arlo is analyzing the puzzle...</i>")
        
        # Run AI hint in separate thread
        def hint_worker():
            try:
                hint_data = self.ai.get_hint_with_position(self._sudoku.board, self._solution.board)
                self.hint_received.emit(hint_data)
            except Exception as e:
                self.hint_error.emit(str(e))
        
        thread = threading.Thread(target=hint_worker)
        thread.daemon = True
        thread.start()
    
    def on_hint_received(self, hint_data):
        """Handle hint received from Arlo"""
        # Remove the loading message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove newline
        
        try:
            if isinstance(hint_data, dict) and 'row' in hint_data and 'col' in hint_data and 'value' in hint_data:
                # AI provided a specific move
                row, col, value = hint_data['row'], hint_data['col'], hint_data['value']
                explanation = hint_data.get('explanation', 'Arlo suggested this move.')
                
                # Update the cell with the hint
                self._sudoku.board[row][col] = value
                self.cells[row][col].set_value(value, is_user_input=False)
                self.cells[row][col].set_hint(True)  # Mark as hint cell
                self.hint_cells.add((row, col))
                
                formatted_explanation = self.markdown_to_html(explanation)
                self.chat_display.append(f"<b>Arlo's Hint:</b><br>{formatted_explanation}")
                self.chat_display.append(f"<i>Applied to row {row+1}, column {col+1}: {value}</i>")
            else:
                # AI provided general advice
                formatted_hint = self.markdown_to_html(str(hint_data))
                self.chat_display.append(f"<b>Arlo's Hint:</b><br>{formatted_hint}")
        except Exception as e:
            self.chat_display.append(f"<b>Error processing hint:</b> {str(e)}")
        finally:
            self.hint_button.setText("Get Hint")
            self.hint_button.setEnabled(True)
    
    def on_hint_error(self, error_msg):
        """Handle hint error"""
        # Remove the loading message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove newline
        
        self.chat_display.append(f"<b>Error:</b> {error_msg}")
        self.hint_button.setText("Get Hint")
        self.hint_button.setEnabled(True)
    
    def send_chat_message(self):
        """Send a chat message to Arlo"""
        message = self.chat_input.toPlainText().strip()
        if not message:
            return
            
        self.initialize_ai()
        if not self.ai:
            return
        
        self.chat_display.append(f"<b>You:</b> {message}")
        self.chat_input.clear()
        self.chat_display.append(f"<i>Arlo is thinking...</i>")
        
        # Run AI chat in separate thread
        def chat_worker():
            try:
                response = self.ai.chat(message, self._sudoku.board, self._solution.board)
                self.chat_response.emit(response)
            except Exception as e:
                self.chat_error.emit(str(e))
        
        thread = threading.Thread(target=chat_worker)
        thread.daemon = True
        thread.start()
    
    def on_chat_response(self, response):
        """Handle chat response from Arlo"""
        # Remove the "thinking" message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove newline
        
        formatted_response = self.markdown_to_html(response)
        self.chat_display.append(f"<b>Arlo:</b><br>{formatted_response}")
    
    def on_chat_error(self, error_msg):
        """Handle chat error"""
        # Remove the "thinking" message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove newline
        
        self.chat_display.append(f"<b>Error:</b> {error_msg}")
    
    def eventFilter(self, obj, event):
        """Handle Enter key in chat input"""
        if obj == self.chat_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_chat_message()
                return True
        return super().eventFilter(obj, event)
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
