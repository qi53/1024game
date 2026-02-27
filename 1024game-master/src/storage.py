import json
import os
from typing import Any, Dict, List, Optional
from .constants import ACHIEVEMENTS, LEVELS, THEMES


class GameData:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.save_file = os.path.join(data_dir, 'save_data.json')
        self.settings_file = os.path.join(data_dir, 'settings.json')
        self.achievements_file = os.path.join(data_dir, 'achievements.json')
        self.stats_file = os.path.join(data_dir, 'stats.json')
        
        self._data = self._load_file(self.save_file, self._default_save_data())
        self._settings = self._load_file(self.settings_file, self._default_settings())
        self._achievements = self._load_file(self.achievements_file, self._default_achievements())
        self._stats = self._load_file(self.stats_file, self._default_stats())
    
    def _default_save_data(self) -> Dict[str, Any]:
        return {
            'unlocked_levels': [1],
            'completed_levels': [],
            'level_scores': {},
            'level_times': {},
            'total_score': 0,
            'last_played_level': 1,
        }
    
    def _default_settings(self) -> Dict[str, Any]:
        return {
            'theme': 'classic',
            'music_volume': 70,
            'sfx_volume': 80,
            'fullscreen': False,
            'show_hints': True,
            'show_particles': True,
            'animation_speed': 'normal',
        }
    
    def _default_achievements(self) -> Dict[str, Any]:
        return {
            'unlocked': [],
            'progress': {},
        }
    
    def _default_stats(self) -> Dict[str, Any]:
        return {
            'games_played': 0,
            'games_won': 0,
            'total_moves': 0,
            'total_score': 0,
            'best_score': 0,
            'total_time_played': 0,
            'highest_tile': 0,
            'total_merges': 0,
            'max_merges_per_move': 0,
            'undos_used': 0,
            'perfect_games': 0,
        }
    
    def _load_file(self, filepath: str, default: Dict) -> Dict[str, Any]:
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return default.copy()
    
    def _save_file(self, filepath: str, data: Dict) -> bool:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def save_all(self):
        self._save_file(self.save_file, self._data)
        self._save_file(self.settings_file, self._settings)
        self._save_file(self.achievements_file, self._achievements)
        self._save_file(self.stats_file, self._stats)
    
    @property
    def last_played_level(self) -> int:
        return self._data.get('last_played_level', 1)
    
    @last_played_level.setter
    def last_played_level(self, value: int):
        self._data['last_played_level'] = value
        self._save_file(self.save_file, self._data)
    
    @property
    def highest_unlocked_level(self) -> int:
        unlocked = self._data.get('unlocked_levels', [1])
        return max(unlocked) if unlocked else 1
    
    def unlock_level(self, level: int):
        if level not in self._data['unlocked_levels']:
            self._data['unlocked_levels'].append(level)
            self._data['unlocked_levels'].sort()
            self._save_file(self.save_file, self._data)
    
    def complete_level(self, level: int, score: int, time: float):
        if level not in self._data['completed_levels']:
            self._data['completed_levels'].append(level)
            self._data['completed_levels'].sort()
        
        if str(level) not in self._data['level_scores'] or self._data['level_scores'][str(level)] < score:
            self._data['level_scores'][str(level)] = score
        
        if str(level) not in self._data['level_times'] or self._data['level_times'][str(level)] > time:
            self._data['level_times'][str(level)] = time
        
        self._data['total_score'] += score
        
        if level + 1 <= len(LEVELS) and level + 1 not in self._data['unlocked_levels']:
            self.unlock_level(level + 1)
        
        self._save_file(self.save_file, self._data)
    
    def is_level_unlocked(self, level: int) -> bool:
        return level in self._data['unlocked_levels']
    
    def is_level_completed(self, level: int) -> bool:
        return level in self._data['completed_levels']
    
    def get_level_score(self, level: int) -> int:
        return self._data['level_scores'].get(str(level), 0)
    
    def get_level_best_time(self, level: int) -> float:
        return self._data['level_times'].get(str(level), 0)
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        if achievement_id not in self._achievements['unlocked']:
            self._achievements['unlocked'].append(achievement_id)
            self._save_file(self.achievements_file, self._achievements)
            return True
        return False
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        return achievement_id in self._achievements['unlocked']
    
    def get_all_unlocked_achievements(self) -> List[str]:
        return self._achievements['unlocked'].copy()
    
    def update_stats(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._stats:
                if key in ['best_score', 'highest_tile', 'max_merges_per_move']:
                    self._stats[key] = max(self._stats[key], value)
                else:
                    self._stats[key] += value
        self._save_file(self.stats_file, self._stats)
    
    def get_stats(self) -> Dict[str, Any]:
        return self._stats.copy()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        self._settings[key] = value
        self._save_file(self.settings_file, self._settings)
    
    def get_unlocked_themes(self) -> List[str]:
        themes = ['classic']
        completed = len(self._data.get('completed_levels', []))
        if completed >= 5:
            themes.append('dark')
        if completed >= 10:
            themes.append('forest')
        if completed >= 15:
            themes.append('ocean')
        if completed >= 20:
            themes.append('sunset')
        return themes
    
    def reset_all_data(self):
        self._data = self._default_save_data()
        self._settings = self._default_settings()
        self._achievements = self._default_achievements()
        self._stats = self._default_stats()
        self.save_all()
