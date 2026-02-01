#!/usr/bin/env python3
"""
1024 Game - Data Persistence Module
Handles saving and loading game data using JSON
"""

import json
import os
from typing import Any, Dict, Optional
from datetime import datetime

from .config import SAVE_FILE, DEFAULT_SETTINGS, TOTAL_LEVELS, ACHIEVEMENTS


class GameStorage:
    """Manages persistent game data storage"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.data = self._load_default_data()
        self.load()
    
    def _load_default_data(self) -> Dict[str, Any]:
        """Get default game data structure"""
        return {
            "settings": DEFAULT_SETTINGS.copy(),
            "player_stats": {
                "total_games": 0,
                "total_wins": 0,
                "total_score": 0,
                "total_moves": 0,
                "total_time_played": 0,
                "high_score": 0,
                "best_move_count": float('inf'),
                "best_time": float('inf'),
                "current_streak": 0,
                "best_streak": 0,
            },
            "levels": {
                "unlocked": [True] + [False] * (TOTAL_LEVELS - 1),
                "completed": [False] * TOTAL_LEVELS,
                "best_scores": [0] * TOTAL_LEVELS,
                "best_times": [float('inf')] * TOTAL_LEVELS,
                "best_moves": [float('inf')] * TOTAL_LEVELS,
                "stars": [0] * TOTAL_LEVELS,
            },
            "achievements": {
                "unlocked": [],
                "progress": {},
            },
            "tutorial": {
                "completed": False,
                "steps_viewed": [],
            },
            "metadata": {
                "first_played": None,
                "last_played": None,
                "version": "1.0.0",
            },
        }
    
    def load(self) -> bool:
        """Load game data from file"""
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self._merge_data(loaded_data)
                return True
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"Error loading save file: {e}")
        return False
    
    def _merge_data(self, loaded: Dict):
        """Merge loaded data with default structure"""
        defaults = self._load_default_data()
        
        for key in defaults:
            if key in loaded:
                if isinstance(defaults[key], dict):
                    self.data[key] = {**defaults[key], **loaded[key]}
                else:
                    self.data[key] = loaded[key]
            else:
                self.data[key] = defaults[key]
    
    def save(self) -> bool:
        """Save game data to file"""
        try:
            os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
            self.data["metadata"]["last_played"] = datetime.now().isoformat()
            if not self.data["metadata"]["first_played"]:
                self.data["metadata"]["first_played"] = datetime.now().isoformat()
            
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving game data: {e}")
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.data["settings"]
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update settings"""
        self.data["settings"].update(new_settings)
        self.save()
    
    def get_player_stats(self) -> Dict[str, Any]:
        """Get player statistics"""
        return self.data["player_stats"]
    
    def update_player_stats(self, stats: Dict[str, Any]):
        """Update player statistics"""
        self.data["player_stats"].update(stats)
        self.save()
    
    def record_game_played(self, won: bool, score: int, moves: int, time_played: float, level: int):
        """Record a completed game"""
        stats = self.data["player_stats"]
        stats["total_games"] += 1
        stats["total_score"] += score
        stats["total_moves"] += moves
        stats["total_time_played"] += time_played
        
        if won:
            stats["total_wins"] += 1
            stats["current_streak"] += 1
            if stats["current_streak"] > stats["best_streak"]:
                stats["best_streak"] = stats["current_streak"]
            if score > stats["high_score"]:
                stats["high_score"] = score
            if moves < stats["best_move_count"]:
                stats["best_move_count"] = moves
            if time_played < stats["best_time"]:
                stats["best_time"] = time_played
        else:
            stats["current_streak"] = 0
        
        level_data = self.data["levels"]
        if won and level <= TOTAL_LEVELS:
            level_data["completed"][level - 1] = True
            if score > level_data["best_scores"][level - 1]:
                level_data["best_scores"][level - 1] = score
            if time_played < level_data["best_times"][level - 1]:
                level_data["best_times"][level - 1] = time_played
            if moves < level_data["best_moves"][level - 1]:
                level_data["best_moves"][level - 1] = moves
            
            stars = self._calculate_stars(score, time_played, moves, level)
            if stars > level_data["stars"][level - 1]:
                level_data["stars"][level - 1] = stars
            
            if level < TOTAL_LEVELS:
                level_data["unlocked"][level] = True
        
        self.save()
    
    def _calculate_stars(self, score: int, time: float, moves: int, level: int) -> int:
        """Calculate star rating for a level"""
        base_target = level * 500
        time_target = 60 - level * 2
        moves_target = 50 - level
        
        stars = 1
        if score >= base_target * 1.5:
            stars += 1
        if time <= time_target and moves <= moves_target:
            stars += 1
        
        return min(3, stars)
    
    def unlock_level(self, level: int):
        """Unlock a specific level"""
        if 1 <= level <= TOTAL_LEVELS:
            self.data["levels"]["unlocked"][level - 1] = True
            self.save()
    
    def is_level_unlocked(self, level: int) -> bool:
        """Check if a level is unlocked"""
        if 1 <= level <= TOTAL_LEVELS:
            return self.data["levels"]["unlocked"][level - 1]
        return False
    
    def is_level_completed(self, level: int) -> bool:
        """Check if a level is completed"""
        if 1 <= level <= TOTAL_LEVELS:
            return self.data["levels"]["completed"][level - 1]
        return False
    
    def get_level_stars(self, level: int) -> int:
        """Get star rating for a level"""
        if 1 <= level <= TOTAL_LEVELS:
            return self.data["levels"]["stars"][level - 1]
        return 0
    
    def get_levels_data(self) -> Dict[str, Any]:
        """Get all levels data as a dictionary"""
        level_data = {}
        for level in range(1, TOTAL_LEVELS + 1):
            level_str = str(level)
            level_data[level_str] = {
                "completed": self.data["levels"]["completed"][level - 1],
                "unlocked": self.data["levels"]["unlocked"][level - 1],
                "best_score": self.data["levels"]["best_scores"][level - 1],
                "best_time": self.data["levels"]["best_times"][level - 1] if self.data["levels"]["best_times"][level - 1] != float('inf') else None,
                "best_moves": self.data["levels"]["best_moves"][level - 1] if self.data["levels"]["best_moves"][level - 1] != float('inf') else None,
                "stars": self.data["levels"]["stars"][level - 1]
            }
        return level_data
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement"""
        if achievement_id in ACHIEVEMENTS:
            if achievement_id not in self.data["achievements"]["unlocked"]:
                self.data["achievements"]["unlocked"].append(achievement_id)
                self.save()
                return True
        return False
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Check if an achievement is unlocked"""
        return achievement_id in self.data["achievements"]["unlocked"]
    
    def get_unlocked_achievements(self) -> list:
        """Get list of unlocked achievement IDs"""
        return self.data["achievements"]["unlocked"]
    
    def set_tutorial_completed(self):
        """Mark tutorial as completed"""
        self.data["tutorial"]["completed"] = True
        self.save()
    
    def is_tutorial_completed(self) -> bool:
        """Check if tutorial is completed"""
        return self.data["tutorial"]["completed"]
    
    def reset_progress(self):
        """Reset all game progress"""
        self.data = self._load_default_data()
        self.save()
    
    def get_completion_percentage(self) -> float:
        """Calculate overall game completion percentage"""
        completed_levels = sum(self.data["levels"]["completed"])
        unlocked_achievements = len(self.data["achievements"]["unlocked"])
        total_achievements = len(ACHIEVEMENTS)
        
        level_progress = (completed_levels / TOTAL_LEVELS) * 60
        achievement_progress = (unlocked_achievements / total_achievements) * 40
        
        return level_progress + achievement_progress
    
    def export_data(self, filepath: str) -> bool:
        """Export game data to a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def import_data(self, filepath: str) -> bool:
        """Import game data from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
                self._merge_data(imported)
                self.save()
            return True
        except (IOError, json.JSONDecodeError):
            return False
