import os
import shutil
import tempfile
import pytest
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.storage import GameData


class TestGameData:
    @pytest.fixture(autouse=True)
    def setup_temp_dir(self):
        self.temp_dir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        game_data = GameData(self.temp_dir)
        assert game_data.is_level_unlocked(1)
        assert not game_data.is_level_unlocked(2)
        assert game_data.get_setting('theme') == 'classic'
        assert game_data.get_stats()['games_played'] == 0

    def test_unlock_level(self):
        game_data = GameData(self.temp_dir)
        assert not game_data.is_level_unlocked(5)
        game_data.unlock_level(5)
        assert game_data.is_level_unlocked(5)

    def test_complete_level(self):
        game_data = GameData(self.temp_dir)
        assert not game_data.is_level_completed(1)
        game_data.complete_level(1, score=1000, time=60.0)
        assert game_data.is_level_completed(1)
        assert game_data.get_level_score(1) == 1000
        assert game_data.is_level_unlocked(2)

    def test_unlock_achievement(self):
        game_data = GameData(self.temp_dir)
        assert not game_data.is_achievement_unlocked('first_win')
        result = game_data.unlock_achievement('first_win')
        assert result
        assert game_data.is_achievement_unlocked('first_win')
        assert 'first_win' in game_data.get_all_unlocked_achievements()

    def test_unlock_achievement_duplicate(self):
        game_data = GameData(self.temp_dir)
        game_data.unlock_achievement('first_win')
        result = game_data.unlock_achievement('first_win')
        assert not result

    def test_update_stats(self):
        game_data = GameData(self.temp_dir)
        game_data.update_stats(games_played=1, total_moves=50)
        stats = game_data.get_stats()
        assert stats['games_played'] == 1
        assert stats['total_moves'] == 50
        game_data.update_stats(games_played=1, total_moves=30)
        stats = game_data.get_stats()
        assert stats['games_played'] == 2
        assert stats['total_moves'] == 80

    def test_update_stats_best_score(self):
        game_data = GameData(self.temp_dir)
        game_data.update_stats(best_score=500)
        game_data.update_stats(best_score=300)
        assert game_data.get_stats()['best_score'] == 500
        game_data.update_stats(best_score=1000)
        assert game_data.get_stats()['best_score'] == 1000

    def test_get_unlocked_themes(self):
        game_data = GameData(self.temp_dir)
        unlocked = game_data.get_unlocked_themes()
        assert 'classic' in unlocked
        assert 'dark' not in unlocked
        for i in range(5):
            game_data.complete_level(i+1, score=100, time=10)
        unlocked = game_data.get_unlocked_themes()
        assert 'dark' in unlocked

    def test_settings(self):
        game_data = GameData(self.temp_dir)
        game_data.set_setting('theme', 'forest')
        game_data.set_setting('music_volume', 50)
        assert game_data.get_setting('theme') == 'forest'
        assert game_data.get_setting('music_volume') == 50

    def test_reset_all_data(self):
        game_data = GameData(self.temp_dir)
        game_data.set_setting('theme', 'forest')
        game_data.unlock_achievement('first_win')
        game_data.update_stats(games_played=10)
        game_data.reset_all_data()
        assert game_data.get_setting('theme') == 'classic'
        assert not game_data.is_achievement_unlocked('first_win')
        assert game_data.get_stats()['games_played'] == 0

    def test_save_and_load(self):
        data1 = GameData(self.temp_dir)
        data1.set_setting('music_volume', 50)
        data1.unlock_achievement('master')
        data1.update_stats(best_score=5000)
        data1.complete_level(3, score=2000, time=30)
        data2 = GameData(self.temp_dir)
        assert data2.get_setting('music_volume') == 50
        assert data2.is_achievement_unlocked('master')
        assert data2.get_stats()['best_score'] == 5000
        assert data2.is_level_completed(3)

    def test_persistence_after_instance_deletion(self):
        data1 = GameData(self.temp_dir)
        data1.set_setting('theme', 'ocean')
        data1.save_all()
        del data1
        data2 = GameData(self.temp_dir)
        assert data2.get_setting('theme') == 'ocean'
