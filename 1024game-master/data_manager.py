"""
1024 Game - Data Persistence Module
Handles save/load for game progress, settings, and achievements
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import config


@dataclass
class LevelProgress:
    """Progress for a single level"""
    completed: bool = False
    best_score: int = 0
    best_time: float = 0.0
    attempts: int = 0
    stars: int = 0


@dataclass
class GameStatistics:
    """Overall game statistics"""
    total_games_played: int = 0
    total_time_played: float = 0.0
    highest_score: int = 0
    total_moves: int = 0
    total_merges: int = 0
    biggest_tile: int = 0
    levels_completed: int = 0
    perfect_games: int = 0
    fastest_win_time: float = float('inf')
    longest_game_time: float = 0.0


@dataclass
class AchievementProgress:
    """Achievement data"""
    unlocked: bool = False
    unlocked_at: Optional[str] = None
    progress: int = 0
    target: int = 1


class DataManager:
    """Manages all game data persistence"""
    
    def __init__(self):
        self._ensure_data_dir()
        self.level_progress: Dict[int, LevelProgress] = {}
        self.statistics = GameStatistics()
        self.achievements: Dict[str, AchievementProgress] = {}
        self.settings: Dict[str, Any] = {}
        self.current_theme = "default"
        self.audio_settings = {
            "master_volume": 0.7,
            "music_volume": 0.5,
            "sfx_volume": 0.8,
            "music_enabled": True,
            "sfx_enabled": True,
        }
        self._init_achievements()
        self.load_all()
    
    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(config.DATA_DIR, exist_ok=True)
    
    def _init_achievements(self) -> None:
        """Initialize achievement tracking"""
        for achievement_id in config.ACHIEVEMENTS:
            self.achievements[achievement_id] = AchievementProgress()
        
        # Set specific targets
        self.achievements["persistent"].target = 50
        self.achievements["combo_master"].target = 5
    
    def save_all(self) -> None:
        """Save all game data"""
        self.save_level_progress()
        self.save_statistics()
        self.save_achievements()
        self.save_settings()
    
    def load_all(self) -> None:
        """Load all game data"""
        self.load_level_progress()
        self.load_statistics()
        self.load_achievements()
        self.load_settings()
    
    def save_level_progress(self) -> None:
        """Save level progress to file"""
        data = {
            str(level): {
                "completed": progress.completed,
                "best_score": progress.best_score,
                "best_time": progress.best_time,
                "attempts": progress.attempts,
                "stars": progress.stars,
            }
            for level, progress in self.level_progress.items()
        }
        
        try:
            with open(config.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
    
    def load_level_progress(self) -> None:
        """Load level progress from file"""
        try:
            if os.path.exists(config.SAVE_FILE):
                with open(config.SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for level_str, progress_data in data.items():
                    level = int(level_str)
                    self.level_progress[level] = LevelProgress(
                        completed=progress_data.get("completed", False),
                        best_score=progress_data.get("best_score", 0),
                        best_time=progress_data.get("best_time", 0.0),
                        attempts=progress_data.get("attempts", 0),
                        stars=progress_data.get("stars", 0),
                    )
        except (IOError, json.JSONDecodeError):
            pass
    
    def save_statistics(self) -> None:
        """Save game statistics"""
        stats_file = os.path.join(config.DATA_DIR, "statistics.json")
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.statistics), f, indent=2)
        except IOError:
            pass
    
    def load_statistics(self) -> None:
        """Load game statistics"""
        stats_file = os.path.join(config.DATA_DIR, "statistics.json")
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.statistics = GameStatistics(**data)
        except (IOError, json.JSONDecodeError):
            pass
    
    def save_achievements(self) -> None:
        """Save achievements"""
        try:
            data = {
                achievement_id: {
                    "unlocked": progress.unlocked,
                    "unlocked_at": progress.unlocked_at,
                    "progress": progress.progress,
                    "target": progress.target,
                }
                for achievement_id, progress in self.achievements.items()
            }
            with open(config.ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
    
    def load_achievements(self) -> None:
        """Load achievements"""
        try:
            if os.path.exists(config.ACHIEVEMENTS_FILE):
                with open(config.ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for achievement_id, progress_data in data.items():
                    if achievement_id in self.achievements:
                        self.achievements[achievement_id] = AchievementProgress(
                            unlocked=progress_data.get("unlocked", False),
                            unlocked_at=progress_data.get("unlocked_at"),
                            progress=progress_data.get("progress", 0),
                            target=progress_data.get("target", 1),
                        )
        except (IOError, json.JSONDecodeError):
            pass
    
    def save_settings(self) -> None:
        """Save settings"""
        try:
            data = {
                "theme": self.current_theme,
                "audio": self.audio_settings,
            }
            with open(config.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
    
    def load_settings(self) -> None:
        """Load settings"""
        try:
            if os.path.exists(config.SETTINGS_FILE):
                with open(config.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_theme = data.get("theme", "default")
                self.audio_settings.update(data.get("audio", {}))
        except (IOError, json.JSONDecodeError):
            pass
    
    def get_level_progress(self, level: int) -> LevelProgress:
        """Get progress for a specific level"""
        if level not in self.level_progress:
            self.level_progress[level] = LevelProgress()
        return self.level_progress[level]
    
    def update_level_progress(
        self,
        level: int,
        completed: bool = False,
        score: int = 0,
        time_taken: float = 0.0,
        stars: int = 0
    ) -> None:
        """Update progress for a level"""
        progress = self.get_level_progress(level)
        progress.attempts += 1
        
        if completed:
            progress.completed = True
            if score > progress.best_score:
                progress.best_score = score
            if time_taken < progress.best_time or progress.best_time == 0:
                progress.best_time = time_taken
            if stars > progress.stars:
                progress.stars = stars
        
        self.save_level_progress()
    
    def is_level_unlocked(self, level: int) -> bool:
        """Check if a level is unlocked"""
        if level == 1:
            return True
        # Level is unlocked if previous level is completed
        prev_progress = self.get_level_progress(level - 1)
        return prev_progress.completed
    
    def get_highest_unlocked_level(self) -> int:
        """Get the highest unlocked level"""
        for level in range(1, config.MAX_LEVELS + 1):
            if not self.is_level_unlocked(level):
                return level - 1
        return config.MAX_LEVELS
    
    def update_statistics(self, **kwargs) -> None:
        """Update game statistics"""
        for key, value in kwargs.items():
            if hasattr(self.statistics, key):
                current = getattr(self.statistics, key)
                if isinstance(current, int):
                    setattr(self.statistics, key, current + value)
                elif isinstance(current, float):
                    if key in ["fastest_win_time"]:
                        setattr(self.statistics, key, min(current, value))
                    elif key in ["longest_game_time"]:
                        setattr(self.statistics, key, max(current, value))
                    else:
                        setattr(self.statistics, key, current + value)
        
        self.save_statistics()
    
    def check_achievement(self, achievement_id: str, progress_increment: int = 1) -> bool:
        """Check and update achievement progress"""
        if achievement_id not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_id]
        
        if achievement.unlocked:
            return False
        
        achievement.progress += progress_increment
        
        if achievement.progress >= achievement.target:
            achievement.unlocked = True
            achievement.unlocked_at = datetime.now().isoformat()
            self.save_achievements()
            return True
        
        self.save_achievements()
        return False
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Force unlock an achievement"""
        if achievement_id not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_id]
        
        if achievement.unlocked:
            return False
        
        achievement.unlocked = True
        achievement.unlocked_at = datetime.now().isoformat()
        achievement.progress = achievement.target
        self.save_achievements()
        return True
    
    def get_unlocked_achievements(self) -> List[str]:
        """Get list of unlocked achievement IDs"""
        return [
            aid for aid, progress in self.achievements.items()
            if progress.unlocked
        ]
    
    def set_theme(self, theme: str) -> None:
        """Set current theme"""
        if theme in config.THEMES:
            self.current_theme = theme
            self.save_settings()
    
    def get_theme(self) -> str:
        """Get current theme"""
        return self.current_theme
    
    def set_audio_setting(self, key: str, value: Any) -> None:
        """Set audio setting"""
        if key in self.audio_settings:
            self.audio_settings[key] = value
            self.save_settings()
    
    def get_audio_setting(self, key: str) -> Any:
        """Get audio setting"""
        return self.audio_settings.get(key)
    
    def reset_all_progress(self) -> None:
        """Reset all game progress"""
        self.level_progress.clear()
        self.statistics = GameStatistics()
        self._init_achievements()
        self.save_all()
    
    def export_save_data(self) -> Dict[str, Any]:
        """Export all save data for backup"""
        return {
            "level_progress": {
                str(level): asdict(progress)
                for level, progress in self.level_progress.items()
            },
            "statistics": asdict(self.statistics),
            "achievements": {
                aid: {
                    "unlocked": progress.unlocked,
                    "unlocked_at": progress.unlocked_at,
                    "progress": progress.progress,
                    "target": progress.target,
                }
                for aid, progress in self.achievements.items()
            },
            "settings": {
                "theme": self.current_theme,
                "audio": self.audio_settings,
            },
        }
    
    def import_save_data(self, data: Dict[str, Any]) -> bool:
        """Import save data from backup"""
        try:
            # Import level progress
            for level_str, progress_data in data.get("level_progress", {}).items():
                level = int(level_str)
                self.level_progress[level] = LevelProgress(**progress_data)
            
            # Import statistics
            self.statistics = GameStatistics(**data.get("statistics", {}))
            
            # Import achievements
            for aid, progress_data in data.get("achievements", {}).items():
                if aid in self.achievements:
                    self.achievements[aid] = AchievementProgress(**progress_data)
            
            # Import settings
            settings = data.get("settings", {})
            self.current_theme = settings.get("theme", "default")
            self.audio_settings.update(settings.get("audio", {}))
            
            self.save_all()
            return True
        except Exception:
            return False
