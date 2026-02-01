import pygame
from typing import Callable
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_COLOR, BG_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, ACHIEVEMENTS
from ..storage import GameStorage
from ..ui import Button, get_font


class AchievementsScreen:
    def __init__(self, screen: pygame.Surface, on_back: Callable):
        self.screen = screen
        self.on_back = on_back
        self.storage = GameStorage()
        
        self.title_font = get_font(64)
        self.name_font = get_font(32)
        self.desc_font = get_font(24)
        self.progress_font = get_font(20)
        
        self.back_button = Button(
            screen, 50, SCREEN_HEIGHT - 80, 120, 50,
            "返回", self.on_back,
            color=SECONDARY_COLOR, text_color=TEXT_COLOR
        )
        
        self.scroll_offset = 0
        self.achievement_items = []
        self._create_achievement_list()
    
    def _create_achievement_list(self):
        self.achievement_items = []
        unlocked = self.storage.get_unlocked_achievements()
        stats = self.storage.get_stats()
        
        for i, (ach_id, ach_data) in enumerate(ACHIEVEMENTS.items()):
            is_unlocked = ach_id in unlocked
            progress = self._calculate_progress(ach_id, ach_data, stats)
            
            self.achievement_items.append({
                "id": ach_id,
                "name": ach_data["name"],
                "description": ach_data["description"],
                "icon": ach_data.get("icon", "🏆"),
                "unlocked": is_unlocked,
                "progress": progress,
                "y": 150 + i * 90
            })
    
    def _calculate_progress(self, ach_id: str, ach_data: dict, stats: dict) -> tuple:
        target = ach_data.get("target", 1)
        
        if ach_id == "first_win":
            current = 1 if stats.get("total_games_played", 0) > 0 else 0
        elif ach_id == "speed_demon":
            current = stats.get("fastest_win", float('inf'))
            target = 60
        elif ach_id == "high_scorer":
            current = stats.get("highest_score", 0)
        elif ach_id == "combo_master":
            current = stats.get("max_combo", 0)
        elif ach_id == "level_master":
            current = stats.get("levels_completed", 0)
        elif ach_id == "perfectionist":
            current = stats.get("total_3_star", 0)
        elif ach_id == "tenacious":
            current = stats.get("total_games_played", 0)
        elif ach_id == "speed_2048":
            current = 1 if stats.get("reached_2048", False) else 0
        else:
            current = 0
        
        return (current, target)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = min(0, self.scroll_offset + 30)
            elif event.button == 5:
                self.scroll_offset = max(-len(self.achievement_items) * 50, self.scroll_offset - 30)
        
        if self.back_button.handle_event(event):
            return True
        
        return False
    
    def update(self, dt: float):
        self.back_button.update()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        title = self.title_font.render("成就", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        unlocked_count = sum(1 for item in self.achievement_items if item["unlocked"])
        total_count = len(self.achievement_items)
        progress_text = self.desc_font.render(f"已解锁: {unlocked_count} / {total_count}", True, TEXT_COLOR)
        self.screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, 110))
        
        clip_rect = pygame.Rect(50, 140, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
        
        for item in self.achievement_items:
            y = item["y"] + self.scroll_offset
            if y < 140 or y > SCREEN_HEIGHT - 120:
                continue
            
            rect = pygame.Rect(100, y, SCREEN_WIDTH - 200, 80)
            
            if item["unlocked"]:
                bg_color = PRIMARY_COLOR
                border_color = (255, 215, 0)
            else:
                bg_color = (60, 60, 60)
                border_color = (80, 80, 80)
            
            pygame.draw.rect(self.screen, border_color, rect, border_radius=10)
            pygame.draw.rect(self.screen, bg_color, rect.inflate(-4, -4), border_radius=8)
            
            icon_text = self.title_font.render(item["icon"], True, TEXT_COLOR)
            self.screen.blit(icon_text, (rect.x + 15, rect.y + 15))
            
            name_text = self.name_font.render(item["name"], True, TEXT_COLOR)
            self.screen.blit(name_text, (rect.x + 80, rect.y + 10))
            
            desc_text = self.desc_font.render(item["description"], True, (200, 200, 200))
            self.screen.blit(desc_text, (rect.x + 80, rect.y + 42))
            
            if not item["unlocked"] and item["progress"][1] > 1:
                current, target = item["progress"]
                progress = min(current / target, 1.0)
                bar_rect = pygame.Rect(rect.x + 80, rect.y + 65, 200, 8)
                pygame.draw.rect(self.screen, (50, 50, 50), bar_rect, border_radius=4)
                pygame.draw.rect(self.screen, PRIMARY_COLOR, 
                                (bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_rect.height),
                                border_radius=4)
                prog_text = self.progress_font.render(f"{int(current)}/{target}", True, (150, 150, 150))
                self.screen.blit(prog_text, (bar_rect.right + 10, bar_rect.y - 5))
        
        self.back_button.draw()
