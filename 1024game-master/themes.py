#!/usr/bin/env python3
"""
1024 Game - Theme System
Contains color themes and visual customization
"""

from typing import Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class ColorScheme:
    """Color scheme for a theme"""
    name: str
    background: Tuple[int, int, int]
    grid_background: Tuple[int, int, int]
    grid_border: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    button_normal: Tuple[int, int, int]
    button_hover: Tuple[int, int, int]
    button_click: Tuple[int, int, int]
    button_text: Tuple[int, int, int]
    panel_background: Tuple[int, int, int]
    panel_border: Tuple[int, int, int]
    accent_color: Tuple[int, int, int]
    tile_colors: Dict[int, Tuple[int, int, int]]
    tile_text_colors: Dict[int, Tuple[int, int, int]]


class ThemeManager:
    """Manages color themes"""
    
    THEMES: Dict[str, ColorScheme] = {}
    
    @classmethod
    def _generate_tile_colors(cls, base_color: Tuple[int, int, int]) -> Dict[int, Tuple[int, int, int]]:
        colors = {}
        values = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
        
        for i, value in enumerate(values):
            factor = 0.3 + (i * 0.05)
            color = (
                min(255, int(base_color[0] * factor)),
                min(255, int(base_color[1] * factor)),
                min(255, int(base_color[2] * factor))
            )
            colors[value] = color
        
        return colors
    
    @classmethod
    def _generate_tile_text_colors(cls) -> Dict[int, Tuple[int, int, int]]:
        colors = {}
        values = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
        
        for i, value in enumerate(values):
            if value <= 4:
                colors[value] = (60, 60, 60)
            else:
                colors[value] = (255, 255, 255)
        
        return colors
    
    @classmethod
    def initialize_themes(cls):
        if cls.THEMES:
            return
        
        cls.THEMES["classic"] = ColorScheme(
            name="经典",
            background=(250, 248, 239),
            grid_background=(187, 173, 160),
            grid_border=(205, 193, 180),
            text_color=(119, 110, 101),
            button_normal=(143, 122, 102),
            button_hover=(160, 140, 120),
            button_click=(120, 100, 80),
            button_text=(255, 255, 255),
            panel_background=(238, 228, 218),
            panel_border=(187, 173, 160),
            accent_color=(255, 215, 0),
            tile_colors={
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
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
        
        cls.THEMES["dark"] = ColorScheme(
            name="暗黑",
            background=(30, 30, 30),
            grid_background=(50, 50, 50),
            grid_border=(70, 70, 70),
            text_color=(220, 220, 220),
            button_normal=(60, 60, 60),
            button_hover=(80, 80, 80),
            button_click=(50, 50, 50),
            button_text=(255, 255, 255),
            panel_background=(40, 40, 40),
            panel_border=(60, 60, 60),
            accent_color=(100, 200, 255),
            tile_colors={
                2: (60, 60, 60),
                4: (80, 80, 80),
                8: (100, 150, 200),
                16: (80, 130, 180),
                32: (60, 110, 160),
                64: (40, 90, 140),
                128: (200, 180, 60),
                256: (200, 170, 40),
                512: (200, 160, 20),
                1024: (200, 150, 0),
                2048: (180, 130, 0),
                4096: (40, 40, 40),
                8192: (40, 40, 40),
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
        
        cls.THEMES["ocean"] = ColorScheme(
            name="海洋",
            background=(240, 248, 255),
            grid_background=(100, 149, 237),
            grid_border=(135, 206, 250),
            text_color=(25, 25, 112),
            button_normal=(70, 130, 180),
            button_hover=(100, 149, 237),
            button_click=(65, 105, 225),
            button_text=(255, 255, 255),
            panel_background=(224, 255, 255),
            panel_border=(100, 149, 237),
            accent_color=(0, 191, 255),
            tile_colors={
                2: (224, 255, 255),
                4: (175, 238, 238),
                8: (135, 206, 250),
                16: (100, 149, 237),
                32: (70, 130, 180),
                64: (65, 105, 225),
                128: (0, 191, 255),
                256: (30, 144, 255),
                512: (0, 128, 255),
                1024: (0, 0, 255),
                2048: (0, 0, 205),
                4096: (25, 25, 112),
                8192: (25, 25, 112),
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
        
        cls.THEMES["forest"] = ColorScheme(
            name="森林",
            background=(245, 245, 220),
            grid_background=(107, 142, 35),
            grid_border=(154, 205, 50),
            text_color=(85, 107, 47),
            button_normal=(85, 107, 47),
            button_hover=(107, 142, 35),
            button_click=(69, 90, 38),
            button_text=(255, 255, 255),
            panel_background=(238, 232, 170),
            panel_border=(107, 142, 35),
            accent_color=(50, 205, 50),
            tile_colors={
                2: (238, 232, 170),
                4: (218, 165, 32),
                8: (205, 133, 63),
                16: (210, 105, 30),
                32: (184, 134, 11),
                64: (139, 69, 19),
                128: (50, 205, 50),
                256: (34, 139, 34),
                512: (0, 128, 0),
                1024: (0, 100, 0),
                2048: (85, 107, 47),
                4096: (47, 79, 79),
                8192: (47, 79, 79),
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
        
        cls.THEMES["sunset"] = ColorScheme(
            name="日落",
            background=(255, 248, 220),
            grid_background=(255, 140, 0),
            grid_border=(255, 165, 0),
            text_color=(139, 69, 19),
            button_normal=(255, 140, 0),
            button_hover=(255, 165, 0),
            button_click=(255, 69, 0),
            button_text=(255, 255, 255),
            panel_background=(255, 235, 205),
            panel_border=(255, 140, 0),
            accent_color=(255, 69, 0),
            tile_colors={
                2: (255, 250, 240),
                4: (255, 228, 181),
                8: (255, 200, 150),
                16: (255, 180, 120),
                32: (255, 160, 90),
                64: (255, 140, 60),
                128: (255, 100, 100),
                256: (255, 80, 80),
                512: (255, 60, 60),
                1024: (255, 40, 40),
                2048: (220, 20, 60),
                4096: (139, 0, 0),
                8192: (139, 0, 0),
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
        
        cls.THEMES["neon"] = ColorScheme(
            name="霓虹",
            background=(10, 10, 20),
            grid_background=(20, 20, 40),
            grid_border=(0, 255, 255),
            text_color=(0, 255, 255),
            button_normal=(0, 100, 100),
            button_hover=(0, 150, 150),
            button_click=(0, 80, 80),
            button_text=(0, 255, 255),
            panel_background=(15, 15, 30),
            panel_border=(0, 255, 255),
            accent_color=(255, 0, 255),
            tile_colors={
                2: (20, 20, 40),
                4: (40, 40, 80),
                8: (0, 255, 255),
                16: (0, 200, 255),
                32: (0, 150, 255),
                64: (0, 100, 255),
                128: (255, 0, 255),
                256: (255, 0, 200),
                512: (255, 0, 150),
                1024: (255, 0, 100),
                2048: (255, 50, 50),
                4096: (100, 0, 100),
                8192: (100, 0, 100),
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
        
        cls.THEMES["pastel"] = ColorScheme(
            name="柔和",
            background=(255, 250, 245),
            grid_background=(255, 228, 225),
            grid_border=(255, 218, 185),
            text_color=(105, 105, 105),
            button_normal=(255, 182, 193),
            button_hover=(255, 192, 203),
            button_click=(255, 160, 180),
            button_text=(105, 105, 105),
            panel_background=(255, 240, 245),
            panel_border=(255, 182, 193),
            accent_color=(255, 105, 180),
            tile_colors={
                2: (255, 250, 245),
                4: (255, 240, 245),
                8: (255, 228, 225),
                16: (255, 218, 185),
                32: (255, 200, 180),
                64: (255, 182, 193),
                128: (221, 160, 221),
                256: (216, 191, 216),
                512: (230, 230, 250),
                1024: (176, 224, 230),
                2048: (175, 238, 238),
                4096: (200, 200, 200),
                8192: (200, 200, 200),
            },
            tile_text_colors=cls._generate_tile_text_colors()
        )
    
    @classmethod
    def get_theme(cls, theme_name: str) -> ColorScheme:
        if not cls.THEMES:
            cls.initialize_themes()
        
        return cls.THEMES.get(theme_name, cls.THEMES["classic"])
    
    @classmethod
    def get_all_themes(cls) -> Dict[str, ColorScheme]:
        if not cls.THEMES:
            cls.initialize_themes()
        return cls.THEMES.copy()
    
    @classmethod
    def get_theme_names(cls) -> List[str]:
        if not cls.THEMES:
            cls.initialize_themes()
        return list(cls.THEMES.keys())
    
    @classmethod
    def get_tile_color(cls, theme_name: str, value: int) -> Tuple[int, int, int]:
        theme = cls.get_theme(theme_name)
        return theme.tile_colors.get(value, theme.tile_colors.get(8192, (60, 58, 50)))
    
    @classmethod
    def get_tile_text_color(cls, theme_name: str, value: int) -> Tuple[int, int, int]:
        theme = cls.get_theme(theme_name)
        return theme.tile_text_colors.get(value, (255, 255, 255))


ThemeManager.initialize_themes()


class AnimationStyle:
    """Animation styles for the game"""
    
    @staticmethod
    def ease_in_out(t: float) -> float:
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def ease_out(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in(t: float) -> float:
        return t * t
    
    @staticmethod
    def elastic(t: float) -> float:
        c4 = (2 * 3.14159) / 3
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return -pow(2, 10 * t - 10) * math.sin((t * 10 - 10.75) * c4)
    
    @staticmethod
    def bounce(t: float) -> float:
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375


import math
