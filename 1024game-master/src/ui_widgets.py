from typing import Optional, Tuple, Callable, Any, List
import pygame
import math
from .font_utils import get_font

pygame.init()

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, theme,
                 on_click: Optional[Callable[[], Any]] = None,
                 text_color: Optional[Tuple[int, int, int]] = None,
                 bg_color: Optional[Tuple[int, int, int]] = None,
                 hover_color: Optional[Tuple[int, int, int]] = None,
                 corner_radius: int = 8,
                 icon: Optional[str] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.theme = theme
        self.on_click = on_click
        self.text_color = text_color or theme.get_text_light()
        self.bg_color = bg_color or theme.get_button_color()
        self.hover_color = hover_color or theme.get_button_hover_color()
        self.corner_radius = corner_radius
        self.icon = icon
        self.is_hovered = False
        self.is_clicked = False
        self.hover_animation = 0.0
        self.click_animation = 0.0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            return self.is_hovered != was_hovered
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_clicked = True
                self.click_animation = 1.0
                return True
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_clicked:
                self.is_clicked = False
                if self.rect.collidepoint(event.pos) and self.on_click:
                    self.on_click()
                    return True
        return False
    
    def update(self, dt: int):
        target_hover = 1.0 if self.is_hovered else 0.0
        self.hover_animation += (target_hover - self.hover_animation) * 0.15
        self.click_animation *= 0.85
    
    def draw(self, surface: pygame.Surface):
        current_color = tuple(
            int(self.bg_color[i] + (self.hover_color[i] - self.bg_color[i]) * self.hover_animation)
            for i in range(3)
        )
        
        offset_y = -3 if self.is_clicked else 0
        draw_rect = self.rect.copy()
        draw_rect.y += offset_y
        
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height + 6), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(0, 6, self.rect.width, self.rect.height)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 40), shadow_rect, border_radius=self.corner_radius)
        surface.blit(shadow_surf, (self.rect.x, self.rect.y))
        
        pygame.draw.rect(surface, current_color, draw_rect, border_radius=self.corner_radius)
        
        accent = self.theme.get_accent_color()
        accent_alpha = int(60 * self.hover_animation)
        if accent_alpha > 0:
            accent_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(accent_surf, (*accent, accent_alpha), accent_surf.get_rect(), border_radius=self.corner_radius)
            surface.blit(accent_surf, draw_rect)
        
        if self.icon:
            icon_surf = self.font.render(self.icon, True, self.text_color)
            icon_rect = icon_surf.get_rect(midleft=(draw_rect.x + 15, draw_rect.centery))
            surface.blit(icon_surf, icon_rect)
            text_x = draw_rect.centerx + 10
        else:
            text_x = draw_rect.centerx
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(text_x, draw_rect.centery))
        if self.icon:
            text_rect.centerx = (draw_rect.left + 40 + draw_rect.right) // 2
        surface.blit(text_surf, text_rect)


