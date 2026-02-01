import pygame
from typing import Callable, Dict, Any
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_COLOR, BG_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from ..ui import Button, StarDisplay, get_font


class GameOverScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        stats: Dict[str, Any],
        on_restart: Callable,
        on_next_level: Callable,
        on_menu: Callable,
        is_win: bool = True
    ):
        self.screen = screen
        self.stats = stats
        self.on_restart = on_restart
        self.on_next_level = on_next_level
        self.on_menu = on_menu
        self.is_win = is_win
        
        self.title_font = get_font(80)
        self.stat_font = get_font(36)
        self.value_font = get_font(48)
        
        button_width = 200
        button_height = 55
        button_y = SCREEN_HEIGHT - 120
        button_spacing = 30
        total_width = button_width * 3 + button_spacing * 2
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        self.restart_button = Button(
            screen, start_x, button_y, button_width, button_height,
            "重玩", self.on_restart,
            color=SECONDARY_COLOR, text_color=TEXT_COLOR
        )
        
        self.next_button = None
        if is_win and stats.get("level", 1) < 20:
            self.next_button = Button(
                screen, start_x + button_width + button_spacing, button_y, button_width, button_height,
                "下一关", self.on_next_level,
                color=ACCENT_COLOR, text_color=(255, 255, 255)
            )
        
        self.menu_button = Button(
            screen, start_x + button_width * 2 + button_spacing * 2, button_y, button_width, button_height,
            "主菜单", self.on_menu,
            color=PRIMARY_COLOR, text_color=TEXT_COLOR
        )
        
        self.star_display = None
        if is_win:
            self.star_display = StarDisplay(screen, SCREEN_WIDTH // 2 - 100, 200, 200, 60, stats.get("stars", 0))
        
        self.animation_alpha = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.restart_button.handle_event(event):
            return True
        if self.next_button and self.next_button.handle_event(event):
            return True
        if self.menu_button.handle_event(event):
            return True
        return False
    
    def update(self, dt: float):
        self.animation_alpha = min(255, self.animation_alpha + dt * 500)
        
        self.restart_button.update()
        if self.next_button:
            self.next_button.update()
        self.menu_button.update()
    
    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.animation_alpha * 0.7)))
        self.screen.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 100, 600, SCREEN_HEIGHT - 250)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((*BG_COLOR[:3], int(self.animation_alpha)))
        pygame.draw.rect(panel_surface, PRIMARY_COLOR, (0, 0, panel_rect.width, panel_rect.height), 3, border_radius=20)
        self.screen.blit(panel_surface, panel_rect)
        
        if self.animation_alpha >= 100:
            title_text = "恭喜过关！" if self.is_win else "游戏结束"
            title_color = ACCENT_COLOR if self.is_win else (200, 50, 50)
            title = self.title_font.render(title_text, True, title_color)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))
            
            if self.star_display:
                self.star_display.draw()
            
            stat_y = 300
            stats_items = [
                ("关卡", str(self.stats.get("level", 1))),
                ("得分", f"{self.stats.get('score', 0):,}"),
                ("最高方块", str(self.stats.get("max_tile", 0))),
                ("移动次数", str(self.stats.get("moves", 0))),
                ("用时", f"{self.stats.get('time', 0):.1f} 秒"),
                ("最大连击", str(self.stats.get("max_combo", 0))),
            ]
            
            for label, value in stats_items:
                label_text = self.stat_font.render(f"{label}:", True, TEXT_COLOR)
                value_text = self.value_font.render(value, True, ACCENT_COLOR)
                self.screen.blit(label_text, (SCREEN_WIDTH // 2 - 150, stat_y))
                self.screen.blit(value_text, (SCREEN_WIDTH // 2 + 50, stat_y - 5))
                stat_y += 50
        
        self.restart_button.draw()
        if self.next_button:
            self.next_button.draw()
        self.menu_button.draw()
