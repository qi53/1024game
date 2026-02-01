import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGameCore(unittest.TestCase):
    def setUp(self):
        from src.game_core import GameCore
        self.game = GameCore()
    
    def test_initial_grid(self):
        self.game.reset(level=1)
        self.assertEqual(self.game.grid_size, 4)
        
        non_zero = sum(1 for row in self.game.grid for val in row if val > 0)
        self.assertEqual(non_zero, 2)
    
    def test_grid_size_by_level(self):
        self.game.reset(level=1)
        self.assertEqual(self.game.grid_size, 4)
        
        self.game.reset(level=6)
        self.assertEqual(self.game.grid_size, 5)
        
        self.game.reset(level=11)
        self.assertEqual(self.game.grid_size, 6)
        
        self.game.reset(level=16)
        self.assertEqual(self.game.grid_size, 7)
    
    def test_move_directions(self):
        from src.game_core import MoveResult
        
        self.game.reset(level=1)
        self.game.grid = [[0, 0, 0, 0],
                         [0, 2, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]
        
        result = self.game.move("left")
        self.assertEqual(result, MoveResult.SUCCESS)
        self.assertEqual(self.game.grid[1][0], 2)
    
    def test_merge_same_values(self):
        from src.game_core import MoveResult
        
        self.game.reset(level=1)
        self.game.grid = [[0, 0, 0, 0],
                         [2, 2, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]
        
        result = self.game.move("left")
        self.assertEqual(result, MoveResult.SUCCESS)
        self.assertEqual(self.game.grid[1][0], 4)
    
    def test_no_move_when_stuck(self):
        from src.game_core import MoveResult
        
        self.game.reset(level=1)
        self.game.grid = [[2, 4, 8, 16],
                         [4, 8, 16, 2],
                         [8, 16, 2, 4],
                         [16, 2, 4, 8]]
        
        result = self.game.move("left")
        self.assertEqual(result, MoveResult.GAME_OVER)
    
    def test_game_over_detection(self):
        from src.game_core import MoveResult
        
        self.game.reset(level=1)
        self.game.grid = [[2, 4, 2, 4],
                         [4, 2, 4, 2],
                         [2, 4, 2, 4],
                         [4, 2, 4, 2]]
        
        result = self.game.move("up")
        self.assertEqual(result, MoveResult.GAME_OVER)
    
    def test_win_detection(self):
        from src.game_core import MoveResult
        from src.config import LEVEL_CONFIGS
        
        self.game.reset(level=1)
        target = LEVEL_CONFIGS[1]["target"]
        
        self.game.grid = [[0, 0, 0, 0],
                         [target // 2, target // 2, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]
        
        result = self.game.move("left")
        self.assertEqual(result, MoveResult.WIN)
    
    def test_score_increase(self):
        self.game.reset(level=1)
        initial_score = self.game.score
        
        self.game.grid = [[0, 0, 0, 0],
                         [2, 2, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]
        self.game.move("left")
        
        self.assertGreater(self.game.score, initial_score)
    
    def test_max_tile_tracking(self):
        self.game.reset(level=1)
        
        self.game.grid = [[0, 0, 0, 0],
                         [4, 4, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, 0, 0]]
        self.game.move("left")
        
        self.assertGreaterEqual(self.game.get_max_tile(), 8)


if __name__ == "__main__":
    unittest.main()
