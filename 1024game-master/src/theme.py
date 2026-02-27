from typing import Dict, Any, Tuple, Optional
import pygame

from .constants import THEMES, BACKGROUND_COLORS, TEXT_COLORS


class ThemeManager:
    def __init__(self, data_storage):
        self.data_storage = data_storage
        self.current_theme_name = self.data_storage.get_setting('theme', 'classic')
        self.themes = THEMES
        self.current_theme = self.themes[self.current_theme_name]
    
    def get_tile_color(self, value: int) -> Tuple[int, int, int]:
        cell_bg = self.current_theme.get('cell_bg', BACKGROUND_COLORS)
        if value in cell_bg:
            return cell_bg[value]
        if value > 2048:
            return (60, 58, 50)
        return cell_bg.get(0, (205, 193, 180))
    
    def get_text_color(self, value: int) -> Tuple[int, int, int]:
        if value >= 8:
            return self.current_theme.get('text_light', (255, 255, 255))
        return self.current_theme.get('text_dark', (119, 110, 101))
    
    def get_background_color(self) -> Tuple[int, int, int]:
        return self.current_theme.get('background', (250, 248, 239))
    
    def get_grid_color(self) -> Tuple[int, int, int]:
        return self.current_theme.get('grid_bg', (187, 173, 160))
    
    def get_empty_color(self) -> Tuple[int, int, int]:
        cell_bg = self.current_theme.get('cell_bg', BACKGROUND_COLORS)
        return cell_bg.get(0, (205, 193, 180))
    
    def get_panel_color(self) -> Tuple[int, int, int]:
        return self.current_theme.get('ui_bg', (255, 255, 255))
    
    def get_accent_color(self) -> Tuple[int, int, int]:
        return (237, 194, 46)
    
    def get_button_color(self) -> Tuple[int, int, int]:
        return self.current_theme.get('grid_bg', (187, 173, 160))
    
    def get_button_hover_color(self) -> Tuple[int, int, int]:
        bg = self.get_button_color()
        return (min(bg[0] + 30, 255), min(bg[1] + 30, 255), min(bg[2] + 30, 255))
    
    def get_text_light(self) -> Tuple[int, int, int]:
        return self.current_theme.get('text_light', (255, 255, 255))
    
    def get_text_dark(self) -> Tuple[int, int, int]:
        return self.current_theme.get('text_dark', (119, 110, 101))
    
    def get_ui_text_color(self) -> Tuple[int, int, int]:
        return self.current_theme.get('ui_text', (70, 70, 70))
    
    def set_theme(self, theme_name: str) -> bool:
        unlocked_themes = self.data_storage.get_unlocked_themes()
        if theme_name in unlocked_themes:
            self.current_theme_name = theme_name
            self.current_theme = self.themes[theme_name]
            self.data_storage.set_setting('theme', theme_name)
            self.data_storage.save_all()
            return True
        return False
    
    def get_all_themes(self) -> Dict[str, Dict[str, Any]]:
        return self.themes
    
    def get_unlocked_themes(self) -> Dict[str, Dict[str, Any]]:
        unlocked = self.data_storage.get_unlocked_themes()
        return {name: self.themes[name] for name in unlocked if name in self.themes}
    
    def is_theme_unlocked(self, theme_name: str) -> bool:
        return theme_name in self.data_storage.get_unlocked_themes()
