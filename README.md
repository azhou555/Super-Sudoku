# Super Sudoku 🧩

An advanced Sudoku puzzle game featuring **Arlo**, an AI assistant powered by OpenAI's language models and trained on expert Sudoku solving techniques.

![Super Sudoku Screenshot](screenshot.png) <!-- Add screenshot if available -->

##  Features

###  **Core Gameplay**
- **Multiple Difficulties**: Easy, Medium, Hard difficulty levels
- **Two Game Modes**:
  - **Classic Mode**: Traditional Sudoku experience
  - **Autocheck Mode**: Real-time error detection and highlighting
- **Intuitive Controls**: Full keyboard and mouse support
- **Smart Selection**: Click numbers to highlight all instances

###  **AI Assistant - "Arlo"**
- **Intelligent Hints**: Get strategic advice based on proven Sudoku techniques
- **Step-by-Step Explanations**: Learn the reasoning behind each move
- **Interactive Chat**: Ask questions about Sudoku strategies
- **Educational**: Trained on Michael Mepham's "How to Solve Sudoku" guide

###  **User Interface**
- **Responsive Design**: Automatically adjusts to window size
- **Visual Feedback**: Completion animations and error indicators
- **Professional Layout**: Clean, modern interface built with PyQt6

###  **Secure Configuration**
- **Private API Keys**: Your OpenAI API key stays on your device
- **Easy Setup**: Built-in settings dialog for configuration
- **Cross-Platform**: Works on Windows, macOS, and Linux

##  Quick Start

### Option 1: Download Pre-built Executable (Recommended)
1. Download the latest release for your platform
2. Run `SuperSudoku.exe` (Windows) or `SuperSudoku` (Mac/Linux)
3. Configure your OpenAI API key in Settings → API Configuration
4. Start playing!

### Option 2: Run from Source
```bash
# Clone the repository
git clone <repository-url>
cd "Super Sudoku"

# Install dependencies
pip install -r requirements_build.txt

# Run the application
python run_app.py
```

##  Setting Up AI Features

To use Arlo, the AI assistant:

1. **Get an OpenAI API Key**:
   - Visit [OpenAI's platform](https://platform.openai.com/api-keys)
   - Create an account and generate an API key
   - Copy the key (starts with `sk-`)

2. **Configure in Super Sudoku**:
   - Open Super Sudoku
   - Go to **Settings** in the menu bar
   - Paste your API key in the **API Configuration** tab
   - Click **Save**

3. **Start Using Arlo**:
   - Click **"Get Hint"** for strategic advice
   - Type questions in the chat box
   - Arlo will analyze your puzzle and provide helpful guidance

##  How to Play

### Basic Controls
- **Mouse**: Click cells to select, right-click to erase
- **Keyboard**: 
  - `1-9`: Enter numbers or highlight all instances
  - `Arrow Keys`: Navigate between cells
  - `Delete/Backspace/0`: Erase cell contents
  - `Escape`: Clear selections

### Game Modes
- **Classic Mode**: Complete the puzzle, check for errors manually
- **Autocheck Mode**: Invalid moves are highlighted in real-time

### Using Arlo
- **Get Hint**: Provides the next logical move with explanation
- **Chat**: Ask about techniques, strategies, or specific situations

##  Building from Source

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Development Setup
```bash
# Install dependencies
pip install -r requirements_build.txt

# Run in development mode
python run_app.py
```

### Building Executable
```bash
# Build standalone application
python build_config.py

# Find your executable in the dist/ folder
```

For detailed build instructions, see `build_instructions.md`.

##  Project Structure
```
Super Sudoku/
├── app.py                  # Main application
├── model.py               # AI assistant implementation
├── config.py              # Configuration management
├── settings_dialog.py     # Settings interface
├── square.py              # Sudoku cell implementation
├── run_app.py             # Development launcher
├── build_config.py        # Build script
├── solving_sudoku.pdf     # AI training material
└── requirements_build.txt # Dependencies
```

##  Technical Details

### Dependencies
- **PyQt6**: GUI framework
- **LangChain**: AI/LLM integration framework
- **OpenAI**: Language model API
- **python-sudoku**: Puzzle generation
- **PyPDF2/pypdf**: PDF processing for RAG

### AI Architecture
- **RAG (Retrieval Augmented Generation)**: Uses expert Sudoku solving guide as knowledge base
- **GPT-4**: Advanced reasoning for hint generation and explanations
- **Vector Search**: Finds relevant solving techniques for each situation

### Security
- API keys stored locally in platform-appropriate directories
- No telemetry or data collection
- All AI processing happens via secure OpenAI API calls

##  License

This project uses the following resources:
- Sudoku solving techniques from Michael Mepham's guide
- py-sudoku library for puzzle generation
- OpenAI API for AI assistance


---

** Enjoy playing Super Sudoku with Arlo! **