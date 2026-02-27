#!/usr/bin/env python3
"""
1024 Game - Data Manager
Handles data persistence, achievements, and settings
"""

import json
import os
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class AchievementType(Enum):
    """Types of achievements"""
    FIRST_WIN = "first_win"
    SCORE_1000 = "score_1000"
    SCORE_5000 = "score_5000"
    SCORE_10000 = "score_10000"
    MERGE_1024 = "merge_1024"
    MERGE_2048 = "merge_2048"
    MERGE_4096 = "merge_4096"
    LEVEL_5 = "level_5"
    LEVEL_10 = "level_10"
    LEVEL_15 = "level_15"
    LEVEL_20 = "level_20"
    COMBO_5 = "combo_5"
    COMBO_10 = "combo_10"
    PERFECT_GAME = "perfect_game"
    SPEED_DEMON = "speed_demon"
    MARATHON = "marathon"


@dataclass
class Achievement:
    """Achievement data"""
    id: str
    name: str
    description: str
    unlocked: bool = False
    unlocked_at: Optional[str] = None
    icon: str = "🏆"
    rarity: str = "common"
    progress: float = 0.0
    max_progress: float = 1.0


class AchievementManager:
    """Manages achievements"""
    
    ACHIEVEMENTS = {
        AchievementType.FIRST_WIN: Achievement(
            "first_win", "初次胜利", "完成任意关卡", icon="🎉", rarity="common"
        ),
        AchievementType.SCORE_1000: Achievement(
            "score_1000", "千分俱乐部", "单局得分达到1000", icon="🥉", rarity="common"
        ),
        AchievementType.SCORE_5000: Achievement(
            "score_5000", "五千分俱乐部", "单局得分达到5000", icon="🥈", rarity="uncommon"
        ),
        AchievementType.SCORE_10000: Achievement(
            "score_10000", "万分俱乐部", "单局得分达到10000", icon="🥇", rarity="rare"
        ),
        AchievementType.MERGE_1024: Achievement(
            "merge_1024", "1024大师", "合并出1024", icon="🔢", rarity="uncommon"
        ),
        AchievementType.MERGE_2048: Achievement(
            "merge_2048", "2048大师", "合并出2048", icon="💎", rarity="rare"
        ),
        AchievementType.MERGE_4096: Achievement(
            "merge_4096", "4096大师", "合并出4096", icon="🌟", rarity="epic"
        ),
        AchievementType.LEVEL_5: Achievement(
            "level_5", "初级玩家", "完成第5关", icon="⭐", rarity="common"
        ),
        AchievementType.LEVEL_10: Achievement(
            "level_10", "中级玩家", "完成第10关", icon="⭐⭐", rarity="uncommon"
        ),
        AchievementType.LEVEL_15: Achievement(
            "level_15", "高级玩家", "完成第15关", icon="⭐⭐⭐", rarity="rare"
        ),
        AchievementType.LEVEL_20: Achievement(
            "level_20", "终极大师", "完成第20关", icon="👑", rarity="legendary"
        ),
        AchievementType.COMBO_5: Achievement(
            "combo_5", "连击新手", "达成5连击", icon="🔥", rarity="common"
        ),
        AchievementType.COMBO_10: Achievement(
            "combo_10", "连击大师", "达成10连击", icon="💥", rarity="rare"
        ),
        AchievementType.PERFECT_GAME: Achievement(
            "perfect_game", "完美游戏", "不浪费任何移动完成关卡", icon="✨", rarity="epic"
        ),
        AchievementType.SPEED_DEMON: Achievement(
            "speed_demon", "速度恶魔", "30秒内完成关卡", icon="⚡", rarity="rare"
        ),
        AchievementType.MARATHON: Achievement(
            "marathon", "马拉松", "连续完成10关", icon="🏃", rarity="epic"
        ),
    }
    
    def __init__(self):
        self.achievements: Dict[AchievementType, Achievement] = {}
        self._load_achievements()
    
    def _load_achievements(self):
        for ach_type, ach_data in self.ACHIEVEMENTS.items():
            self.achievements[ach_type] = Achievement(
                **asdict(ach_data)
            )
    
    def unlock(self, achievement_type: AchievementType) -> bool:
        if achievement_type not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_type]
        if achievement.unlocked:
            return False
        
        achievement.unlocked = True
        achievement.unlocked_at = datetime.now().isoformat()
        achievement.progress = achievement.max_progress
        return True
    
    def update_progress(self, achievement_type: AchievementType, progress: float):
        if achievement_type not in self.achievements:
            return
        
        achievement = self.achievements[achievement_type]
        if not achievement.unlocked:
            achievement.progress = min(achievement.max_progress, progress)
    
    def get_unlocked_count(self) -> int:
        return sum(1 for ach in self.achievements.values() if ach.unlocked)
    
    def get_total_count(self) -> int:
        return len(self.achievements)
    
    def get_achievements_by_rarity(self, rarity: str) -> List[Achievement]:
        return [ach for ach in self.achievements.values() if ach.rarity == rarity]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            ach_type.value: asdict(ach)
            for ach_type, ach in self.achievements.items()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        for ach_type_str, ach_data in data.items():
            try:
                ach_type = AchievementType(ach_type_str)
                if ach_type in self.achievements:
                    self.achievements[ach_type] = Achievement(**ach_data)
            except ValueError:
                pass


