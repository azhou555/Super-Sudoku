"""
Build configuration for PyInstaller
Run with: python build_config.py
"""

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_app():
    """Build the Super Sudoku application using PyInstaller"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define paths
    main_script = str(current_dir / "app.py")
    pdf_file = str(current_dir / "solving_sudoku.pdf")
    icon_file = None  # Add icon path if you have one
    
    # Determine the correct path separator for --add-data
    if sys.platform.startswith('win'):
        data_separator = ';'
    else:
        data_separator = ':'
    
    # PyInstaller arguments
    args = [
        main_script,
        '--name=SuperSudoku',
        '--onefile',  # Create a single executable file
        '--windowed',  # Don't show console window on Windows
        f'--add-data={pdf_file}{data_separator}.',  # Include PDF file
        '--hidden-import=langchain_community.document_loaders.pdf',
        '--hidden-import=langchain_openai',
        '--hidden-import=langchain_text_splitters',
        '--hidden-import=PyPDF2',
        '--hidden-import=pypdf',
        '--collect-all=langchain',
        '--collect-all=langchain_community',
        '--collect-all=langchain_openai',
        '--clean',  # Clean PyInstaller cache
        '--noconfirm',  # Don't ask for confirmation to overwrite
    ]
    
    # Add icon if available
    if icon_file and os.path.exists(icon_file):
        args.append(f'--icon={icon_file}')
    
    # Add platform-specific arguments
    if sys.platform.startswith('win'):
        # Only add version file if it exists
        version_file = current_dir / "version_info.txt"
        if version_file.exists():
            args.append(f'--version-file={version_file}')
    
    print("Building Super Sudoku application...")
    print(f"Arguments: {' '.join(args)}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print("Executable can be found in the 'dist' folder")

if __name__ == "__main__":
    build_app()