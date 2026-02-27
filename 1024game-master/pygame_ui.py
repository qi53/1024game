#!/usr/bin/env python3
"""
1024 Game - Pygame UI Manager
Contains all UI components: Main Menu, Level Select, Settings, Achievements
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass

from themes import ThemeManager, ColorScheme
from data_manager import DataManager, AchievementType


class GameState(Enum):
    """Game states"""
    MAIN_MENU = "main_menu"
    LEVEL_SELECT = "level_select"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    ACHIEVEMENTS = "achievements"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"
    TUTORIAL = "tutorial"
    STATS = "stats"


@dataclass
class Button:
    """Button component"""
    rect: pygame.Rect
    text: str
    callback: Callable
    hover: bool = False
    click: bool = False
    enabled: bool = True
    icon: str = ""


@dataclass
class Slider:
    """Slider component"""
    rect: pygame.Rect
    value: float
    min_val: float
    max_val: float
    label: str
    dragging: bool = False


@dataclass
class Toggle:
    """Toggle switch component"""
    rect: pygame.Rect
    value: bool
    label: str


class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def draw_button(surface: pygame.Surface, button: Button, theme: ColorScheme, 
                   fonts: Dict[str, pygame.font.Font]):
        color = theme.button_click if button.click else (
            theme.button_hover if button.hover else theme.button_normal
        )
        
        if not button.enabled:
            color = tuple(c // 2 for c in theme.button_normal)
        
        pygame.draw.rect(surface, color, button.rect, border_radius=10)
        pygame.draw.rect(surface, theme.panel_border, button.rect, 2, border_radius=10)
        
        font = fonts.get("medium", fonts["small"])
        text = button.text
        if button.icon:
            text = f"{button.icon} {button.text}"
        text_surface = font.render(text, True, theme.button_text)
        text_rect = text_surface.get_rect(center=button.rect.center)
        surface.blit(text_surface, text_rect)
    
    @staticmethod
    def draw_slider(surface: pygame.Surface, slider: Slider, theme: ColorScheme,
                   fonts: Dict[str, pygame.font.Font]):
        track_rect = pygame.Rect(
            slider.rect.x, 
            slider.rect.centery - 4,
            slider.rect.width, 
            8
        )
        pygame.draw.rect(surface, theme.panel_border, track_rect, border_radius=4)
        
        fill_width = int((slider.value - slider.min_val) / (slider.max_val - slider.min_val) * slider.rect.width)
        fill_rect = pygame.Rect(
            slider.rect.x,
            slider.rect.centery - 4,
            fill_width,
            8
        )
        pygame.draw.rect(surface, theme.accent_color, fill_rect, border_radius=4)
        
        handle_x = slider.rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 8, slider.rect.centery - 12, 16, 24)
        pygame.draw.rect(surface, theme.button_normal, handle_rect, border_radius=4)
        
        font = fonts["small"]
        label_surface = font.render(slider.label, True, theme.text_color)
        surface.blit(label_surface, (slider.rect.x, slider.rect.y - 20))
        
        value_text = f"{int(slider.value * 100)}%"
        value_surface = font.render(value_text, True, theme.text_color)
        surface.blit(value_surface, (slider.rect.right - value_surface.get_width(), slider.rect.y - 20))
    
    @staticmethod
    def draw_toggle(surface: pygame.Surface, toggle: Toggle, theme: ColorScheme,
                   fonts: Dict[str, pygame.font.Font]):
        font = fonts["small"]
        label_surface = font.render(toggle.label, True, theme.text_color)
        surface.blit(label_surface, (toggle.rect.x, toggle.rect.y))
        
        switch_rect = pygame.Rect(
            toggle.rect.right - 50,
            toggle.rect.y,
            50,
            24
        )
        
        bg_color = theme.accent_color if toggle.value else theme.panel_border
        pygame.draw.rect(surface, bg_color, switch_rect, border_radius=12)
        
        handle_x = switch_rect.right - 22 if toggle.value else switch_rect.left + 2
        handle_rect = pygame.Rect(handle_x, switch_rect.y + 2, 20, 20)
        pygame.draw.rect(surface, theme.button_text, handle_rect, border_radius=10)
    
    @staticmethod
    def draw_panel(surface: pygame.Surface, rect: pygame.Rect, theme: ColorScheme):
        pygame.draw.rect(surface, theme.panel_background, rect, border_radius=15)
        pygame.draw.rect(surface, theme.panel_border, rect, 3, border_radius=15)


class MainMenuUI:
    """Main menu UI"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons: List[Button] = []
        self.title_animation = 0
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 200
        button_height = 50
        start_y = 280
        spacing = 70
        
        button_data = [
            ("开始游戏", "🎮", self._start_game),
            ("关卡选择", "🗺️", self._level_select),
            ("成就", "🏆", self._achievements),
            ("设置", "⚙️", self._settings),
            ("统计数据", "📊", self._stats),
            ("退出", "🚪", self._quit),
        ]
        
        self.buttons = []
        for i, (text, icon, callback) in enumerate(button_data):
            rect = pygame.Rect(
                (self.screen_width - button_width) // 2,
                start_y + i * spacing,
                button_width,
                button_height
            )
            self.buttons.append(Button(rect=rect, text=text, callback=callback, icon=icon))
    
    def _start_game(self):
        return GameState.PLAYING
    
    def _level_select(self):
        return GameState.LEVEL_SELECT
    
    def _achievements(self):
        return GameState.ACHIEVEMENTS
    
    def _settings(self):
        return GameState.SETTINGS
    
    def _stats(self):
        return GameState.STATS
    
    def _quit(self):
        return None
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        self.title_animation += 0.05
        
        for button in self.buttons:
            button.hover = button.rect.collidepoint(mouse_pos) and button.enabled
            
            if mouse_click and button.hover and button.enabled:
                button.click = True
                return button.callback()
            else:
                button.click = False
        
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        surface.fill(theme.background)
        
        title_font = fonts["title"]
        title_text = "1024"
        
        offset_y = math.sin(self.title_animation) * 5
        title_surface = title_font.render(title_text, True, theme.accent_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 120 + offset_y))
        surface.blit(title_surface, title_rect)
        
        subtitle_font = fonts["medium"]
        subtitle_text = "滑动合并数字"
        subtitle_surface = subtitle_font.render(subtitle_text, True, theme.text_color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 180))
        surface.blit(subtitle_surface, subtitle_rect)
        
        for button in self.buttons:
            UIComponents.draw_button(surface, button, theme, fonts)
        
        version_font = fonts["small"]
        version_text = "v2.0 - Pygame Edition"
        version_surface = version_font.render(version_text, True, theme.panel_border)
        surface.blit(version_surface, (10, self.screen_height - 25))


