#!/usr/bin/env python3
"""
1024 Game - Core Game Logic
Contains the Game class with all game mechanics
"""

import random
import os
from typing import List, Tuple, Optional


class Game:
    """Main game class containing all game logic"""

    GRID_SIZE = 4
    WIN_VALUE = 1024

    def __init__(self):
        """Initialize the game"""
        self.grid = [[0] * self.GRID_SIZE for _ in range(self.GRID_SIZE)]
        self.score = 0
        self.high_score = 0
        self.load_high_score()
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game to initial state"""
        self.grid = [[0] * self.GRID_SIZE for _ in range(self.GRID_SIZE)]
        self.score = 0
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self) -> bool:
        """Add a random tile (2 or 4) to an empty cell"""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return False

        # 90% chance for 2, 10% chance for 4
        value = 2 if random.random() < 0.9 else 4
        row, col = random.choice(empty_cells)
        self.grid[row][col] = value
        return True

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates"""
        empty_cells = []
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells

    def move(self, direction: str) -> bool:
        """Move tiles in the specified direction"""
        if direction not in ['up', 'down', 'left', 'right']:
            return False

        original_grid = [row[:] for row in self.grid]
        moved = False

        if direction == 'left':
            moved = self._move_left()
        elif direction == 'right':
            moved = self._move_right()
        elif direction == 'up':
            moved = self._move_up()
        elif direction == 'down':
            moved = self._move_down()

        # Update high score if current score is higher
        if self.score > self.high_score:
            self.high_score = self.score

        return moved

    def _move_left(self) -> bool:
        """Move tiles to the left"""
        moved = False
        for i in range(self.GRID_SIZE):
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
        for i in range(self.GRID_SIZE):
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
        for j in range(self.GRID_SIZE):
            # Extract column
            col = [self.grid[i][j] for i in range(self.GRID_SIZE)]

            # Move and merge
            new_col, col_score = self._merge_row(col)
            self.score += col_score

            # Update grid
            for i in range(self.GRID_SIZE):
                if new_col[i] != self.grid[i][j]:
                    moved = True
                self.grid[i][j] = new_col[i]

        return moved

    def _move_down(self) -> bool:
        """Move tiles down"""
        moved = False
        for j in range(self.GRID_SIZE):
            # Extract column and reverse for down movement
            col = [self.grid[i][j] for i in range(self.GRID_SIZE)][::-1]

            # Move and merge
            new_col, col_score = self._merge_row(col)
            self.score += col_score

            # Reverse back and update grid
            new_col = new_col[::-1]
            for i in range(self.GRID_SIZE):
                if new_col[i] != self.grid[i][j]:
                    moved = True
                self.grid[i][j] = new_col[i]

        return moved

    def _merge_row(self, row: List[int]) -> Tuple[List[int], int]:
        """Merge a row and return new row and score gained"""
        # Remove zeros and merge identical adjacent numbers
        non_zero = [x for x in row if x != 0]
        new_row = [0] * self.GRID_SIZE
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

    def is_game_over(self) -> bool:
        """Check if the game is over (no more moves possible)"""
        # Check for empty cells
        if self.get_empty_cells():
            return False

        # Check for possible merges
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE - 1):
                # Check horizontal merges
                if self.grid[i][j] == self.grid[i][j + 1]:
                    return False
                # Check vertical merges
                if self.grid[j][i] == self.grid[j + 1][i]:
                    return False

        return True

    def is_win(self) -> bool:
        """Check if player has won (reached 1024)"""
        for row in self.grid:
            if self.WIN_VALUE in row:
                return True
        return False

    def load_high_score(self) -> None:
        """Load high score from file"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            high_score_file = os.path.join(data_dir, 'high_score.txt')

            if os.path.exists(high_score_file):
                with open(high_score_file, 'r') as f:
                    self.high_score = int(f.read().strip())
        except (ValueError, IOError):
            self.high_score = 0

    def save_high_score(self) -> None:
        """Save high score to file"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            high_score_file = os.path.join(data_dir, 'high_score.txt')

            with open(high_score_file, 'w') as f:
                f.write(str(self.high_score))
        except IOError:
            pass  # Silently fail if can't save

    def get_grid(self) -> List[List[int]]:
        """Get current grid state"""
        return [row[:] for row in self.grid]

    def get_score(self) -> int:
        """Get current score"""
        return self.score

    def get_high_score(self) -> int:
        """Get high score"""
        return self.high_score
