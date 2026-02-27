"""
1024 Game - Core Game Engine Module
Handles game logic, state management, and animations
"""

import random
import copy
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import config


class GameState(Enum):
    """Game state enumeration"""
    IDLE = auto()
    ANIMATING = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    PAUSED = auto()


@dataclass
class Tile:
    """Represents a single tile on the grid"""
    value: int
    row: int
    col: int
    is_obstacle: bool = False
    is_new: bool = False
    is_merging: bool = False
    merge_target: Optional[Tuple[int, int]] = None
    animation_progress: float = 0.0
    
    def __hash__(self):
        return hash((self.value, self.row, self.col, id(self)))


@dataclass
class MoveResult:
    """Result of a move operation"""
    moved: bool
    score_gained: int
    merges: List[Tuple[int, int, int]] = field(default_factory=list)  # (row, col, value)
    new_tiles: List[Tuple[int, int, int]] = field(default_factory=list)  # (row, col, value)


class GameEngine:
    """Core game engine with level support"""
    
    def __init__(self, level: int = 1):
        self.level = level
        self.grid_size = config.GRID_SIZE
        self.grid: List[List[Optional[Tile]]] = []
        self.score = 0
        self.moves = 0
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.state = GameState.IDLE
        self.difficulty = config.DIFFICULTY_SETTINGS.get(
            level, config.DIFFICULTY_SETTINGS[1]
        )
        self.target_value = self.difficulty["target"]
        self.obstacles: List[Tuple[int, int]] = []
        self.undo_stack: List[Dict] = []
        self.max_undos = 3
        self.undos_used = 0
        
        self._init_grid()
        self._place_obstacles()
        self._spawn_initial_tiles()
    
    def _init_grid(self) -> None:
        """Initialize empty grid"""
        self.grid = [
            [None for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]
    
    def _place_obstacles(self) -> None:
        """Place obstacles on the grid"""
        num_obstacles = self.difficulty.get("obstacles", 0)
        if num_obstacles == 0:
            return
        
        empty_cells = self._get_empty_cells()
        random.shuffle(empty_cells)
        
        for i in range(min(num_obstacles, len(empty_cells))):
            row, col = empty_cells[i]
            self.obstacles.append((row, col))
            self.grid[row][col] = Tile(
                value=-1,
                row=row,
                col=col,
                is_obstacle=True
            )
    
    def _spawn_initial_tiles(self) -> None:
        """Spawn initial tiles"""
        for _ in range(2):
            self._spawn_tile()
    
    def _spawn_tile(self) -> Optional[Tuple[int, int, int]]:
        """Spawn a new tile at random empty position"""
        empty_cells = self._get_empty_cells()
        if not empty_cells:
            return None
        
        row, col = random.choice(empty_cells)
        spawn_values = self.difficulty.get("spawn_values", [2])
        
        # Weighted random selection
        if len(spawn_values) == 1:
            value = spawn_values[0]
        else:
            # Higher values less likely
            weights = [1 / (i + 1) for i in range(len(spawn_values))]
            total = sum(weights)
            weights = [w / total for w in weights]
            value = random.choices(spawn_values, weights=weights)[0]
        
        self.grid[row][col] = Tile(
            value=value,
            row=row,
            col=col,
            is_new=True
        )
        
        return (row, col, value)
    
    def _get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates"""
        empty = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] is None:
                    empty.append((row, col))
        return empty
    
    def save_state(self) -> None:
        """Save current state for undo"""
        if len(self.undo_stack) >= self.max_undos:
            self.undo_stack.pop(0)
        
        state = {
            "grid": copy.deepcopy(self.grid),
            "score": self.score,
            "moves": self.moves,
        }
        self.undo_stack.append(state)
    
    def undo(self) -> bool:
        """Undo last move"""
        if not self.undo_stack or self.undos_used >= self.max_undos:
            return False
        
        state = self.undo_stack.pop()
        self.grid = state["grid"]
        self.score = state["score"]
        self.moves = state["moves"]
        self.undos_used += 1
        return True
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0 and self.undos_used < self.max_undos
    
    def move(self, direction: str) -> MoveResult:
        """Execute move in specified direction"""
        if self.state in [GameState.GAME_OVER, GameState.LEVEL_COMPLETE]:
            return MoveResult(False, 0)
        
        # Save state before move
        self.save_state()
        
        result = MoveResult(False, 0)
        
        if direction == "left":
            result = self._move_left()
        elif direction == "right":
            result = self._move_right()
        elif direction == "up":
            result = self._move_up()
        elif direction == "down":
            result = self._move_down()
        
        if result.moved:
            self.moves += 1
            self.score += result.score_gained
            
            # Spawn new tiles
            spawn_count = self.difficulty.get("spawn_count", 1)
            for _ in range(spawn_count):
                new_tile = self._spawn_tile()
                if new_tile:
                    result.new_tiles.append(new_tile)
            
            # Check win condition
            if self._check_win():
                self.state = GameState.LEVEL_COMPLETE
            elif self._check_game_over():
                self.state = GameState.GAME_OVER
        else:
            # No move made, don't count undo
            if self.undo_stack:
                self.undo_stack.pop()
        
        return result
    
    def _move_left(self) -> MoveResult:
        """Move tiles left"""
        result = MoveResult(False, 0)
        
        for row in range(self.grid_size):
            # Extract non-obstacle tiles
            tiles = []
            for col in range(self.grid_size):
                tile = self.grid[row][col]
                if tile and not tile.is_obstacle:
                    tiles.append(tile)
            
            # Merge tiles
            merged_row, score, merges = self._merge_tiles(tiles)
            result.score_gained += score
            result.merges.extend(merges)
            
            # Place tiles back
            new_row = [None] * self.grid_size
            for i, tile in enumerate(merged_row):
                if tile:
                    if tile.col != i:
                        result.moved = True
                    tile.col = i
                    tile.row = row
                    new_row[i] = tile
            
            # Check if anything moved
            for col in range(self.grid_size):
                if self.grid[row][col] != new_row[col]:
                    if not (self.grid[row][col] and self.grid[row][col].is_obstacle):
                        result.moved = True
            
            # Place obstacles back
            for col in range(self.grid_size):
                if self.grid[row][col] and self.grid[row][col].is_obstacle:
                    new_row[col] = self.grid[row][col]
            
            self.grid[row] = new_row
        
        return result
    
    def _move_right(self) -> MoveResult:
        """Move tiles right"""
        result = MoveResult(False, 0)
        
        for row in range(self.grid_size):
            tiles = []
            for col in range(self.grid_size - 1, -1, -1):
                tile = self.grid[row][col]
                if tile and not tile.is_obstacle:
                    tiles.append(tile)
            
            merged_row, score, merges = self._merge_tiles(tiles)
            result.score_gained += score
            result.merges.extend(merges)
            
            new_row = [None] * self.grid_size
            for i, tile in enumerate(merged_row):
                if tile:
                    col = self.grid_size - 1 - i
                    if tile.col != col:
                        result.moved = True
                    tile.col = col
                    tile.row = row
                    new_row[col] = tile
            
            for col in range(self.grid_size):
                if self.grid[row][col] != new_row[col]:
                    if not (self.grid[row][col] and self.grid[row][col].is_obstacle):
                        result.moved = True
            
            for col in range(self.grid_size):
                if self.grid[row][col] and self.grid[row][col].is_obstacle:
                    new_row[col] = self.grid[row][col]
            
            self.grid[row] = new_row
        
        return result
    
    def _move_up(self) -> MoveResult:
        """Move tiles up"""
        result = MoveResult(False, 0)
        
        for col in range(self.grid_size):
            tiles = []
            for row in range(self.grid_size):
                tile = self.grid[row][col]
                if tile and not tile.is_obstacle:
                    tiles.append(tile)
            
            merged_col, score, merges = self._merge_tiles(tiles)
            result.score_gained += score
            result.merges.extend(merges)
            
            new_col = [None] * self.grid_size
            for i, tile in enumerate(merged_col):
                if tile:
                    if tile.row != i:
                        result.moved = True
                    tile.row = i
                    tile.col = col
                    new_col[i] = tile
            
            for row in range(self.grid_size):
                if self.grid[row][col] != new_col[row]:
                    if not (self.grid[row][col] and self.grid[row][col].is_obstacle):
                        result.moved = True
            
            for row in range(self.grid_size):
                if self.grid[row][col] and self.grid[row][col].is_obstacle:
                    new_col[row] = self.grid[row][col]
            
            for row in range(self.grid_size):
                self.grid[row][col] = new_col[row]
        
        return result
    
    def _move_down(self) -> MoveResult:
        """Move tiles down"""
        result = MoveResult(False, 0)
        
        for col in range(self.grid_size):
            tiles = []
            for row in range(self.grid_size - 1, -1, -1):
                tile = self.grid[row][col]
                if tile and not tile.is_obstacle:
                    tiles.append(tile)
            
            merged_col, score, merges = self._merge_tiles(tiles)
            result.score_gained += score
            result.merges.extend(merges)
            
            new_col = [None] * self.grid_size
            for i, tile in enumerate(merged_col):
                if tile:
                    row = self.grid_size - 1 - i
                    if tile.row != row:
                        result.moved = True
                    tile.row = row
                    tile.col = col
                    new_col[row] = tile
            
            for row in range(self.grid_size):
                if self.grid[row][col] != new_col[row]:
                    if not (self.grid[row][col] and self.grid[row][col].is_obstacle):
                        result.moved = True
            
            for row in range(self.grid_size):
                if self.grid[row][col] and self.grid[row][col].is_obstacle:
                    new_col[row] = self.grid[row][col]
            
            for row in range(self.grid_size):
                self.grid[row][col] = new_col[row]
        
        return result
    
    def _merge_tiles(
        self,
        tiles: List[Tile]
    ) -> Tuple[List[Tile], int, List[Tuple[int, int, int]]]:
        """Merge adjacent tiles with same value"""
        if not tiles:
            return [], 0, []
        
        merged = []
        score = 0
        merges = []
        i = 0
        
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i].value == tiles[i + 1].value:
                # Merge tiles
                new_value = tiles[i].value * 2
                merged_tile = Tile(
                    value=new_value,
                    row=tiles[i].row,
                    col=tiles[i].col,
                    is_merging=True
                )
                merged.append(merged_tile)
                score += new_value
                merges.append((merged_tile.row, merged_tile.col, new_value))
                i += 2
            else:
                tiles[i].is_merging = False
                merged.append(tiles[i])
                i += 1
        
        return merged, score, merges
    
    def _check_win(self) -> bool:
        """Check if target value is reached"""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                tile = self.grid[row][col]
                if tile and not tile.is_obstacle and tile.value >= self.target_value:
                    return True
        return False
    
    def _check_game_over(self) -> bool:
        """Check if no moves are possible"""
        # Check for empty cells
        if self._get_empty_cells():
            return False
        
        # Check for possible merges
        for row in range(self.grid_size):
            for col in range(self.grid_size - 1):
                tile1 = self.grid[row][col]
                tile2 = self.grid[row][col + 1]
                if (tile1 and tile2 and 
                    not tile1.is_obstacle and not tile2.is_obstacle and
                    tile1.value == tile2.value):
                    return False
        
        for col in range(self.grid_size):
            for row in range(self.grid_size - 1):
                tile1 = self.grid[row][col]
                tile2 = self.grid[row + 1][col]
                if (tile1 and tile2 and 
                    not tile1.is_obstacle and not tile2.is_obstacle and
                    tile1.value == tile2.value):
                    return False
        
        return True
    
    def get_grid_values(self) -> List[List[int]]:
        """Get grid as 2D list of values (0 for empty, -1 for obstacle)"""
        result = []
        for row in range(self.grid_size):
            row_values = []
            for col in range(self.grid_size):
                tile = self.grid[row][col]
                if tile is None:
                    row_values.append(0)
                elif tile.is_obstacle:
                    row_values.append(-1)
                else:
                    row_values.append(tile.value)
            result.append(row_values)
        return result
    
    def get_tile(self, row: int, col: int) -> Optional[Tile]:
        """Get tile at position"""
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return self.grid[row][col]
        return None
    
    def reset(self) -> None:
        """Reset game to initial state"""
        self.score = 0
        self.moves = 0
        self.elapsed_time = 0.0
        self.undos_used = 0
        self.undo_stack.clear()
        self.state = GameState.IDLE
        self._init_grid()
        self._place_obstacles()
        self._spawn_initial_tiles()
    
    def get_stars(self) -> int:
        """Calculate stars earned for this level"""
        if self.state != GameState.LEVEL_COMPLETE:
            return 0
        
        stars = 1  # Base star for completion
        
        # Bonus star for high score
        if self.score >= self.target_value * 2:
            stars += 1
        
        # Bonus star for efficiency (no undos used)
        if self.undos_used == 0:
            stars += 1
        
        return min(stars, 3)
