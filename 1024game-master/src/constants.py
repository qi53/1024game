import pygame

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60
GAME_TITLE = "1024 Game Deluxe"

GRID_SIZE = 4
CELL_SIZE = 100
CELL_PADDING = 10
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING) // 2
GRID_OFFSET_Y = 180

BACKGROUND_COLORS = {
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
}

TEXT_COLORS = {
    0: (0, 0, 0),
    2: (119, 110, 101),
    4: (119, 110, 101),
}
DEFAULT_TEXT_COLOR = (249, 246, 242)
DEFAULT_TEXT_COLOR_DARK = (119, 110, 101)

FONT_PATH = None
FONT_SIZES = {
    'title': 64,
    'subtitle': 32,
    'button': 28,
    'cell_large': 36,
    'cell_medium': 28,
    'cell_small': 20,
    'normal': 24,
    'small': 18,
}

LEVELS = [
    {'level': 1, 'target': 32, 'grid_size': 3, 'time_limit': 0, 'description': '入门 - 达到32'},
    {'level': 2, 'target': 64, 'grid_size': 3, 'time_limit': 0, 'description': '简单 - 达到64'},
    {'level': 3, 'target': 128, 'grid_size': 3, 'time_limit': 0, 'description': '基础 - 达到128'},
    {'level': 4, 'target': 256, 'grid_size': 4, 'time_limit': 0, 'description': '进阶 - 达到256'},
    {'level': 5, 'target': 512, 'grid_size': 4, 'time_limit': 180, 'description': '挑战 - 限时3分钟'},
    {'level': 6, 'target': 512, 'grid_size': 4, 'time_limit': 0, 'description': '突破 - 达到512'},
    {'level': 7, 'target': 1024, 'grid_size': 4, 'time_limit': 240, 'description': '高手 - 限时4分钟'},
    {'level': 8, 'target': 1024, 'grid_size': 5, 'time_limit': 0, 'description': '大师 - 5x5棋盘'},
    {'level': 9, 'target': 1024, 'grid_size': 5, 'time_limit': 180, 'description': '专家 - 限时3分钟5x5'},
    {'level': 10, 'target': 2048, 'grid_size': 4, 'time_limit': 300, 'description': '传奇 - 达到2048'},
    {'level': 11, 'target': 2048, 'grid_size': 5, 'time_limit': 0, 'description': '精英 - 5x5达到2048'},
    {'level': 12, 'target': 2048, 'grid_size': 6, 'time_limit': 0, 'description': '史诗 - 6x6棋盘'},
    {'level': 13, 'target': 2048, 'grid_size': 5, 'time_limit': 180, 'description': '勇者 - 限时3分钟'},
    {'level': 14, 'target': 4096, 'grid_size': 5, 'time_limit': 300, 'description': '王者 - 达到4096'},
    {'level': 15, 'target': 4096, 'grid_size': 6, 'time_limit': 240, 'description': '至尊 - 6x6限时4分钟'},
    {'level': 16, 'target': 4096, 'grid_size': 6, 'time_limit': 0, 'description': '神话 - 不限时4096'},
    {'level': 17, 'target': 8192, 'grid_size': 5, 'time_limit': 360, 'description': '超神 - 6分钟达到8192'},
    {'level': 18, 'target': 8192, 'grid_size': 6, 'time_limit': 300, 'description': '无敌 - 5分钟达到8192'},
    {'level': 19, 'target': 8192, 'grid_size': 7, 'time_limit': 0, 'description': '传奇 - 7x7棋盘'},
    {'level': 20, 'target': 16384, 'grid_size': 6, 'time_limit': 420, 'description': '终极挑战 - 7分钟达到16384'},
]

ACHIEVEMENTS = [
    {'id': 'first_win', 'name': '初次胜利', 'description': '完成第一关', 'icon': '🏆'},
    {'id': 'level_5', 'name': '挑战者', 'description': '完成第5关', 'icon': '⭐'},
    {'id': 'level_10', 'name': '传奇玩家', 'description': '完成第10关', 'icon': '👑'},
    {'id': 'level_15', 'name': '大师级', 'description': '完成第15关', 'icon': '💎'},
    {'id': 'level_20', 'name': '终极玩家', 'description': '完成所有关卡', 'icon': '🏅'},
    {'id': 'speed_demon', 'name': '速度恶魔', 'description': '在限时关卡中剩余超过30秒完成', 'icon': '⚡'},
    {'id': 'perfect_move', 'name': '完美一步', 'description': '单次移动合并超过3对', 'icon': '🎯'},
    {'id': 'high_score', 'name': '高分王者', 'description': '单局得分超过10000', 'icon': '🔥'},
    {'id': 'no_undo', 'name': '硬核玩家', 'description': '不使用撤销完成一关', 'icon': '💪'},
    {'id': 'collector', 'name': '收藏家', 'description': '解锁所有主题', 'icon': '🎨'},
]

THEMES = {
    'classic': {
        'name': '经典',
        'background': (250, 248, 239),
        'grid_bg': (187, 173, 160),
        'cell_bg': BACKGROUND_COLORS,
        'text_light': DEFAULT_TEXT_COLOR,
        'text_dark': DEFAULT_TEXT_COLOR_DARK,
        'ui_bg': (255, 255, 255),
        'ui_text': (70, 70, 70),
    },
    'dark': {
        'name': '暗黑',
        'background': (30, 30, 40),
        'grid_bg': (50, 50, 60),
        'cell_bg': BACKGROUND_COLORS,
        'text_light': (255, 255, 255),
        'text_dark': (200, 200, 200),
        'ui_bg': (45, 45, 55),
        'ui_text': (220, 220, 230),
    },
    'forest': {
        'name': '森林',
        'background': (230, 245, 230),
        'grid_bg': (100, 150, 100),
        'cell_bg': BACKGROUND_COLORS,
        'text_light': (255, 255, 255),
        'text_dark': (50, 80, 50),
        'ui_bg': (200, 230, 200),
        'ui_text': (40, 70, 40),
    },
    'ocean': {
        'name': '海洋',
        'background': (220, 240, 255),
        'grid_bg': (80, 150, 200),
        'cell_bg': BACKGROUND_COLORS,
        'text_light': (255, 255, 255),
        'text_dark': (40, 80, 120),
        'ui_bg': (200, 230, 255),
        'ui_text': (30, 70, 110),
    },
    'sunset': {
        'name': '日落',
        'background': (255, 230, 210),
        'grid_bg': (220, 130, 80),
        'cell_bg': BACKGROUND_COLORS,
        'text_light': (255, 255, 255),
        'text_dark': (100, 50, 30),
        'ui_bg': (255, 210, 180),
        'ui_text': (90, 40, 20),
    },
}

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 100, 100)
COLOR_GREEN = (100, 255, 100)
COLOR_BLUE = (100, 100, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_TRANSPARENT = (0, 0, 0, 0)

ANIMATION_DURATION = 150
PARTICLE_LIFETIME = 500
PARTICLE_COUNT = 20

MOVE_UP = 0
MOVE_DOWN = 1
MOVE_LEFT = 2
MOVE_RIGHT = 3
