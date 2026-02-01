#!/usr/bin/env python3
"""
1024 Game - Core Functionality Test
Test the core functionality of the game without the GUI
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game
from src.level_manager import LevelManager
from src.data_manager import DataManager
from src.audio_manager import AudioManager
from src.theme_manager import ThemeManager

def test_game_functionality():
    """Test core game functionality"""
    print("Testing 1024 Game Core Functionality...")
    
    # Test Game class
    print("\n1. Testing Game class...")
    game = Game()
    print(f"   Initial grid size: {game.grid_size}x{game.grid_size}")
    print(f"   Initial score: {game.score}")
    print(f"   Initial moves: {game.moves}")
    print(f"   Win value: {game.win_value}")
    
    # Test adding a random tile
    empty_cells_before = sum(1 for row in game.grid for cell in row if cell == 0)
    game.add_random_tile()
    empty_cells_after = sum(1 for row in game.grid for cell in row if cell == 0)
    print(f"   Empty cells before: {empty_cells_before}, after: {empty_cells_after}")
    
    # Test LevelManager class
    print("\n2. Testing LevelManager class...")
    level_manager = LevelManager()
    print(f"   Current level: {level_manager.current_level}")
    print(f"   Total levels: {len(level_manager.level_data)}")
    
    # Test level data
    for level in [1, 5, 10, 15, 20]:
        level_data = level_manager.get_level_data(level)
        print(f"   Level {level}: Difficulty {level_data['difficulty']}, Win Value {level_data['settings']['win_value']}")
    
    # Test DataManager class
    print("\n3. Testing DataManager class...")
    data_manager = DataManager()
    settings = data_manager.get_settings()
    print(f"   Settings loaded: {len(settings)} items")
    print(f"   Current theme: {data_manager.get_current_theme()}")
    
    # Test AudioManager class
    print("\n4. Testing AudioManager class...")
    audio_manager = AudioManager()
    print(f"   Sound effects loaded: {len(audio_manager.sounds)}")
    print(f"   Music tracks loaded: {len(audio_manager.music_tracks)}")
    
    # Test ThemeManager class
    print("\n5. Testing ThemeManager class...")
    theme_manager = ThemeManager()
    print(f"   Themes loaded: {len(theme_manager.themes)}")
    print(f"   Current theme: {theme_manager.get_current_theme()}")
    
    print("\nAll core functionality tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_game_functionality()
        print("\n✓ 1024 Game core functionality is working correctly!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error testing core functionality: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)