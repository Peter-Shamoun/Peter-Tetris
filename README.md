I'll help create a README.md and requirements.txt for your Tetris project.

```markdown:README.md
# Python Tetris

A classic Tetris implementation using Pygame with dark/light mode support and customizable controls.

## Features
- Classic Tetris gameplay
- Dark/Light mode toggle
- Score tracking
- Level progression
- Ghost piece preview
- Pause functionality

## Requirements
- Python 3.6+
- Required packages listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Creating Desktop Shortcut

1. Open `tetris.pyw` in a text editor
2. Locate the bottom of the file and uncomment the line `# create_shortcut()` by removing the `#`
3. Run the game once to create the shortcut
4. Re-comment the line by adding the `#` back to prevent creating duplicate shortcuts

## Controls
- Left/Right Arrow: Move piece
- Up Arrow: Rotate piece
- Down Arrow: Soft drop
- Space: Hard drop
- P: Pause game
- D: Toggle dark/light mode

## Running the Game
Simply double-click the `tetris.pyw` file or run:
```bash
pythonw tetris.pyw
```
```

```text:requirements.txt
pygame>=2.0.0
pywin32>=305
winshell>=0.6
```