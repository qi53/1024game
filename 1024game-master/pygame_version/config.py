"""
1024 Game - Pygame Version - Configuration
全局配置和常量定义
"""

import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Tuple, List

# 游戏版本
VERSION = "2.0.0"

# 屏幕设置
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 游戏网格设置
GRID_SIZE = 4
CELL_SIZE = 100
CELL_PADDING = 10
GRID_OFFSET_X = 340
GRID_OFFSET_Y = 110

# 颜色定义
class Colors:
    # 背景色
    BACKGROUND = (250, 248, 239)
    BACKGROUND_DARK = (40, 40, 40)
    
    # 网格背景
    GRID_BG = (187, 173, 160)
    GRID_BG_DARK = (60, 60, 60)
    
    # 空单元格
    EMPTY_CELL = (205, 193, 180)
    EMPTY_CELL_DARK = (80, 80, 80)
    
    # 文字颜色
    TEXT_DARK = (119, 110, 101)
    TEXT_LIGHT = (255, 255, 255)
    TEXT_DARK_THEME = (220, 220, 220)
    
    # 按钮颜色
    BUTTON_BG = (143, 122, 102)
    BUTTON_HOVER = (160, 140, 120)
    BUTTON_TEXT = (255, 255, 255)
    
    # 特殊颜色
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    BRONZE = (205, 127, 50)
    
    # 粒子颜色
    PARTICLE_COLORS = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255),
        (255, 255, 100), (255, 100, 255), (100, 255, 255),
        (255, 200, 100), (200, 100, 255), (100, 255, 200)
    ]

# 数字方块颜色映射
TILE_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (205, 193, 180),
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
    4096: (60, 58, 50),
    8192: (60, 58, 50),
}

TILE_COLORS_DARK: Dict[int, Tuple[int, int, int]] = {
    0: (80, 80, 80),
    2: (120, 110, 100),
    4: (130, 120, 100),
    8: (180, 140, 80),
    16: (190, 120, 70),
    32: (200, 100, 60),
    64: (210, 80, 50),
    128: (180, 160, 80),
    256: (190, 160, 70),
    512: (200, 160, 60),
    1024: (210, 160, 50),
    2048: (220, 160, 40),
    4096: (40, 40, 40),
    8192: (40, 40, 40),
}

# 文字颜色映射
TEXT_COLORS: Dict[int, Tuple[int, int, int]] = {
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (255, 255, 255),
    16: (255, 255, 255),
    32: (255, 255, 255),
    64: (255, 255, 255),
    128: (255, 255, 255),
    256: (255, 255, 255),
    512: (255, 255, 255),
    1024: (255, 255, 255),
    2048: (255, 255, 255),
    4096: (255, 255, 255),
    8192: (255, 255, 255),
}

# 字体大小
FONT_SIZES = {
    'small': 20,
    'normal': 28,
    'medium': 36,
    'large': 48,
    'xlarge': 64,
    'title': 80
}

# 游戏状态
class GameState(Enum):
    MENU = auto()
    LEVEL_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    SETTINGS = auto()
    ACHIEVEMENTS = auto()
    TUTORIAL = auto()

# 移动方向
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

# 难度设置
@dataclass
class LevelConfig:
    level: int
    target_score: int
    spawn_values: List[int]
    spawn_weights: List[float]
    time_limit: int  # 秒，0表示无限制
    obstacle_count: int
    special_tile_chance: float

