from typing import List, Tuple, Optional, Dict, Set
import pygame

from .game_logic import GameLogic
from .particles import ParticleSystem, GlowEffect
from .theme import ThemeManager


class GameRenderer:
    def __init__(self, grid_size: int, theme_manager: ThemeManager,
                 audio_manager, particle_system: ParticleSystem):
        self.grid_size = grid_size
        self.theme = theme_manager
        self.audio = audio_manager
        self.particles = particle_system
        
        self.cell_size = 80
        self.cell_padding = 8
        self.grid_padding = 20
        
        self.recalculate_dimensions()
        
        self.font_cache: Dict[int, pygame.font.Font] = {}
        self.glow_effect = GlowEffect()
        
        self.animations: List[dict] = []
        self.new_tile_animations: List[dict] = []
        self.merge_animations: Set[Tuple[int, int]] = set()
        self.spawn_positions: Dict[Tuple[int, int], float] = {}
        
        self.shake_offset = [0, 0]
        self.shake_decay = 0
    
    def recalculate_dimensions(self):
        if self.grid_size <= 4:
            self.cell_size = 90
            self.cell_padding = 10
        elif self.grid_size <= 5:
            self.cell_size = 75
            self.cell_padding = 8
        elif self.grid_size <= 6:
            self.cell_size = 65
            self.cell_padding = 6
        else:
            self.cell_size = 55
            self.cell_padding = 5
        
        self.grid_width = self.grid_size * (self.cell_size + self.cell_padding) + self.cell_padding
        self.grid_height = self.grid_width
    
    def set_grid_size(self, size: int):
        self.grid_size = size
        self.recalculate_dimensions()
    
    def get_grid_position(self, x: int, y: int) -> Tuple[int, int]:
        gx = self.cell_padding + x * (self.cell_size + self.cell_padding)
        gy = self.cell_padding + y * (self.cell_size + self.cell_padding)
        return (gx, gy)
    
    def get_font(self, size: int) -> pygame.font.Font:
        from .font_utils import get_font as get_chinese_font
        if size not in self.font_cache:
            self.font_cache[size] = get_chinese_font(size)
        return self.font_cache[size]
    
    def get_tile_font_size(self, value: int) -> int:
        digits = len(str(value))
        base_size = self.cell_size // 2
        if digits <= 2:
            return base_size
        elif digits <= 3:
            return base_size - 10
        else:
            return max(20, base_size - digits * 4)
    
    def clear_spawn_animations(self):
        self.spawn_positions.clear()
    
    def add_spawn_animation(self, row: int, col: int):
        self.spawn_positions[(row, col)] = pygame.time.get_ticks()
    
    def add_merge_animation(self, positions: Set[Tuple[int, int]]):
        self.merge_animations.update(positions)
        for pos in positions:
            x, y = pos
            gx, gy = self.get_grid_position(y, x)
            center_x = gx + self.cell_size // 2
            center_y = gy + self.cell_size // 2
            self.particles.spawn_merge_particles(
                center_x, center_y,
                self.theme.get_accent_color()
            )
    
    def clear_merge_animations(self):
        self.merge_animations.clear()
    
    def trigger_shake(self, intensity: int = 5):
        self.shake_offset = [intensity, intensity]
        self.shake_decay = 0.9
    
    def draw(self, surface: pygame.Surface, grid: List[List[int]], offset_x: int = 0, offset_y: int = 0):
        grid_surface = pygame.Surface((self.grid_width, self.grid_height), pygame.SRCALPHA)
        
        bg_color = self.theme.get_grid_color()
        pygame.draw.rect(grid_surface, bg_color, grid_surface.get_rect(), border_radius=12)
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                gx, gy = self.get_grid_position(x, y)
                cell_rect = pygame.Rect(gx, gy, self.cell_size, self.cell_size)
                
                value = grid[y][x]
                if value == 0:
                    empty_color = self.theme.get_empty_color()
                    pygame.draw.rect(grid_surface, empty_color, cell_rect, border_radius=6)
                    continue
                
                spawn_time = self.spawn_positions.get((y, x))
                is_new = spawn_time is not None
                scale = 1.0
                pop_scale = 1.0
                
                if is_new:
                    elapsed = pygame.time.get_ticks() - spawn_time
                    if elapsed < 200:
                        t = elapsed / 200
                        scale = 0.3 + 0.7 * t
                        pop_scale = 1.0 + 0.3 * (1 - abs(t - 0.5) * 2)
                    else:
                        del self.spawn_positions[(y, x)]
                
                is_merged = (y, x) in self.merge_animations
                if is_merged:
                    pop_scale = 1.2
                
                tile_color = self.theme.get_tile_color(value)
                
                if scale != 1.0 or pop_scale != 1.0:
                    final_scale = scale * pop_scale
                    draw_size = int(self.cell_size * final_scale)
                    offset = (self.cell_size - draw_size) // 2
                    draw_rect = pygame.Rect(gx + offset, gy + offset, draw_size, draw_size)
                else:
                    draw_rect = cell_rect
                
                self.glow_effect.draw_glow(grid_surface, draw_rect, tile_color, 0.05 if value >= 512 else 0)
                
                pygame.draw.rect(grid_surface, tile_color, draw_rect, border_radius=6)
                
                text_color = self.theme.get_text_color(value)
                font_size = self.get_tile_font_size(value)
                font = self.get_font(font_size)
                text_surf = font.render(str(value), True, text_color)
                text_rect = text_surf.get_rect(center=draw_rect.center)
                grid_surface.blit(text_surf, text_rect)
        
        if self.shake_decay > 0.1:
            import random
            self.shake_offset[0] = random.randint(-5, 5) * self.shake_decay
            self.shake_offset[1] = random.randint(-5, 5) * self.shake_decay
            self.shake_decay *= 0.85
        else:
            self.shake_offset = [0, 0]
        
        final_x = offset_x + int(self.shake_offset[0])
        final_y = offset_y + int(self.shake_offset[1])
        surface.blit(grid_surface, (final_x, final_y))
    
    def draw_game_info(self, surface: pygame.Surface, score: int, moves: int,
                        max_tile: int, target: int, remaining_time: Optional[float] = None):
        info_panel_y = 50
        panel_width = 150
        panel_height = 80
        spacing = 20
        start_x = (surface.get_width() - (panel_width * 2 + spacing * 3)) // 2
        
        info_bg = (40, 40, 50)
        corner_radius = 10
        
        score_rect = pygame.Rect(start_x + spacing, info_panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, info_bg, score_rect, border_radius=corner_radius)
        
        font = self.get_font(20)
        title_color = (150, 150, 150)
        value_color = self.theme.get_text_light()
        
        text = font.render("分数", True, title_color)
        surface.blit(text, text.get_rect(center=(score_rect.centerx, score_rect.y + 18)))
        font_val = self.get_font(32)
        text = font_val.render(f"{score}", True, self.theme.get_accent_color())
        surface.blit(text, text.get_rect(center=(score_rect.centerx, score_rect.y + 52)))
        
        moves_rect = pygame.Rect(start_x + panel_width + spacing * 2, info_panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, info_bg, moves_rect, border_radius=corner_radius)
        text = font.render("步数", True, title_color)
        surface.blit(text, text.get_rect(center=(moves_rect.centerx, moves_rect.y + 18)))
        text = font_val.render(f"{moves}", True, value_color)
        surface.blit(text, text.get_rect(center=(moves_rect.centerx, moves_rect.y + 52)))
        
        target_rect = pygame.Rect(start_x + panel_width * 2 + spacing * 3, info_panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, info_bg, target_rect, border_radius=corner_radius)
        text = font.render("目标", True, title_color)
        surface.blit(text, text.get_rect(center=(target_rect.centerx, target_rect.y + 18)))
        text = font_val.render(f"{target}", True, value_color)
        surface.blit(text, text.get_rect(center=(target_rect.centerx, target_rect.y + 52)))
        
        if remaining_time is not None:
            time_rect = pygame.Rect(start_x + panel_width // 2, info_panel_y + panel_height + 15, 
                                    panel_width * 3 + spacing * 2, 30)
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            
            progress_width = time_rect.width * (remaining_time / 420) if remaining_time > 0 else 0
            progress_rect = pygame.Rect(time_rect.x, time_rect.y, max(1, int(progress_width)), time_rect.height)
            
            if remaining_time > 120:
                bar_color = (76, 175, 80)
            elif remaining_time > 60:
                bar_color = (255, 152, 0)
            else:
                bar_color = (244, 67, 54)
            
            pygame.draw.rect(surface, (30, 30, 40), time_rect, border_radius=6)
            if progress_width > 0:
                pygame.draw.rect(surface, bar_color, progress_rect, border_radius=6)
            
            time_str = f"⏱ {minutes}:{seconds:02d}"
            text = font.render(time_str, True, value_color)
            surface.blit(text, text.get_rect(center=time_rect.center))
    
    def draw_controls_hint(self, surface: pygame.Surface, y_pos: int):
        font = self.get_font(18)
        hints = "⬆⬇⬅➡ 或 WASD 移动 | ESC 返回"
        text = font.render(hints, True, (120, 120, 130))
        surface.blit(text, text.get_rect(midtop=(surface.get_width() // 2, y_pos)))