class LevelSelectUI:
    """Level selection UI"""
    
    def __init__(self, screen_width: int, screen_height: int, data_manager: DataManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.data_manager = data_manager
        self.level_buttons: List[Button] = []
        self.scroll_offset = 0
        self.selected_level = 1
        self.back_button: Optional[Button] = None
        self._create_ui()
    
    def _create_ui(self):
        self.back_button = Button(
            rect=pygame.Rect(20, 20, 100, 40),
            text="返回",
            callback=lambda: GameState.MAIN_MENU,
            icon="←"
        )
        
        self.level_buttons = []
        levels_per_row = 5
        button_size = 80
        spacing = 20
        start_x = (self.screen_width - (levels_per_row * (button_size + spacing) - spacing)) // 2
        start_y = 100
        
        for i in range(20):
            level_id = i + 1
            row = i // levels_per_row
            col = i % levels_per_row
            
            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + spacing)
            
            progress = self.data_manager.get_level_progress(level_id)
            
            button = Button(
                rect=pygame.Rect(x, y, button_size, button_size),
                text=str(level_id),
                callback=lambda lid=level_id: self._select_level(lid),
                enabled=level_id <= self._get_max_unlocked_level()
            )
            self.level_buttons.append(button)
    
    def _get_max_unlocked_level(self) -> int:
        max_level = 1
        for level_id in range(1, 21):
            progress = self.data_manager.get_level_progress(level_id)
            if progress.completed:
                max_level = level_id + 1
        return min(20, max_level)
    
    def _select_level(self, level_id: int) -> GameState:
        self.selected_level = level_id
        return GameState.PLAYING
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        if self.back_button:
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.back_button.hover:
                return self.back_button.callback()
        
        for i, button in enumerate(self.level_buttons):
            button.hover = button.rect.collidepoint(mouse_pos) and button.enabled
            if mouse_click and button.hover and button.enabled:
                return button.callback()
        
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        surface.fill(theme.background)
        
        title_font = fonts["large"]
        title_text = "关卡选择"
        title_surface = title_font.render(title_text, True, theme.text_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        if self.back_button:
            UIComponents.draw_button(surface, self.back_button, theme, fonts)
        
        for i, button in enumerate(self.level_buttons):
            level_id = i + 1
            progress = self.data_manager.get_level_progress(level_id)
            
            color = theme.button_normal
            if progress.completed:
                color = theme.accent_color
            elif not button.enabled:
                color = theme.panel_border
            
            pygame.draw.rect(surface, color, button.rect, border_radius=10)
            pygame.draw.rect(surface, theme.panel_border, button.rect, 2, border_radius=10)
            
            font = fonts["medium"]
            text_surface = font.render(str(level_id), True, theme.button_text)
            text_rect = text_surface.get_rect(center=button.rect.center)
            surface.blit(text_surface, text_rect)
            
            if progress.stars > 0:
                star_font = fonts["small"]
                star_text = "⭐" * progress.stars
                star_surface = star_font.render(star_text, True, theme.accent_color)
                star_rect = star_surface.get_rect(centerx=button.rect.centerx, bottom=button.rect.bottom - 5)
                surface.blit(star_surface, star_rect)
        
        self._draw_level_info(surface, theme, fonts)
    
    def _draw_level_info(self, surface: pygame.Surface, theme: ColorScheme, 
                        fonts: Dict[str, pygame.font.Font]):
        info_rect = pygame.Rect(20, self.screen_height - 100, self.screen_width - 40, 80)
        UIComponents.draw_panel(surface, info_rect, theme)
        
        font = fonts["small"]
        info_text = "点击关卡开始游戏 | ⭐ 表示关卡评分 | 灰色关卡需要先完成前置关卡"
        info_surface = font.render(info_text, True, theme.text_color)
        info_rect_text = info_surface.get_rect(center=info_rect.center)
        surface.blit(info_surface, info_rect_text)
    
    def get_selected_level(self) -> int:
        return self.selected_level


class SettingsUI:
    """Settings UI"""
    
    def __init__(self, screen_width: int, screen_height: int, data_manager: DataManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.data_manager = data_manager
        self.sliders: List[Slider] = []
        self.toggles: List[Toggle] = []
        self.back_button: Optional[Button] = None
        self.theme_buttons: List[Button] = []
        self._create_ui()
    
    def _create_ui(self):
        self.back_button = Button(
            rect=pygame.Rect(20, 20, 100, 40),
            text="返回",
            callback=lambda: GameState.MAIN_MENU,
            icon="←"
        )
        
        start_y = 100
        slider_width = 300
        slider_height = 40
        
        self.sliders = [
            Slider(
                rect=pygame.Rect((self.screen_width - slider_width) // 2, start_y, slider_width, slider_height),
                value=self.data_manager.get_setting("volume", 0.7),
                min_val=0.0,
                max_val=1.0,
                label="音效音量"
            ),
            Slider(
                rect=pygame.Rect((self.screen_width - slider_width) // 2, start_y + 80, slider_width, slider_height),
                value=self.data_manager.get_setting("music_volume", 0.3),
                min_val=0.0,
                max_val=1.0,
                label="音乐音量"
            ),
        ]
        
        toggle_start_y = start_y + 180
        self.toggles = [
            Toggle(
                rect=pygame.Rect((self.screen_width - 250) // 2, toggle_start_y, 250, 30),
                value=self.data_manager.get_setting("sound_enabled", True),
                label="启用音效"
            ),
            Toggle(
                rect=pygame.Rect((self.screen_width - 250) // 2, toggle_start_y + 50, 250, 30),
                value=self.data_manager.get_setting("music_enabled", False),
                label="启用音乐"
            ),
            Toggle(
                rect=pygame.Rect((self.screen_width - 250) // 2, toggle_start_y + 100, 250, 30),
                value=self.data_manager.get_setting("particles_enabled", True),
                label="启用粒子特效"
            ),
            Toggle(
                rect=pygame.Rect((self.screen_width - 250) // 2, toggle_start_y + 150, 250, 30),
                value=self.data_manager.get_setting("show_fps", False),
                label="显示帧率"
            ),
        ]
        
        theme_names = ThemeManager.get_theme_names()
        button_width = 80
        spacing = 10
        total_width = len(theme_names) * (button_width + spacing) - spacing
        start_x = (self.screen_width - total_width) // 2
        
        self.theme_buttons = []
        current_theme = self.data_manager.get_setting("theme", "classic")
        
        for i, theme_name in enumerate(theme_names):
            theme = ThemeManager.get_theme(theme_name)
            button = Button(
                rect=pygame.Rect(start_x + i * (button_width + spacing), toggle_start_y + 220, button_width, 40),
                text=theme.name,
                callback=lambda tn=theme_name: self._set_theme(tn)
            )
            if theme_name == current_theme:
                button.hover = True
            self.theme_buttons.append(button)
    
    def _set_theme(self, theme_name: str):
        self.data_manager.set_setting("theme", theme_name)
        return None
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool, 
               mouse_down: bool) -> Optional[GameState]:
        if self.back_button:
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.back_button.hover:
                self._save_settings()
                return self.back_button.callback()
        
        for slider in self.sliders:
            if mouse_down and slider.rect.collidepoint(mouse_pos):
                slider.dragging = True
            
            if not mouse_down:
                slider.dragging = False
            
            if slider.dragging:
                relative_x = mouse_pos[0] - slider.rect.x
                slider.value = slider.min_val + (relative_x / slider.rect.width) * (slider.max_val - slider.min_val)
                slider.value = max(slider.min_val, min(slider.max_val, slider.value))
        
        for toggle in self.toggles:
            toggle_rect = pygame.Rect(toggle.rect.right - 50, toggle.rect.y, 50, 24)
            if mouse_click and toggle_rect.collidepoint(mouse_pos):
                toggle.value = not toggle.value
        
        for button in self.theme_buttons:
            button.hover = button.rect.collidepoint(mouse_pos)
            if mouse_click and button.hover:
                button.callback()
        
        return None
    
    def _save_settings(self):
        self.data_manager.set_setting("volume", self.sliders[0].value)
        self.data_manager.set_setting("music_volume", self.sliders[1].value)
        self.data_manager.set_setting("sound_enabled", self.toggles[0].value)
        self.data_manager.set_setting("music_enabled", self.toggles[1].value)
        self.data_manager.set_setting("particles_enabled", self.toggles[2].value)
        self.data_manager.set_setting("show_fps", self.toggles[3].value)
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        surface.fill(theme.background)
        
        title_font = fonts["large"]
        title_text = "设置"
        title_surface = title_font.render(title_text, True, theme.text_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        if self.back_button:
            UIComponents.draw_button(surface, self.back_button, theme, fonts)
        
        for slider in self.sliders:
            UIComponents.draw_slider(surface, slider, theme, fonts)
        
        for toggle in self.toggles:
            UIComponents.draw_toggle(surface, toggle, theme, fonts)
        
        theme_label = fonts["small"].render("主题选择:", True, theme.text_color)
        surface.blit(theme_label, (self.theme_buttons[0].rect.x, self.theme_buttons[0].rect.y - 25))
        
        current_theme = self.data_manager.get_setting("theme", "classic")
        for i, button in enumerate(self.theme_buttons):
            theme_names = ThemeManager.get_theme_names()
            is_current = theme_names[i] == current_theme
            
            color = theme.accent_color if is_current else theme.button_normal
            pygame.draw.rect(surface, color, button.rect, border_radius=5)
            pygame.draw.rect(surface, theme.panel_border, button.rect, 2, border_radius=5)
            
            font = fonts["small"]
            text_surface = font.render(button.text, True, theme.button_text)
            text_rect = text_surface.get_rect(center=button.rect.center)
            surface.blit(text_surface, text_rect)


class AchievementsUI:
    """Achievements UI"""
    
    def __init__(self, screen_width: int, screen_height: int, data_manager: DataManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.data_manager = data_manager
        self.back_button: Optional[Button] = None
        self.scroll_offset = 0
        self._create_ui()
    
    def _create_ui(self):
        self.back_button = Button(
            rect=pygame.Rect(20, 20, 100, 40),
            text="返回",
            callback=lambda: GameState.MAIN_MENU,
            icon="←"
        )
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool,
               scroll_y: int = 0) -> Optional[GameState]:
        if self.back_button:
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.back_button.hover:
                return self.back_button.callback()
        
        self.scroll_offset += scroll_y
        self.scroll_offset = max(0, self.scroll_offset)
        
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        surface.fill(theme.background)
        
        title_font = fonts["large"]
        title_text = "成就"
        title_surface = title_font.render(title_text, True, theme.text_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        if self.back_button:
            UIComponents.draw_button(surface, self.back_button, theme, fonts)
        
        ach_manager = self.data_manager.achievement_manager
        unlocked_count = ach_manager.get_unlocked_count()
        total_count = ach_manager.get_total_count()
        
        progress_font = fonts["medium"]
        progress_text = f"已解锁: {unlocked_count}/{total_count}"
        progress_surface = progress_font.render(progress_text, True, theme.text_color)
        progress_x = self.screen_width - progress_surface.get_width() - 20
        surface.blit(progress_surface, (progress_x, 30))
        
        achievements = list(ach_manager.achievements.values())
        card_height = 75
        card_width = self.screen_width - 80
        start_y = 100 - self.scroll_offset
        
        for i, achievement in enumerate(achievements):
            y = start_y + i * (card_height + 10)
            
            if y < 60 or y > self.screen_height - card_height:
                continue
            
            card_rect = pygame.Rect(40, y, card_width, card_height)
            
            bg_color = theme.accent_color if achievement.unlocked else theme.panel_background
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=10)
            pygame.draw.rect(surface, theme.panel_border, card_rect, 2, border_radius=10)
            
            icon_font = fonts["medium"]
            icon_surface = icon_font.render(achievement.icon, True, theme.text_color)
            surface.blit(icon_surface, (card_rect.x + 15, card_rect.centery - 12))
            
            name_font = fonts["medium"]
            name_surface = name_font.render(achievement.name, True, theme.text_color)
            surface.blit(name_surface, (card_rect.x + 55, card_rect.y + 12))
            
            desc_font = fonts["small"]
            desc_surface = desc_font.render(achievement.description, True, theme.panel_border)
            surface.blit(desc_surface, (card_rect.x + 55, card_rect.y + 42))
            
            rarity_colors = {
                "common": (150, 150, 150),
                "uncommon": (100, 200, 100),
                "rare": (100, 150, 255),
                "epic": (200, 100, 255),
                "legendary": (255, 200, 50)
            }
            rarity_color = rarity_colors.get(achievement.rarity, theme.text_color)
            rarity_surface = desc_font.render(achievement.rarity.upper(), True, rarity_color)
            rarity_x = card_rect.right - rarity_surface.get_width() - 15
            surface.blit(rarity_surface, (rarity_x, card_rect.centery - 8))


class StatsUI:
    """Statistics UI"""
    
    def __init__(self, screen_width: int, screen_height: int, data_manager: DataManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.data_manager = data_manager
        self.back_button: Optional[Button] = None
        self._create_ui()
    
    def _create_ui(self):
        self.back_button = Button(
            rect=pygame.Rect(20, 20, 100, 40),
            text="返回",
            callback=lambda: GameState.MAIN_MENU,
            icon="←"
        )
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        if self.back_button:
            self.back_button.hover = self.back_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.back_button.hover:
                return self.back_button.callback()
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        surface.fill(theme.background)
        
        title_font = fonts["large"]
        title_text = "统计数据"
        title_surface = title_font.render(title_text, True, theme.text_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        if self.back_button:
            UIComponents.draw_button(surface, self.back_button, theme, fonts)
        
        sessions_stats = self.data_manager.get_sessions_stats()
        total_score = self.data_manager.get_total_score()
        completed_levels = self.data_manager.get_completed_levels_count()
        
        stats = [
            ("总游戏次数", str(sessions_stats["total_sessions"])),
            ("胜利次数", str(sessions_stats["total_wins"])),
            ("失败次数", str(sessions_stats["total_losses"])),
            ("最高得分", str(sessions_stats["highest_score"])),
            ("平均得分", str(sessions_stats["average_score"])),
            ("总得分", str(total_score)),
            ("完成关卡", f"{completed_levels}/20"),
            ("总游戏时间", f"{sessions_stats['total_play_time']:.1f}秒"),
        ]
        
        panel_rect = pygame.Rect(50, 100, self.screen_width - 100, len(stats) * 50 + 20)
        UIComponents.draw_panel(surface, panel_rect, theme)
        
        font = fonts["medium"]
        for i, (label, value) in enumerate(stats):
            y = panel_rect.y + 20 + i * 50
            
            label_surface = font.render(label, True, theme.text_color)
            surface.blit(label_surface, (panel_rect.x + 20, y))
            
            value_surface = font.render(value, True, theme.accent_color)
            surface.blit(value_surface, (panel_rect.right - value_surface.get_width() - 20, y))


class GameOverUI:
    """Game over screen UI"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons: List[Button] = []
        self.stats: Dict[str, Any] = {}
        self.won = False
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 130
        button_height = 40
        start_y = 380
        
        self.buttons = [
            Button(
                rect=pygame.Rect((self.screen_width - button_width * 3 - 30) // 2, start_y, button_width, button_height),
                text="重试",
                callback=lambda: GameState.PLAYING,
                icon="🔄"
            ),
            Button(
                rect=pygame.Rect((self.screen_width - button_width) // 2, start_y, button_width, button_height),
                text="关卡选择",
                callback=lambda: GameState.LEVEL_SELECT,
                icon="🗺️"
            ),
            Button(
                rect=pygame.Rect((self.screen_width + button_width + 30) // 2, start_y, button_width, button_height),
                text="主菜单",
                callback=lambda: GameState.MAIN_MENU,
                icon="🏠"
            ),
        ]
    
    def set_result(self, won: bool, score: int, stats: Dict[str, Any]):
        self.won = won
        self.stats = stats
        self.stats["score"] = score
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        for button in self.buttons:
            button.hover = button.rect.collidepoint(mouse_pos)
            if mouse_click and button.hover:
                return button.callback()
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))
        
        panel_width = 420
        panel_height = 380
        panel_rect = pygame.Rect(
            (self.screen_width - panel_width) // 2,
            80,
            panel_width,
            panel_height
        )
        UIComponents.draw_panel(surface, panel_rect, theme)
        
        title_font = fonts["title"]
        title_text = "🎉 胜利!" if self.won else "💔 游戏结束"
        title_color = theme.accent_color if self.won else (200, 100, 100)
        title_surface = title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 130))
        surface.blit(title_surface, title_rect)
        
        stats_font = fonts["medium"]
        stats_items = [
            ("得分", str(self.stats.get("score", 0))),
            ("移动次数", str(self.stats.get("total_moves", 0))),
            ("合并次数", str(self.stats.get("total_merges", 0))),
            ("最大数字", str(self.stats.get("max_tile", 0))),
            ("最大连击", str(self.stats.get("max_combo", 0))),
            ("游戏时间", f"{self.stats.get('time_elapsed', 0):.1f}秒"),
        ]
        
        for i, (label, value) in enumerate(stats_items):
            y = panel_rect.y + 70 + i * 32
            
            label_surface = stats_font.render(label, True, theme.text_color)
            surface.blit(label_surface, (panel_rect.x + 40, y))
            
            value_surface = stats_font.render(value, True, theme.accent_color)
            surface.blit(value_surface, (panel_rect.right - value_surface.get_width() - 40, y))
        
        for button in self.buttons:
            UIComponents.draw_button(surface, button, theme, fonts)


class TutorialUI:
    """Tutorial UI"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_step = 0
        self.steps = [
            {"title": "欢迎来到1024!", "text": "这是一个数字合并游戏\n目标是将相同的数字合并\n直到达到目标数字"},
            {"title": "如何移动", "text": "使用方向键或WASD\n来滑动所有方块\n方块会向指定方向移动"},
            {"title": "合并规则", "text": "相同数字相撞时会合并\n例如: 2 + 2 = 4\n每次移动后会生成新方块"},
            {"title": "游戏目标", "text": "每关有不同的目标数字\n在移动次数用完前\n达到目标数字即可过关"},
            {"title": "准备好了吗?", "text": "点击\"开始游戏\"\n开始你的挑战吧!"},
        ]
        self.skip_button: Optional[Button] = None
        self.next_button: Optional[Button] = None
        self._create_buttons()
    
    def _create_buttons(self):
        self.skip_button = Button(
            rect=pygame.Rect(20, self.screen_height - 60, 100, 40),
            text="跳过",
            callback=lambda: GameState.MAIN_MENU
        )
        self.next_button = Button(
            rect=pygame.Rect(self.screen_width - 120, self.screen_height - 60, 100, 40),
            text="下一步",
            callback=self._next_step
        )
    
    def _next_step(self) -> Optional[GameState]:
        self.current_step += 1
        if self.current_step >= len(self.steps):
            return GameState.MAIN_MENU
        return None
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        if self.skip_button:
            self.skip_button.hover = self.skip_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.skip_button.hover:
                return self.skip_button.callback()
        
        if self.next_button:
            self.next_button.hover = self.next_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.next_button.hover:
                result = self.next_button.callback()
                if result:
                    return result
        
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        surface.fill(theme.background)
        
        step = self.steps[self.current_step]
        
        title_font = fonts["title"]
        title_surface = title_font.render(step["title"], True, theme.accent_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        surface.blit(title_surface, title_rect)
        
        text_font = fonts["medium"]
        lines = step["text"].split("\n")
        for i, line in enumerate(lines):
            line_surface = text_font.render(line, True, theme.text_color)
            line_rect = line_surface.get_rect(center=(self.screen_width // 2, 250 + i * 40))
            surface.blit(line_surface, line_rect)
        
        progress_font = fonts["small"]
        progress_text = f"{self.current_step + 1} / {len(self.steps)}"
        progress_surface = progress_font.render(progress_text, True, theme.panel_border)
        progress_rect = progress_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        surface.blit(progress_surface, progress_rect)
        
        if self.skip_button:
            UIComponents.draw_button(surface, self.skip_button, theme, fonts)
        
        if self.next_button:
            if self.current_step >= len(self.steps) - 1:
                self.next_button.text = "完成"
            UIComponents.draw_button(surface, self.next_button, theme, fonts)


class GameUI:
    """In-game UI"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pause_button: Optional[Button] = None
        self._create_ui()
    
    def _create_ui(self):
        self.pause_button = Button(
            rect=pygame.Rect(self.screen_width - 50, 10, 40, 40),
            text="⏸",
            callback=lambda: GameState.PAUSED
        )
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        if self.pause_button:
            self.pause_button.hover = self.pause_button.rect.collidepoint(mouse_pos)
            if mouse_click and self.pause_button.hover:
                return self.pause_button.callback()
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font],
             score: int, moves_remaining: int, level_info: Dict[str, Any]):
        
        if self.pause_button:
            UIComponents.draw_button(surface, self.pause_button, theme, fonts)
        
        score_font = fonts["large"]
        score_text = f"得分: {score}"
        score_surface = score_font.render(score_text, True, theme.text_color)
        surface.blit(score_surface, (20, 15))
        
        moves_font = fonts["medium"]
        moves_text = f"剩余移动: {moves_remaining}"
        moves_surface = moves_font.render(moves_text, True, theme.text_color)
        surface.blit(moves_surface, (20, 55))
        
        level_font = fonts["small"]
        level_text = f"关卡 {level_info['id']}: {level_info['name']}"
        level_surface = level_font.render(level_text, True, theme.panel_border)
        surface.blit(level_surface, (20, 85))
        
        target_font = fonts["small"]
        target_text = f"目标: {level_info['target']}"
        target_surface = target_font.render(target_text, True, theme.accent_color)
        surface.blit(target_surface, (20, 108))
        
        progress = level_info.get('progress', 0)
        progress_width = 150
        progress_height = 10
        progress_x = 20
        progress_y = 130
        
        pygame.draw.rect(surface, theme.panel_border, 
                        (progress_x, progress_y, progress_width, progress_height), border_radius=5)
        
        fill_width = int(progress * progress_width)
        if fill_width > 0:
            pygame.draw.rect(surface, theme.accent_color,
                           (progress_x, progress_y, fill_width, progress_height), border_radius=5)


class PauseUI:
    """Pause menu UI"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons: List[Button] = []
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 160
        button_height = 42
        start_y = 240
        
        self.buttons = [
            Button(
                rect=pygame.Rect((self.screen_width - button_width) // 2, start_y, button_width, button_height),
                text="继续游戏",
                callback=lambda: GameState.PLAYING,
                icon="▶"
            ),
            Button(
                rect=pygame.Rect((self.screen_width - button_width) // 2, start_y + 55, button_width, button_height),
                text="重新开始",
                callback=lambda: GameState.PLAYING,
                icon="🔄"
            ),
            Button(
                rect=pygame.Rect((self.screen_width - button_width) // 2, start_y + 110, button_width, button_height),
                text="关卡选择",
                callback=lambda: GameState.LEVEL_SELECT,
                icon="🗺️"
            ),
            Button(
                rect=pygame.Rect((self.screen_width - button_width) // 2, start_y + 165, button_width, button_height),
                text="主菜单",
                callback=lambda: GameState.MAIN_MENU,
                icon="🏠"
            ),
        ]
    
    def update(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> Optional[GameState]:
        for button in self.buttons:
            button.hover = button.rect.collidepoint(mouse_pos)
            if mouse_click and button.hover:
                return button.callback()
        return None
    
    def draw(self, surface: pygame.Surface, theme: ColorScheme, fonts: Dict[str, pygame.font.Font]):
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(
            (self.screen_width - 220) // 2,
            150,
            220,
            300
        )
        UIComponents.draw_panel(surface, panel_rect, theme)
        
        title_font = fonts["large"]
        title_text = "暂停"
        title_surface = title_font.render(title_text, True, theme.text_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 190))
        surface.blit(title_surface, title_rect)
        
        for button in self.buttons:
            UIComponents.draw_button(surface, button, theme, fonts)
