from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QTabWidget,
                             QWidget, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import config

class SettingsDialog(QDialog):
    """Settings dialog for configuring API keys and other preferences"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Super Sudoku Settings")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # API Configuration tab
        api_tab = self.create_api_tab()
        tab_widget.addTab(api_tab, "API Configuration")
        
        # About tab
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, "About")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test API Key")
        self.test_button.clicked.connect(self.test_api_key)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_api_tab(self):
        """Create the API configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("OpenAI API Configuration")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "To use Arlo, the AI assistant, you need to provide your OpenAI API key.\n"
            "You can get one from: https://platform.openai.com/api-keys"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # API Key input
        api_key_label = QLabel("OpenAI API Key:")
        layout.addWidget(api_key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.api_key_input)
        
        # Show/Hide API key checkbox
        self.show_key_checkbox = QCheckBox("Show API key")
        self.show_key_checkbox.toggled.connect(self.toggle_key_visibility)
        layout.addWidget(self.show_key_checkbox)
        
        # Status info
        self.status_label = QLabel()
        self.status_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        # Info box
        info_text = (
            "Note: Your API key is stored securely on your local machine and is never "
            "shared with anyone except OpenAI's servers for processing your requests."
        )
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "background-color: #e3f2fd; padding: 10px; border-radius: 5px; "
            "border: 1px solid #90caf9; margin-top: 10px;"
        )
        layout.addWidget(info_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_about_tab(self):
        """Create the about tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Super Sudoku")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(version_label)
        
        # Description
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMaximumHeight(200)
        about_text.setHtml("""
        <p><b>Super Sudoku</b> is an advanced Sudoku puzzle game featuring an AI assistant named Arlo.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>Multiple difficulty levels</li>
        <li>Classic and Autocheck game modes</li>
        <li>AI-powered hints and assistance</li>
        <li>Intuitive keyboard and mouse controls</li>
        <li>Beautiful, responsive interface</li>
        </ul>
        
        <p><b>AI Assistant:</b> Arlo uses advanced reasoning to provide helpful hints and explanations 
        based on standard Sudoku solving techniques.</p>
        """)
        layout.addWidget(about_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def toggle_key_visibility(self, show):
        """Toggle API key visibility"""
        if show:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def load_current_settings(self):
        """Load current settings into the dialog"""
        api_key = config.get_openai_api_key()
        if api_key:
            self.api_key_input.setText(api_key)
            self.status_label.setText("✓ API key configured")
            self.status_label.setStyleSheet("color: green; margin-top: 10px;")
        else:
            self.status_label.setText("⚠ No API key configured - AI features disabled")
            self.status_label.setStyleSheet("color: orange; margin-top: 10px;")
    
    def test_api_key(self):
        """Test the API key validity"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Test API Key", "Please enter an API key first.")
            return
        
        # Simple validation - check format
        if not api_key.startswith('sk-') or len(api_key) < 20:
            QMessageBox.warning(
                self, "Test API Key", 
                "API key format appears invalid. OpenAI API keys typically start with 'sk-' and are longer."
            )
            return
        
        # For now, just show a success message
        # In a real implementation, you might want to make a test API call
        QMessageBox.information(
            self, "Test API Key", 
            "API key format looks valid. The key will be tested when you use AI features."
        )
    
    def save_settings(self):
        """Save the settings"""
        api_key = self.api_key_input.text().strip()
        
        if api_key:
            if not api_key.startswith('sk-'):
                reply = QMessageBox.question(
                    self, "Save Settings",
                    "The API key doesn't appear to follow OpenAI's format (starting with 'sk-'). "
                    "Are you sure you want to save it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            config.set_openai_api_key(api_key)
            QMessageBox.information(self, "Settings Saved", "API key has been saved successfully!")
        else:
            # Clear the API key
            config.set_openai_api_key("")
            QMessageBox.information(self, "Settings Saved", "API key has been cleared.")
        
        self.accept()
    
    @staticmethod
    def show_settings(parent=None):
        """Show the settings dialog"""
        dialog = SettingsDialog(parent)
        return dialog.exec()