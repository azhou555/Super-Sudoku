from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class Cell (QWidget):
    cellSelected = pyqtSignal(int, int)
    
    def __init__(self, num, row=0, col=0, is_given=True):
        super().__init__()
        self.selected = False
        self.row = row
        self.col = col
        self.value = num
        self.is_given = is_given and num != 0  # Given numbers are pre-filled
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(str(num) if num != 0 else "")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set font and styling
        font = QFont("Arial", 16, QFont.Weight.Bold)
        self.label.setFont(font)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.setFixedSize(55, 55)
        self.update_style()
    
    def get_border_style(self):
        """Get border style based on position in 3x3 grid"""
        # Thick borders for outer edges of 3x3 boxes
        top = "2px" if self.row % 3 == 0 else "0.5px"
        bottom = "2px" if self.row % 3 == 2 else "0.5px" 
        left = "2px" if self.col % 3 == 0 else "0.5px"
        right = "2px" if self.col % 3 == 2 else "0.5px"
        
        return f"border-top: {top} solid #333; border-bottom: {bottom} solid #333; border-left: {left} solid #333; border-right: {right} solid #333;"
    
    def update_style(self):
        """Update cell styling"""
        border_style = self.get_border_style()
        
        if self.selected:
            bg_color = "#E3F2FD"  # Light blue
            text_color = "#1976D2"  # Blue
        else:
            bg_color = "white"
            text_color = "#1976D2" if self.is_given else "#424242"  # Blue for given, gray for user
        
        style = f"""
            QWidget {{
                {border_style}
                background-color: {bg_color};
            }}
            QLabel {{
                color: {text_color};
                font-weight: {'bold' if self.is_given else 'normal'};
            }}
        """
        self.setStyleSheet(style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.cellSelected.emit(self.row, self.col)
    
    def set_selected(self, selected):
        self.selected = selected
        self.update_style()
    
    def set_value(self, value, is_user_input=True):
        self.value = value
        if is_user_input:
            self.is_given = False
        self.label.setText(str(value) if value != 0 else "")
        self.update_style()