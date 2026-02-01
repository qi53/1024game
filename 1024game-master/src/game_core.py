#!/usr/bin/env python3
"""
1024 Game - Core Game Logic
Extended game logic with level system and animations
"""

import random
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

from .config import LEVEL_CONFIGS, TOTAL_LEVELS


class MoveResult(Enum):
    SUCCESS = 1
    NO_MOVE = 2
    WIN = 3
    GAME_OVER = 4


@dataclass
class TileAnimation:
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    value: int
    progress: float
    is_new: bool = False
    is_merged: bool = False


class GameCore:
    """Extended game core with level support"""
    
    def __init__(self, grid_size: int = 4):
        self.grid_size = grid_size
        self.grid = [[0] * grid_size for _ in range(grid_size)]
        self.score = 0
        self.moves = 0
        self.level = 1
        self.target_value = 32
        self.time_limit = 180
        self.time_remaining = 180
        self.animations: List[TileAnimation] = []
        self.merged_positions: List[Tuple[int, int]] = []
        self.new_positions: List[Tuple[int, int]] = []
        self.combo_count = 0
        self.last_merge_count = 0
    
    def reset(self, level: int = 1):
        """Reset game for a new level"""
        if 1 <= level <= TOTAL_LEVELS:
            config = LEVEL_CONFIGS[level]
            self.grid_size = config["grid_size"]
            self.target_value = config["target"]
            self.time_limit = config["time_limit"]
            self.time_remaining = config["time_limit"]
        else:
            self.grid_size = 4
            self.target_value = 1024
            self.time_limit = 180
            self.time_remaining = 180
        
        self.level = level
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.moves = 0
        self.animations = []
        self.merged_positions = []
        self.new_positions = []
        self.combo_count = 0
        self.last_merge_count = 0
        
        self.add_random_tile()
        self.add_random_tile()
    
    def add_random_tile(self) -> bool:
        """Add a random tile to an empty cell"""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return False
        
        value = 2 if random.random() < 0.9 else 4
        row, col = random.choice(empty_cells)
        self.grid[row][col] = value
        self.new_positions.append((row, col))
        
        return True
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates"""
        return [(i, j) for i in range(self.grid_size) 
                for j in range(self.grid_size) if self.grid[i][j] == 0]
    
    def move(self, direction: str) -> MoveResult:
        """Execute a move in the given direction"""
        self.animations = []
        self.merged_positions = []
        self.new_positions = []
        self.last_merge_count = 0
        
        original_grid = [row[:] for row in self.grid]
        
        if direction == 'left':
            moved, merge_count = self._move_left()
        elif direction == 'right':
            moved, merge_count = self._move_right()
        elif direction == 'up':
            moved, merge_count = self._move_up()
        elif direction == 'down':
            moved, merge_count = self._move_down()
        else:
            return MoveResult.NO_MOVE
        
        if not moved:
            if self._check_game_over():
                return MoveResult.GAME_OVER
            return MoveResult.NO_MOVE
        
        self.moves += 1
        self.last_merge_count = merge_count
        
        if self.add_random_tile():
            pass
        
        if self._check_win():
            return MoveResult.WIN
        
        if self._check_game_over():
            return MoveResult.GAME_OVER
        
        return MoveResult.SUCCESS
    
    def _move_left(self) -> Tuple[bool, int]:
        """Move tiles left"""
        moved = False
        total_merges = 0
        
        for i in range(self.grid_size):
            row = self.grid[i][:]
            new_row, row_score, merges, animations = self._merge_row(row, i, 'left')
            self.score += row_score
            total_merges += merges
            
            if new_row != self.grid[i]:
                moved = True
            self.grid[i] = new_row
            self.animations.extend(animations)
        
        return moved, total_merges
    
    def _move_right(self) -> Tuple[bool, int]:
        """Move tiles right"""
        moved = False
        total_merges = 0
        
        for i in range(self.grid_size):
            row = self.grid[i][::-1]
            new_row, row_score, merges, animations = self._merge_row(row, i, 'right')
            self.score += row_score
            total_merges += merges
            new_row = new_row[::-1]
            
            if new_row != self.grid[i]:
                moved = True
            self.grid[i] = new_row
            self.animations.extend(animations)
        
        return moved, total_merges
    
    def _move_up(self) -> Tuple[bool, int]:
        """Move tiles up"""
        moved = False
        total_merges = 0
        
        for j in range(self.grid_size):
            col = [self.grid[i][j] for i in range(self.grid_size)]
            new_col, col_score, merges, animations = self._merge_column(col, j, 'up')
            self.score += col_score
            total_merges += merges
            
            for i in range(self.grid_size):
                if new_col[i] != self.grid[i][j]:
                    moved = True
                self.grid[i][j] = new_col[i]
            
            self.animations.extend(animations)
        
        return moved, total_merges
    
    def _move_down(self) -> Tuple[bool, int]:
        """Move tiles down"""
        moved = False
        total_merges = 0
        
        for j in range(self.grid_size):
            col = [self.grid[i][j] for i in range(self.grid_size)][::-1]
            new_col, col_score, merges, animations = self._merge_column(col, j, 'down')
            self.score += col_score
            total_merges += merges
            new_col = new_col[::-1]
            
            for i in range(self.grid_size):
                if new_col[i] != self.grid[i][j]:
                    moved = True
                self.grid[i][j] = new_col[i]
            
            self.animations.extend(animations)
        
        return moved, total_merges
    
    def _merge_row(self, row: List[int], row_idx: int, direction: str) -> Tuple[List[int], int, int, List[TileAnimation]]:
        """Merge a row and return animations"""
        non_zero = [x for x in row if x != 0]
        new_row = [0] * self.grid_size
        score_gained = 0
        merges = 0
        animations = []
        
        i = 0
        output_idx = 0
        
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                new_row[output_idx] = merged_value
                score_gained += merged_value
                merges += 1
                self.merged_positions.append((row_idx, output_idx))
                
                start_col = row.index(non_zero[i]) if direction == 'left' else (self.grid_size - 1 - row[::-1].index(non_zero[i]))
                
                animations.append(TileAnimation(
                    start_x=start_col, start_y=row_idx,
                    end_x=output_idx, end_y=row_idx,
                    value=merged_value, progress=0, is_merged=True
                ))
                i += 2
            else:
                new_row[output_idx] = non_zero[i]
                i += 1
            
            output_idx += 1
        
        return new_row, score_gained, merges, animations
    
    def _merge_column(self, col: List[int], col_idx: int, direction: str) -> Tuple[List[int], int, int, List[TileAnimation]]:
        """Merge a column and return animations"""
        non_zero = [x for x in col if x != 0]
        new_col = [0] * self.grid_size
        score_gained = 0
        merges = 0
        animations = []
        
        i = 0
        output_idx = 0
        
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                new_col[output_idx] = merged_value
                score_gained += merged_value
                merges += 1
                self.merged_positions.append((output_idx, col_idx))
                
                animations.append(TileAnimation(
                    start_x=col_idx, start_y=i,
                    end_x=col_idx, end_y=output_idx,
                    value=merged_value, progress=0, is_merged=True
                ))
                i += 2
            else:
                new_col[output_idx] = non_zero[i]
                i += 1
            
            output_idx += 1
        
        return new_col, score_gained, merges, animations
    
    def _check_win(self) -> bool:
        """Check if player has reached the target"""
        for row in self.grid:
            if self.target_value in row:
                return True
        return False
    
    def _check_game_over(self) -> bool:
        """Check if no more moves are possible"""
        if self.get_empty_cells():
            return False
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                current = self.grid[i][j]
                
                if j < self.grid_size - 1 and current == self.grid[i][j + 1]:
                    return False
                if i < self.grid_size - 1 and current == self.grid[i + 1][j]:
                    return False
        
        return True
    
    def get_grid(self) -> List[List[int]]:
        """Get current grid state"""
        return [row[:] for row in self.grid]
    
    def get_score(self) -> int:
        """Get current score"""
        return self.score
    
    def get_moves(self) -> int:
        """Get number of moves"""
        return self.moves
    
    def get_target(self) -> int:
        """Get target value"""
        return self.target_value
    
    def get_time_remaining(self) -> float:
        """Get remaining time"""
        return self.time_remaining
    
    def update_time(self, delta_time: float):
        """Update game timer"""
        self.time_remaining -= delta_time
        if self.time_remaining < 0:
            self.time_remaining = 0
    
    def is_time_up(self) -> bool:
        """Check if time is up"""
        return self.time_remaining <= 0
    
    def get_grid_size(self) -> int:
        """Get current grid size"""
        return self.grid_size
    
    def get_max_tile(self) -> int:
        """Get the maximum tile value on grid"""
        return max(max(row) for row in self.grid)
    
    def get_animations(self) -> List[TileAnimation]:
        """Get current animations"""
        return self.animations
    
    def get_merged_positions(self) -> List[Tuple[int, int]]:
        """Get positions of merged tiles"""
        return self.merged_positions
    
    def get_new_positions(self) -> List[Tuple[int, int]]:
        """Get positions of new tiles"""
        return self.new_positions
    
    def get_merge_count(self) -> int:
        """Get number of merges in last move"""
        return self.last_merge_count
    
    def can_move(self) -> bool:
        """Check if any moves are possible"""
        return not self._check_game_over()
    
    def get_hint(self) -> Optional[str]:
        """Get a suggested move"""
        test_grid = [row[:] for row in self.grid]
        
        for direction in ['up', 'down', 'left', 'right']:
            if direction == 'left':
                moved, _ = self._test_move_left(test_grid)
            elif direction == 'right':
                moved, _ = self._test_move_right(test_grid)
            elif direction == 'up':
                moved, _ = self._test_move_up(test_grid)
            else:
                moved, _ = self._test_move_down(test_grid)
            
            if moved:
                return direction
        
        return None
    
    def _test_move_left(self, test_grid: List[List[int]]) -> Tuple[bool, List[List[int]]]:
        """Test if left move changes grid"""
        new_grid = [row[:] for row in test_grid]
        moved = False
        
        for i in range(self.grid_size):
            row = new_grid[i][:]
            non_zero = [x for x in row if x != 0]
            result = [0] * self.grid_size
            
            idx = 0
            j = 0
            while j < len(non_zero):
                if j + 1 < len(non_zero) and non_zero[j] == non_zero[j + 1]:
                    result[idx] = non_zero[j] * 2
                    j += 2
                else:
                    result[idx] = non_zero[j]
                    j += 1
                idx += 1
            
            if result != new_grid[i]:
                moved = True
            new_grid[i] = result
        
        return moved, new_grid
    
    def _test_move_right(self, test_grid: List[List[int]]) -> Tuple[bool, List[List[int]]]:
        """Test if right move changes grid"""
        new_grid = [row[:] for row in test_grid]
        moved = False
        
        for i in range(self.grid_size):
            row = new_grid[i][::-1]
            non_zero = [x for x in row if x != 0]
            result = [0] * self.grid_size
            
            idx = 0
            j = 0
            while j < len(non_zero):
                if j + 1 < len(non_zero) and non_zero[j] == non_zero[j + 1]:
                    result[idx] = non_zero[j] * 2
                    j += 2
                else:
                    result[idx] = non_zero[j]
                    j += 1
                idx += 1
            
            result = result[::-1]
            if result != new_grid[i]:
                moved = True
            new_grid[i] = result
        
        return moved, new_grid
    
    def _test_move_up(self, test_grid: List[List[int]]) -> Tuple[bool, List[List[int]]]:
        """Test if up move changes grid"""
        new_grid = [row[:] for row in test_grid]
        moved = False
        
        for j in range(self.grid_size):
            col = [new_grid[i][j] for i in range(self.grid_size)]
            non_zero = [x for x in col if x != 0]
            result = [0] * self.grid_size
            
            idx = 0
            k = 0
            while k < len(non_zero):
                if k + 1 < len(non_zero) and non_zero[k] == non_zero[k + 1]:
                    result[idx] = non_zero[k] * 2
                    k += 2
                else:
                    result[idx] = non_zero[k]
                    k += 1
                idx += 1
            
            for i in range(self.grid_size):
                if result[i] != new_grid[i][j]:
                    moved = True
                new_grid[i][j] = result[i]
        
        return moved, new_grid
    
    def _test_move_down(self, test_grid: List[List[int]]) -> Tuple[bool, List[List[int]]]:
        """Test if down move changes grid"""
        new_grid = [row[:] for row in test_grid]
        moved = False
        
        for j in range(self.grid_size):
            col = [new_grid[i][j] for i in range(self.grid_size)][::-1]
            non_zero = [x for x in col if x != 0]
            result = [0] * self.grid_size
            
            idx = 0
            k = 0
            while k < len(non_zero):
                if k + 1 < len(non_zero) and non_zero[k] == non_zero[k + 1]:
                    result[idx] = non_zero[k] * 2
                    k += 2
                else:
                    result[idx] = non_zero[k]
                    k += 1
                idx += 1
            
            result = result[::-1]
            for i in range(self.grid_size):
                if result[i] != new_grid[i][j]:
                    moved = True
                new_grid[i][j] = result[i]
        
        return moved, new_grid
