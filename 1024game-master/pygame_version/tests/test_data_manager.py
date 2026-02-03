"""
1024 Game - Pygame Version - Tests - Data Manager
数据管理器测试
"""

import unittest
import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import DataManager, GameSaveData, GameSettings, GameStatistics


class TestDataManager(unittest.TestCase):
    """测试数据管理器"""
    
    def setUp(self):
        """每个测试前执行"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 修改数据目录
        import data_manager
        data_manager.DATA_DIR = self.temp_dir
        data_manager.SAVE_FILE = os.path.join(self.temp_dir, 'save_data.json')
        data_manager.SETTINGS_FILE = os.path.join(self.temp_dir, 'settings.json')
        data_manager.STATS_FILE = os.path.join(self.temp_dir, 'stats.json')
        
        # 重置单例
        data_manager._data_manager = None
        
        self.data_manager = DataManager()
    
    def tearDown(self):
        """每个测试后执行"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.data_manager.save_data.current_level, 1)
        self.assertEqual(self.data_manager.save_data.unlocked_levels, 1)
        self.assertEqual(len(self.data_manager.save_data.achievements), 0)
    
    def test_unlock_level(self):
        """测试解锁关卡"""
        self.data_manager.unlock_level(2)
        self.assertEqual(self.data_manager.get_unlocked_levels(), 2)
        
        self.data_manager.unlock_level(5)
        self.assertEqual(self.data_manager.get_unlocked_levels(), 5)
    
    def test_is_level_unlocked(self):
        """测试检查关卡是否解锁"""
        self.data_manager.save_data.unlocked_levels = 3
        
        self.assertTrue(self.data_manager.is_level_unlocked(1))
        self.assertTrue(self.data_manager.is_level_unlocked(3))
        self.assertFalse(self.data_manager.is_level_unlocked(4))
    
    def test_achievement_unlock(self):
        """测试成就解锁"""
        self.data_manager.update_achievement("test_achievement", True)
        self.assertTrue(self.data_manager.is_achievement_unlocked("test_achievement"))
        
        self.data_manager.update_achievement("test_achievement", False)
        self.assertFalse(self.data_manager.is_achievement_unlocked("test_achievement"))
    
    def test_setting_get_set(self):
        """测试设置获取和设置"""
        self.data_manager.set_setting('dark_theme', True)
        self.assertTrue(self.data_manager.get_setting('dark_theme'))
        
        self.data_manager.set_setting('dark_theme', False)
        self.assertFalse(self.data_manager.get_setting('dark_theme'))
    
    def test_setting_default(self):
        """测试设置默认值"""
        value = self.data_manager.get_setting('nonexistent_key', 'default')
        self.assertEqual(value, 'default')
    
    def test_volume_settings(self):
        """测试音量设置"""
        self.data_manager.set_volume(master=0.5, sfx=0.7, music=0.3)
        
        volumes = self.data_manager.get_volumes()
        self.assertEqual(volumes['master'], 0.5)
        self.assertEqual(volumes['sfx'], 0.7)
        self.assertEqual(volumes['music'], 0.3)
    
    def test_volume_clamping(self):
        """测试音量限制在0-1范围"""
        self.data_manager.set_volume(master=1.5, sfx=-0.5)
        
        volumes = self.data_manager.get_volumes()
        self.assertEqual(volumes['master'], 1.0)
        self.assertEqual(volumes['sfx'], 0.0)
    
    def test_toggle_dark_theme(self):
        """测试切换深色主题"""
        initial = self.data_manager.settings.dark_theme
        result = self.data_manager.toggle_dark_theme()
        self.assertEqual(result, not initial)
        self.assertEqual(self.data_manager.settings.dark_theme, not initial)
    
    def test_record_game_result(self):
        """测试记录游戏结果"""
        self.data_manager.record_game_result(
            level=1, won=True, score=1000,
            moves=50, time_taken=60.0, max_tile=128
        )
        
        stats = self.data_manager.get_statistics()
        self.assertEqual(stats.total_games_played, 1)
        self.assertEqual(stats.total_wins, 1)
        self.assertEqual(stats.highest_score, 1000)
    
    def test_record_multiple_games(self):
        """测试记录多局游戏"""
        for i in range(5):
            self.data_manager.record_game_result(
                level=1, won=i % 2 == 0, score=500 + i * 100,
                moves=40 + i, time_taken=50.0 + i, max_tile=64 + i * 32
            )
        
        stats = self.data_manager.get_statistics()
        self.assertEqual(stats.total_games_played, 5)
        self.assertEqual(stats.total_wins, 3)
        self.assertEqual(stats.total_losses, 2)
    
    def test_add_play_time(self):
        """测试添加游戏时间"""
        self.data_manager.add_play_time(3600)
        stats = self.data_manager.get_statistics()
        self.assertEqual(stats.total_play_time, 3600)
    
    def test_save_and_load(self):
        """测试保存和加载"""
        # 修改数据
        self.data_manager.unlock_level(5)
        self.data_manager.update_achievement("test_ach", True)
        self.data_manager.set_setting('dark_theme', True)
        
        # 保存
        self.assertTrue(self.data_manager.save_all())
        
        # 重置单例并重新加载
        import data_manager
        data_manager._data_manager = None
        new_manager = DataManager()
        
        # 验证数据
        self.assertEqual(new_manager.get_unlocked_levels(), 5)
        self.assertTrue(new_manager.is_achievement_unlocked("test_ach"))
        self.assertTrue(new_manager.get_setting('dark_theme'))
    
    def test_export_import(self):
        """测试导出和导入"""
        # 设置一些数据
        self.data_manager.unlock_level(10)
        self.data_manager.record_game_result(
            level=1, won=True, score=2000,
            moves=100, time_taken=120.0, max_tile=256
        )
        
        # 导出
        export_path = os.path.join(self.temp_dir, 'export.json')
        self.assertTrue(self.data_manager.export_data(export_path))
        self.assertTrue(os.path.exists(export_path))
        
        # 重置数据
        self.data_manager.reset_all_data()
        self.assertEqual(self.data_manager.get_unlocked_levels(), 1)
        
        # 导入
        self.assertTrue(self.data_manager.import_data(export_path))
        self.assertEqual(self.data_manager.get_unlocked_levels(), 10)
    
    def test_reset_all_data(self):
        """测试重置所有数据"""
        self.data_manager.unlock_level(10)
        self.data_manager.record_game_result(
            level=1, won=True, score=1000,
            moves=50, time_taken=60.0, max_tile=128
        )
        
        self.data_manager.reset_all_data()
        
        self.assertEqual(self.data_manager.get_unlocked_levels(), 1)
        self.assertEqual(self.data_manager.get_statistics().total_games_played, 0)
    
    def test_reset_statistics_only(self):
        """测试仅重置统计"""
        self.data_manager.unlock_level(5)
        self.data_manager.record_game_result(
            level=1, won=True, score=1000,
            moves=50, time_taken=60.0, max_tile=128
        )
        
        self.data_manager.reset_statistics()
        
        # 存档应该保留
        self.assertEqual(self.data_manager.get_unlocked_levels(), 5)
        # 统计应该重置
        self.assertEqual(self.data_manager.get_statistics().total_games_played, 0)
    
    def test_level_stats(self):
        """测试关卡统计"""
        self.data_manager.record_game_result(
            level=3, won=True, score=1500,
            moves=60, time_taken=90.0, max_tile=256
        )
        
        level_stats = self.data_manager.get_level_stats(3)
        self.assertIn('completions', level_stats)
        self.assertIn('fastest_time', level_stats)


