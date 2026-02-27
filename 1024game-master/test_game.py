"""
1024 Game - Test Suite
Comprehensive tests for all game components
"""

import pytest
import pygame
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Import game modules
import config
from game_engine import GameEngine, GameState, Tile, MoveResult
from particles import ParticleSystem, Particle
from data_manager import DataManager, LevelProgress, GameStatistics, AchievementProgress
from audio import AudioManager, SoundType, SoundGenerator
from ui_components import Button, ButtonStyle, Slider, Toggle, ProgressBar, StarRating


# =============================================================================
# Game Engine Tests
# =============================================================================

class TestGameEngine:
    """Tests for the game engine"""
    
    def test_initialization(self):
        """Test game engine initialization"""
        game = GameEngine(level=1)
        assert game.level == 1
        assert game.grid_size == 4
        assert game.score == 0
        assert game.moves == 0
        assert game.state == GameState.IDLE
        assert len(game.undo_stack) == 0
    
    def test_initial_tiles_spawned(self):
        """Test that initial tiles are spawned"""
        game = GameEngine(level=1)
        empty_cells = game._get_empty_cells()
        # Should have 14 empty cells (16 - 2 initial tiles)
        assert len(empty_cells) == 14
    
    def test_move_left(self):
        """Test left movement"""
        game = GameEngine(level=1)
        # Clear grid and set up test
        game._init_grid()
        game.grid[0][0] = Tile(2, 0, 0)
        game.grid[0][1] = Tile(2, 0, 1)
        
        result = game.move("left")
        
        assert result.moved == True
        assert result.score_gained == 4
        assert game.grid[0][0].value == 4
    
    def test_move_right(self):
        """Test right movement"""
        game = GameEngine(level=1)
        game._init_grid()
        game.grid[0][2] = Tile(2, 0, 2)
        game.grid[0][3] = Tile(2, 0, 3)
        
        result = game.move("right")
        
        assert result.moved == True
        assert result.score_gained == 4
        assert game.grid[0][3].value == 4
    
    def test_move_up(self):
        """Test up movement"""
        game = GameEngine(level=1)
        game._init_grid()
        game.grid[0][0] = Tile(2, 0, 0)
        game.grid[1][0] = Tile(2, 1, 0)
        
        result = game.move("up")
        
        assert result.moved == True
        assert result.score_gained == 4
        assert game.grid[0][0].value == 4
    
    def test_move_down(self):
        """Test down movement"""
        game = GameEngine(level=1)
        game._init_grid()
        game.grid[2][0] = Tile(2, 2, 0)
        game.grid[3][0] = Tile(2, 3, 0)
        
        result = game.move("down")
        
        assert result.moved == True
        assert result.score_gained == 4
        assert game.grid[3][0].value == 4
    
    def test_no_move_when_blocked(self):
        """Test that no move is made when tiles can't move"""
        game = GameEngine(level=1)
        game._init_grid()
        game.grid[0][0] = Tile(2, 0, 0)
        game.grid[0][1] = Tile(4, 0, 1)
        
        result = game.move("left")
        
        assert result.moved == False
        assert result.score_gained == 0
    
    def test_undo(self):
        """Test undo functionality"""
        game = GameEngine(level=1)
        initial_score = game.score
        
        # Make a move
        game.move("left")
        
        # Undo
        assert game.can_undo() == True
        undone = game.undo()
        assert undone == True
    
    def test_undo_limit(self):
        """Test undo limit"""
        game = GameEngine(level=1)
        game.max_undos = 1
        
        # Use undo
        game.move("left")
        game.undo()
        
        # Should not be able to undo again
        assert game.can_undo() == False
    
    def test_win_condition(self):
        """Test win condition detection"""
        game = GameEngine(level=1)
        game._init_grid()
        game.grid[0][0] = Tile(128, 0, 0)  # Target for level 1
        
        assert game._check_win() == True
    
    def test_game_over_condition(self):
        """Test game over condition"""
        game = GameEngine(level=1)
        game._init_grid()
        
        # Fill grid with non-matching tiles
        values = [2, 4, 2, 4, 4, 2, 4, 2, 2, 4, 2, 4, 4, 2, 4, 2]
        idx = 0
        for row in range(4):
            for col in range(4):
                game.grid[row][col] = Tile(values[idx], row, col)
                idx += 1
        
        assert game._check_game_over() == True
    
    def test_obstacles_in_higher_levels(self):
        """Test that obstacles are placed in higher levels"""
        game = GameEngine(level=5)  # Level 5 has obstacles
        obstacle_count = len(game.obstacles)
        assert obstacle_count > 0
    
    def test_difficulty_settings(self):
        """Test difficulty settings for different levels"""
        level1 = GameEngine(level=1)
        level10 = GameEngine(level=10)
        level20 = GameEngine(level=20)
        
        assert level1.target_value < level10.target_value
        assert level10.target_value < level20.target_value
    
    def test_get_stars(self):
        """Test star calculation"""
        game = GameEngine(level=1)
        game.state = GameState.LEVEL_COMPLETE
        game.score = 256  # High score
        game.undos_used = 0  # No undos
        
        stars = game.get_stars()
        assert stars >= 1
        assert stars <= 3


