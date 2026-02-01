#!/usr/bin/env python3
"""
1024 Game - Configuration Module
Contains all game constants and configuration settings
"""

import os
from enum import Enum
from typing import Dict, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SAVE_FILE = os.path.join(DATA_DIR, 'game_data.json')

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

class GameState(Enum):
    MENU = 1
    LEVEL_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    SETTINGS = 5
    ACHIEVEMENTS = 6
    TUTORIAL = 7
    GAME_OVER = 8
    LEVEL_COMPLETE = 9

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "1024 Game"
FPS = 60

SCREEN_WIDTH = WINDOW_WIDTH
SCREEN_HEIGHT = WINDOW_HEIGHT
BG_COLOR = (30, 30, 40)
PRIMARY_COLOR = (100, 149, 237)
SECONDARY_COLOR = (60, 60, 70)
ACCENT_COLOR = (120, 169, 255)

GRID_SIZE = 4
CELL_SIZE = 100
CELL_PADDING = 10
GRID_PADDING = 20

GRID_START_X = (WINDOW_WIDTH - (GRID_SIZE * CELL_SIZE + (GRID_SIZE - 1) * CELL_PADDING + GRID_PADDING * 2)) // 2 + GRID_PADDING
GRID_START_Y = 120

BACKGROUND_COLOR = (30, 30, 40)
GRID_BACKGROUND_COLOR = (60, 60, 70)
TEXT_COLOR = (255, 255, 255)
UI_ACCENT_COLOR = (100, 149, 237)
UI_HOVER_COLOR = (120, 169, 255)

TILE_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (50, 50, 60),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 60, 60),
    8192: (50, 50, 50),
}

TILE_TEXT_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (0, 0, 0),
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
    4096: (249, 246, 242),
    8192: (249, 246, 242),
}

TOTAL_LEVELS = 20
LEVELS_PER_DIFFICULTY = 5

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

LEVEL_CONFIGS: Dict[int, Dict] = {
    1: {"target": 32, "time_limit": 180, "difficulty": Difficulty.EASY, "grid_size": 4},
    2: {"target": 64, "time_limit": 150, "difficulty": Difficulty.EASY, "grid_size": 4},
    3: {"target": 128, "time_limit": 120, "difficulty": Difficulty.EASY, "grid_size": 4},
    4: {"target": 256, "time_limit": 100, "difficulty": Difficulty.EASY, "grid_size": 4},
    5: {"target": 512, "time_limit": 90, "difficulty": Difficulty.EASY, "grid_size": 4},
    6: {"target": 512, "time_limit": 80, "difficulty": Difficulty.MEDIUM, "grid_size": 5},
    7: {"target": 1024, "time_limit": 70, "difficulty": Difficulty.MEDIUM, "grid_size": 5},
    8: {"target": 1024, "time_limit": 60, "difficulty": Difficulty.MEDIUM, "grid_size": 5},
    9: {"target": 2048, "time_limit": 55, "difficulty": Difficulty.MEDIUM, "grid_size": 5},
    10: {"target": 2048, "time_limit": 50, "difficulty": Difficulty.MEDIUM, "grid_size": 5},
    11: {"target": 2048, "time_limit": 45, "difficulty": Difficulty.HARD, "grid_size": 6},
    12: {"target": 4096, "time_limit": 40, "difficulty": Difficulty.HARD, "grid_size": 6},
    13: {"target": 4096, "time_limit": 35, "difficulty": Difficulty.HARD, "grid_size": 6},
    14: {"target": 8192, "time_limit": 30, "difficulty": Difficulty.HARD, "grid_size": 6},
    15: {"target": 8192, "time_limit": 25, "difficulty": Difficulty.HARD, "grid_size": 6},
    16: {"target": 8192, "time_limit": 22, "difficulty": Difficulty.EXPERT, "grid_size": 7},
    17: {"target": 16384, "time_limit": 20, "difficulty": Difficulty.EXPERT, "grid_size": 7},
    18: {"target": 16384, "time_limit": 18, "difficulty": Difficulty.EXPERT, "grid_size": 7},
    19: {"target": 32768, "time_limit": 15, "difficulty": Difficulty.EXPERT, "grid_size": 7},
    20: {"target": 65536, "time_limit": 12, "difficulty": Difficulty.EXPERT, "grid_size": 7},
}

