"""
1024 Game - Pygame Version - Data Manager
数据持久化管理，支持存档、设置、统计数据和主题定制
"""

import json
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from config import DATA_DIR, SAVE_FILE, SETTINGS_FILE, STATS_FILE, Achievement


@dataclass
class GameSaveData:
    """游戏存档数据"""
    current_level: int = 1
    unlocked_levels: int = 1
    achievements: Dict[str, Any] = None
    last_played: float = 0
    
    def __post_init__(self):
        if self.achievements is None:
            self.achievements = {}


@dataclass
class GameSettings:
    """游戏设置"""
    # 显示设置
    fullscreen: bool = False
    screen_width: int = 1280
    screen_height: int = 720
    vsync: bool = True
    
    # 音频设置
    master_volume: float = 1.0
    sfx_volume: float = 0.7
    music_volume: float = 0.5
    mute: bool = False
    
    # 游戏设置
    dark_theme: bool = False
    show_particles: bool = True
    show_animations: bool = True
    auto_save: bool = True
    
    # 控制设置
    key_bindings: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.key_bindings is None:
            self.key_bindings = {
                'up': ['w', 'up'],
                'down': ['s', 'down'],
                'left': ['a', 'left'],
                'right': ['d', 'right'],
                'undo': ['ctrl+z'],
                'pause': ['p', 'esc'],
                'restart': ['r'],
            }


@dataclass
class GameStatistics:
    """游戏统计数据"""
    # 基本统计
    total_games_played: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_play_time: float = 0  # 秒
    
    # 分数统计
    highest_score: int = 0
    total_score_accumulated: int = 0
    average_score: float = 0
    
    # 移动统计
    total_moves: int = 0
    total_merges: int = 0
    max_combo: int = 0
    
    # 方块统计
    max_tile_ever: int = 0
    tiles_merged: Dict[str, int] = None  # 各数值合并次数
    
    # 关卡统计
    level_completions: Dict[str, Any] = None  # 每关完成情况
    fastest_level_clear: Dict[str, float] = None  # 每关最快完成时间
    
    # 历史记录
    recent_games: List[Dict] = None  # 最近游戏记录
    
    def __post_init__(self):
        if self.tiles_merged is None:
            self.tiles_merged = {}
        if self.level_completions is None:
            self.level_completions = {}
        if self.fastest_level_clear is None:
            self.fastest_level_clear = {}
        if self.recent_games is None:
            self.recent_games = []
    
    def add_game_result(self, level: int, won: bool, score: int, 
                       moves: int, time_taken: float, max_tile: int) -> None:
        """添加游戏结果"""
        self.total_games_played += 1
        
        if won:
            self.total_wins += 1
            # 更新关卡完成记录
            level_str = str(level)
            if level_str not in self.level_completions:
                self.level_completions[level_str] = {'count': 0, 'best_score': 0}
            self.level_completions[level_str]['count'] += 1
            self.level_completions[level_str]['best_score'] = max(
                self.level_completions[level_str]['best_score'], score
            )
            
            # 更新最快时间
            if level_str not in self.fastest_level_clear or \
               time_taken < self.fastest_level_clear[level_str]:
                self.fastest_level_clear[level_str] = time_taken
        else:
            self.total_losses += 1
        
        # 更新分数统计
        self.total_score_accumulated += score
        self.highest_score = max(self.highest_score, score)
        self.average_score = self.total_score_accumulated / self.total_games_played
        
        # 更新最大方块
        self.max_tile_ever = max(self.max_tile_ever, max_tile)
        
        # 添加到最近游戏
        game_record = {
            'level': level,
            'won': won,
            'score': score,
            'moves': moves,
            'time': time_taken,
            'max_tile': max_tile,
            'timestamp': time.time()
        }
        self.recent_games.insert(0, game_record)
        if len(self.recent_games) > 50:  # 只保留最近50条
            self.recent_games = self.recent_games[:50]
    
    def add_merge(self, tile_value: int) -> None:
        """记录合并"""
        self.total_merges += 1
        key = str(tile_value)
        self.tiles_merged[key] = self.tiles_merged.get(key, 0) + 1
    
    def add_move(self) -> None:
        """记录移动"""
        self.total_moves += 1
    
    def add_play_time(self, seconds: float) -> None:
        """添加游戏时间"""
        self.total_play_time += seconds


