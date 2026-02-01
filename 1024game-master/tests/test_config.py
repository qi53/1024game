import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig(unittest.TestCase):
    def test_level_configs_count(self):
        from src.config import LEVEL_CONFIGS
        self.assertEqual(len(LEVEL_CONFIGS), 20)
    
    def test_level_difficulty_progression(self):
        from src.config import LEVEL_CONFIGS, Difficulty
        
        for level in range(1, 6):
            self.assertEqual(LEVEL_CONFIGS[level]["difficulty"], Difficulty.EASY)
        
        for level in range(6, 11):
            self.assertEqual(LEVEL_CONFIGS[level]["difficulty"], Difficulty.MEDIUM)
        
        for level in range(11, 16):
            self.assertEqual(LEVEL_CONFIGS[level]["difficulty"], Difficulty.HARD)
        
        for level in range(16, 21):
            self.assertEqual(LEVEL_CONFIGS[level]["difficulty"], Difficulty.EXPERT)
    
    def test_level_targets_increase(self):
        from src.config import LEVEL_CONFIGS
        
        targets = [LEVEL_CONFIGS[i]["target"] for i in range(1, 21)]
        self.assertEqual(targets, sorted(targets))
    
    def test_grid_size_increases(self):
        from src.config import LEVEL_CONFIGS
        
        self.assertEqual(LEVEL_CONFIGS[1]["grid_size"], 4)
        self.assertEqual(LEVEL_CONFIGS[6]["grid_size"], 5)
        self.assertEqual(LEVEL_CONFIGS[11]["grid_size"], 6)
        self.assertEqual(LEVEL_CONFIGS[16]["grid_size"], 7)
    
    def test_themes_exist(self):
        from src.config import THEMES
        
        self.assertIn("classic", THEMES)
        self.assertIn("dark", THEMES)
        self.assertIn("light", THEMES)
        self.assertIn("ocean", THEMES)
        self.assertIn("sunset", THEMES)
    
    def test_achievements_defined(self):
        from src.config import ACHIEVEMENTS
        
        self.assertGreater(len(ACHIEVEMENTS), 0)
        for ach_id, ach_data in ACHIEVEMENTS.items():
            self.assertIn("name", ach_data)
            self.assertIn("description", ach_data)


if __name__ == "__main__":
    unittest.main()