class Slider:
    def __init__(self, x: int, y: int, width: int, height: int,
                 min_val: float, max_val: float, initial_val: float,
                 theme, label: str = "",
                 on_change: Optional[Callable[[float], Any]] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.theme = theme
        self.label = label
        self.on_change = on_change
        self.is_dragging = False
        self.handle_radius = height // 2 + 3
        self.track_height = 4
        self.font = get_font(24)
    
    def get_handle_x(self) -> int:
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * (self.rect.width - 2 * self.handle_radius) + self.handle_radius)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                handle_x = self.get_handle_x()
                handle_rect = pygame.Rect(
                    handle_x - self.handle_radius,
                    self.rect.centery - self.handle_radius,
                    self.handle_radius * 2,
                    self.handle_radius * 2
                )
                if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self._update_value(event.pos[0])
                    return True
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        
        if event.type == pygame.MOUSEMOTION:
            if self.is_dragging and event.buttons[0]:
                self._update_value(event.pos[0])
                return True
        return False
    
    def _update_value(self, mouse_x: int):
        ratio = (mouse_x - self.rect.x - self.handle_radius) / (self.rect.width - 2 * self.handle_radius)
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        if self.on_change:
            self.on_change(self.value)
    
    def draw(self, surface: pygame.Surface):
        if self.label:
            label_surf = self.font.render(self.label, True, self.theme.get_text_light())
            surface.blit(label_surf, (self.rect.x, self.rect.y - 20))
        
        track_rect = pygame.Rect(
            self.rect.x,
            self.rect.centery - self.track_height // 2,
            self.rect.width,
            self.track_height
        )
        pygame.draw.rect(surface, (60, 60, 70), track_rect, border_radius=2)
        
        fill_ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_rect = track_rect.copy()
        fill_rect.width = int(fill_ratio * self.rect.width)
        pygame.draw.rect(surface, self.theme.get_accent_color(), fill_rect, border_radius=2)
        
        handle_x = self.get_handle_x()
        handle_y = self.rect.centery
        
        pygame.draw.circle(surface, (30, 30, 40), (handle_x, handle_y), self.handle_radius + 2)
        pygame.draw.circle(surface, self.theme.get_accent_color(), (handle_x, handle_y), self.handle_radius)
        
        value_surf = self.font.render(f"{self.value:.1f}", True, self.theme.get_text_light())
        value_rect = value_surf.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        surface.blit(value_surf, value_rect)


class Panel:
    def __init__(self, x: int, y: int, width: int, height: int, theme,
                 bg_color: Optional[Tuple[int, int, int]] = None,
                 corner_radius: int = 12,
                 border: bool = False,
                 border_color: Optional[Tuple[int, int, int]] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.theme = theme
        self.bg_color = bg_color or theme.get_panel_color()
        self.corner_radius = corner_radius
        self.border = border
        self.border_color = border_color or theme.get_accent_color()
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.widgets: List[Any] = []
    
    def add_widget(self, widget: Any):
        if hasattr(widget, 'rect'):
            widget.rect.x += self.rect.x
            widget.rect.y += self.rect.y
        self.widgets.append(widget)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for widget in self.widgets:
            if hasattr(widget, 'handle_event'):
                if widget.handle_event(event):
                    return True
        return False
    
    def update(self, dt: int):
        for widget in self.widgets:
            if hasattr(widget, 'update'):
                widget.update(dt)
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(self.surface, (*self.bg_color, 230), self.surface.get_rect(), border_radius=self.corner_radius)
        
        if self.border:
            pygame.draw.rect(self.surface, self.border_color, self.surface.get_rect(), width=2, border_radius=self.corner_radius)
        
        surface.blit(self.surface, self.rect)
        
        for widget in self.widgets:
            if hasattr(widget, 'draw'):
                widget.draw(surface)


class Label:
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font, theme,
                 color: Optional[Tuple[int, int, int]] = None,
                 center: bool = False):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.theme = theme
        self.color = color or theme.get_text_light()
        self.center = center
        self._render()
    
    def _render(self):
        self.surface = self.font.render(self.text, True, self.color)
        if self.center:
            self.rect = self.surface.get_rect(center=(self.x, self.y))
        else:
            self.rect = self.surface.get_rect(topleft=(self.x, self.y))
    
    def set_text(self, text: str):
        self.text = text
        self._render()
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)


