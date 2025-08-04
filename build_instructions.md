# Building Super Sudoku for Distribution

This guide explains how to build Super Sudoku into a standalone executable that users can run without installing Python or dependencies.

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **All dependencies** installed (see installation section below)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements_build.txt
   ```

2. **Ensure you have the PDF file:**
   - Make sure `solving_sudoku.pdf` is in the project directory
   - This file will be bundled with the application

## Building the Application

### Option 1: Using the Build Script (Recommended)

```bash
python build_config.py
```

This will create a single executable file in the `dist/` folder.

### Option 2: Manual PyInstaller Command

```bash
pyinstaller --name=SuperSudoku --onefile --windowed --add-data="solving_sudoku.pdf;." --hidden-import=langchain_community.document_loaders.pdf --hidden-import=langchain_openai --collect-all=langchain --collect-all=langchain_community --collect-all=langchain_openai --clean --noconfirm app.py
```

## Output

After building, you'll find:
- **`dist/SuperSudoku.exe`** (Windows) or **`dist/SuperSudoku`** (Mac/Linux) - The standalone executable
- **`build/`** folder - Temporary build files (can be deleted)
- **`SuperSudoku.spec`** - PyInstaller spec file (can be deleted)

## Distribution

The executable in the `dist/` folder is completely self-contained and can be:
- Copied to any computer with the same operating system
- Distributed to users without requiring Python installation
- Run directly by double-clicking

## Platform-Specific Notes

### Windows
- The executable will be named `SuperSudoku.exe`
- No console window will appear when running the app
- Users may need to allow the app through Windows Defender

### macOS
- The executable will be named `SuperSudoku`
- Users may need to right-click and select "Open" the first time due to security settings
- Consider code signing for wider distribution

### Linux
- The executable will be named `SuperSudoku`
- Make sure it has execute permissions: `chmod +x dist/SuperSudoku`

## Troubleshooting

### Common Issues

1. **Missing modules error:**
   - Add the missing module to the `--hidden-import` list in the build script
   - Or use `--collect-all=module_name` for entire packages

2. **PDF file not found:**
   - Ensure `solving_sudoku.pdf` is in the project directory
   - Check that the `--add-data` parameter is correct for your platform

3. **Large file size:**
   - This is normal for PyInstaller builds as they include the Python interpreter
   - Consider using `--onedir` instead of `--onefile` for slightly better performance

4. **Slow startup:**
   - First run may be slower as the executable unpacks
   - Subsequent runs will be faster
   - Using `--onedir` can improve startup time

### Testing the Build

Before distributing:
1. Test the executable on a clean system without Python installed
2. Verify that all features work (Sudoku generation, AI assistance)
3. Test the settings dialog and API key configuration
4. Ensure PDF loading works correctly

## File Structure for Distribution

When distributing your app, include:
```
SuperSudoku/
├── SuperSudoku.exe (or SuperSudoku on Mac/Linux)
├── README.txt (optional - user instructions)
└── LICENSE.txt (if applicable)
```

## User Instructions

Create a simple README.txt for end users:

```
Super Sudoku - AI-Powered Sudoku Game

Getting Started:
1. Double-click SuperSudoku.exe to run the application
2. To use the AI assistant "Arlo":
   - Go to Settings in the menu bar
   - Enter your OpenAI API key
   - Get your API key from: https://platform.openai.com/api-keys

Features:
- Multiple difficulty levels
- AI-powered hints and assistance
- Two game modes: Classic and Autocheck
- Keyboard and mouse controls

For support or questions, visit: [your website/contact]
```