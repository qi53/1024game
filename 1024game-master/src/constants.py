"""
1024 Game - Constants
Contains all game constants and configuration
"""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Game settings
FPS = 60
GRID_SIZE = 4
WIN_VALUE = 1024

# Colors (default theme)
COLORS = {
    'background': (250, 248, 239),
    'grid_background': (187, 173, 160),
    'empty_cell': (205, 193, 180),
    'text_dark': (119, 110, 101),
    'text_light': (249, 246, 242),
    'button': (143, 122, 102),
    'button_hover': (163, 142, 122),
    'score_bg': (187, 173, 160),
    'tile_colors': {
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
        8192: (60, 58, 50)
    },
    'tile_text_colors': {
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
        8192: (249, 246, 242)
    }
}

# Game states
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_PAUSED = "paused"
GAME_STATE_GAME_OVER = "game_over"
GAME_STATE_WIN = "win"
GAME_STATE_LEVEL_SELECT = "level_select"
GAME_STATE_SETTINGS = "settings"
GAME_STATE_ACHIEVEMENTS = "achievements"
GAME_STATE_TUTORIAL = "tutorial"
GAME_STATE_STATS = "stats"

# UI constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20
GRID_PADDING = 10
CELL_MARGIN = 10
CELL_SIZE = 80
TILE_SIZE = CELL_SIZE
TILE_MARGIN = CELL_MARGIN
ANIMATION_SPEED = 8

# Particle effects
PARTICLE_COUNT = 20
PARTICLE_LIFETIME = 1.0
PARTICLE_SIZE_RANGE = (2, 6)
PARTICLE_SPEED_RANGE = (50, 150)

# Audio
SFX_VOLUME = 0.7
MUSIC_VOLUME = 0.5
AUDIO_CHANNELS = 8

# Level configuration
LEVEL_COUNT = 20
LEVELS_PER_DIFFICULTY = 5
DIFFICULTY_SETTINGS = {
    1: {  # Levels 1-5: Easy
        'win_value': 512,
        'grid_size': 4,
        'initial_tiles': 2,
        'spawn_4_chance': 0.1,
        'time_limit': None,
        'move_limit': None
    },
    2: {  # Levels 6-10: Medium
        'win_value': 1024,
        'grid_size': 4,
        'initial_tiles': 2,
        'spawn_4_chance': 0.15,
        'time_limit': None,
        'move_limit': None
    },
    3: {  # Levels 11-15: Hard
        'win_value': 1024,
        'grid_size': 4,
        'initial_tiles': 2,
        'spawn_4_chance': 0.2,
        'time_limit': 300,  # 5 minutes
        'move_limit': 200
    },
    4: {  # Levels 16-20: Expert
        'win_value': 2048,
        'grid_size': 5,
        'initial_tiles': 3,
        'spawn_4_chance': 0.25,
        'time_limit': 240,  # 4 minutes
        'move_limit': 150
    }
}

# Achievement IDs
ACHIEVEMENT_FIRST_WIN = "first_win"
ACHIEVEMENT_SPEED_RUNNER = "speed_runner"
ACHIEVEMENT_PERFECT_GAME = "perfect_game"
ACHIEVEMENT_HIGH_SCORER = "high_scorer"
ACHIEVEMENT_EXPLORER = "explorer"
ACHIEVEMENT_MASTER = "master"

# File paths
DATA_DIR = "data"
SAVE_FILE = "save_data.json"
THEMES_DIR = "themes"
AUDIO_DIR = "audio"
FONTS_DIR = "fonts"

# Animation durations (in seconds)
ANIMATION_TILE_MOVE = 0.15
ANIMATION_TILE_APPEAR = 0.2
ANIMATION_TILE_MERGE = 0.2
ANIMATION_BUTTON_HOVER = 0.1
ANIMATION_TRANSITION = 0.3