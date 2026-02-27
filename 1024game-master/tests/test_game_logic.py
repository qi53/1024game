import pytest

from src.game_logic import GameLogic, LevelSystem


class TestGameLogic:
    def test_initialization(self):
        game = GameLogic(4)
        assert game.grid_size == 4
        assert len(game.grid) == 4
        assert len(game.grid[0]) == 4
        
        non_zero = sum(1 for row in game.grid for val in row if val != 0)
        assert non_zero == 2
    
    def test_different_grid_sizes(self):
        game3 = GameLogic(3)
        assert game3.grid_size == 3
        assert len(game3.grid) == 3
        
        game6 = GameLogic(6)
        assert game6.grid_size == 6
        assert len(game6.grid) == 6
    
    def test_reset(self):
        game = GameLogic(4)
        game.score = 1000
        game.moves = 50
        game.reset()
        
        assert game.score == 0
        assert game.moves == 0
        non_zero = sum(1 for row in game.grid for val in row if val != 0)
        assert non_zero == 2
    
    def test_get_empty_cells(self):
        game = GameLogic(4)
        game.grid = [[2, 4, 2, 4],
                     [4, 2, 4, 2],
                     [2, 4, 2, 4],
                     [4, 2, 4, 0]]
        
        empty = game.get_empty_cells()
        assert len(empty) == 1
        assert empty[0] == (3, 3)
    
    def test_move_left_basic(self):
        game = GameLogic(4)
        game.grid = [[2, 0, 0, 0],
                     [0, 0, 2, 0],
                     [0, 0, 0, 0],
                     [4, 0, 0, 0]]
        
        moved, score, merged = game.move_left()
        
        assert moved == True
        assert game.grid[0][0] == 2
        assert game.grid[1][0] == 2
        assert game.grid[3][0] == 4
    
    def test_merge(self):
        game = GameLogic(4)
        game.grid = [[2, 2, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        moved, score, merged = game.move_left()
        
        assert moved == True
        assert game.grid[0][0] == 4
        assert game.grid[0][1] == 0
        assert score == 4
    
    def test_no_move(self):
        game = GameLogic(4)
        game.grid = [[2, 0, 0, 0],
                     [4, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        moved1, _, _ = game.move_left()
        game.grid[0][0] = 2
        game.grid[1][0] = 4
        moved2, _, _ = game.move_left()
        
        assert moved2 == False
    
    def test_move_right(self):
        game = GameLogic(4)
        game.grid = [[0, 0, 0, 2],
                     [0, 0, 4, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        moved, _, _ = game.move_right()
        
        assert moved == True
        assert game.grid[0][3] == 2
        assert game.grid[1][3] == 4
    
    def test_move_up(self):
        game = GameLogic(4)
        game.grid = [[0, 0, 0, 0],
                     [2, 0, 0, 0],
                     [4, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        moved, _, _ = game.move_up()
        
        assert moved == True
        assert game.grid[0][0] == 2
        assert game.grid[1][0] == 4
    
    def test_move_down(self):
        game = GameLogic(4)
        game.grid = [[0, 0, 0, 0],
                     [2, 0, 0, 0],
                     [4, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        moved, _, _ = game.move_down()
        
        assert moved == True
        assert game.grid[2][0] == 2
        assert game.grid[3][0] == 4
    
    def test_can_move(self):
        game = GameLogic(4)
        game.grid = [[2, 4, 2, 4],
                     [4, 2, 4, 2],
                     [2, 4, 2, 4],
                     [4, 2, 4, 0]]
        assert game.can_move() == True
        
        game.grid = [[2, 4, 2, 4],
                     [4, 2, 4, 2],
                     [2, 4, 2, 4],
                     [4, 2, 4, 8]]
        assert game.can_move() == False
    
    def test_can_move_with_merge(self):
        game = GameLogic(4)
        game.grid = [[2, 2, 4, 8],
                     [4, 8, 2, 4],
                     [2, 4, 8, 2],
                     [4, 2, 4, 8]]
        assert game.can_move() == True
    
    def test_has_won(self):
        game = GameLogic(4)
        game.grid = [[2, 4, 8, 16],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        assert game.has_won(16) == True
        assert game.has_won(32) == False
    
    def test_score_tracking(self):
        game = GameLogic(4)
        game.grid = [[2, 2, 2, 2],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
        
        game.move_left()
        assert game.score == 8
        assert game.moves == 1


class TestLevelSystem:
    def test_total_levels(self):
        levels = LevelSystem()
        assert levels.get_total_levels() == 20
    
    def test_level_info(self):
        levels = LevelSystem()
        level1 = levels.get_level(1)
        
        assert level1['level'] == 1
        assert level1['target'] == 32
        assert level1['grid_size'] == 3
    
    def test_level_20(self):
        levels = LevelSystem()
        level20 = levels.get_level(20)
        
        assert level20['level'] == 20
        assert level20['target'] == 16384
        assert level20['time_limit'] == 420
    
    def test_difficulty_tier(self):
        levels = LevelSystem()
        
        assert levels.get_difficulty_tier(1) == 1
        assert levels.get_difficulty_tier(5) == 1
        assert levels.get_difficulty_tier(6) == 2
        assert levels.get_difficulty_tier(10) == 2
        assert levels.get_difficulty_tier(11) == 3
        assert levels.get_difficulty_tier(20) == 4
    
    def test_is_timed(self):
        levels = LevelSystem()
        
        assert levels.is_timed_level(1) == False
        assert levels.is_timed_level(2) == False
        assert levels.is_timed_level(3) == False
        assert levels.is_timed_level(4) == False
        assert levels.is_timed_level(5) == True
        
        assert levels.is_timed_level(6) == False
        assert levels.is_timed_level(7) == True
        assert levels.is_timed_level(8) == False
        assert levels.is_timed_level(9) == True
        assert levels.is_timed_level(10) == True
        
        assert levels.is_timed_level(20) == True
    
    def test_invalid_level(self):
        levels = LevelSystem()
        
        assert levels.get_level(0) is None
        assert levels.get_level(21) is None
        assert levels.get_level(100) is None