class Toast:
    def __init__(self, text: str, duration: int = 2000, theme = None):
        self.text = text
        self.duration = duration
        self.theme = theme
        self.alpha = 0
        self.font = get_font(28)
        self.start_time = pygame.time.get_ticks()
        self.y_offset = 0
    
    def update(self, dt: int):
        elapsed = pygame.time.get_ticks() - self.start_time
        
        if elapsed < 300:
            self.alpha = min(255, self.alpha + dt * 1.5)
            self.y_offset = 50 - (elapsed / 300) * 50
        elif elapsed > self.duration - 300:
            self.alpha = max(0, self.alpha - dt * 1.5)
            self.y_offset = (elapsed - (self.duration - 300)) / 300 * 50
    
    def is_done(self) -> bool:
        return pygame.time.get_ticks() - self.start_time > self.duration
    
    def draw(self, surface: pygame.Surface):
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        padding = 20
        
        bg_rect = pygame.Rect(
            surface.get_width() // 2 - text_surf.get_width() // 2 - padding,
            surface.get_height() - 80 + self.y_offset,
            text_surf.get_width() + padding * 2,
            text_surf.get_height() + padding // 2
        )
        
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (30, 30, 40, int(self.alpha * 0.9)), bg_surf.get_rect(), border_radius=8)
        if self.theme:
            accent = (*self.theme.get_accent_color(), int(self.alpha * 0.3))
            pygame.draw.rect(bg_surf, accent, bg_surf.get_rect(), width=2, border_radius=8)
        
        bg_surf.set_alpha(int(self.alpha))
        surface.blit(bg_surf, bg_rect)
        
        text_surf.set_alpha(int(self.alpha))
        text_rect = text_surf.get_rect(center=bg_rect.center)
        surface.blit(text_surf, text_rect)


class ProgressBar:
    def __init__(self, x: int, y: int, width: int, height: int,
                 max_value: float, theme, show_text: bool = True):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = max_value
        self.theme = theme
        self.show_text = show_text
        self.font = get_font(22)
    
    def set_value(self, value: float):
        self.current_value = max(0, min(value, self.max_value))
    
    def get_ratio(self) -> float:
        return self.current_value / self.max_value if self.max_value > 0 else 1.0
    
    def draw(self, surface: pygame.Surface):
        ratio = self.get_ratio()
        
        pygame.draw.rect(surface, (30, 30, 40), self.rect, border_radius=4)
        
        if ratio > 0:
            fill_rect = self.rect.copy()
            fill_rect.width = max(1, int(self.rect.width * ratio))
            
            if ratio > 0.5:
                color = (76, 175, 80)
            elif ratio > 0.25:
                color = (255, 152, 0)
            else:
                color = (244, 67, 54)
            
            pygame.draw.rect(surface, color, fill_rect, border_radius=4)
        
        if self.show_text:
            text = f"{self.current_value:.0f} / {self.max_value:.0f}"
            text_surf = self.font.render(text, True, self.theme.get_text_light())
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)


class AnimatedTile:
    def __init__(self, value: int, start_pos: Tuple[float, float],
                 end_pos: Tuple[float, float], size: float,
                 duration: int = 150):
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.size = size
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.scale = 0.3
        self.is_done = False
    
    def update(self, dt: int):
        elapsed = pygame.time.get_ticks() - self.start_time
        t = min(1.0, elapsed / self.duration)
        
        ease_out_back = 1 - t
        ease_out_back = 1 - ease_out_back * ease_out_back * (1 - 0.7 * t)
        
        self.current_pos[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease_out_back
        self.current_pos[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease_out_back
        
        self.scale = 0.3 + 0.7 * (1 - abs(t - 0.5) * 1.2)
        
        if t >= 1.0:
            self.is_done = True
    
    def draw(self, surface: pygame.Surface, theme):
        if self.is_done:
            return
        
        color = theme.get_tile_color(self.value)
        draw_size = int(self.size * self.scale)
        
        x = int(self.current_pos[0] + (self.size - draw_size) / 2)
        y = int(self.current_pos[1] + (self.size - draw_size) / 2)
        
        tile_rect = pygame.Rect(x, y, draw_size, draw_size)
        pygame.draw.rect(surface, color, tile_rect, border_radius=6)
        
        font_size = max(16, int(draw_size / 3))
        font = get_font(font_size)
        text_color = theme.get_text_color(self.value)
        text_surf = font.render(str(self.value), True, text_color)
        text_rect = text_surf.get_rect(center=tile_rect.center)
        surface.blit(text_surf, text_rect)
