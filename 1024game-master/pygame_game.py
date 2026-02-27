#!/usr/bin/env python3
"""
1024 Game - Pygame Core Game Logic
Contains the Game class with 20 levels and progressive difficulty
"""

import random
import copy
from typing import List, Tuple, Optional, Dict, Any


class LevelConfig:
    """Configuration for each level"""
    
    LEVELS = [
        {"id": 1, "grid_size": 3, "target": 128, "moves": 100, "initial_tiles": 2, "spawn_4_chance": 0.05, "name": "入门"},
        {"id": 2, "grid_size": 3, "target": 256, "moves": 90, "initial_tiles": 2, "spawn_4_chance": 0.08, "name": "初学"},
        {"id": 3, "grid_size": 3, "target": 512, "moves": 80, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "入门进阶"},
        {"id": 4, "grid_size": 3, "target": 1024, "moves": 70, "initial_tiles": 2, "spawn_4_chance": 0.12, "name": "小试牛刀"},
        {"id": 5, "grid_size": 4, "target": 512, "moves": 100, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "标准开始"},
        {"id": 6, "grid_size": 4, "target": 1024, "moves": 120, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "经典挑战"},
        {"id": 7, "grid_size": 4, "target": 1024, "moves": 100, "initial_tiles": 2, "spawn_4_chance": 0.12, "name": "速度考验"},
        {"id": 8, "grid_size": 4, "target": 1024, "moves": 80, "initial_tiles": 3, "spawn_4_chance": 0.12, "name": "压力测试"},
        {"id": 9, "grid_size": 4, "target": 2048, "moves": 150, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "翻倍挑战"},
        {"id": 10, "grid_size": 4, "target": 2048, "moves": 120, "initial_tiles": 3, "spawn_4_chance": 0.12, "name": "中级巅峰"},
        {"id": 11, "grid_size": 5, "target": 1024, "moves": 100, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "大棋盘"},
        {"id": 12, "grid_size": 5, "target": 2048, "moves": 150, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "扩展挑战"},
        {"id": 13, "grid_size": 5, "target": 2048, "moves": 120, "initial_tiles": 3, "spawn_4_chance": 0.12, "name": "高级玩家"},
        {"id": 14, "grid_size": 5, "target": 4096, "moves": 180, "initial_tiles": 2, "spawn_4_chance": 0.10, "name": "专家之路"},
        {"id": 15, "grid_size": 5, "target": 4096, "moves": 150, "initial_tiles": 3, "spawn_4_chance": 0.15, "name": "大师考验"},
        {"id": 16, "grid_size": 6, "target": 2048, "moves": 150, "initial_tiles": 3, "spawn_4_chance": 0.10, "name": "超大棋盘"},
        {"id": 17, "grid_size": 6, "target": 4096, "moves": 200, "initial_tiles": 3, "spawn_4_chance": 0.12, "name": "终极挑战"},
        {"id": 18, "grid_size": 6, "target": 4096, "moves": 150, "initial_tiles": 4, "spawn_4_chance": 0.15, "name": "极限模式"},
        {"id": 19, "grid_size": 6, "target": 8192, "moves": 250, "initial_tiles": 3, "spawn_4_chance": 0.12, "name": "传奇之路"},
        {"id": 20, "grid_size": 6, "target": 8192, "moves": 200, "initial_tiles": 4, "spawn_4_chance": 0.15, "name": "终极大师"},
    ]
    
    @classmethod
    def get_level(cls, level_id: int) -> Dict[str, Any]:
        if 1 <= level_id <= 20:
            return cls.LEVELS[level_id - 1].copy()
        return cls.LEVELS[0].copy()
    
    @classmethod
    def get_difficulty_tier(cls, level_id: int) -> int:
        if level_id <= 5:
            return 1
        elif level_id <= 10:
            return 2
        elif level_id <= 15:
            return 3
        else:
            return 4