# =============================================================================
# Particle System Tests
# =============================================================================

class TestParticleSystem:
    """Tests for the particle system"""
    
    def test_particle_initialization(self):
        """Test particle initialization"""
        particle = Particle(
            x=100, y=100,
            vx=5, vy=-5,
            lifetime=60,
            max_lifetime=60,
            size=10,
            color=(255, 255, 255)
        )
        
        assert particle.x == 100
        assert particle.y == 100
        assert particle.is_alive == True
    
    def test_particle_update(self):
        """Test particle update"""
        particle = Particle(
            x=100, y=100,
            vx=5, vy=-5,
            lifetime=60,
            max_lifetime=60,
            size=10,
            color=(255, 255, 255)
        )
        
        initial_x = particle.x
        particle.update()
        
        assert particle.x == initial_x + 5
        assert particle.lifetime == 59
    
    def test_particle_death(self):
        """Test particle dies when lifetime reaches 0"""
        particle = Particle(
            x=100, y=100,
            vx=0, vy=0,
            lifetime=1,
            max_lifetime=1,
            size=10,
            color=(255, 255, 255)
        )
        
        particle.update()
        assert particle.is_alive == False
    
    def test_particle_system_initialization(self):
        """Test particle system initialization"""
        system = ParticleSystem()
        assert len(system.particles) == 0
    
    def test_spawn_explosion(self):
        """Test explosion spawning"""
        system = ParticleSystem()
        system.spawn_explosion(100, 100, (255, 0, 0), count=20)
        
        assert len(system.particles) == 20
    
    def test_spawn_merge_effect(self):
        """Test merge effect spawning"""
        system = ParticleSystem()
        system.spawn_merge_effect(100, 100, (255, 255, 0), 1024)
        
        assert len(system.particles) > 0
    
    def test_particle_update_system(self):
        """Test particle system update"""
        system = ParticleSystem()
        system.spawn_explosion(100, 100, (255, 0, 0), count=5)
        
        initial_count = len(system.particles)
        
        # Update many times to kill particles
        for _ in range(100):
            system.update()
        
        assert len(system.particles) < initial_count
    
    def test_clear_particles(self):
        """Test clearing all particles"""
        system = ParticleSystem()
        system.spawn_explosion(100, 100, (255, 0, 0), count=10)
        
        system.clear()
        
        assert len(system.particles) == 0


# =============================================================================
# Data Manager Tests
# =============================================================================

class TestDataManager:
    """Tests for the data manager"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory"""
        temp_dir = tempfile.mkdtemp()
        original_dir = config.DATA_DIR
        config.DATA_DIR = temp_dir
        config.SAVE_FILE = os.path.join(temp_dir, "save.json")
        config.SETTINGS_FILE = os.path.join(temp_dir, "settings.json")
        config.ACHIEVEMENTS_FILE = os.path.join(temp_dir, "achievements.json")
        
        yield temp_dir
        
        # Cleanup
        config.DATA_DIR = original_dir
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_data_dir):
        """Test data manager initialization"""
        data = DataManager()
        assert data.current_theme == "default"
        assert len(data.achievements) == len(config.ACHIEVEMENTS)
    
    def test_level_progress(self, temp_data_dir):
        """Test level progress tracking"""
        data = DataManager()
        
        # Update progress
        data.update_level_progress(1, True, 1000, 60.0, 3)
        
        progress = data.get_level_progress(1)
        assert progress.completed == True
        assert progress.best_score == 1000
        assert progress.stars == 3
    
    def test_level_unlock(self, temp_data_dir):
        """Test level unlocking"""
        data = DataManager()
        
        # Level 1 should always be unlocked
        assert data.is_level_unlocked(1) == True
        
        # Level 2 should be locked initially
        assert data.is_level_unlocked(2) == False
        
        # Complete level 1
        data.update_level_progress(1, True)
        
        # Level 2 should now be unlocked
        assert data.is_level_unlocked(2) == True
    
    def test_achievement_unlock(self, temp_data_dir):
        """Test achievement unlocking"""
        data = DataManager()
        
        # Unlock achievement
        unlocked = data.unlock_achievement("first_win")
        assert unlocked == True
        
        # Check it's unlocked
        assert data.achievements["first_win"].unlocked == True
        
        # Try to unlock again
        unlocked_again = data.unlock_achievement("first_win")
        assert unlocked_again == False
    
    def test_achievement_progress(self, temp_data_dir):
        """Test achievement progress tracking"""
        data = DataManager()
        
        # Increment progress
        data.check_achievement("persistent", 10)
        
        assert data.achievements["persistent"].progress == 10
    
    def test_theme_setting(self, temp_data_dir):
        """Test theme setting"""
        data = DataManager()
        
        data.set_theme("dark")
        
        assert data.get_theme() == "dark"
    
    def test_audio_settings(self, temp_data_dir):
        """Test audio settings"""
        data = DataManager()
        
        data.set_audio_setting("master_volume", 0.5)
        
        assert data.get_audio_setting("master_volume") == 0.5
    
    def test_statistics_update(self, temp_data_dir):
        """Test statistics update"""
        data = DataManager()
        
        data.update_statistics(total_games_played=1, total_moves=10)
        
        assert data.statistics.total_games_played == 1
        assert data.statistics.total_moves == 10
    
    def test_persistence(self, temp_data_dir):
        """Test data persistence"""
        # Create and save data
        data1 = DataManager()
        data1.update_level_progress(1, True, 500, 30.0, 2)
        data1.save_all()
        
        # Load in new instance
        data2 = DataManager()
        
        progress = data2.get_level_progress(1)
        assert progress.completed == True
        assert progress.best_score == 500