DIFFICULTY_COLORS: Dict[Difficulty, Tuple[int, int, int]] = {
    Difficulty.EASY: (76, 175, 80),
    Difficulty.MEDIUM: (255, 193, 7),
    Difficulty.HARD: (244, 67, 54),
    Difficulty.EXPERT: (156, 39, 176),
}

DIFFICULTY_NAMES: Dict[Difficulty, str] = {
    Difficulty.EASY: "简单",
    Difficulty.MEDIUM: "中等",
    Difficulty.HARD: "困难",
    Difficulty.EXPERT: "专家",
}

THEMES: Dict[str, Dict] = {
    "classic": {
        "name": "经典",
        "background": (30, 30, 40),
        "grid_bg": (60, 60, 70),
        "accent": (100, 149, 237),
    },
    "dark": {
        "name": "暗黑",
        "background": (18, 18, 18),
        "grid_bg": (30, 30, 30),
        "accent": (80, 200, 120),
    },
    "light": {
        "name": "明亮",
        "background": (240, 240, 245),
        "grid_bg": (200, 200, 210),
        "accent": (60, 120, 200),
    },
    "ocean": {
        "name": "海洋",
        "background": (15, 40, 60),
        "grid_bg": (30, 60, 90),
        "accent": (64, 224, 208),
    },
    "sunset": {
        "name": "日落",
        "background": (60, 30, 40),
        "grid_bg": (90, 50, 60),
        "accent": (255, 165, 0),
    },
}

ACHIEVEMENTS: Dict[str, Dict] = {
    "first_win": {
        "name": "初次胜利",
        "description": "完成第一个关卡",
        "icon": "🏆",
        "xp": 100,
    },
    "speed_demon": {
        "name": "速度之魔",
        "description": "在30秒内完成任意关卡",
        "icon": "⚡",
        "xp": 200,
    },
    "perfectionist": {
        "name": "完美主义者",
        "description": "在不使用撤销的情况下完成一个关卡",
        "icon": "⭐",
        "xp": 150,
    },
    "combo_master": {
        "name": "连击大师",
        "description": "在一次移动中合并3对或更多方块",
        "icon": "🔥",
        "xp": 250,
    },
    "explorer": {
        "name": "探索者",
        "description": "完成10个关卡",
        "icon": "🗺️",
        "xp": 300,
    },
    "champion": {
        "name": "冠军",
        "description": "完成所有20个关卡",
        "icon": "👑",
        "xp": 1000,
    },
    "high_scorer": {
        "name": "高分达人",
        "description": "在任意关卡获得10000分以上",
        "icon": "💯",
        "xp": 400,
    },
    "persistent": {
        "name": "坚持不懈",
        "description": "游玩超过100局",
        "icon": "💪",
        "xp": 350,
    },
    "no_mistakes": {
        "name": "零失误",
        "description": "在不产生无效移动的情况下完成一个关卡",
        "icon": "🎯",
        "xp": 200,
    },
    "collector": {
        "name": "收藏家",
        "description": "解锁所有成就",
        "icon": "🎖️",
        "xp": 500,
    },
}

SOUND_EFFECTS = [
    "move", "merge", "level_complete", "game_over", 
    "button_click", "achievement", "countdown", "tutorial"
]

MUSIC_TRACKS = [
    "menu_theme", "game_theme", "victory_theme"
]

ANIMATION_DURATION = 150
PARTICLE_LIFETIME = 500
MAX_PARTICLES = 100

DEFAULT_SETTINGS = {
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "master_volume": 0.8,
    "current_theme": "classic",
    "show_fps": False,
    "show_timer": True,
    "show_hints": True,
    "particles_enabled": True,
    "screen_shake": True,
}
