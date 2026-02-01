import pygame
from typing import Callable, Optional
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_CONFIGS, Difficulty,
    PRIMARY_COLOR, SECONDARY_COLOR, TEXT_COLOR, BG_COLOR,
    DIFFICULTY_COLORS, TILE_COLORS
)
from ..storage import GameStorage
from ..ui import Button, get_font


class LevelSelect:
    def __init__(self, screen: pygame.Surface, on_back: Callable, on_select_level: Callable[[int], None]):
        self.screen = screen
        self.on_back = on_back
        self.on_select_level = on_select_level
        self.storage = GameStorage()
        
        self.title_font = get_font(64)
        self.level_font = get_font(36)
        self.info_font = get_font(24)
        
        self.back_button = Button(
            screen, 50, SCREEN_HEIGHT - 80, 120, 50,
            "返回", self.on_back,
            color=SECONDARY_COLOR, text_color=TEXT_COLOR
        )
        
        self.scroll_offset = 0
        self.max_scroll = 0
        self.level_buttons = []
        self._create_level_buttons()
        
    def _create_level_buttons(self):
        self.level_buttons = []
        level_data = self.storage.get_levels_data()
        
        cols = 5
        rows = 4
        button_width = 100
        button_height = 100
        spacing = 20
        start_x = (SCREEN_WIDTH - (cols * (button_width + spacing) - spacing)) // 2
        start_y = 150
        
        for level in range(1, 21):
            col = (level - 1) % cols
            row = (level - 1) // cols
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            config = LEVEL_CONFIGS[level]
            is_unlocked = level == 1 or level_data.get(str(level - 1), {}).get("completed", False)
            
            level_data_item = level_data.get(str(level), {})
            stars = level_data_item.get("stars", 0)
            best_time = level_data_item.get("best_time", None)
            
            self.level_buttons.append({
                "level": level,
                "rect": pygame.Rect(x, y, button_width, button_height),
                "config": config,
                "unlocked": is_unlocked,
                "stars": stars,
                "best_time": best_time
            })
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = min(0, self.scroll_offset + 30)
            elif event.button == 5:
                self.scroll_offset = max(self.max_scroll, self.scroll_offset - 30)
        
        if self.back_button.handle_event(event):
            return True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for lb in self.level_buttons:
                rect = lb["rect"].copy()
                rect.y += self.scroll_offset
                if rect.collidepoint(mouse_pos) and lb["unlocked"]:
                    self.on_select_level(lb["level"])
                    return True
        
        return False
    
    def update(self, dt: float):
        self.back_button.update()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        title = self.title_font.render("选择关卡", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        for lb in self.level_buttons:
            rect = lb["rect"].copy()
            rect.y += self.scroll_offset
            
            difficulty = lb["config"]["difficulty"]
            diff_color = DIFFICULTY_COLORS.get(difficulty, SECONDARY_COLOR)
            
            if lb["unlocked"]:
                pygame.draw.rect(self.screen, diff_color, rect, border_radius=10)
                pygame.draw.rect(self.screen, TILE_COLORS.get(2, (238, 228, 218)), rect.inflate(-4, -4), border_radius=8)
                
                level_text = self.level_font.render(str(lb["level"]), True, TEXT_COLOR)
                self.screen.blit(level_text, (rect.centerx - level_text.get_width() // 2, rect.centery - 20))
                
                if lb["stars"] > 0:
                    for i in range(3):
                        star_color = (255, 215, 0) if i < lb["stars"] else (100, 100, 100)
                        star_x = rect.x + 20 + i * 25
                        star_y = rect.y + 65
                        pygame.draw.circle(self.screen, star_color, (star_x, star_y), 6)
                
                if lb["best_time"]:
                    time_text = self.info_font.render(f"{lb['best_time']:.1f}s", True, (100, 100, 100))
                    self.screen.blit(time_text, (rect.centerx - time_text.get_width() // 2, rect.y + 80))
            else:
                pygame.draw.rect(self.screen, (80, 80, 80), rect, border_radius=10)
                pygame.draw.rect(self.screen, (60, 60, 60), rect.inflate(-4, -4), border_radius=8)
                lock_text = self.info_font.render("🔒", True, (150, 150, 150))
                self.screen.blit(lock_text, (rect.centerx - lock_text.get_width() // 2, rect.centery - 10))
        
        difficulty_legend = [
            ("简单", Difficulty.EASY, DIFFICULTY_COLORS[Difficulty.EASY]),
            ("中等", Difficulty.MEDIUM, DIFFICULTY_COLORS[Difficulty.MEDIUM]),
            ("困难", Difficulty.HARD, DIFFICULTY_COLORS[Difficulty.HARD]),
            ("专家", Difficulty.EXPERT, DIFFICULTY_COLORS[Difficulty.EXPERT]),
        ]
        
        legend_y = SCREEN_HEIGHT - 120
        legend_x = 250
        for i, (name, diff, color) in enumerate(difficulty_legend):
            pygame.draw.rect(self.screen, color, (legend_x + i * 100, legend_y, 15, 15), border_radius=3)
            text = self.info_font.render(name, True, TEXT_COLOR)
            self.screen.blit(text, (legend_x + i * 100 + 22, legend_y))
        
        self.back_button.draw()
