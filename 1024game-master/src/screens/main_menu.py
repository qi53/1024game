import pygame
from typing import Callable
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PRIMARY_COLOR, SECONDARY_COLOR,
    TEXT_COLOR, BG_COLOR, ACCENT_COLOR
)
from ..ui import Button, Title, get_font


class MainMenu:
    def __init__(
        self,
        screen: pygame.Surface,
        on_play: Callable,
        on_level_select: Callable,
        on_settings: Callable,
        on_achievements: Callable,
        on_tutorial: Callable,
        on_quit: Callable
    ):
        self.screen = screen
        self.title_font = get_font(96, bold=True)
        self.subtitle_font = get_font(32)
        
        button_width = 280
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        start_y = 280
        spacing = 70
        
        self.buttons = [
            Button(screen, button_x, start_y, button_width, button_height,
                   "开始游戏", on_play, color=ACCENT_COLOR, text_color=(255, 255, 255)),
            Button(screen, button_x, start_y + spacing, button_width, button_height,
                   "选择关卡", on_level_select, color=PRIMARY_COLOR, text_color=TEXT_COLOR),
            Button(screen, button_x, start_y + spacing * 2, button_width, button_height,
                   "设置", on_settings, color=SECONDARY_COLOR, text_color=TEXT_COLOR),
            Button(screen, button_x, start_y + spacing * 3, button_width, button_height,
                   "成就", on_achievements, color=SECONDARY_COLOR, text_color=TEXT_COLOR),
            Button(screen, button_x, start_y + spacing * 4, button_width, button_height,
                   "教程", on_tutorial, color=SECONDARY_COLOR, text_color=TEXT_COLOR),
            Button(screen, button_x, start_y + spacing * 5, button_width, button_height,
                   "退出游戏", on_quit, color=(180, 70, 70), text_color=(255, 255, 255)),
        ]
        
        self.particles = []
        self.animation_time = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def update(self, dt: float):
        self.animation_time += dt
        
        for button in self.buttons:
            button.update()
        
        if self.animation_time > 0.5:
            self.animation_time = 0
            self._add_particle()
        
        for p in self.particles[:]:
            p["life"] -= dt
            p["y"] += p["vy"] * dt
            p["alpha"] = int(255 * max(0, p["life"] / 2))
            if p["life"] <= 0:
                self.particles.remove(p)
    
    def _add_particle(self):
        import random
        self.particles.append({
            "x": random.randint(0, SCREEN_WIDTH),
            "y": -10,
            "vy": random.randint(30, 80),
            "size": random.randint(3, 8),
            "life": random.uniform(3, 6),
            "color": random.choice([PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR]),
            "alpha": 255
        })
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        for p in self.particles:
            s = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            alpha = max(0, min(255, p["alpha"]))
            color = (p["color"][0], p["color"][1], p["color"][2], alpha)
            pygame.draw.circle(s, color, (p["size"], p["size"]), p["size"])
            self.screen.blit(s, (p["x"] - p["size"], p["y"] - p["size"]))
        
        title = self.title_font.render("1024", True, ACCENT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        
        subtitle = self.subtitle_font.render("挑战20个关卡，到达65536！", True, TEXT_COLOR)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 180))
        
        for button in self.buttons:
            button.draw()
