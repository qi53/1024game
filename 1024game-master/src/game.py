#!/usr/bin/env python3
"""
1024 Game - Core Game Logic
Enhanced version with level system and additional features
"""

import random
import copy
from typing import List, Tuple, Optional, Dict, Any
from src.constants import GRID_SIZE, WIN_VALUE, DIFFICULTY_SETTINGS


class Game:
    """Enhanced game class with level system and additional features"""

    def __init__(self, level: int = 1):
        """Initialize the game with specified level"""
        self.level = level
        self.difficulty = self._get_difficulty_for_level(level)
        self.settings = DIFFICULTY_SETTINGS[self.difficulty]
        
        # Set game parameters based on difficulty
        self.grid_size = self.settings['grid_size']
        self.win_value = self.settings['win_value']
        self.spawn_4_chance = self.settings['spawn_4_chance']
        self.time_limit = self.settings['time_limit']
        self.move_limit = self.settings['move_limit']
        
        # Initialize game state
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.moves = 0
        self.time_elapsed = 0
        self.game_over = False
        self.won = False
        self.undo_stack = []  # For undo functionality
        
        # Initialize the game
        self.reset_game()

    def _get_difficulty_for_level(self, level: int) -> int:
        """Get difficulty setting based on level number"""
        if level <= 5:
            return 1  # Easy
        elif level <= 10:
            return 2  # Medium
        elif level <= 15:
            return 3  # Hard
        else:
            return 4  # Expert

    def reset_game(self) -> None:
        """Reset the game to initial state"""
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.moves = 0
        self.time_elapsed = 0
        self.game_over = False
        self.won = False
        self.undo_stack = []
        
        # Add initial tiles based on difficulty
        for _ in range(self.settings['initial_tiles']):
            self.add_random_tile()

    def add_random_tile(self) -> bool:
        """Add a random tile (2 or 4) to an empty cell"""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return False

        # Use difficulty-specific spawn chance for 4
        value = 2 if random.random() > self.spawn_4_chance else 4
        row, col = random.choice(empty_cells)
        self.grid[row][col] = value
        return True

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates"""
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells

    def move(self, direction: str) -> bool:
        """Move tiles in the specified direction"""
        if direction not in ['up', 'down', 'left', 'right']:
            return False

        # Save state for undo
        if len(self.undo_stack) >= 10:  # Limit undo stack size
            self.undo_stack.pop(0)
        self.undo_stack.append({
            'grid': copy.deepcopy(self.grid),
            'score': self.score,
            'moves': self.moves
        })

        original_grid = copy.deepcopy(self.grid)
        moved = False

        if direction == 'left':
            moved = self._move_left()
        elif direction == 'right':
            moved = self._move_right()
        elif direction == 'up':
            moved = self._move_up()
        elif direction == 'down':
            moved = self._move_down()

        if moved:
            self.moves += 1
            # Check win/lose conditions
            self._check_game_state()

        return moved

    def undo(self) -> bool:
        """Undo the last move"""
        if not self.undo_stack:
            return False
        
        last_state = self.undo_stack.pop()
        self.grid = last_state['grid']
        self.score = last_state['score']
        self.moves = last_state['moves']
        self.game_over = False
        self.won = False
        return True

    def _move_left(self) -> bool:
        """Move tiles to the left"""
        moved = False
        for i in range(self.grid_size):
            # Extract row
            row = self.grid[i][:]

            # Move and merge
            new_row, row_score = self._merge_row(row)
            self.score += row_score

            # Update grid
            if new_row != self.grid[i]:
                moved = True
            self.grid[i] = new_row

        return moved

    def _move_right(self) -> bool:
        """Move tiles to the right"""
        moved = False
        for i in range(self.grid_size):
            # Extract row and reverse for right movement
            row = self.grid[i][::-1]

            # Move and merge
            new_row, row_score = self._merge_row(row)
            self.score += row_score

            # Reverse back and update grid
            new_row = new_row[::-1]
            if new_row != self.grid[i]:
                moved = True
            self.grid[i] = new_row

        return moved

    def _move_up(self) -> bool:
        """Move tiles up"""
        moved = False
        for j in range(self.grid_size):
            # Extract column
            col = [self.grid[i][j] for i in range(self.grid_size)]

            # Move and merge
            new_col, col_score = self._merge_row(col)
            self.score += col_score

            # Update grid
            for i in range(self.grid_size):
                if new_col[i] != self.grid[i][j]:
                    moved = True
                self.grid[i][j] = new_col[i]

        return moved

    def _move_down(self) -> bool:
        """Move tiles down"""
        moved = False
        for j in range(self.grid_size):
            # Extract column and reverse for down movement
            col = [self.grid[i][j] for i in range(self.grid_size)][::-1]

            # Move and merge
            new_col, col_score = self._merge_row(col)
            self.score += col_score

            # Reverse back and update grid
            new_col = new_col[::-1]
            for i in range(self.grid_size):
                if new_col[i] != self.grid[i][j]:
                    moved = True
                self.grid[i][j] = new_col[i]

        return moved

    def _merge_row(self, row: List[int]) -> Tuple[List[int], int]:
        """Merge a row and return new row and score gained"""
        # Remove zeros and merge identical adjacent numbers
        non_zero = [x for x in row if x != 0]
        new_row = [0] * self.grid_size
        score_gained = 0

        i = 0
        while i < len(non_zero) - 1:
            if non_zero[i] == non_zero[i + 1]:
                # Merge
                merged_value = non_zero[i] * 2
                new_row[i // 2] = merged_value
                score_gained += merged_value
                i += 2
            else:
                new_row[i // 2] = non_zero[i]
                i += 1

        # Add remaining element if any
        if i < len(non_zero):
            new_row[i // 2] = non_zero[i]

        return new_row, score_gained

    def _check_game_state(self) -> None:
        """Check if the game is won or lost"""
        # Check win condition
        for row in self.grid:
            if self.win_value in row:
                self.won = True
                return

        # Check if game is over
        if not self.get_empty_cells():
            # Check for possible merges
            for i in range(self.grid_size):
                for j in range(self.grid_size - 1):
                    # Check horizontal merges
                    if self.grid[i][j] == self.grid[i][j + 1]:
                        return
                    # Check vertical merges
                    if self.grid[j][i] == self.grid[j + 1][i]:
                        return

            # No moves left
            self.game_over = True

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.game_over

    def is_win(self) -> bool:
        """Check if player has won"""
        return self.won

    def get_grid(self) -> List[List[int]]:
        """Get current grid state"""
        return copy.deepcopy(self.grid)

    def get_score(self) -> int:
        """Get current score"""
        return self.score

    def get_moves(self) -> int:
        """Get number of moves made"""
        return self.moves

    def get_time_elapsed(self) -> float:
        """Get time elapsed in seconds"""
        return self.time_elapsed

    def update_time(self, dt: float) -> None:
        """Update time elapsed"""
        self.time_elapsed += dt

    def is_time_limit_exceeded(self) -> bool:
        """Check if time limit is exceeded"""
        return self.time_limit is not None and self.time_elapsed >= self.time_limit

    def is_move_limit_exceeded(self) -> bool:
        """Check if move limit is exceeded"""
        return self.move_limit is not None and self.moves >= self.move_limit

    def get_level(self) -> int:
        """Get current level"""
        return self.level

    def get_difficulty(self) -> int:
        """Get current difficulty"""
        return self.difficulty

    def get_settings(self) -> Dict[str, Any]:
        """Get current game settings"""
        return self.settings.copy()

    def get_max_tile_value(self) -> int:
        """Get the maximum tile value on the grid"""
        max_value = 0
        for row in self.grid:
            for cell in row:
                if cell > max_value:
                    max_value = cell
        return max_value

    def get_empty_cell_count(self) -> int:
        """Get the number of empty cells"""
        return len(self.get_empty_cells())

    def get_merge_count(self) -> int:
        """Get the number of merges possible"""
        count = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size - 1):
                # Check horizontal merges
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i][j + 1]:
                    count += 1
                # Check vertical merges
                if self.grid[j][i] != 0 and self.grid[j][i] == self.grid[j + 1][i]:
                    count += 1
        return count