"""
1024 Game - Configuration Module
Contains all game constants and settings
"""

import os

# Window Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
TITLE = "1024 Game - Pygame Edition"

# Grid Settings
GRID_SIZE = 4
CELL_SIZE = 120
CELL_PADDING = 15
GRID_OFFSET_X = 350
GRID_OFFSET_Y = 150

# Animation Settings
ANIMATION_SPEED = 0.15
PARTICLE_LIFETIME = 60
TILE_SPAWN_ANIMATION_DURATION = 20
TILE_MERGE_ANIMATION_DURATION = 15

# Level Settings
MAX_LEVELS = 20
LEVELS_PER_DIFFICULTY = 5

# Difficulty Multipliers
DIFFICULTY_SETTINGS = {
    1: {"spawn_values": [2], "spawn_count": 1, "target": 128, "obstacles": 0},
    2: {"spawn_values": [2], "spawn_count": 1, "target": 256, "obstacles": 0},
    3: {"spawn_values": [2, 4], "spawn_count": 1, "target": 512, "obstacles": 0},
    4: {"spawn_values": [2, 4], "spawn_count": 1, "target": 1024, "obstacles": 0},
    5: {"spawn_values": [2, 4], "spawn_count": 2, "target": 1024, "obstacles": 1},
    6: {"spawn_values": [2, 4], "spawn_count": 2, "target": 2048, "obstacles": 1},
    7: {"spawn_values": [2, 4, 8], "spawn_count": 2, "target": 2048, "obstacles": 2},
    8: {"spawn_values": [2, 4, 8], "spawn_count": 2, "target": 4096, "obstacles": 2},
    9: {"spawn_values": [2, 4, 8], "spawn_count": 2, "target": 4096, "obstacles": 3},
    10: {"spawn_values": [2, 4, 8], "spawn_count": 3, "target": 8192, "obstacles": 3},
    11: {"spawn_values": [2, 4, 8, 16], "spawn_count": 3, "target": 8192, "obstacles": 4},
    12: {"spawn_values": [2, 4, 8, 16], "spawn_count": 3, "target": 16384, "obstacles": 4},
    13: {"spawn_values": [2, 4, 8, 16], "spawn_count": 3, "target": 16384, "obstacles": 5},
    14: {"spawn_values": [2, 4, 8, 16, 32], "spawn_count": 3, "target": 32768, "obstacles": 5},
    15: {"spawn_values": [2, 4, 8, 16, 32], "spawn_count": 4, "target": 32768, "obstacles": 6},
    16: {"spawn_values": [4, 8, 16, 32], "spawn_count": 4, "target": 65536, "obstacles": 6},
    17: {"spawn_values": [4, 8, 16, 32], "spawn_count": 4, "target": 65536, "obstacles": 7},
    18: {"spawn_values": [4, 8, 16, 32, 64], "spawn_count": 4, "target": 131072, "obstacles": 7},
    19: {"spawn_values": [4, 8, 16, 32, 64], "spawn_count": 5, "target": 131072, "obstacles": 8},
    20: {"spawn_values": [8, 16, 32, 64, 128], "spawn_count": 5, "target": 262144, "obstacles": 8},
}

# Colors - Default Theme
THEMES = {
    "default": {
        "background": (250, 248, 239),
        "grid_background": (187, 173, 160),
        "empty_cell": (205, 193, 180),
        "text_dark": (119, 110, 101),
        "text_light": (255, 255, 255),
        "button": (143, 122, 102),
        "button_hover": (160, 140, 120),
        "tile_colors": {
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
            16384: (60, 58, 50),
            32768: (60, 58, 50),
            65536: (60, 58, 50),
            131072: (60, 58, 50),
            262144: (60, 58, 50),
        },
        "obstacle": (80, 80, 80),
    },
    "dark": {
        "background": (40, 40, 50),
        "grid_background": (60, 60, 70),
        "empty_cell": (80, 80, 90),
        "text_dark": (200, 200, 210),
        "text_light": (255, 255, 255),
        "button": (100, 100, 120),
        "button_hover": (120, 120, 140),
        "tile_colors": {
            0: (80, 80, 90),
            2: (100, 100, 120),
            4: (120, 120, 140),
            8: (140, 120, 100),
            16: (160, 140, 80),
            32: (180, 160, 60),
            64: (200, 100, 50),
            128: (220, 180, 40),
            256: (230, 190, 35),
            512: (240, 200, 30),
            1024: (250, 210, 25),
            2048: (255, 220, 20),
            4096: (200, 50, 50),
            8192: (200, 50, 50),
            16384: (200, 50, 50),
            32768: (200, 50, 50),
            65536: (200, 50, 50),
            131072: (200, 50, 50),
            262144: (200, 50, 50),
        },
        "obstacle": (30, 30, 35),
    },
    "neon": {
        "background": (10, 10, 20),
        "grid_background": (30, 30, 50),
        "empty_cell": (20, 20, 35),
        "text_dark": (180, 180, 200),
        "text_light": (255, 255, 255),
        "button": (0, 150, 200),
        "button_hover": (0, 200, 255),
        "tile_colors": {
            0: (20, 20, 35),
            2: (0, 200, 255),
            4: (0, 255, 200),
            8: (100, 255, 100),
            16: (200, 255, 0),
            32: (255, 200, 0),
            64: (255, 100, 0),
            128: (255, 0, 100),
            256: (255, 0, 200),
            512: (200, 0, 255),
            1024: (150, 0, 255),
            2048: (100, 0, 255),
            4096: (255, 255, 255),
            8192: (255, 255, 255),
            16384: (255, 255, 255),
            32768: (255, 255, 255),
            65536: (255, 255, 255),
            131072: (255, 255, 255),
            262144: (255, 255, 255),
        },
        "obstacle": (50, 50, 60),
    },
}

# Fonts
FONT_SIZES = {
    "small": 20,
    "medium": 28,
    "large": 36,
    "xlarge": 48,
    "title": 64,
}

# Data Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SAVE_FILE = os.path.join(DATA_DIR, "save.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, "achievements.json")

# Audio Settings
AUDIO_ENABLED = True
DEFAULT_VOLUME = 0.7
SOUND_EFFECTS_VOLUME = 0.8
MUSIC_VOLUME = 0.5

# Achievement IDs
ACHIEVEMENTS = {
    "first_win": {"name": "First Victory", "description": "Complete level 1", "icon": "🏆"},
    "level_5_master": {"name": "Level 5 Master", "description": "Complete level 5", "icon": "⭐"},
    "level_10_master": {"name": "Level 10 Master", "description": "Complete level 10", "icon": "🌟"},
    "level_15_master": {"name": "Level 15 Master", "description": "Complete level 15", "icon": "💫"},
    "grand_master": {"name": "Grand Master", "description": "Complete all 20 levels", "icon": "👑"},
    "speed_demon": {"name": "Speed Demon", "description": "Complete a level in under 60 seconds", "icon": "⚡"},
    "perfectionist": {"name": "Perfectionist", "description": "Complete a level without undo", "icon": "💎"},
    "combo_master": {"name": "Combo Master", "description": "Make 5 merges in a single move", "icon": "🔥"},
    "millionaire": {"name": "Millionaire", "description": "Score over 1,000,000 points", "icon": "💰"},
    "persistent": {"name": "Persistent", "description": "Play 50 games", "icon": "🎮"},
}
