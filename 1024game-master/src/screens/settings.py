import pygame
from typing import Callable
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PRIMARY_COLOR, SECONDARY_COLOR,
    TEXT_COLOR, BG_COLOR, ACCENT_COLOR, THEMES
)
from ..storage import GameStorage
from ..ui import Button, Slider, Toggle, get_font


class SettingsScreen:
    def __init__(self, screen: pygame.Surface, on_back: Callable):
        self.screen = screen
        self.on_back = on_back
        self.storage = GameStorage()
        self.settings = self.storage.get_settings()
        
        self.title_font = get_font(64)
        self.label_font = get_font(36)
        self.small_font = get_font(24)
        
        self.back_button = Button(
            screen, 50, SCREEN_HEIGHT - 80, 120, 50,
            "返回", self._on_back_click,
            color=SECONDARY_COLOR, text_color=TEXT_COLOR
        )
        
        slider_x = 300
        slider_width = 300
        start_y = 180
        spacing = 80
        
        self.music_slider = Slider(
            screen, slider_x, start_y, slider_width, 20,
            self.settings.get("music_volume", 0.7),
            (0, 1), "音乐音量"
        )
        
        self.sfx_slider = Slider(
            screen, slider_x, start_y + spacing, slider_width, 20,
            self.settings.get("sfx_volume", 1.0),
            (0, 1), "音效音量"
        )
        
        self.particles_toggle = Toggle(
            screen, slider_x, start_y + spacing * 2, 60, 30,
            self.settings.get("particles_enabled", True),
            "粒子效果"
        )
        
        self.themes = list(THEMES.keys())
        self.current_theme_index = self.themes.index(self.settings.get("theme", "classic"))
        self.theme_buttons = []
        for i, theme_name in enumerate(self.themes):
            btn = Button(
                screen, 300 + i * 120, start_y + spacing * 3, 100, 40,
                theme_name, lambda t=theme_name: self._select_theme(t),
                color=ACCENT_COLOR if i == self.current_theme_index else SECONDARY_COLOR,
                text_color=(255, 255, 255)
            )
            self.theme_buttons.append(btn)
    
    def _select_theme(self, theme_name: str):
        self.current_theme_index = self.themes.index(theme_name)
        for i, btn in enumerate(self.theme_buttons):
            btn.color = ACCENT_COLOR if i == self.current_theme_index else SECONDARY_COLOR
    
    def _on_back_click(self):
        self._save_settings()
        self.on_back()
    
    def _save_settings(self):
        self.settings["music_volume"] = self.music_slider.value
        self.settings["sfx_volume"] = self.sfx_slider.value
        self.settings["particles_enabled"] = self.particles_toggle.value
        self.settings["theme"] = self.themes[self.current_theme_index]
        self.storage.set_settings(self.settings)
        self.storage.save()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.back_button.handle_event(event):
            return True
        
        self.music_slider.handle_event(event)
        self.sfx_slider.handle_event(event)
        self.particles_toggle.handle_event(event)
        
        for btn in self.theme_buttons:
            if btn.handle_event(event):
                return True
        
        return False
    
    def update(self, dt: float):
        self.back_button.update()
        self.music_slider.update()
        self.sfx_slider.update()
        self.particles_toggle.update()
        for btn in self.theme_buttons:
            btn.update()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        title = self.title_font.render("设置", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        labels = ["音乐音量", "音效音量", "粒子效果", "主题"]
        label_y = 170
        for label in labels:
            text = self.label_font.render(label, True, TEXT_COLOR)
            self.screen.blit(text, (100, label_y))
            label_y += 80
        
        self.music_slider.draw()
        self.sfx_slider.draw()
        self.particles_toggle.draw()
        
        for btn in self.theme_buttons:
            btn.draw()
        
        self.back_button.draw()