# 20关配置
LEVEL_CONFIGS: List[LevelConfig] = [
    # 第1-5关：入门难度
    LevelConfig(1, 512, [2], [1.0], 0, 0, 0.0),
    LevelConfig(2, 1024, [2, 4], [0.9, 0.1], 0, 0, 0.0),
    LevelConfig(3, 1024, [2, 4], [0.85, 0.15], 0, 0, 0.0),
    LevelConfig(4, 1024, [2, 4], [0.8, 0.2], 0, 1, 0.0),
    LevelConfig(5, 1024, [2, 4], [0.75, 0.25], 0, 1, 0.05),
    
    # 第6-10关：中等难度
    LevelConfig(6, 2048, [2, 4], [0.7, 0.3], 0, 2, 0.1),
    LevelConfig(7, 2048, [2, 4, 8], [0.7, 0.25, 0.05], 0, 2, 0.15),
    LevelConfig(8, 2048, [2, 4, 8], [0.65, 0.3, 0.05], 180, 3, 0.2),
    LevelConfig(9, 2048, [2, 4, 8], [0.6, 0.35, 0.05], 180, 3, 0.25),
    LevelConfig(10, 2048, [2, 4, 8], [0.55, 0.4, 0.05], 180, 4, 0.3),
    
    # 第11-15关：困难难度
    LevelConfig(11, 4096, [2, 4, 8], [0.5, 0.45, 0.05], 150, 4, 0.35),
    LevelConfig(12, 4096, [2, 4, 8, 16], [0.5, 0.4, 0.08, 0.02], 150, 5, 0.4),
    LevelConfig(13, 4096, [2, 4, 8, 16], [0.45, 0.45, 0.08, 0.02], 120, 5, 0.45),
    LevelConfig(14, 4096, [2, 4, 8, 16], [0.4, 0.5, 0.08, 0.02], 120, 6, 0.5),
    LevelConfig(15, 4096, [2, 4, 8, 16], [0.35, 0.55, 0.08, 0.02], 120, 6, 0.55),
    
    # 第16-20关：专家难度
    LevelConfig(16, 8192, [2, 4, 8, 16], [0.3, 0.6, 0.08, 0.02], 90, 7, 0.6),
    LevelConfig(17, 8192, [2, 4, 8, 16, 32], [0.3, 0.55, 0.1, 0.04, 0.01], 90, 7, 0.65),
    LevelConfig(18, 8192, [2, 4, 8, 16, 32], [0.25, 0.6, 0.1, 0.04, 0.01], 60, 8, 0.7),
    LevelConfig(19, 8192, [2, 4, 8, 16, 32], [0.2, 0.65, 0.1, 0.04, 0.01], 60, 8, 0.75),
    LevelConfig(20, 8192, [2, 4, 8, 16, 32], [0.15, 0.7, 0.1, 0.04, 0.01], 60, 9, 0.8),
]

# 成就定义
class Achievement:
    def __init__(self, id: str, name: str, description: str, icon: str, condition_type: str, condition_value: int):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.condition_type = condition_type
        self.condition_value = condition_value
        self.unlocked = False
        self.unlocked_at = None

ACHIEVEMENTS: List[Achievement] = [
    Achievement("first_win", "初次胜利", "完成第1关", "🏆", "level_complete", 1),
    Achievement("level_5", "进阶玩家", "完成第5关", "🥉", "level_complete", 5),
    Achievement("level_10", "高手", "完成第10关", "🥈", "level_complete", 10),
    Achievement("level_15", "大师", "完成第15关", "🥇", "level_complete", 15),
    Achievement("level_20", "传奇", "完成第20关", "👑", "level_complete", 20),
    Achievement("score_1000", "千分达人", "单局得分超过1000", "💯", "score", 1000),
    Achievement("score_5000", "五千分神手", "单局得分超过5000", "🔥", "score", 5000),
    Achievement("score_10000", "万分传奇", "单局得分超过10000", "⭐", "score", 10000),
    Achievement("speed_demon", "速度恶魔", "在30秒内完成一关", "⚡", "time", 30),
    Achievement("combo_master", "连击大师", "连续合并10次", "🔗", "combo", 10),
    Achievement("tile_2048", "2048达成", "合成2048方块", "🎯", "max_tile", 2048),
    Achievement("tile_4096", "4096达成", "合成4096方块", "🚀", "max_tile", 4096),
    Achievement("tile_8192", "8192达成", "合成8192方块", "💎", "max_tile", 8192),
    Achievement("perfect_game", "完美游戏", "无撤销完成一关", "✨", "no_undo", 1),
    Achievement("persistent", "持之以恒", "累计游戏时间超过1小时", "⏰", "total_time", 3600),
]

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SAVE_FILE = os.path.join(DATA_DIR, 'save_data.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
STATS_FILE = os.path.join(DATA_DIR, 'stats.json')

# 音效设置
SOUND_FREQUENCIES = {
    'move': 440,
    'merge': 660,
    'spawn': 330,
    'win': 880,
    'lose': 220,
    'button': 550,
    'achievement': 770,
}

# 动画设置
ANIMATION_DURATION = 150  # 毫秒
PARTICLE_LIFETIME = 1500  # 毫秒，增加粒子生命周期
TILE_SPAWN_SCALE = 0.1
TILE_MERGE_SCALE = 1.2
