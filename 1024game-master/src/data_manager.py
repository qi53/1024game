#!/usr/bin/env python3
"""
1024 Game - Data Manager
Handles data persistence and storage
"""

import json
import os
import pickle
from typing import Dict, Any, Optional, List
from src.constants import DATA_DIR


class DataManager:
    """Manages all data persistence for the game"""
    
    def __init__(self):
        """Initialize the data manager"""
        # Ensure data directory exists
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', DATA_DIR)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File paths
        self.save_file = os.path.join(self.data_dir, 'save_data.json')
        self.settings_file = os.path.join(self.data_dir, 'settings.json')
        self.stats_file = os.path.join(self.data_dir, 'stats.json')
        self.achievements_file = os.path.join(self.data_dir, 'achievements.json')
        self.themes_file = os.path.join(self.data_dir, 'themes.json')
        
        # Default data
        self.default_settings = {
            'volume': 0.7,
            'sfx_volume': 0.8,
            'music_volume': 0.5,
            'sfx_enabled': True,
            'music_enabled': True,
            'current_theme': 'default',
            'language': 'en',
            'fullscreen': False,
            'show_fps': False,
            'show_grid': True,
            'animation_speed': 1.0,
            'particle_effects': True,
            'auto_save': True,
            'tutorial_completed': False
        }
        
        self.default_stats = {
            'games_played': 0,
            'total_score': 0,
            'high_score': 0,
            'total_moves': 0,
            'total_time': 0,
            'levels_completed': 0,
            'achievements_unlocked': 0,
            'perfect_games': 0,
            'wins': 0,
            'losses': 0,
            'current_streak': 0,
            'best_streak': 0,
            'total_playtime': 0,
            'last_played': None,
            'first_played': None
        }
        
        self.default_achievements = {
            'first_win': {
                'name': 'First Victory',
                'description': 'Win your first game',
                'unlocked': False,
                'unlock_date': None,
                'progress': 0,
                'target': 1
            },
            'speed_runner': {
                'name': 'Speed Runner',
                'description': 'Complete a level in under 2 minutes',
                'unlocked': False,
                'unlock_date': None,
                'progress': 0,
                'target': 1
            },
            'perfect_game': {
                'name': 'Perfect Game',
                'description': 'Win a game without using undo',
                'unlocked': False,
                'unlock_date': None,
                'progress': 0,
                'target': 1
            },
            'high_scorer': {
                'name': 'High Scorer',
                'description': 'Score over 10,000 points in a single game',
                'unlocked': False,
                'unlock_date': None,
                'progress': 0,
                'target': 10000
            },
            'explorer': {
                'name': 'Explorer',
                'description': 'Complete 10 different levels',
                'unlocked': False,
                'unlock_date': None,
                'progress': 0,
                'target': 10
            },
            'master': {
                'name': '1024 Master',
                'description': 'Complete all 20 levels',
                'unlocked': False,
                'unlock_date': None,
                'progress': 0,
                'target': 20
            }
        }
        
        # In-memory data
        self.settings = {}
        self.stats = {}
        self.achievements = {}
        self.save_data = {}
        self.themes = {}
        
        # Load data from files
        self.load_all_data()

    def load_all_data(self) -> None:
        """Load all data from files"""
        self.load_settings()
        self.load_stats()
        self.load_achievements()
        self.load_save_data()
        self.load_themes()

    def save_all_data(self) -> None:
        """Save all data to files"""
        self.save_settings()
        self.save_stats()
        self.save_achievements()
        self.save_save_data()
        self.save_themes()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.settings = {**self.default_settings, **loaded_settings}
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
        except (json.JSONDecodeError, IOError):
            self.settings = self.default_settings.copy()
        
        return self.settings

    def save_settings(self) -> None:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def load_stats(self) -> Dict[str, Any]:
        """Load statistics from file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    loaded_stats = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.stats = {**self.default_stats, **loaded_stats}
            else:
                self.stats = self.default_stats.copy()
                self.save_stats()
        except (json.JSONDecodeError, IOError):
            self.stats = self.default_stats.copy()
        
        return self.stats

    def save_stats(self, stats: Dict[str, Any] = None) -> None:
        """Save statistics to file"""
        if stats:
            self.stats.update(stats)
        
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def load_achievements(self) -> Dict[str, Any]:
        """Load achievements from file"""
        try:
            if os.path.exists(self.achievements_file):
                with open(self.achievements_file, 'r') as f:
                    loaded_achievements = json.load(f)
                # Merge with defaults to ensure all achievements exist
                self.achievements = {**self.default_achievements, **loaded_achievements}
            else:
                self.achievements = self.default_achievements.copy()
                self.save_achievements()
        except (json.JSONDecodeError, IOError):
            self.achievements = self.default_achievements.copy()
        
        return self.achievements

    def save_achievements(self, achievements: Dict[str, Any] = None) -> None:
        """Save achievements to file"""
        if achievements:
            self.achievements.update(achievements)
        
        try:
            with open(self.achievements_file, 'w') as f:
                json.dump(self.achievements, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def load_save_data(self) -> Dict[str, Any]:
        """Load game save data from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    self.save_data = json.load(f)
            else:
                self.save_data = {}
        except (json.JSONDecodeError, IOError):
            self.save_data = {}
        
        return self.save_data

    def save_save_data(self, save_data: Dict[str, Any] = None) -> None:
        """Save game save data to file"""
        if save_data:
            self.save_data.update(save_data)
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.save_data, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def load_themes(self) -> Dict[str, Any]:
        """Load themes from file"""
        try:
            if os.path.exists(self.themes_file):
                with open(self.themes_file, 'r') as f:
                    self.themes = json.load(f)
            else:
                self.themes = {}
        except (json.JSONDecodeError, IOError):
            self.themes = {}
        
        return self.themes

    def save_themes(self, themes: Dict[str, Any] = None) -> None:
        """Save themes to file"""
        if themes:
            self.themes.update(themes)
        
        try:
            with open(self.themes_file, 'w') as f:
                json.dump(self.themes, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings.copy()
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.settings.get('current_theme', 'default')

    def update_setting(self, key: str, value: Any) -> None:
        """Update a specific setting"""
        self.settings[key] = value
        self.save_settings()

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return self.stats.copy()

    def update_stat(self, key: str, value: Any) -> None:
        """Update a specific statistic"""
        self.stats[key] = value
        self.save_stats()

    def get_achievements(self) -> Dict[str, Any]:
        """Get current achievements"""
        return self.achievements.copy()

    def update_achievement(self, key: str, achievement: Dict[str, Any]) -> None:
        """Update a specific achievement"""
        self.achievements[key] = achievement
        self.save_achievements()

    def unlock_achievement(self, key: str) -> bool:
        """Unlock an achievement"""
        if key in self.achievements and not self.achievements[key]['unlocked']:
            import datetime
            self.achievements[key]['unlocked'] = True
            self.achievements[key]['unlock_date'] = datetime.datetime.now().isoformat()
            self.achievements[key]['progress'] = self.achievements[key]['target']
            
            # Update total achievements unlocked
            self.stats['achievements_unlocked'] += 1
            
            self.save_achievements()
            self.save_stats()
            return True
        return False

    def update_achievement_progress(self, key: str, progress: int) -> bool:
        """Update achievement progress"""
        if key in self.achievements and not self.achievements[key]['unlocked']:
            old_progress = self.achievements[key]['progress']
            self.achievements[key]['progress'] = min(progress, self.achievements[key]['target'])
            
            # Check if achievement should be unlocked
            if self.achievements[key]['progress'] >= self.achievements[key]['target']:
                return self.unlock_achievement(key)
            else:
                self.save_achievements()
                return self.achievements[key]['progress'] > old_progress
        return False

    def get_save_data(self) -> Dict[str, Any]:
        """Get current save data"""
        return self.save_data.copy()

    def save_game(self, game_data: Dict[str, Any]) -> None:
        """Save game state"""
        import datetime
        self.save_data['current_game'] = game_data
        self.save_data['save_time'] = datetime.datetime.now().isoformat()
        self.save_save_data()

    def load_game(self) -> Optional[Dict[str, Any]]:
        """Load game state"""
        return self.save_data.get('current_game')

    def delete_save(self) -> None:
        """Delete saved game"""
        if 'current_game' in self.save_data:
            del self.save_data['current_game']
        if 'save_time' in self.save_data:
            del self.save_data['save_time']
        self.save_save_data()

    def has_save(self) -> bool:
        """Check if there's a saved game"""
        return 'current_game' in self.save_data

    def reset_all_data(self) -> None:
        """Reset all data to defaults"""
        self.settings = self.default_settings.copy()
        self.stats = self.default_stats.copy()
        self.achievements = self.default_achievements.copy()
        self.save_data = {}
        self.themes = {}
        
        self.save_all_data()

    def export_data(self, file_path: str) -> bool:
        """Export all data to a file"""
        try:
            export_data = {
                'settings': self.settings,
                'stats': self.stats,
                'achievements': self.achievements,
                'save_data': self.save_data,
                'themes': self.themes,
                'export_date': datetime.datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            return True
        except (IOError, TypeError):
            return False

    def import_data(self, file_path: str) -> bool:
        """Import data from a file"""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            if 'settings' in import_data:
                self.settings = import_data['settings']
            if 'stats' in import_data:
                self.stats = import_data['stats']
            if 'achievements' in import_data:
                self.achievements = import_data['achievements']
            if 'save_data' in import_data:
                self.save_data = import_data['save_data']
            if 'themes' in import_data:
                self.themes = import_data['themes']
            
            self.save_all_data()
            return True
        except (IOError, json.JSONDecodeError, KeyError):
            return False

    def get_data_size(self) -> Dict[str, int]:
        """Get the size of data files in bytes"""
        sizes = {}
        for name, path in [
            ('settings', self.settings_file),
            ('stats', self.stats_file),
            ('achievements', self.achievements_file),
            ('save_data', self.save_file),
            ('themes', self.themes_file)
        ]:
            if os.path.exists(path):
                sizes[name] = os.path.getsize(path)
            else:
                sizes[name] = 0
        return sizes