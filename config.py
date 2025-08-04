import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration management for Super Sudoku app"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.env_file = self.config_dir / ".env"
        self._ensure_config_dir()
        load_dotenv(self.env_file)
    
    def _get_config_dir(self):
        """Get the configuration directory based on the platform"""
        if sys.platform.startswith('win'):
            # Windows: use APPDATA
            base_dir = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        elif sys.platform.startswith('darwin'):
            # macOS: use Application Support
            base_dir = Path.home() / 'Library' / 'Application Support'
        else:
            # Linux/Unix: use XDG config or ~/.config
            base_dir = Path(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')))
        
        return base_dir / 'SuperSudoku'
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_openai_api_key(self):
        """Get OpenAI API key from multiple sources in order of priority"""
        # 1. Environment variable (highest priority)
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            return api_key
        
        # 2. Legacy API_KEY environment variable
        api_key = os.environ.get('API_KEY')
        if api_key:
            return api_key
            
        # 3. Config file
        config_data = self.load_config()
        api_key = config_data.get('openai_api_key')
        if api_key:
            return api_key
        
        return None
    
    def set_openai_api_key(self, api_key):
        """Save OpenAI API key to config file"""
        config_data = self.load_config()
        config_data['openai_api_key'] = api_key
        self.save_config(config_data)
        
        # Also set in environment for current session
        os.environ['OPENAI_API_KEY'] = api_key
    
    def load_config(self):
        """Load configuration from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_config(self, config_data):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get_pdf_path(self):
        """Get the path to the solving_sudoku.pdf file"""
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = Path(sys._MEIPASS)
        else:
            # Running as script
            base_path = Path(__file__).parent
        
        return base_path / "solving_sudoku.pdf"
    
    def has_valid_api_key(self):
        """Check if a valid API key is available"""
        api_key = self.get_openai_api_key()
        return api_key is not None and len(api_key.strip()) > 0

# Global config instance
config = Config()