# =============================================================================
# Audio Tests
# =============================================================================

class TestAudioManager:
    """Tests for the audio manager"""
    
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Initialize pygame for audio tests"""
        pygame.init()
        pygame.mixer.init()
        yield
        pygame.mixer.quit()
        pygame.quit()
    
    def test_initialization(self):
        """Test audio manager initialization"""
        audio = AudioManager()
        
        assert audio.master_volume == 0.7
        assert audio.music_volume == 0.5
        assert audio.sfx_volume == 0.8
        assert len(audio.sounds) > 0
    
    def test_volume_settings(self):
        """Test volume setting"""
        audio = AudioManager()
        
        audio.set_master_volume(0.5)
        assert audio.master_volume == 0.5
        
        audio.set_music_volume(0.3)
        assert audio.music_volume == 0.3
        
        audio.set_sfx_volume(0.9)
        assert audio.sfx_volume == 0.9
    
    def test_volume_clamping(self):
        """Test volume is clamped to valid range"""
        audio = AudioManager()
        
        audio.set_master_volume(1.5)
        assert audio.master_volume == 1.0
        
        audio.set_master_volume(-0.5)
        assert audio.master_volume == 0.0
    
    def test_toggle_music(self):
        """Test music toggle"""
        audio = AudioManager()
        
        initial_state = audio.music_enabled
        new_state = audio.toggle_music()
        
        assert new_state == (not initial_state)
    
    def test_toggle_sfx(self):
        """Test SFX toggle"""
        audio = AudioManager()
        
        initial_state = audio.sfx_enabled
        new_state = audio.toggle_sfx()
        
        assert new_state == (not initial_state)


class TestSoundGenerator:
    """Tests for the sound generator"""
    
    def test_tone_generation(self):
        """Test tone generation"""
        gen = SoundGenerator()
        wave = gen.generate_tone(440, 0.1, 0.5, "sine")
        
        assert isinstance(wave, np.ndarray)
        assert len(wave) > 0
    
    def test_chord_generation(self):
        """Test chord generation"""
        gen = SoundGenerator()
        wave = gen.generate_chord([440, 554, 659], 0.1, 0.5)
        
        assert isinstance(wave, np.ndarray)
        assert len(wave) > 0
    
    def test_slide_generation(self):
        """Test frequency slide generation"""
        gen = SoundGenerator()
        wave = gen.generate_slide(400, 800, 0.1, 0.5)
        
        assert isinstance(wave, np.ndarray)
        assert len(wave) > 0


# =============================================================================
# UI Component Tests
# =============================================================================

class TestUIComponents:
    """Tests for UI components"""
    
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Initialize pygame for UI tests"""
        pygame.init()
        yield
        pygame.quit()
    
    def test_button_initialization(self):
        """Test button initialization"""
        screen = pygame.display.set_mode((100, 100))
        font = pygame.font.Font(None, 24)
        style = ButtonStyle(
            normal_color=(100, 100, 100),
            hover_color=(150, 150, 150),
            pressed_color=(50, 50, 50),
            text_color=(255, 255, 255)
        )
        
        button = Button(10, 10, 80, 30, "Test", font, style)
        
        assert button.rect.x == 10
        assert button.rect.y == 10
        assert button.rect.width == 80
        assert button.rect.height == 30
        assert button.text == "Test"
    
    def test_button_hover(self):
        """Test button hover detection"""
        screen = pygame.display.set_mode((100, 100))
        font = pygame.font.Font(None, 24)
        style = ButtonStyle(
            normal_color=(100, 100, 100),
            hover_color=(150, 150, 150),
            pressed_color=(50, 50, 50),
            text_color=(255, 255, 255)
        )
        
        button = Button(10, 10, 80, 30, "Test", font, style)
        
        # Test hover
        clicked = button.update((50, 25), False)
        assert button.is_hovered == True
        
        # Test no hover
        button.update((200, 200), False)
        assert button.is_hovered == False
    
    def test_slider_initialization(self):
        """Test slider initialization"""
        theme = {"empty_cell": (200, 200, 200), "button": (100, 100, 100)}
        slider = Slider(10, 10, 100, 20, 0.0, 1.0, 0.5, theme)
        
        assert slider.value == 0.5
        assert slider.min_value == 0.0
        assert slider.max_value == 1.0
    
    def test_toggle_initialization(self):
        """Test toggle initialization"""
        theme = {"empty_cell": (200, 200, 200), "button": (100, 100, 100), "button_hover": (150, 150, 150)}
        toggle = Toggle(10, 10, 60, 30, True, theme)
        
        assert toggle.state == True
    
    def test_progress_bar(self):
        """Test progress bar"""
        theme = {"empty_cell": (200, 200, 200), "button": (100, 100, 100)}
        progress = ProgressBar(10, 10, 100, 20, theme)
        
        progress.set_progress(0.5)
        assert progress.progress == 0.5
        
        # Test clamping
        progress.set_progress(1.5)
        assert progress.progress == 1.0
        
        progress.set_progress(-0.5)
        assert progress.progress == 0.0
    
    def test_star_rating(self):
        """Test star rating"""
        stars = StarRating(10, 10, 30, max_stars=3)
        
        stars.set_rating(2)
        assert stars.filled_stars == 2
        
        # Test clamping
        stars.set_rating(5)
        assert stars.filled_stars == 3