class GameStats:
    """Game statistics tracking"""
    
    def __init__(self):
        self.total_moves = 0
        self.total_merges = 0
        self.max_tile = 0
        self.tiles_merged_by_value: Dict[int, int] = {}
        self.moves_by_direction: Dict[str, int] = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.time_elapsed = 0.0
        self.combo_count = 0
        self.max_combo = 0
        self.score_history: List[int] = []
    
    def reset(self):
        self.total_moves = 0
        self.total_merges = 0
        self.max_tile = 0
        self.tiles_merged_by_value = {}
        self.moves_by_direction = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.time_elapsed = 0.0
        self.combo_count = 0
        self.max_combo = 0
        self.score_history = []
    
    def record_move(self, direction: str, merges: int, score_gained: int):
        self.total_moves += 1
        self.moves_by_direction[direction] = self.moves_by_direction.get(direction, 0) + 1
        if merges > 0:
            self.total_merges += merges
            self.combo_count += 1
            self.max_combo = max(self.max_combo, self.combo_count)
        else:
            self.combo_count = 0
        self.score_history.append(score_gained)
    
    def record_merge(self, value: int):
        self.tiles_merged_by_value[value] = self.tiles_merged_by_value.get(value, 0) + 1
        self.max_tile = max(self.max_tile, value)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_moves": self.total_moves,
            "total_merges": self.total_merges,
            "max_tile": self.max_tile,
            "tiles_merged_by_value": self.tiles_merged_by_value.copy(),
            "moves_by_direction": self.moves_by_direction.copy(),
            "time_elapsed": self.time_elapsed,
            "max_combo": self.max_combo,
            "score_history": self.score_history.copy()
        }


