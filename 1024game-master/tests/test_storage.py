import unittest
import tempfile
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.environ["GAME_DATA_DIR"] = self.test_dir
        
        from src.storage import GameStorage
        GameStorage._instance = None
    
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_singleton_pattern(self):
        from src.storage import GameStorage
        
        s1 = GameStorage()
        s2 = GameStorage()
        self.assertIs(s1, s2)
    
    def test_default_settings(self):
        from src.storage import GameStorage
        
        s = GameStorage()
        settings = s.get_settings()
        
        self.assertIn("music_volume", settings)
        self.assertIn("sfx_volume", settings)
        self.assertIn("particles_enabled", settings)
        self.assertIn("current_theme", settings)
    
    def test_save_and_load_settings(self):
        from src.storage import GameStorage
        
        s = GameStorage()
        s.update_settings({"music_volume": 0.5, "sfx_volume": 0.8})
        s.save()
        
        GameStorage._instance = None
        s2 = GameStorage()
        settings = s2.get_settings()
        
        self.assertEqual(settings["music_volume"], 0.5)
        self.assertEqual(settings["sfx_volume"], 0.8)
    
    def test_level_progress(self):
        from src.storage import GameStorage
        
        s = GameStorage()
        self.assertTrue(s.is_level_unlocked(1))
        self.assertFalse(s.is_level_unlocked(2))
        
        s.unlock_level(2)
        self.assertTrue(s.is_level_unlocked(2))
        
        s.save()
        
        GameStorage._instance = None
        s2 = GameStorage()
        
        self.assertTrue(s2.is_level_unlocked(2))
    
    def test_achievement_unlock(self):
        from src.storage import GameStorage
        from src.config import ACHIEVEMENTS
        
        s = GameStorage()
        first_achievement = list(ACHIEVEMENTS.keys())[0] if ACHIEVEMENTS else "first_win"
        
        if first_achievement in ACHIEVEMENTS:
            self.assertNotIn(first_achievement, s.get_unlocked_achievements())
            
            result = s.unlock_achievement(first_achievement)
            self.assertTrue(result)
            self.assertIn(first_achievement, s.get_unlocked_achievements())
    
    def test_stats_tracking(self):
        from src.storage import GameStorage
        
        s = GameStorage()
        stats = s.get_player_stats()
        self.assertIsInstance(stats, dict)
        
        s.record_game_played(True, 1000, 50, 45.0, 1)
        s.save()
        
        GameStorage._instance = None
        s2 = GameStorage()
        self.assertEqual(s2.get_player_stats()["total_games"], 1)
        self.assertEqual(s2.get_player_stats()["total_wins"], 1)


if __name__ == "__main__":
    unittest.main()