# =============================================================================
# Configuration Tests
# =============================================================================

class TestConfig:
    """Tests for configuration"""
    
    def test_difficulty_settings_exist(self):
        """Test that difficulty settings exist for all levels"""
        for level in range(1, config.MAX_LEVELS + 1):
            assert level in config.DIFFICULTY_SETTINGS
    
    def test_difficulty_progression(self):
        """Test that difficulty increases with level"""
        level1 = config.DIFFICULTY_SETTINGS[1]
        level20 = config.DIFFICULTY_SETTINGS[20]
        
        assert level1["target"] < level20["target"]
    
    def test_themes_exist(self):
        """Test that themes are properly defined"""
        required_themes = ["default", "dark", "neon"]
        for theme in required_themes:
            assert theme in config.THEMES
    
    def test_theme_structure(self):
        """Test that themes have required keys"""
        required_keys = ["background", "grid_background", "empty_cell", 
                        "text_dark", "text_light", "button", "tile_colors"]
        
        for theme_name, theme in config.THEMES.items():
            for key in required_keys:
                assert key in theme
    
    def test_achievements_exist(self):
        """Test that achievements are defined"""
        assert len(config.ACHIEVEMENTS) > 0
        
        for achievement_id, info in config.ACHIEVEMENTS.items():
            assert "name" in info
            assert "description" in info
            assert "icon" in info


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Initialize pygame"""
        pygame.init()
        pygame.mixer.init()
        yield
        pygame.mixer.quit()
        pygame.quit()
    
    def test_full_game_flow(self):
        """Test a complete game flow"""
        # Create game
        game = GameEngine(level=1)
        
        # Make some moves
        moves = ["left", "right", "up", "down"]
        for move in moves:
            game.move(move)
        
        # Check that game state is valid
        assert game.moves >= 0
        assert game.score >= 0
    
    def test_data_persistence_integration(self, tmp_path):
        """Test data persistence integration"""
        # Set up temp data directory
        original_dir = config.DATA_DIR
        config.DATA_DIR = str(tmp_path)
        config.SAVE_FILE = os.path.join(str(tmp_path), "save.json")
        config.SETTINGS_FILE = os.path.join(str(tmp_path), "settings.json")
        config.ACHIEVEMENTS_FILE = os.path.join(str(tmp_path), "achievements.json")
        
        try:
            # Create data manager and save
            data1 = DataManager()
            data1.update_level_progress(1, True, 1000, 60.0, 3)
            data1.unlock_achievement("first_win")
            data1.set_theme("dark")
            data1.save_all()
            
            # Create new data manager and verify
            data2 = DataManager()
            
            progress = data2.get_level_progress(1)
            assert progress.completed == True
            assert data2.achievements["first_win"].unlocked == True
            assert data2.get_theme() == "dark"
        finally:
            config.DATA_DIR = original_dir


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