class TestGameSaveData(unittest.TestCase):
    """测试游戏存档数据"""
    
    def test_default_values(self):
        """测试默认值"""
        data = GameSaveData()
        self.assertEqual(data.current_level, 1)
        self.assertEqual(data.unlocked_levels, 1)
        self.assertIsNotNone(data.achievements)


class TestGameSettings(unittest.TestCase):
    """测试游戏设置"""
    
    def test_default_values(self):
        """测试默认值"""
        settings = GameSettings()
        self.assertFalse(settings.fullscreen)
        self.assertEqual(settings.screen_width, 1280)
        self.assertEqual(settings.screen_height, 720)
        self.assertEqual(settings.master_volume, 1.0)
        self.assertFalse(settings.dark_theme)
        self.assertTrue(settings.show_particles)
    
    def test_key_bindings(self):
        """测试按键绑定"""
        settings = GameSettings()
        self.assertIn('up', settings.key_bindings)
        self.assertIn('down', settings.key_bindings)
        self.assertIn('left', settings.key_bindings)
        self.assertIn('right', settings.key_bindings)


class TestGameStatistics(unittest.TestCase):
    """测试游戏统计"""
    
    def test_default_values(self):
        """测试默认值"""
        stats = GameStatistics()
        self.assertEqual(stats.total_games_played, 0)
        self.assertEqual(stats.total_wins, 0)
        self.assertEqual(stats.total_losses, 0)
        self.assertIsNotNone(stats.tiles_merged)
        self.assertIsNotNone(stats.level_completions)
        self.assertIsNotNone(stats.recent_games)
    
    def test_add_game_result(self):
        """测试添加游戏结果"""
        stats = GameStatistics()
        stats.add_game_result(1, True, 1000, 50, 60.0, 128)
        
        self.assertEqual(stats.total_games_played, 1)
        self.assertEqual(stats.total_wins, 1)
        self.assertEqual(stats.highest_score, 1000)
        self.assertEqual(stats.average_score, 1000)
    
    def test_average_score_calculation(self):
        """测试平均分计算"""
        stats = GameStatistics()
        stats.add_game_result(1, True, 1000, 50, 60.0, 128)
        stats.add_game_result(1, False, 500, 30, 40.0, 64)
        
        self.assertEqual(stats.average_score, 750)
    
    def test_add_merge(self):
        """测试添加合并记录"""
        stats = GameStatistics()
        stats.add_merge(4)
        stats.add_merge(4)
        stats.add_merge(8)
        
        self.assertEqual(stats.tiles_merged['4'], 2)
        self.assertEqual(stats.tiles_merged['8'], 1)
        self.assertEqual(stats.total_merges, 3)
    
    def test_recent_games_limit(self):
        """测试最近游戏记录限制"""
        stats = GameStatistics()
        
        for i in range(60):
            stats.add_game_result(1, True, 100 + i, 50, 60.0, 128)
        
        self.assertEqual(len(stats.recent_games), 50)


if __name__ == '__main__':
    unittest.main()
