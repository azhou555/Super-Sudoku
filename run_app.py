#!/usr/bin/env python3
"""
Super Sudoku Launcher Script

This script provides a convenient way to run Super Sudoku with proper error handling
and environment setup. It can be used during development or as an alternative to
the compiled executable.
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('PyQt6', 'PyQt6'),
        ('sudoku', 'python-sudoku'),
        ('langchain', 'langchain'),
        ('langchain_openai', 'langchain-openai'),
        ('openai', 'openai'),
        ('dotenv', 'python-dotenv'),
    ]
    
    missing_packages = []
    
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append((package_name, pip_name))
    
    if missing_packages:
        print("Error: Missing required packages:")
        for package_name, pip_name in missing_packages:
            print(f"  - {package_name} (install with: pip install {pip_name})")
        print("\nPlease install missing packages and try again.")
        print("Or install all at once with: pip install -r requirements_build.txt")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    current_dir = Path(__file__).parent
    required_files = [
        'app.py',
        'model.py',
        'square.py',
        'config.py',
        'settings_dialog.py',
        'solving_sudoku.pdf'
    ]
    
    missing_files = []
    for file_name in required_files:
        if not (current_dir / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print("Error: Missing required files:")
        for file_name in missing_files:
            print(f"  - {file_name}")
        return False
    
    return True

def setup_environment():
    """Set up the environment for running the application"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Set working directory to the script's directory
    os.chdir(current_dir)

def main():
    """Main entry point"""
    print("Super Sudoku Launcher")
    print("=" * 20)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check required files
    print("Checking required files...")
    if not check_files():
        sys.exit(1)
    
    # Set up environment
    print("Setting up environment...")
    setup_environment()
    
    # Import and run the application
    try:
        print("Starting Super Sudoku...")
        from PyQt6.QtWidgets import QApplication
        from app import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("Super Sudoku")
        app.setApplicationVersion("1.0.0")
        
        window = MainWindow()
        window.show()
        
        print("Application started successfully!")
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error importing application modules: {e}")
        print("Please check that all files are present and dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()