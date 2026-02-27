from typing import List, Optional, Tuple, Set
import random
import copy

from .constants import LEVELS


class GameLogic:
    def __init__(self, grid_size: int = 4):
        self.grid_size = grid_size
        self.grid = self.create_grid()
        self.score = 0
        self.moves = 0
        self.max_tile = 0
        self.merge_history: List[int] = []
        self.last_merge_positions: Set[Tuple[int, int]] = set()
        self.game_over = False
        self.won = False
        self.add_random_tile()
        self.add_random_tile()
    
    def create_grid(self) -> List[List[int]]:
        return [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
    
    def reset(self):
        self.grid = self.create_grid()
        self.score = 0
        self.moves = 0
        self.max_tile = 0
        self.merge_history = []
        self.last_merge_positions = set()
        self.game_over = False
        self.won = False
        self.add_random_tile()
        self.add_random_tile()
    
    def set_grid_size(self, size: int):
        self.grid_size = size
        self.reset()
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        empty = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    empty.append((i, j))
        return empty
    
    def add_random_tile(self) -> Optional[Tuple[int, int, int]]:
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None
        
        row, col = random.choice(empty_cells)
        value = 2 if random.random() < 0.9 else 4
        self.grid[row][col] = value
        
        if value > self.max_tile:
            self.max_tile = value
        
        return (row, col, value)
    
    def compress(self, grid: List[List[int]]) -> Tuple[List[List[int]], bool]:
        changed = False
        new_grid = self.create_grid()
        
        for i in range(self.grid_size):
            pos = 0
            for j in range(self.grid_size):
                if grid[i][j] != 0:
                    new_grid[i][pos] = grid[i][j]
                    if j != pos:
                        changed = True
                    pos += 1
        
        return new_grid, changed
    
    def merge(self, grid: List[List[int]]) -> Tuple[List[List[int]], int, Set[Tuple[int, int]], bool]:
        score = 0
        merged_positions = set()
        changed = False
        new_grid = copy.deepcopy(grid)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size - 1):
                if new_grid[i][j] == new_grid[i][j + 1] and new_grid[i][j] != 0:
                    new_grid[i][j] *= 2
                    new_grid[i][j + 1] = 0
                    score += new_grid[i][j]
                    merged_positions.add((i, j))
                    changed = True
        
        return new_grid, score, merged_positions, changed
    
    def reverse(self, grid: List[List[int]]) -> List[List[int]]:
        new_grid = []
        for row in grid:
            new_grid.append(row[::-1])
        return new_grid
    
    def transpose(self, grid: List[List[int]]) -> List[List[int]]:
        new_grid = self.create_grid()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                new_grid[i][j] = grid[j][i]
        return new_grid
    
    def move_left(self) -> Tuple[bool, int, Set[Tuple[int, int]]]:
        grid = copy.deepcopy(self.grid)
        grid, _ = self.compress(grid)
        grid, score, merged, changed = self.merge(grid)
        grid, _ = self.compress(grid)
        
        if grid != self.grid:
            self.grid = grid
            self.score += score
            self.moves += 1
            if merged:
                self.merge_history.extend([grid[i][j] for i, j in merged])
            self.last_merge_positions = merged
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.grid[i][j] > self.max_tile:
                        self.max_tile = self.grid[i][j]
            return True, score, merged
        return False, 0, set()
    
    def move_right(self) -> Tuple[bool, int, Set[Tuple[int, int]]]:
        grid = self.reverse(copy.deepcopy(self.grid))
        grid, _ = self.compress(grid)
        grid, score, merged, changed = self.merge(grid)
        grid, _ = self.compress(grid)
        grid = self.reverse(grid)
        
        merged_fixed = set()
        for i, j in merged:
            merged_fixed.add((i, self.grid_size - 1 - j))
        
        if grid != self.grid:
            self.grid = grid
            self.score += score
            self.moves += 1
            if merged:
                self.merge_history.extend([grid[i][j] for i, j in merged_fixed])
            self.last_merge_positions = merged_fixed
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.grid[i][j] > self.max_tile:
                        self.max_tile = self.grid[i][j]
            return True, score, merged_fixed
        return False, 0, set()
    
    def move_up(self) -> Tuple[bool, int, Set[Tuple[int, int]]]:
        grid = self.transpose(copy.deepcopy(self.grid))
        grid, _ = self.compress(grid)
        grid, score, merged, changed = self.merge(grid)
        grid, _ = self.compress(grid)
        grid = self.transpose(grid)
        
        merged_fixed = set()
        for i, j in merged:
            merged_fixed.add((j, i))
        
        if grid != self.grid:
            self.grid = grid
            self.score += score
            self.moves += 1
            if merged:
                self.merge_history.extend([grid[i][j] for i, j in merged_fixed])
            self.last_merge_positions = merged_fixed
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.grid[i][j] > self.max_tile:
                        self.max_tile = self.grid[i][j]
            return True, score, merged_fixed
        return False, 0, set()
    
    def move_down(self) -> Tuple[bool, int, Set[Tuple[int, int]]]:
        grid = self.transpose(copy.deepcopy(self.grid))
        grid = self.reverse(grid)
        grid, _ = self.compress(grid)
        grid, score, merged, changed = self.merge(grid)
        grid, _ = self.compress(grid)
        grid = self.reverse(grid)
        grid = self.transpose(grid)
        
        merged_fixed = set()
        for i, j in merged:
            merged_fixed.add((self.grid_size - 1 - j, i))
        
        if grid != self.grid:
            self.grid = grid
            self.score += score
            self.moves += 1
            if merged:
                self.merge_history.extend([grid[i][j] for i, j in merged_fixed])
            self.last_merge_positions = merged_fixed
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.grid[i][j] > self.max_tile:
                        self.max_tile = self.grid[i][j]
            return True, score, merged_fixed
        return False, 0, set()
    
    def can_move(self) -> bool:
        if len(self.get_empty_cells()) > 0:
            return True
        
        for i in range(self.grid_size):
            for j in range(self.grid_size - 1):
                if self.grid[i][j] == self.grid[i][j + 1]:
                    return True
                if self.grid[j][i] == self.grid[j + 1][i]:
                    return True
        
        return False
    
    def has_won(self, target: int) -> bool:
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] >= target:
                    self.won = True
                    return True
        return False
    
    def is_game_over(self) -> bool:
        if not self.can_move():
            self.game_over = True
            return True
        return False
    
    def get_grid(self) -> List[List[int]]:
        return self.grid
    
    def get_score(self) -> int:
        return self.score
    
    def get_moves(self) -> int:
        return self.moves
    
    def get_max_tile(self) -> int:
        return self.max_tile
    
    def get_merge_history(self) -> List[int]:
        return self.merge_history
    
    def get_last_merge_positions(self) -> Set[Tuple[int, int]]:
        return self.last_merge_positions
    
    def __str__(self) -> str:
        result = ""
        for row in self.grid:
            result += str(row) + "\n"
        return result


class LevelSystem:
    def __init__(self):
        self.levels = LEVELS
    
    def get_level(self, level_num: int) -> Optional[dict]:
        for level in self.levels:
            if level['level'] == level_num:
                return level
        return None
    
    def get_total_levels(self) -> int:
        return len(self.levels)
    
    def get_target(self, level_num: int) -> int:
        level = self.get_level(level_num)
        return level['target'] if level else 2048
    
    def get_grid_size(self, level_num: int) -> int:
        level = self.get_level(level_num)
        return level['grid_size'] if level else 4
    
    def get_time_limit(self, level_num: int) -> int:
        level = self.get_level(level_num)
        return level['time_limit'] if level else 0
    
    def get_description(self, level_num: int) -> str:
        level = self.get_level(level_num)
        return level['description'] if level else f'Level {level_num}'
    
    def is_timed_level(self, level_num: int) -> bool:
        return self.get_time_limit(level_num) > 0
    
    def get_difficulty_tier(self, level_num: int) -> int:
        return ((level_num - 1) // 5) + 1
    
    def get_all_levels(self) -> List[dict]:
        return self.levels
