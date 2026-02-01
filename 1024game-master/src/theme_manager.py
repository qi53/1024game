#!/usr/bin/env python3
"""
1024 Game - Theme Manager
Manages visual themes and customization
"""

import os
import json
from typing import Dict, List, Any, Tuple, Optional
from src.constants import COLORS


class Theme:
    """Represents a visual theme"""
    
    def __init__(self, name: str, display_name: str, colors: Dict[str, Any], 
                 fonts: Dict[str, Any] = None, effects: Dict[str, Any] = None):
        """Initialize a theme"""
        self.name = name
        self.display_name = display_name
        self.colors = colors
        self.fonts = fonts or {}
        self.effects = effects or {}
        
    def get_color(self, color_name: str, fallback: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get a color from the theme"""
        return self.colors.get(color_name, fallback)
        
    def get_font(self, font_name: str, fallback: str = None) -> str:
        """Get a font from the theme"""
        return self.fonts.get(font_name, fallback)
        
    def get_effect(self, effect_name: str, fallback: Any = None) -> Any:
        """Get an effect setting from the theme"""
        return self.effects.get(effect_name, fallback)


class ThemeManager:
    """Manages all visual themes"""
    
    def __init__(self):
        """Initialize the theme manager"""
        self.themes: Dict[str, Theme] = {}
        self.current_theme_name = 'default'
        
        # Create default themes
        self._create_default_themes()
        
    def _create_default_themes(self) -> None:
        """Create default themes"""
        # Default theme (classic 1024 style)
        default_colors = {
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
        
        default_fonts = {
            'title': 'Arial',
            'ui': 'Arial',
            'score': 'Arial',
            'tile': 'Arial'
        }
        
        default_effects = {
            'particle_intensity': 1.0,
            'animation_speed': 1.0,
            'glow_enabled': False
        }
        
        self.themes['default'] = Theme(
            'default', 'Classic', default_colors, default_fonts, default_effects
        )
        
        # Dark theme
        dark_colors = {
            'background': (20, 20, 30),
            'grid_background': (40, 40, 50),
            'empty_cell': (60, 60, 70),
            'text_dark': (220, 220, 230),
            'text_light': (240, 240, 250),
            'button': (80, 80, 90),
            'button_hover': (100, 100, 110),
            'score_bg': (40, 40, 50),
            'tile_colors': {
                2: (70, 70, 80),
                4: (90, 90, 100),
                8: (130, 80, 180),
                16: (160, 60, 160),
                32: (190, 50, 140),
                64: (220, 40, 120),
                128: (230, 180, 50),
                256: (240, 160, 40),
                512: (250, 140, 30),
                1024: (255, 120, 20),
                2048: (255, 100, 10),
                4096: (200, 50, 50),
                8192: (180, 30, 30)
            },
            'tile_text_colors': {
                2: (220, 220, 230),
                4: (220, 220, 230),
                8: (240, 240, 250),
                16: (240, 240, 250),
                32: (240, 240, 250),
                64: (240, 240, 250),
                128: (240, 240, 250),
                256: (240, 240, 250),
                512: (240, 240, 250),
                1024: (240, 240, 250),
                2048: (240, 240, 250),
                4096: (240, 240, 250),
                8192: (240, 240, 250)
            }
        }
        
        dark_effects = {
            'particle_intensity': 0.8,
            'animation_speed': 1.2,
            'glow_enabled': True
        }
        
        self.themes['dark'] = Theme(
            'dark', 'Dark Mode', dark_colors, default_fonts, dark_effects
        )
        
        # Ocean theme
        ocean_colors = {
            'background': (230, 240, 250),
            'grid_background': (180, 210, 230),
            'empty_cell': (200, 220, 240),
            'text_dark': (20, 50, 80),
            'text_light': (240, 250, 255),
            'button': (100, 150, 200),
            'button_hover': (120, 170, 220),
            'score_bg': (180, 210, 230),
            'tile_colors': {
                2: (210, 230, 250),
                4: (190, 220, 250),
                8: (100, 180, 230),
                16: (50, 160, 220),
                32: (20, 140, 210),
                64: (10, 120, 200),
                128: (80, 180, 180),
                256: (60, 170, 170),
                512: (40, 160, 160),
                1024: (20, 150, 150),
                2048: (10, 140, 140),
                4096: (5, 100, 120),
                8192: (0, 80, 100)
            },
            'tile_text_colors': {
                2: (20, 50, 80),
                4: (20, 50, 80),
                8: (240, 250, 255),
                16: (240, 250, 255),
                32: (240, 250, 255),
                64: (240, 250, 255),
                128: (240, 250, 255),
                256: (240, 250, 255),
                512: (240, 250, 255),
                1024: (240, 250, 255),
                2048: (240, 250, 255),
                4096: (240, 250, 255),
                8192: (240, 250, 255)
            }
        }
        
        ocean_effects = {
            'particle_intensity': 1.2,
            'animation_speed': 0.9,
            'glow_enabled': False
        }
        
        self.themes['ocean'] = Theme(
            'ocean', 'Ocean', ocean_colors, default_fonts, ocean_effects
        )
        
        # Forest theme
        forest_colors = {
            'background': (240, 250, 230),
            'grid_background': (180, 200, 170),
            'empty_cell': (200, 220, 190),
            'text_dark': (40, 80, 40),
            'text_light': (250, 255, 245),
            'button': (120, 160, 100),
            'button_hover': (140, 180, 120),
            'score_bg': (180, 200, 170),
            'tile_colors': {
                2: (220, 240, 210),
                4: (210, 230, 200),
                8: (180, 220, 120),
                16: (160, 210, 100),
                32: (140, 200, 80),
                64: (120, 190, 60),
                128: (200, 200, 80),
                256: (190, 190, 70),
                512: (180, 180, 60),
                1024: (170, 170, 50),
                2048: (160, 160, 40),
                4096: (100, 120, 50),
                8192: (80, 100, 40)
            },
            'tile_text_colors': {
                2: (40, 80, 40),
                4: (40, 80, 40),
                8: (250, 255, 245),
                16: (250, 255, 245),
                32: (250, 255, 245),
                64: (250, 255, 245),
                128: (250, 255, 245),
                256: (250, 255, 245),
                512: (250, 255, 245),
                1024: (250, 255, 245),
                2048: (250, 255, 245),
                4096: (250, 255, 245),
                8192: (250, 255, 245)
            }
        }
        
        forest_effects = {
            'particle_intensity': 1.0,
            'animation_speed': 0.8,
            'glow_enabled': False
        }
        
        self.themes['forest'] = Theme(
            'forest', 'Forest', forest_colors, default_fonts, forest_effects
        )
        
        # Sunset theme
        sunset_colors = {
            'background': (255, 240, 220),
            'grid_background': (230, 180, 140),
            'empty_cell': (240, 200, 170),
            'text_dark': (100, 50, 20),
            'text_light': (255, 250, 245),
            'button': (200, 140, 100),
            'button_hover': (220, 160, 120),
            'score_bg': (230, 180, 140),
            'tile_colors': {
                2: (250, 230, 210),
                4: (250, 220, 200),
                8: (250, 180, 120),
                16: (250, 160, 100),
                32: (250, 140, 80),
                64: (250, 120, 60),
                128: (250, 200, 100),
                256: (250, 190, 90),
                512: (250, 180, 80),
                1024: (250, 170, 70),
                2048: (250, 160, 60),
                4096: (200, 100, 50),
                8192: (180, 80, 40)
            },
            'tile_text_colors': {
                2: (100, 50, 20),
                4: (100, 50, 20),
                8: (255, 250, 245),
                16: (255, 250, 245),
                32: (255, 250, 245),
                64: (255, 250, 245),
                128: (255, 250, 245),
                256: (255, 250, 245),
                512: (255, 250, 245),
                1024: (255, 250, 245),
                2048: (255, 250, 245),
                4096: (255, 250, 245),
                8192: (255, 250, 245)
            }
        }
        
        sunset_effects = {
            'particle_intensity': 1.3,
            'animation_speed': 1.1,
            'glow_enabled': True
        }
        
        self.themes['sunset'] = Theme(
            'sunset', 'Sunset', sunset_colors, default_fonts, sunset_effects
        )

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get a theme by name"""
        return self.themes.get(name)
        
    def get_current_theme(self) -> Theme:
        """Get the current theme"""
        return self.themes.get(self.current_theme_name, self.themes['default'])
        
    def set_theme(self, name: str) -> bool:
        """Set the current theme"""
        if name in self.themes:
            self.current_theme_name = name
            return True
        return False
        
    def get_all_themes(self) -> List[Theme]:
        """Get all available themes"""
        return list(self.themes.values())
        
    def get_theme_names(self) -> List[str]:
        """Get all theme names"""
        return list(self.themes.keys())
        
    def add_theme(self, theme: Theme) -> None:
        """Add a new theme"""
        self.themes[theme.name] = theme
        
    def remove_theme(self, name: str) -> bool:
        """Remove a theme (can't remove the default theme)"""
        if name == 'default':
            return False
        if name in self.themes:
            del self.themes[name]
            # If the current theme was removed, switch to default
            if self.current_theme_name == name:
                self.current_theme_name = 'default'
            return True
        return False
        
    def create_custom_theme(self, name: str, display_name: str, 
                           base_theme: str = 'default') -> Theme:
        """Create a custom theme based on an existing one"""
        if base_theme not in self.themes:
            base_theme = 'default'
            
        base = self.themes[base_theme]
        
        # Create a copy of the base theme
        colors = {k: v.copy() if isinstance(v, dict) else v for k, v in base.colors.items()}
        fonts = base.fonts.copy()
        effects = base.effects.copy()
        
        custom_theme = Theme(name, display_name, colors, fonts, effects)
        self.add_theme(custom_theme)
        
        return custom_theme
        
    def update_theme_color(self, theme_name: str, color_name: str, 
                         color_value: Tuple[int, int, int]) -> bool:
        """Update a color in a theme"""
        if theme_name not in self.themes:
            return False
            
        theme = self.themes[theme_name]
        theme.colors[color_name] = color_value
        return True
        
    def update_theme_tile_color(self, theme_name: str, tile_value: int, 
                               color_value: Tuple[int, int, int]) -> bool:
        """Update a tile color in a theme"""
        if theme_name not in self.themes:
            return False
            
        theme = self.themes[theme_name]
        if 'tile_colors' not in theme.colors:
            theme.colors['tile_colors'] = {}
            
        theme.colors['tile_colors'][tile_value] = color_value
        return True
        
    def update_theme_effect(self, theme_name: str, effect_name: str, 
                           effect_value: Any) -> bool:
        """Update an effect setting in a theme"""
        if theme_name not in self.themes:
            return False
            
        theme = self.themes[theme_name]
        theme.effects[effect_name] = effect_value
        return True
        
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """Export a theme to a file"""
        if theme_name not in self.themes:
            return False
            
        theme = self.themes[theme_name]
        theme_data = {
            'name': theme.name,
            'display_name': theme.display_name,
            'colors': theme.colors,
            'fonts': theme.fonts,
            'effects': theme.effects
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=2)
            return True
        except (IOError, TypeError):
            return False
            
    def import_theme(self, file_path: str) -> bool:
        """Import a theme from a file"""
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
                
            theme = Theme(
                theme_data['name'],
                theme_data['display_name'],
                theme_data['colors'],
                theme_data.get('fonts', {}),
                theme_data.get('effects', {})
            )
            
            self.add_theme(theme)
            return True
        except (IOError, json.JSONDecodeError, KeyError):
            return False
            
    def get_color(self, color_name: str, fallback: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get a color from the current theme"""
        current_theme = self.get_current_theme()
        return current_theme.get_color(color_name, fallback)
        
    def get_tile_color(self, tile_value: int, fallback: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """Get a tile color from the current theme"""
        current_theme = self.get_current_theme()
        tile_colors = current_theme.colors.get('tile_colors', {})
        return tile_colors.get(tile_value, fallback)
        
    def get_tile_text_color(self, tile_value: int, fallback: Tuple[int, int, int] = (0, 0, 0)) -> Tuple[int, int, int]:
        """Get a tile text color from the current theme"""
        current_theme = self.get_current_theme()
        tile_text_colors = current_theme.colors.get('tile_text_colors', {})
        return tile_text_colors.get(tile_value, fallback)