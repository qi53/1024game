#!/usr/bin/env python3
"""
1024 Game - Comprehensive Test Suite
Tests all game functionality including 20 levels, particles, audio, data persistence
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pygame_game import Game, LevelConfig, GameStats
from particles import ParticleSystem, Particle, FloatingTextManager, ParticleType
from data_manager import DataManager, AchievementType, Achievement, LevelProgress
from themes import ThemeManager, ColorScheme


class TestLevelConfig(unittest.TestCase):
    """Test level configuration"""
    
    def test_get_level(self):
        level = LevelConfig.get_level(1)
        self.assertEqual(level["id"], 1)
        self.assertEqual(level["grid_size"], 3)
        self.assertEqual(level["target"], 128)
        
        level = LevelConfig.get_level(10)
        self.assertEqual(level["id"], 10)
        self.assertEqual(level["grid_size"], 4)
        self.assertEqual(level["target"], 2048)
    
    def test_get_difficulty_tier(self):
        self.assertEqual(LevelConfig.get_difficulty_tier(1), 1)
        self.assertEqual(LevelConfig.get_difficulty_tier(5), 1)
        self.assertEqual(LevelConfig.get_difficulty_tier(6), 2)
        self.assertEqual(LevelConfig.get_difficulty_tier(10), 2)
        self.assertEqual(LevelConfig.get_difficulty_tier(11), 3)
        self.assertEqual(LevelConfig.get_difficulty_tier(15), 3)
        self.assertEqual(LevelConfig.get_difficulty_tier(16), 4)
        self.assertEqual(LevelConfig.get_difficulty_tier(20), 4)
    
    def test_all_levels_exist(self):
        for i in range(1, 21):
            level = LevelConfig.get_level(i)
            self.assertEqual(level["id"], i)
            self.assertIn("grid_size", level)
            self.assertIn("target", level)
            self.assertIn("moves", level)
            self.assertIn("spawn_4_chance", level)
            self.assertIn("name", level)
    
    def test_difficulty_progression(self):
        level_1 = LevelConfig.get_level(1)
        level_5 = LevelConfig.get_level(5)
        level_10 = LevelConfig.get_level(10)
        level_15 = LevelConfig.get_level(15)
        level_20 = LevelConfig.get_level(20)
        
        self.assertLess(level_1["target"], level_5["target"])
        self.assertLess(level_5["target"], level_10["target"])
        self.assertLess(level_10["target"], level_15["target"])
        self.assertLess(level_15["target"], level_20["target"])


class TestGameStats(unittest.TestCase):
    """Test game statistics"""
    
    def setUp(self):
        self.stats = GameStats()
    
    def test_initial_state(self):
        self.assertEqual(self.stats.total_moves, 0)
        self.assertEqual(self.stats.total_merges, 0)
        self.assertEqual(self.stats.max_tile, 0)
        self.assertEqual(self.stats.max_combo, 0)
        self.assertEqual(len(self.stats.score_history), 0)
    
    def test_record_move(self):
        self.stats.record_move("up", 2, 100)
        self.assertEqual(self.stats.total_moves, 1)
        self.assertEqual(self.stats.total_merges, 2)
        self.assertEqual(self.stats.max_combo, 1)
        self.assertEqual(self.stats.score_history, [100])
    
    def test_combo_tracking(self):
        self.stats.record_move("left", 1, 50)
        self.assertEqual(self.stats.combo_count, 1)
        
        self.stats.record_move("right", 1, 50)
        self.assertEqual(self.stats.combo_count, 2)
        self.assertEqual(self.stats.max_combo, 2)
        
        self.stats.record_move("up", 0, 0)
        self.assertEqual(self.stats.combo_count, 0)
    
    def test_record_merge(self):
        self.stats.record_merge(4)
        self.assertEqual(self.stats.max_tile, 4)
        
        self.stats.record_merge(8)
        self.assertEqual(self.stats.max_tile, 8)
        
        self.stats.record_merge(1024)
        self.assertEqual(self.stats.max_tile, 1024)
    
    def test_to_dict(self):
        self.stats.record_move("up", 1, 100)
        self.stats.record_merge(4)
        
        data = self.stats.to_dict()
        self.assertEqual(data["total_moves"], 1)
        self.assertEqual(data["total_merges"], 1)
        self.assertEqual(data["max_tile"], 4)
        self.assertIn("moves_by_direction", data)
    
    def test_reset(self):
        self.stats.record_move("up", 1, 100)
        self.stats.record_merge(4)
        
        self.stats.reset()
        
        self.assertEqual(self.stats.total_moves, 0)
        self.assertEqual(self.stats.total_merges, 0)
        self.assertEqual(self.stats.max_tile, 0)


class TestGame(unittest.TestCase):
    """Test core game logic"""
    
    def setUp(self):
        self.game = Game(level_id=1)
    
    def test_initialization(self):
        self.assertEqual(self.game.level_id, 1)
        self.assertEqual(self.game.grid_size, 3)
        self.assertEqual(self.game.target, 128)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_won)
        self.assertFalse(self.game.is_over)
    
    def test_initial_tiles(self):
        non_zero_count = sum(1 for row in self.game.grid for cell in row if cell != 0)
        self.assertEqual(non_zero_count, 2)
    
    def test_get_empty_cells(self):
        empty_cells = self.game.get_empty_cells()
        self.assertEqual(len(empty_cells), 7)
        
        for row, col in empty_cells:
            self.assertEqual(self.game.grid[row][col], 0)
    
    def test_add_random_tile(self):
        initial_non_zero = sum(1 for row in self.game.grid for cell in row if cell != 0)
        result = self.game.add_random_tile()
        self.assertTrue(result)
        
        new_non_zero = sum(1 for row in self.game.grid for cell in row if cell != 0)
        self.assertEqual(new_non_zero, initial_non_zero + 1)
    
    def test_move_left(self):
        self.game.grid = [
            [2, 2, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        moved, score, merges = self.game.move("left")
        self.assertTrue(moved)
        self.assertEqual(score, 4)
        self.assertEqual(len(merges), 1)
        self.assertEqual(self.game.grid[0][0], 4)
    
    def test_move_right(self):
        self.game.grid = [
            [0, 2, 2],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        moved, score, merges = self.game.move("right")
        self.assertTrue(moved)
        self.assertEqual(score, 4)
        self.assertEqual(self.game.grid[0][2], 4)
    
    def test_move_up(self):
        self.game.grid = [
            [2, 0, 0],
            [2, 0, 0],
            [0, 0, 0]
        ]
        
        moved, score, merges = self.game.move("up")
        self.assertTrue(moved)
        self.assertEqual(score, 4)
        self.assertEqual(self.game.grid[0][0], 4)
    
    def test_move_down(self):
        self.game.grid = [
            [0, 0, 0],
            [2, 0, 0],
            [2, 0, 0]
        ]
        
        moved, score, merges = self.game.move("down")
        self.assertTrue(moved)
        self.assertEqual(score, 4)
        self.assertEqual(self.game.grid[2][0], 4)
    
    def test_no_move_possible(self):
        self.game.grid = [
            [2, 4, 8],
            [4, 8, 16],
            [8, 16, 32]
        ]
        
        moved, score, merges = self.game.move("left")
        self.assertFalse(moved)
        self.assertEqual(score, 0)
    
    def test_multiple_merges(self):
        self.game.grid = [
            [2, 2, 2],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        moved, score, merges = self.game.move("left")
        self.assertTrue(moved)
        self.assertEqual(score, 4)
        self.assertEqual(self.game.grid[0][0], 4)
        self.assertEqual(self.game.grid[0][1], 2)
    
    def test_check_win(self):
        self.game.grid = [
            [128, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        self.assertTrue(self.game.check_win())
        self.assertFalse(self.game.is_won)
    
    def test_check_game_over_empty_cells(self):
        self.assertFalse(self.game.check_game_over())
    
    def test_check_game_over_possible_merges(self):
        self.game.grid = [
            [2, 2, 4],
            [4, 8, 16],
            [8, 16, 32]
        ]
        
        self.assertFalse(self.game.check_game_over())
    
    def test_check_game_over_no_moves(self):
        self.game.grid = [
            [2, 4, 8],
            [4, 8, 16],
            [8, 16, 32]
        ]
        self.game.moves_remaining = 0
        
        self.assertTrue(self.game.check_game_over())
    
    def test_set_level(self):
        self.game.set_level(5)
        self.assertEqual(self.game.level_id, 5)
        self.assertEqual(self.game.grid_size, 4)
        self.assertEqual(self.game.target, 512)
    
    def test_get_progress(self):
        self.game.grid = [
            [64, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        progress = self.game.get_progress()
        self.assertEqual(progress, 0.5)
    
    def test_get_level_info(self):
        info = self.game.get_level_info()
        self.assertEqual(info["id"], 1)
        self.assertEqual(info["name"], "入门")
        self.assertEqual(info["grid_size"], 3)
        self.assertEqual(info["target"], 128)
        self.assertIn("progress", info)


class TestParticleSystem(unittest.TestCase):
    """Test particle system"""
    
    def setUp(self):
        self.particle_system = ParticleSystem()
    
    def test_initialization(self):
        self.assertEqual(len(self.particle_system.particles), 0)
        self.assertTrue(self.particle_system.enabled)
    
    def test_emit(self):
        self.particle_system.emit(100, 100, ParticleType.MERGE, (255, 0, 0), count=5)
        self.assertEqual(len(self.particle_system.particles), 5)
    
    def test_emit_merge(self):
        self.particle_system.emit_merge(100, 100, 4)
        self.assertEqual(len(self.particle_system.particles), 15)
    
    def test_emit_spawn(self):
        self.particle_system.emit_spawn(100, 100)
        self.assertEqual(len(self.particle_system.particles), 8)
    
    def test_emit_win(self):
        self.particle_system.emit_win(100, 100)
        self.assertEqual(len(self.particle_system.particles), 30)
    
    def test_emit_combo(self):
        self.particle_system.emit_combo(100, 100, 5)
        self.assertEqual(len(self.particle_system.particles), 20)
    
    def test_update(self):
        self.particle_system.emit(100, 100, ParticleType.MERGE, (255, 0, 0), count=5)
        initial_count = len(self.particle_system.particles)
        
        self.particle_system.update()
        
        self.assertLessEqual(len(self.particle_system.particles), initial_count)
    
    def test_max_particles(self):
        for _ in range(100):
            self.particle_system.emit(100, 100, ParticleType.MERGE, (255, 0, 0), count=10)
        
        self.assertLessEqual(len(self.particle_system.particles), self.particle_system.max_particles)
    
    def test_set_enabled(self):
        self.particle_system.set_enabled(False)
        self.assertFalse(self.particle_system.enabled)
        
        self.particle_system.emit(100, 100, ParticleType.MERGE, (255, 0, 0), count=5)
        self.assertEqual(len(self.particle_system.particles), 0)
    
    def test_clear(self):
        self.particle_system.emit(100, 100, ParticleType.MERGE, (255, 0, 0), count=10)
        self.particle_system.clear()
        
        self.assertEqual(len(self.particle_system.particles), 0)


class TestFloatingTextManager(unittest.TestCase):
    """Test floating text manager"""
    
    def setUp(self):
        self.text_manager = FloatingTextManager()
    
    def test_initialization(self):
        self.assertEqual(len(self.text_manager.texts), 0)
    
    def test_add_score(self):
        self.text_manager.add_score(100, 100, 100)
        self.assertEqual(len(self.text_manager.texts), 1)
    
    def test_add_combo(self):
        self.text_manager.add_combo(100, 100, 5)
        self.assertEqual(len(self.text_manager.texts), 1)
    
    def test_add_message(self):
        self.text_manager.add_message(100, 100, "Test", (255, 0, 0))
        self.assertEqual(len(self.text_manager.texts), 1)
    
    def test_update(self):
        self.text_manager.add_score(100, 100, 100)
        initial_count = len(self.text_manager.texts)
        
        self.text_manager.update()
        
        self.assertLessEqual(len(self.text_manager.texts), initial_count)
    
    def test_clear(self):
        self.text_manager.add_score(100, 100, 100)
        self.text_manager.clear()
        
        self.assertEqual(len(self.text_manager.texts), 0)


class TestDataManager(unittest.TestCase):
    """Test data manager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager()
        self.data_manager.data_dir = self.temp_dir
        self.data_manager.settings_file = os.path.join(self.temp_dir, "settings.json")
        self.data_manager.progress_file = os.path.join(self.temp_dir, "progress.json")
        self.data_manager.achievements_file = os.path.join(self.temp_dir, "achievements.json")
        self.data_manager.sessions_file = os.path.join(self.temp_dir, "sessions.json")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        self.assertIsNotNone(self.data_manager.settings)
        self.assertIsInstance(self.data_manager.level_progress, dict)
        self.assertIsInstance(self.data_manager.sessions, list)
    
    def test_get_setting(self):
        value = self.data_manager.get_setting("volume", 0.5)
        self.assertIsNotNone(value)
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)
    
    def test_set_setting(self):
        self.data_manager.set_setting("test_key", "test_value")
        self.assertEqual(self.data_manager.get_setting("test_key"), "test_value")
    
    def test_get_level_progress(self):
        progress = self.data_manager.get_level_progress(1)
        self.assertEqual(progress.level_id, 1)
        self.assertFalse(progress.completed)
    
    def test_update_level_progress(self):
        progress = self.data_manager.update_level_progress(
            level_id=1,
            won=True,
            score=1000,
            time_elapsed=30.0,
            moves=50,
            max_tile=128
        )
        
        self.assertTrue(progress.completed)
        self.assertEqual(progress.best_score, 1000)
        self.assertEqual(progress.best_time, 30.0)
    
    def test_add_session(self):
        self.data_manager.add_session(
            level_id=1,
            score=100,
            moves=10,
            time_elapsed=5.0,
            max_tile=32,
            won=True,
            stats={"test": "data"}
        )
        
        self.assertEqual(len(self.data_manager.sessions), 1)
    
    def test_get_total_score(self):
        self.data_manager.update_level_progress(1, True, 1000, 30.0, 50, 128)
        self.data_manager.update_level_progress(2, True, 2000, 40.0, 60, 256)
        
        total_score = self.data_manager.get_total_score()
        self.assertEqual(total_score, 3000)
    
    def test_get_completed_levels_count(self):
        self.data_manager.update_level_progress(1, True, 1000, 30.0, 50, 128)
        self.data_manager.update_level_progress(2, True, 2000, 40.0, 60, 256)
        
        count = self.data_manager.get_completed_levels_count()
        self.assertEqual(count, 2)
    
    def test_get_sessions_stats(self):
        self.data_manager.add_session(1, 100, 10, 5.0, 32, True, {})
        self.data_manager.add_session(2, 200, 20, 10.0, 64, False, {})
        
        stats = self.data_manager.get_sessions_stats()
        self.assertEqual(stats["total_sessions"], 2)
        self.assertEqual(stats["total_wins"], 1)
        self.assertEqual(stats["total_losses"], 1)
        self.assertEqual(stats["highest_score"], 200)
    
    def test_check_and_unlock_achievements(self):
        unlocked = self.data_manager.check_and_unlock_achievements(
            level_id=5,
            score=1500,
            max_tile=1024,
            combo=6,
            time_elapsed=20.0
        )
        
        self.assertGreater(len(unlocked), 0)
    
    def test_save_and_load(self):
        self.data_manager.set_setting("test_key", "test_value")
        self.data_manager.save_all()
        
        new_manager = DataManager()
        new_manager.data_dir = self.temp_dir
        new_manager.settings_file = os.path.join(self.temp_dir, "settings.json")
        new_manager.progress_file = os.path.join(self.temp_dir, "progress.json")
        new_manager.achievements_file = os.path.join(self.temp_dir, "achievements.json")
        new_manager.sessions_file = os.path.join(self.temp_dir, "sessions.json")
        new_manager._load_all_data()
        
        self.assertEqual(new_manager.get_setting("test_key"), "test_value")