@dataclass
class LevelProgress:
    """Level progress data"""
    level_id: int
    completed: bool = False
    best_score: int = 0
    best_time: float = 0.0
    attempts: int = 0
    stars: int = 0
    completed_at: Optional[str] = None


@dataclass
class GameSession:
    """Game session data"""
    session_id: str
    level_id: int
    score: int
    moves: int
    time_elapsed: float
    max_tile: int
    won: bool
    stats: Dict[str, Any]
    played_at: str


class DataManager:
    """Main data manager for persistence"""
    
    def __init__(self):
        self.data_dir = self._get_data_dir()
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.progress_file = os.path.join(self.data_dir, "progress.json")
        self.achievements_file = os.path.join(self.data_dir, "achievements.json")
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        
        self.settings: Dict[str, Any] = {}
        self.level_progress: Dict[int, LevelProgress] = {}
        self.sessions: List[GameSession] = []
        self.achievement_manager = AchievementManager()
        
        self._lock = threading.Lock()
        
        self._load_all_data()
    
    def _get_data_dir(self) -> str:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _load_all_data(self):
        self._load_settings()
        self._load_progress()
        self._load_achievements()
        self._load_sessions()
    
    def _load_settings(self):
        default_settings = {
            "volume": 0.7,
            "music_volume": 0.3,
            "sound_enabled": True,
            "music_enabled": False,
            "particles_enabled": True,
            "theme": "classic",
            "language": "zh",
            "screen_width": 800,
            "screen_height": 600,
            "fullscreen": False,
            "vsync": True,
            "show_fps": False,
            "tutorial_completed": False
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                    for key, value in default_settings.items():
                        if key not in self.settings:
                            self.settings[key] = value
            except (json.JSONDecodeError, IOError):
                self.settings = default_settings.copy()
        else:
            self.settings = default_settings.copy()
    
    def _load_progress(self):
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for level_id, progress_data in data.items():
                        self.level_progress[int(level_id)] = LevelProgress(**progress_data)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _load_achievements(self):
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.achievement_manager.from_dict(data)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _load_sessions(self):
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = [GameSession(**session) for session in data]
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_all(self):
        self._save_settings()
        self._save_progress()
        self._save_achievements()
        self._save_sessions()
    
    def _save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def _save_progress(self):
        try:
            data = {
                str(level_id): asdict(progress)
                for level_id, progress in self.level_progress.items()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def _save_achievements(self):
        try:
            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                json.dump(self.achievement_manager.to_dict(), f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def _save_sessions(self):
        try:
            data = [asdict(session) for session in self.sessions[-100:]]
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        self.settings[key] = value
        self._save_settings()
    
    def get_level_progress(self, level_id: int) -> LevelProgress:
        if level_id not in self.level_progress:
            self.level_progress[level_id] = LevelProgress(level_id=level_id)
        return self.level_progress[level_id]
    
    def update_level_progress(self, level_id: int, won: bool, score: int, 
                             time_elapsed: float, moves: int, max_tile: int):
        progress = self.get_level_progress(level_id)
        progress.attempts += 1
        
        if won:
            progress.completed = True
            progress.completed_at = datetime.now().isoformat()
            
            if score > progress.best_score:
                progress.best_score = score
            
            if progress.best_time == 0 or time_elapsed < progress.best_time:
                progress.best_time = time_elapsed
            
            progress.stars = self._calculate_stars(score, time_elapsed, moves)
        
        self._save_progress()
        return progress
    
    def _calculate_stars(self, score: int, time: float, moves: int) -> int:
        stars = 1
        if score > 5000:
            stars = 2
        if score > 10000 and time < 60:
            stars = 3
        return stars
    
    def add_session(self, level_id: int, score: int, moves: int, 
                   time_elapsed: float, max_tile: int, won: bool, stats: Dict[str, Any]):
        session = GameSession(
            session_id=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{level_id}",
            level_id=level_id,
            score=score,
            moves=moves,
            time_elapsed=time_elapsed,
            max_tile=max_tile,
            won=won,
            stats=stats,
            played_at=datetime.now().isoformat()
        )
        self.sessions.append(session)
        self._save_sessions()
    
    def get_total_score(self) -> int:
        return sum(p.best_score for p in self.level_progress.values())
    
    def get_total_play_time(self) -> float:
        return sum(p.best_time for p in self.level_progress.values())
    
    def get_completed_levels_count(self) -> int:
        return sum(1 for p in self.level_progress.values() if p.completed)
    
    def get_max_level_reached(self) -> int:
        completed = [level_id for level_id, p in self.level_progress.items() if p.completed]
        return max(completed) if completed else 0
    
    def get_sessions_stats(self) -> Dict[str, Any]:
        if not self.sessions:
            return {
                "total_sessions": 0,
                "total_wins": 0,
                "total_losses": 0,
                "average_score": 0,
                "highest_score": 0,
                "total_play_time": 0
            }
        
        total_wins = sum(1 for s in self.sessions if s.won)
        total_score = sum(s.score for s in self.sessions)
        highest_score = max(s.score for s in self.sessions)
        total_play_time = sum(s.time_elapsed for s in self.sessions)
        
        return {
            "total_sessions": len(self.sessions),
            "total_wins": total_wins,
            "total_losses": len(self.sessions) - total_wins,
            "average_score": total_score // len(self.sessions),
            "highest_score": highest_score,
            "total_play_time": total_play_time
        }
    
    def check_and_unlock_achievements(self, level_id: int, score: int, 
                                      max_tile: int, combo: int, time_elapsed: float):
        unlocked = []
        
        if score >= 1000:
            if self.achievement_manager.unlock(AchievementType.SCORE_1000):
                unlocked.append(AchievementType.SCORE_1000)
        
        if score >= 5000:
            if self.achievement_manager.unlock(AchievementType.SCORE_5000):
                unlocked.append(AchievementType.SCORE_5000)
        
        if score >= 10000:
            if self.achievement_manager.unlock(AchievementType.SCORE_10000):
                unlocked.append(AchievementType.SCORE_10000)
        
        if max_tile >= 1024:
            if self.achievement_manager.unlock(AchievementType.MERGE_1024):
                unlocked.append(AchievementType.MERGE_1024)
        
        if max_tile >= 2048:
            if self.achievement_manager.unlock(AchievementType.MERGE_2048):
                unlocked.append(AchievementType.MERGE_2048)
        
        if max_tile >= 4096:
            if self.achievement_manager.unlock(AchievementType.MERGE_4096):
                unlocked.append(AchievementType.MERGE_4096)
        
        if level_id >= 5:
            if self.achievement_manager.unlock(AchievementType.LEVEL_5):
                unlocked.append(AchievementType.LEVEL_5)
        
        if level_id >= 10:
            if self.achievement_manager.unlock(AchievementType.LEVEL_10):
                unlocked.append(AchievementType.LEVEL_10)
        
        if level_id >= 15:
            if self.achievement_manager.unlock(AchievementType.LEVEL_15):
                unlocked.append(AchievementType.LEVEL_15)
        
        if level_id >= 20:
            if self.achievement_manager.unlock(AchievementType.LEVEL_20):
                unlocked.append(AchievementType.LEVEL_20)
        
        if combo >= 5:
            if self.achievement_manager.unlock(AchievementType.COMBO_5):
                unlocked.append(AchievementType.COMBO_5)
        
        if combo >= 10:
            if self.achievement_manager.unlock(AchievementType.COMBO_10):
                unlocked.append(AchievementType.COMBO_10)
        
        if time_elapsed < 30:
            if self.achievement_manager.unlock(AchievementType.SPEED_DEMON):
                unlocked.append(AchievementType.SPEED_DEMON)
        
        if unlocked:
            self._save_achievements()
        
        return unlocked
    
    def reset_progress(self):
        self.level_progress.clear()
        self.sessions.clear()
        self._save_progress()
        self._save_sessions()
