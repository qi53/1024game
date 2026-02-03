"""
1024 Game - Pygame Version - Tests - Game Engine
游戏引擎测试
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_engine import LevelGame, GameStats
from config import Direction, LevelConfig, GRID_SIZE


class TestLevelGame(unittest.TestCase):
    """测试关卡游戏类"""
    
    def setUp(self):
        """每个测试前执行"""
        self.game = LevelGame(level=1)
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.game.level, 1)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_won)
        self.assertFalse(self.game.is_over)
        self.assertFalse(self.game.is_paused)
    
    def test_grid_size(self):
        """测试网格大小"""
        grid = self.game.get_grid()
        self.assertEqual(len(grid), GRID_SIZE)
        self.assertEqual(len(grid[0]), GRID_SIZE)
    
    def test_initial_tiles(self):
        """测试初始方块"""
        grid = self.game.get_grid()
        non_zero_count = sum(1 for row in grid for cell in row if cell > 0)
        self.assertEqual(non_zero_count, 2)  # 初始有两个方块
    
    def test_move_left(self):
        """测试向左移动"""
        # 设置测试网格
        self.game.grid = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        moved = self.game.move(Direction.LEFT)
        self.assertTrue(moved)
        
        grid = self.game.get_grid()
        self.assertEqual(grid[0][0], 4)  # 合并成4
        self.assertGreater(self.game.score, 0)
    
    def test_move_right(self):
        """测试向右移动"""
        self.game.grid = [
            [0, 0, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        moved = self.game.move(Direction.RIGHT)
        self.assertTrue(moved)
        
        grid = self.game.get_grid()
        self.assertEqual(grid[0][3], 4)
    
    def test_move_up(self):
        """测试向上移动"""
        self.game.grid = [
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        moved = self.game.move(Direction.UP)
        self.assertTrue(moved)
        
        grid = self.game.get_grid()
        self.assertEqual(grid[0][0], 4)
    
    def test_move_down(self):
        """测试向下移动"""
        self.game.grid = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [2, 0, 0, 0]
        ]
        
        moved = self.game.move(Direction.DOWN)
        self.assertTrue(moved)
        
        grid = self.game.get_grid()
        self.assertEqual(grid[3][0], 4)
    
    def test_no_move(self):
        """测试无法移动的情况"""
        self.game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2]
        ]
        
        # 保存历史记录长度
        history_len = len(self.game.history)
        
        moved = self.game.move(Direction.LEFT)
        self.assertFalse(moved)
        
        # 无法移动时不应保存历史
        self.assertEqual(len(self.game.history), history_len)
    
    def test_merge_score(self):
        """测试合并得分"""
        self.game.grid = [
            [2, 2, 4, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        initial_score = self.game.score
        self.game.move(Direction.LEFT)
        
        # 2+2=4 得4分，4+4=8 得8分
        self.assertEqual(self.game.score - initial_score, 12)
    
    def test_undo(self):
        """测试撤销功能"""
        initial_grid = [row[:] for row in self.game.grid]
        
        self.game.move(Direction.LEFT)
        self.assertTrue(len(self.game.history) > 0)
        
        # 撤销
        result = self.game.undo()
        self.assertTrue(result)
        
        # 检查网格恢复
        grid = self.game.get_grid()
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.assertEqual(grid[i][j], initial_grid[i][j])
    
    def test_cannot_undo_when_won(self):
        """测试胜利后不能撤销"""
        self.game.is_won = True
        result = self.game.undo()
        self.assertFalse(result)
    
    def test_cannot_undo_when_over(self):
        """测试结束后不能撤销"""
        self.game.is_over = True
        result = self.game.undo()
        self.assertFalse(result)
    
    def test_win_condition(self):
        """测试胜利条件"""
        # 设置达到目标分数
        self.game.score = self.game.target_score
        self.game._check_win_condition()
        self.assertTrue(self.game.is_won)
    
    def test_game_over_condition(self):
        """测试失败条件"""
        # 填满网格且无法合并
        self.game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2]
        ]
        
        self.game._check_game_over()
        self.assertTrue(self.game.is_over)
    
    def test_not_game_over_with_empty(self):
        """测试有空格时未结束"""
        self.game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 0, 4],
            [4, 2, 4, 2]
        ]
        
        self.game._check_game_over()
        self.assertFalse(self.game.is_over)
    
    def test_not_game_over_with_merge(self):
        """测试可合并时未结束"""
        self.game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 2, 4, 4],
            [4, 2, 4, 2]
        ]
        
        self.game._check_game_over()
        self.assertFalse(self.game.is_over)
    
    def test_pause_resume(self):
        """测试暂停和恢复"""
        self.game.pause()
        self.assertTrue(self.game.is_paused)
        
        self.game.resume()
        self.assertFalse(self.game.is_paused)
    
    def test_restart(self):
        """测试重新开始"""
        self.game.move(Direction.LEFT)
        old_score = self.game.score
        
        self.game.restart()
        
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_won)
        self.assertFalse(self.game.is_over)
        self.assertEqual(len(self.game.history), 0)
    
    def test_level_config(self):
        """测试关卡配置"""
        # 测试不同关卡有不同的配置
        game1 = LevelGame(level=1)
        game5 = LevelGame(level=5)
        game10 = LevelGame(level=10)
        game20 = LevelGame(level=20)
        
        self.assertEqual(game1.config.level, 1)
        self.assertEqual(game5.config.level, 5)
        self.assertEqual(game10.config.level, 10)
        self.assertEqual(game20.config.level, 20)
        
        # 高难度关卡应该有时间限制
        self.assertEqual(game1.config.time_limit, 0)
        self.assertGreater(game10.config.time_limit, 0)
    
    def test_obstacles(self):
        """测试障碍物"""
        game = LevelGame(level=10)  # 第10关有障碍物
        obstacle_count = sum(1 for row in game.grid for cell in row if cell == -1)
        self.assertGreater(obstacle_count, 0)
    
    def test_time_limit(self):
        """测试时间限制"""
        game = LevelGame(level=10)  # 有时间限制的关卡
        game.time_limit = 1  # 1秒限制
        
        import time
        time.sleep(1.1)
        
        self.assertTrue(game.check_time_limit())
    
    def test_get_remaining_time(self):
        """测试获取剩余时间"""
        game = LevelGame(level=10)
        remaining = game.get_remaining_time()
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, game.time_limit)


class TestGameStats(unittest.TestCase):
    """测试游戏统计"""
    
    def test_initial_stats(self):
        """测试初始统计"""
        stats = GameStats()
        self.assertEqual(stats.total_score, 0)
        self.assertEqual(stats.total_moves, 0)
        self.assertEqual(stats.total_merges, 0)
        self.assertEqual(stats.max_tile_achieved, 0)
        self.assertEqual(stats.combo_count, 0)
        self.assertEqual(stats.max_combo, 0)
        self.assertEqual(stats.undo_count, 0)
    
    def test_update_time(self):
        """测试更新时间"""
        import time
        stats = GameStats()
        
        time.sleep(0.1)
        stats.update_time()
        
        self.assertGreater(stats.elapsed_time, 0)


class TestLevelConfig(unittest.TestCase):
    """测试关卡配置"""
    
    def test_level_configs_exist(self):
        """测试所有关卡配置存在"""
        from config import LEVEL_CONFIGS
        
        self.assertEqual(len(LEVEL_CONFIGS), 20)
        
        for i, config in enumerate(LEVEL_CONFIGS, 1):
            self.assertEqual(config.level, i)
            self.assertIsInstance(config.target_score, int)
            self.assertIsInstance(config.spawn_values, list)
            self.assertIsInstance(config.spawn_weights, list)
            self.assertIsInstance(config.time_limit, int)
            self.assertIsInstance(config.obstacle_count, int)
            self.assertIsInstance(config.special_tile_chance, float)
    
    def test_difficulty_progression(self):
        """测试难度递进"""
        from config import LEVEL_CONFIGS
        
        # 检查目标分数递增
        for i in range(1, len(LEVEL_CONFIGS)):
            prev = LEVEL_CONFIGS[i - 1]
            curr = LEVEL_CONFIGS[i]
            
            # 目标分数应该递增或保持不变
            self.assertGreaterEqual(curr.target_score, prev.target_score)
        
        # 高难度关卡有更多障碍物
        self.assertGreater(LEVEL_CONFIGS[19].obstacle_count, LEVEL_CONFIGS[0].obstacle_count)


if __name__ == '__main__':
    unittest.main()
