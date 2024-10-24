from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class Cell (QWidget):
    def __init__(self, num):
        super().__init__()
        self.selected = False
        if num == 0:
            self.pixmap = QPixmap("0")
        else:
            self.pixmap = QPixmap(str(num))
    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.selected = not self.selected
            self.update()