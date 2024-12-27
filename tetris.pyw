import pygame
import random
from typing import List, Tuple
import os
import winshell
from win32com.client import Dispatch

# Set window icon (add this code before pygame.init())
icon_path = os.path.join(os.path.dirname(__file__), 'tetris_icon.ico')
if os.path.exists(icon_path):
    pygame.display.set_icon(pygame.image.load(icon_path))

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GRID_COLOR = (211, 211, 211)  # Light gray for grid lines
SHADOW_COLOR = (169, 169, 169)  # Dark gray for shadow
INITIAL_MOVE_DELAY = 170  # Milliseconds before starting continuous movement
CONTINUOUS_MOVE_DELAY = 80  # Milliseconds between continuous movements

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Color schemes
LIGHT_THEME = {
    'background': WHITE,
    'grid': GRID_COLOR,
    'text': BLACK,
    'shadow': SHADOW_COLOR
}

DARK_THEME = {
    'background': (40, 44, 52),    # Dark background
    'grid': (70, 74, 82),          # Darker grid lines
    'text': WHITE,                 # White text
    'shadow': (100, 104, 112)      # Lighter shadow (changed from 60, 64, 72)
}

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.paused = False
        self.dark_mode = False
        self.theme = LIGHT_THEME
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_speed = 500  # Initial fall speed in milliseconds (from 1000)
        self.last_fall = pygame.time.get_ticks()
        self.last_move_time = 0
        self.move_delay = 0
        self.moving_left = False
        self.moving_right = False

    def new_piece(self) -> dict:
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }

    def valid_move(self, piece: dict, x_offset: int = 0, y_offset: int = 0) -> bool:
        for y, row in enumerate(piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece['x'] + x + x_offset
                    new_y = piece['y'] + y + y_offset
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def rotate_piece(self, piece: dict) -> None:
        # Create a rotated version of the shape
        rotated = list(zip(*piece['shape'][::-1]))
        old_shape = piece['shape']
        piece['shape'] = rotated
        
        # Define possible offset positions to try (wall kicks)
        # Format: (x_offset, y_offset)
        kick_positions = [
            (0, 0),   # Try original position
            (-1, 0),  # Try shifting left
            (1, 0),   # Try shifting right
            (-2, 0),  # Try shifting two spaces left
            (2, 0),   # Try shifting two spaces right
        ]
        
        # Try each kick position
        original_x = piece['x']
        rotation_successful = False
        
        for x_offset, y_offset in kick_positions:
            piece['x'] += x_offset
            if self.valid_move(piece):
                rotation_successful = True
                break
            piece['x'] = original_x  # Reset position if kick failed
        
        # If no kick position works, revert the rotation
        if not rotation_successful:
            piece['shape'] = old_shape

    def merge_piece(self) -> None:
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']

    def clear_lines(self) -> None:
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            else:
                y -= 1
        
        if lines_cleared:
            self.lines += lines_cleared
            self.score += [100, 300, 500, 800][lines_cleared - 1] * self.level
            self.level = self.lines // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)  # Faster base speed and faster level scaling

    def draw(self) -> None:
        self.screen.fill(self.theme['background'])
        
        # Draw grid lines
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(self.screen, self.theme['grid'],
                               (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw shadow - Create a deep copy of the current piece to avoid reference issues
        shadow_piece = {
            'shape': [row[:] for row in self.current_piece['shape']],  # Deep copy of shape
            'color': self.current_piece['color'],
            'x': self.current_piece['x'],
            'y': self.current_piece['y']
        }
        
        while self.valid_move(shadow_piece, y_offset=1):
            shadow_piece['y'] += 1
        
        # Draw shadow piece without rotation validation
        for y, row in enumerate(shadow_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.theme['shadow'],
                                   ((shadow_piece['x'] + x) * BLOCK_SIZE,
                                    (shadow_piece['y'] + y) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw placed blocks
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color:
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_piece['color'],
                                   ((self.current_piece['x'] + x) * BLOCK_SIZE,
                                    (self.current_piece['y'] + y) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, self.theme['text'])
        level_text = font.render(f'Level: {self.level}', True, self.theme['text'])
        lines_text = font.render(f'Lines: {self.lines}', True, self.theme['text'])
        controls_text = font.render('Press P to Pause', True, self.theme['text'])
        dark_mode_text = font.render('Press D for Dark Mode', True, self.theme['text'])
        
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, 50))
        self.screen.blit(lines_text, (GRID_WIDTH * BLOCK_SIZE + 10, 90))
        self.screen.blit(controls_text, (GRID_WIDTH * BLOCK_SIZE + 10, 130))
        self.screen.blit(dark_mode_text, (GRID_WIDTH * BLOCK_SIZE + 10, 170))

        if self.paused:
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            # Draw pause text
            font = pygame.font.Font(None, 48)
            pause_text = font.render('PAUSED', True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
            
            # Draw "Press P to continue" text
            font_small = pygame.font.Font(None, 36)
            continue_text = font_small.render('Press P to continue', True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()

    def run(self) -> None:
        while not self.game_over:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_d:
                        self.dark_mode = not self.dark_mode
                        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
                    if not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.moving_left = True
                            self.moving_right = False
                            self.last_move_time = current_time
                            self.move_delay = INITIAL_MOVE_DELAY
                            if self.valid_move(self.current_piece, x_offset=-1):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            self.moving_right = True
                            self.moving_left = False
                            self.last_move_time = current_time
                            self.move_delay = INITIAL_MOVE_DELAY
                            if self.valid_move(self.current_piece, x_offset=1):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_UP:
                            self.rotate_piece(self.current_piece)
                        elif event.key == pygame.K_SPACE:
                            while self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece['y'] += 1
                            self.merge_piece()
                            self.clear_lines()
                            self.current_piece = self.new_piece()
                            if not self.valid_move(self.current_piece):
                                self.game_over = True
                
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.moving_left = False
                    elif event.key == pygame.K_RIGHT:
                        self.moving_right = False

            # Handle continuous movement
            if not self.paused:
                if (self.moving_left or self.moving_right) and current_time - self.last_move_time > self.move_delay:
                    if self.moving_left and self.valid_move(self.current_piece, x_offset=-1):
                        self.current_piece['x'] -= 1
                    elif self.moving_right and self.valid_move(self.current_piece, x_offset=1):
                        self.current_piece['x'] += 1
                    self.last_move_time = current_time
                    self.move_delay = CONTINUOUS_MOVE_DELAY

                # Handle soft drop (down key)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    self.fall_speed = 50
                else:
                    self.fall_speed = max(100, 1000 - (self.level - 1) * 100)

                # Handle piece falling
                if current_time - self.last_fall > self.fall_speed:
                    if self.valid_move(self.current_piece, y_offset=1):
                        self.current_piece['y'] += 1
                    else:
                        self.merge_piece()
                        self.clear_lines()
                        self.current_piece = self.new_piece()
                        if not self.valid_move(self.current_piece):
                            self.game_over = True
                    self.last_fall = current_time

            self.draw()
            self.clock.tick(60)

        # Game over screen
        font = pygame.font.Font(None, 48)
        game_over_text = font.render('Game Over!', True, WHITE)
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                         SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.flip()
        
        # Wait for a moment before closing
        pygame.time.wait(2000)

def create_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Tetris.lnk")
    target = os.path.abspath(__file__)
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = 'pythonw'
    shortcut.Arguments = f'"{target}"'
    shortcut.IconLocation = icon_path if os.path.exists(icon_path) else target
    shortcut.save()

# Uncomment the following line to create the shortcut
create_shortcut()

if __name__ == '__main__':
    game = Tetris()
    game.run()
    pygame.quit()