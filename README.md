# Python Tetris Game

A basic Tetris game built with Pygame.

## Requirements

- Python 3.x
- Required packages:
  ```
  pygame>=2.0.0
  pywin32>=305
  winshell>=0.6
  ```

## Installation

1. Clone this repository 

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python tetris.pyw
   ```

2. Controls:
   - **Left Arrow**: Move piece left
   - **Right Arrow**: Move piece right
   - **Down Arrow**: Soft drop (faster falling)
   - **Up Arrow**: Rotate piece
   - **Spacebar**: Hard drop (instant placement)
   - **P**: Pause/Unpause game
   - **D**: Toggle dark/light mode

## Creating a Desktop Shortcut (Windows Only)

1. Open `tetris.pyw` in a text editor
2. Uncomment the line near the bottom that says:
   ```python
   # create_shortcut()
   ```
3. Run the script once to create the shortcut
4. Re-comment the line to prevent creating multiple shortcuts

## Scoring System

- 1 line: 100 points × level
- 2 lines: 300 points × level
- 3 lines: 500 points × level
- 4 lines: 800 points × level

## Leveling System

- Every 10 lines cleared increases the level
- Each level increases the falling speed of the pieces
- Maximum fall speed is reached at higher levels

## Development

The game is built using Pygame and implements the following key features:

- Wall kick system for piece rotation
- Ghost piece preview for better placement
- Smooth piece movement with initial and continuous movement delays
- Responsive controls and collision detection
- Dynamic difficulty scaling

## License

This project is open source and available under the MIT License.