class TestThemeManager(unittest.TestCase):
    """Test theme manager"""
    
    def test_get_theme(self):
        theme = ThemeManager.get_theme("classic")
        self.assertIsInstance(theme, ColorScheme)
        self.assertEqual(theme.name, "经典")
    
    def test_get_all_themes(self):
        themes = ThemeManager.get_all_themes()
        self.assertGreater(len(themes), 0)
        self.assertIn("classic", themes)
    
    def test_get_theme_names(self):
        names = ThemeManager.get_theme_names()
        self.assertGreater(len(names), 0)
        self.assertIn("classic", names)
    
    def test_get_tile_color(self):
        color = ThemeManager.get_tile_color("classic", 2)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)
        
        for value in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]:
            color = ThemeManager.get_tile_color("classic", value)
            self.assertIsInstance(color, tuple)
    
    def test_get_tile_text_color(self):
        color = ThemeManager.get_tile_text_color("classic", 2)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_game_cycle(self):
        game = Game(level_id=1)
        
        self.assertFalse(game.is_won)
        self.assertFalse(game.is_over)
        
        game.grid = [
            [64, 64, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        moved, score, merges = game.move("left")
        self.assertTrue(moved)
        self.assertEqual(game.grid[0][0], 128)
        
        self.assertTrue(game.check_win())
    
    def test_level_progression(self):
        for level_id in [1, 5, 10, 15, 20]:
            game = Game(level_id=level_id)
            self.assertEqual(game.level_id, level_id)
            self.assertGreater(game.target, 0)
    
    def test_data_persistence_integration(self):
        temp_dir = tempfile.mkdtemp()
        
        try:
            data_manager = DataManager()
            data_manager.data_dir = temp_dir
            data_manager.settings_file = os.path.join(temp_dir, "settings.json")
            data_manager.progress_file = os.path.join(temp_dir, "progress.json")
            data_manager.achievements_file = os.path.join(temp_dir, "achievements.json")
            data_manager.sessions_file = os.path.join(temp_dir, "sessions.json")
            
            game = Game(level_id=1)
            game.grid = [[128, 0, 0], [0, 0, 0], [0, 0, 0]]
            
            data_manager.update_level_progress(1, True, 1000, 30.0, 50, 128)
            data_manager.save_all()
            
            new_manager = DataManager()
            new_manager.data_dir = temp_dir
            new_manager.settings_file = os.path.join(temp_dir, "settings.json")
            new_manager.progress_file = os.path.join(temp_dir, "progress.json")
            new_manager.achievements_file = os.path.join(temp_dir, "achievements.json")
            new_manager.sessions_file = os.path.join(temp_dir, "sessions.json")
            new_manager._load_all_data()
            
            progress = new_manager.get_level_progress(1)
            self.assertTrue(progress.completed)
            
        finally:
            shutil.rmtree(temp_dir)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLevelConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestGameStats))
    suite.addTests(loader.loadTestsFromTestCase(TestGame))
    suite.addTests(loader.loadTestsFromTestCase(TestParticleSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestFloatingTextManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDataManager))
    suite.addTests(loader.loadTestsFromTestCase(TestThemeManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