class Game:
    """Main game class with 20 levels and progressive difficulty"""
    
    def __init__(self, level_id: int = 1):
        self.level_id = level_id
        self.level_config = LevelConfig.get_level(level_id)
        self.grid_size = self.level_config["grid_size"]
        self.target = self.level_config["target"]
        self.max_moves = self.level_config["moves"]
        self.moves_remaining = self.max_moves
        self.spawn_4_chance = self.level_config["spawn_4_chance"]
        
        self.grid: List[List[int]] = []
        self.score = 0
        self.stats = GameStats()
        self.is_won = False
        self.is_over = False
        self.last_move_success = False
        self.last_merge_positions: List[Tuple[int, int, int]] = []
        self.new_tile_position: Optional[Tuple[int, int]] = None
        
        self.reset_game()
    
    def reset_game(self) -> None:
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.moves_remaining = self.max_moves
        self.is_won = False
        self.is_over = False
        self.last_move_success = False
        self.last_merge_positions = []
        self.new_tile_position = None
        self.stats.reset()
        
        for _ in range(self.level_config["initial_tiles"]):
            self.add_random_tile()
    
    def set_level(self, level_id: int) -> None:
        self.level_id = max(1, min(20, level_id))
        self.level_config = LevelConfig.get_level(self.level_id)
        self.grid_size = self.level_config["grid_size"]
        self.target = self.level_config["target"]
        self.max_moves = self.level_config["moves"]
        self.spawn_4_chance = self.level_config["spawn_4_chance"]
        self.reset_game()
    
    def add_random_tile(self) -> bool:
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return False
        
        value = 4 if random.random() < self.spawn_4_chance else 2
        row, col = random.choice(empty_cells)
        self.grid[row][col] = value
        self.new_tile_position = (row, col)
        return True
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells
    
    def move(self, direction: str) -> Tuple[bool, int, List[Tuple[int, int, int]]]:
        if direction not in ['up', 'down', 'left', 'right'] or self.is_over:
            return False, 0, []
        
        original_grid = copy.deepcopy(self.grid)
        self.last_merge_positions = []
        total_score = 0
        
        if direction == 'left':
            total_score = self._move_left()
        elif direction == 'right':
            total_score = self._move_right()
        elif direction == 'up':
            total_score = self._move_up()
        elif direction == 'down':
            total_score = self._move_down()
        
        moved = self.grid != original_grid
        self.last_move_success = moved
        
        if moved:
            self.moves_remaining -= 1
            merges = len(self.last_merge_positions)
            self.stats.record_move(direction, merges, total_score)
            
            for _, _, value in self.last_merge_positions:
                self.stats.record_merge(value)
            
            self.add_random_tile()
            
            if self.check_win():
                self.is_won = True
                self.is_over = True
            elif self.check_game_over():
                self.is_over = True
        
        return moved, total_score, self.last_merge_positions.copy()
    
    def _move_left(self) -> int:
        total_score = 0
        for i in range(self.grid_size):
            row = self.grid[i][:]
            new_row, score, merges = self._merge_row_with_positions(row, i, 'row')
            self.grid[i] = new_row
            total_score += score
            self.last_merge_positions.extend(merges)
        return total_score
    
    def _move_right(self) -> int:
        total_score = 0
        for i in range(self.grid_size):
            row = self.grid[i][::-1]
            new_row, score, merges = self._merge_row_with_positions(row, i, 'row_rev')
            new_row = new_row[::-1]
            self.grid[i] = new_row
            total_score += score
            adjusted_merges = [(m[0], self.grid_size - 1 - m[1], m[2]) for m in merges]
            self.last_merge_positions.extend(adjusted_merges)
        return total_score
    
    def _move_up(self) -> int:
        total_score = 0
        for j in range(self.grid_size):
            col = [self.grid[i][j] for i in range(self.grid_size)]
            new_col, score, merges = self._merge_row_with_positions(col, j, 'col')
            for i in range(self.grid_size):
                self.grid[i][j] = new_col[i]
            total_score += score
            adjusted_merges = [(m[1], m[0], m[2]) for m in merges]
            self.last_merge_positions.extend(adjusted_merges)
        return total_score
    
    def _move_down(self) -> int:
        total_score = 0
        for j in range(self.grid_size):
            col = [self.grid[i][j] for i in range(self.grid_size)][::-1]
            new_col, score, merges = self._merge_row_with_positions(col, j, 'col_rev')
            new_col = new_col[::-1]
            for i in range(self.grid_size):
                self.grid[i][j] = new_col[i]
            total_score += score
            adjusted_merges = [(self.grid_size - 1 - m[1], m[0], m[2]) for m in merges]
            self.last_merge_positions.extend(adjusted_merges)
        return total_score
    
    def _merge_row_with_positions(self, row: List[int], index: int, mode: str) -> Tuple[List[int], int, List[Tuple[int, int, int]]]:
        non_zero = [(i, v) for i, v in enumerate(row) if v != 0]
        new_row = [0] * self.grid_size
        score = 0
        merges = []
        
        write_pos = 0
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i][1] == non_zero[i + 1][1]:
                merged_value = non_zero[i][1] * 2
                new_row[write_pos] = merged_value
                score += merged_value
                
                if mode == 'row':
                    merges.append((index, write_pos, merged_value))
                elif mode == 'row_rev':
                    merges.append((index, self.grid_size - 1 - write_pos, merged_value))
                elif mode == 'col':
                    merges.append((write_pos, index, merged_value))
                elif mode == 'col_rev':
                    merges.append((self.grid_size - 1 - write_pos, index, merged_value))
                
                i += 2
            else:
                new_row[write_pos] = non_zero[i][1]
                i += 1
            write_pos += 1
        
        self.score += score
        return new_row, score, merges
    
    def check_win(self) -> bool:
        for row in self.grid:
            if self.target in row:
                return True
        return False
    
    def check_game_over(self) -> bool:
        if self.get_empty_cells():
            return False
        
        for i in range(self.grid_size):
            for j in range(self.grid_size - 1):
                if self.grid[i][j] == self.grid[i][j + 1]:
                    return False
                if self.grid[j][i] == self.grid[j + 1][i]:
                    return False
        
        if self.moves_remaining <= 0:
            return True
        
        return True
    
    def get_grid(self) -> List[List[int]]:
        return copy.deepcopy(self.grid)
    
    def get_score(self) -> int:
        return self.score
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats.to_dict()
    
    def get_progress(self) -> float:
        max_tile = max(max(row) for row in self.grid)
        if max_tile >= self.target:
            return 1.0
        return max_tile / self.target
    
    def get_level_info(self) -> Dict[str, Any]:
        return {
            "id": self.level_id,
            "name": self.level_config["name"],
            "grid_size": self.grid_size,
            "target": self.target,
            "moves_remaining": self.moves_remaining,
            "max_moves": self.max_moves,
            "difficulty_tier": LevelConfig.get_difficulty_tier(self.level_id),
            "progress": self.get_progress()
        }