class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self._ensure_data_dir()
        self.save_data = GameSaveData()
        self.settings = GameSettings()
        self.statistics = GameStatistics()
        self._load_all()
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """安全加载JSON文件"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(default, dict):
                        return {**default, **data}
                    return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any) -> bool:
        """安全保存JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving {filepath}: {e}")
            return False
    
    def _load_all(self) -> None:
        """加载所有数据"""
        # 加载存档
        save_dict = self._load_json(SAVE_FILE, {})
        self.save_data = GameSaveData(
            current_level=save_dict.get('current_level', 1),
            unlocked_levels=save_dict.get('unlocked_levels', 1),
            achievements=save_dict.get('achievements', {}),
            last_played=save_dict.get('last_played', 0)
        )
        
        # 加载设置
        settings_dict = self._load_json(SETTINGS_FILE, {})
        self.settings = GameSettings(
            fullscreen=settings_dict.get('fullscreen', False),
            screen_width=settings_dict.get('screen_width', 1280),
            screen_height=settings_dict.get('screen_height', 720),
            vsync=settings_dict.get('vsync', True),
            master_volume=settings_dict.get('master_volume', 1.0),
            sfx_volume=settings_dict.get('sfx_volume', 0.7),
            music_volume=settings_dict.get('music_volume', 0.5),
            mute=settings_dict.get('mute', False),
            dark_theme=settings_dict.get('dark_theme', False),
            show_particles=settings_dict.get('show_particles', True),
            show_animations=settings_dict.get('show_animations', True),
            auto_save=settings_dict.get('auto_save', True),
            key_bindings=settings_dict.get('key_bindings', None)
        )
        
        # 加载统计
        stats_dict = self._load_json(STATS_FILE, {})
        self.statistics = GameStatistics(
            total_games_played=stats_dict.get('total_games_played', 0),
            total_wins=stats_dict.get('total_wins', 0),
            total_losses=stats_dict.get('total_losses', 0),
            total_play_time=stats_dict.get('total_play_time', 0),
            highest_score=stats_dict.get('highest_score', 0),
            total_score_accumulated=stats_dict.get('total_score_accumulated', 0),
            average_score=stats_dict.get('average_score', 0),
            total_moves=stats_dict.get('total_moves', 0),
            total_merges=stats_dict.get('total_merges', 0),
            max_combo=stats_dict.get('max_combo', 0),
            max_tile_ever=stats_dict.get('max_tile_ever', 0),
            tiles_merged=stats_dict.get('tiles_merged', None),
            level_completions=stats_dict.get('level_completions', None),
            fastest_level_clear=stats_dict.get('fastest_level_clear', None),
            recent_games=stats_dict.get('recent_games', None)
        )
    
    def save_all(self) -> bool:
        """保存所有数据"""
        success = True
        
        # 更新最后游戏时间
        self.save_data.last_played = time.time()
        
        # 保存存档
        if not self._save_json(SAVE_FILE, asdict(self.save_data)):
            success = False
        
        # 保存设置
        if not self._save_json(SETTINGS_FILE, asdict(self.settings)):
            success = False
        
        # 保存统计
        if not self._save_json(STATS_FILE, asdict(self.statistics)):
            success = False
        
        return success
    
    # 存档相关方法
    def get_unlocked_levels(self) -> int:
        """获取已解锁关卡数"""
        return self.save_data.unlocked_levels
    
    def unlock_level(self, level: int) -> None:
        """解锁关卡"""
        if level > self.save_data.unlocked_levels:
            self.save_data.unlocked_levels = level
            if self.settings.auto_save:
                self.save_all()
    
    def is_level_unlocked(self, level: int) -> bool:
        """检查关卡是否已解锁"""
        return level <= self.save_data.unlocked_levels
    
    def update_achievement(self, achievement_id: str, unlocked: bool = True) -> None:
        """更新成就状态"""
        self.save_data.achievements[achievement_id] = {
            'unlocked': unlocked,
            'unlocked_at': time.time() if unlocked else None
        }
        if self.settings.auto_save:
            self.save_all()
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """检查成就是否已解锁"""
        ach = self.save_data.achievements.get(achievement_id)
        return ach.get('unlocked', False) if ach else False
    
    # 设置相关方法
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取设置值"""
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """设置设置值"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            if self.settings.auto_save:
                self.save_all()
    
    def toggle_dark_theme(self) -> bool:
        """切换深色主题"""
        self.settings.dark_theme = not self.settings.dark_theme
        if self.settings.auto_save:
            self.save_all()
        return self.settings.dark_theme
    
    def set_volume(self, master: Optional[float] = None, 
                  sfx: Optional[float] = None, 
                  music: Optional[float] = None) -> None:
        """设置音量"""
        if master is not None:
            self.settings.master_volume = max(0, min(1, master))
        if sfx is not None:
            self.settings.sfx_volume = max(0, min(1, sfx))
        if music is not None:
            self.settings.music_volume = max(0, min(1, music))
        if self.settings.auto_save:
            self.save_all()
    
    def get_volumes(self) -> Dict[str, float]:
        """获取音量设置"""
        return {
            'master': self.settings.master_volume,
            'sfx': self.settings.sfx_volume,
            'music': self.settings.music_volume,
            'mute': self.settings.mute
        }
    
    # 统计相关方法
    def record_game_result(self, level: int, won: bool, score: int,
                          moves: int, time_taken: float, max_tile: int) -> None:
        """记录游戏结果"""
        self.statistics.add_game_result(level, won, score, moves, time_taken, max_tile)
        if self.settings.auto_save:
            self.save_all()
    
    def record_merge(self, tile_value: int) -> None:
        """记录合并"""
        self.statistics.add_merge(tile_value)
    
    def record_move(self) -> None:
        """记录移动"""
        self.statistics.add_move()
    
    def add_play_time(self, seconds: float) -> None:
        """添加游戏时间"""
        self.statistics.add_play_time(seconds)
        if self.settings.auto_save:
            self.save_all()
    
    def get_statistics(self) -> GameStatistics:
        """获取统计数据"""
        return self.statistics
    
    def get_level_stats(self, level: int) -> Dict[str, Any]:
        """获取关卡统计"""
        level_str = str(level)
        return {
            'completions': self.statistics.level_completions.get(level_str, {}),
            'fastest_time': self.statistics.fastest_level_clear.get(level_str, None)
        }
    
    # 导入/导出
    def export_data(self, filepath: str) -> bool:
        """导出所有数据"""
        try:
            data = {
                'save_data': asdict(self.save_data),
                'settings': asdict(self.settings),
                'statistics': asdict(self.statistics),
                'export_time': time.time(),
                'version': '2.0.0'
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_data(self, filepath: str) -> bool:
        """导入数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'save_data' in data:
                self.save_data = GameSaveData(**data['save_data'])
            if 'settings' in data:
                self.settings = GameSettings(**data['settings'])
            if 'statistics' in data:
                self.statistics = GameStatistics(**data['statistics'])
            
            self.save_all()
            return True
        except (json.JSONDecodeError, IOError, TypeError) as e:
            print(f"Error importing data: {e}")
            return False
    
    def reset_all_data(self) -> None:
        """重置所有数据"""
        self.save_data = GameSaveData()
        self.settings = GameSettings()
        self.statistics = GameStatistics()
        self.save_all()
    
    def reset_statistics(self) -> None:
        """仅重置统计数据"""
        self.statistics = GameStatistics()
        self.save_all()


# 全局数据管理器实例
_data_manager: Optional[DataManager] = None


def get_data_manager() -> DataManager:
    """获取数据管理器单例"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager
