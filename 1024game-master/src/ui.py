#!/usr/bin/env python3
"""
1024 Game - UI Components
All pygame-based UI components
"""

import pygame
from typing import Tuple, Optional, Callable, Dict, List
from dataclasses import dataclass

from .config import THEMES, TILE_COLORS, TILE_TEXT_COLORS


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Get a font that supports Chinese characters"""
    font_names = [
        "PingFang SC",
        "Songti SC",
        "STHeiti",
        "Arial Unicode MS",
        "Microsoft YaHei",
        "SimHei",
        "Sans"
    ]
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                return font
        except:
            continue
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont(None, size)


@dataclass
class ColorScheme:
    background: Tuple[int, int, int]
    grid_bg: Tuple[int, int, int]
    accent: Tuple[int, int, int]
    text: Tuple[int, int, int] = (255, 255, 255)


class Button:
    """Interactive button component"""
    
    def __init__(self, screen: pygame.Surface, x: int, y: int, width: int, height: int, text: str,
                 callback: Optional[Callable] = None,
                 color: Optional[Tuple[int, int, int]] = None,
                 text_color: Optional[Tuple[int, int, int]] = None,
                 color_scheme: Optional[ColorScheme] = None):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color or (60, 60, 70)
        self.text_color = text_color or (255, 255, 255)
        self.color_scheme = color_scheme or ColorScheme(
            background=self.color,
            grid_bg=(80, 80, 90),
            accent=(100, 149, 237)
        )
        
        self.hovered = False
        self.clicked = False
        self.enabled = True
        
        self.font = get_font(min(height // 2, 36))
    
    def update(self):
        """Update button state"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked and self.rect.collidepoint(event.pos):
                self.clicked = False
                if self.callback:
                    self.callback()
                    return True
            self.clicked = False
        
        return False
    
    def draw(self):
        """Draw the button"""
        color = self.color
        if self.hovered:
            color = tuple(min(255, c + 30) for c in self.color)
        
        if self.clicked:
            color = tuple(min(255, c + 50) for c in self.color)
        
        pygame.draw.rect(self.screen, color, self.rect, border_radius=8)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def render(self, surface: pygame.Surface):
        """Render the button (alternative method)"""
        color = self.color
        if self.hovered:
            color = tuple(min(255, c + 30) for c in self.color)
        
        if self.clicked:
            color = tuple(min(255, c + 50) for c in self.color)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Title:
    """Title text component"""
    
    def __init__(self, text: str, x: int, y: int, font_size: int = 64,
                 color: Tuple[int, int, int] = (255, 255, 255),
                 center: bool = True):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color
        self.center = center
        self.font = get_font(font_size)
    
    def draw(self, surface: pygame.Surface):
        """Draw the title"""
        text_surface = self.font.render(self.text, True, self.color)
        if self.center:
            rect = text_surface.get_rect(center=(self.x, self.y))
        else:
            rect = text_surface.get_rect(topleft=(self.x, self.y))
        surface.blit(text_surface, rect)


class Slider:
    """Volume/setting slider component"""
    
    def __init__(self, screen: pygame.Surface, x: int, y: int, width: int, height: int,
                 value: float = 0.5, val_range: tuple = (0, 1), label: str = ""):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = val_range[0]
        self.max_val = val_range[1]
        self._value = max(self.min_val, min(self.max_val, value))
        self.label = label
        self.dragging = False
        
        self.handle_radius = height
        self.track_height = 4
    
    @property
    def value(self) -> float:
        return self._value
    
    @value.setter
    def value(self, new_value: float):
        self._value = max(self.min_val, min(self.max_val, new_value))
    
    def get_handle_x(self) -> int:
        """Get x position of handle"""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_x = self.get_handle_x()
            handle_rect = pygame.Rect(
                handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value(event.pos[0])
                return True
        
        return False
    
    def _update_value(self, mouse_x: int):
        """Update slider value based on mouse position"""
        ratio = (mouse_x - self.rect.x) / self.rect.width
        ratio = max(0, min(1, ratio))
        new_value = self.min_val + ratio * (self.max_val - self.min_val)
        self._value = new_value
    
    def update(self):
        """Update slider state"""
        pass
    
    def draw(self):
        """Draw the slider"""
        self.render(self.screen)
    
    def render(self, surface: pygame.Surface):
        """Render the slider"""
        track_y = self.rect.centery - self.track_height // 2
        track_rect = pygame.Rect(
            self.rect.x, track_y,
            self.rect.width, self.track_height
        )
        pygame.draw.rect(surface, (80, 80, 90), track_rect, border_radius=2)
        
        filled_width = int((self.value - self.min_val) / 
                          (self.max_val - self.min_val) * self.rect.width)
        if filled_width > 0:
            filled_rect = pygame.Rect(
                self.rect.x, track_y,
                filled_width, self.track_height
            )
            pygame.draw.rect(surface, (100, 149, 237), filled_rect, border_radius=2)
        
        handle_x = self.get_handle_x()
        pygame.draw.circle(
            surface, (255, 255, 255),
            (handle_x, self.rect.centery),
            self.handle_radius
        )
        pygame.draw.circle(
            surface, (100, 149, 237),
            (handle_x, self.rect.centery),
            self.handle_radius - 2
        )
        
        font = get_font(24)
        text = f"{self.label}: {int(self.value * 100)}%"
        text_surface = font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, (self.rect.x, self.rect.y - 25))


class Toggle:
    """Toggle switch component"""
    
    def __init__(self, screen: pygame.Surface, x: int, y: int, width: int, height: int,
                 value: bool = False, label: str = ""):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value = value
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.value = not self.value
                return True
        return False
    
    def update(self):
        """Update toggle state"""
        pass
    
    def draw(self):
        """Draw the toggle"""
        self.render(self.screen)
    
    def render(self, surface: pygame.Surface):
        """Render the toggle"""
        bg_color = (100, 149, 237) if self.value else (80, 80, 90)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.rect.height // 2)
        
        knob_x = self.rect.right - self.rect.height + 4 if self.value else self.rect.x + 4
        pygame.draw.circle(
            surface, (255, 255, 255),
            (knob_x, self.rect.centery),
            self.rect.height // 2 - 4
        )
        
        font = get_font(24)
        text_surface = font.render(self.label, True, (255, 255, 255))
        surface.blit(text_surface, (self.rect.right + 10, self.rect.y))


class Tile:
    """Game tile component with animation support"""
    
    def __init__(self, value: int, x: int, y: int, size: int):
        self.value = value
        self.x = x
        self.y = y
        self.size = size
        self.target_x = x
        self.target_y = y
        self.scale = 1.0
        self.target_scale = 1.0
        self.rotation = 0
        self.animating = False
        self.new_tile = False
        self.merged_tile = False
    
    def set_position(self, x: int, y: int, animate: bool = False):
        """Set tile position"""
        if animate:
            self.target_x = x
            self.target_y = y
            self.animating = True
        else:
            self.x = x
            self.y = y
            self.target_x = x
            self.target_y = y
    
    def update(self, delta_time: float):
        """Update tile animation"""
        if self.animating:
            speed = 8 * delta_time
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            
            if abs(dx) < 1 and abs(dy) < 1:
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
            else:
                self.x += dx * speed
                self.y += dy * speed
        
        ds = self.target_scale - self.scale
        if abs(ds) > 0.01:
            self.scale += ds * 8 * delta_time
        else:
            self.scale = self.target_scale
    
    def render(self, surface: pygame.Surface):
        """Render the tile"""
        if self.value == 0:
            return
        
        color = TILE_COLORS.get(self.value, (60, 60, 60))
        text_color = TILE_TEXT_COLORS.get(self.value, (255, 255, 255))
        
        scaled_size = int(self.size * self.scale)
        draw_x = int(self.x + (self.size - scaled_size) / 2)
        draw_y = int(self.y + (self.size - scaled_size) / 2)
        
        tile_rect = pygame.Rect(draw_x, draw_y, scaled_size, scaled_size)
        pygame.draw.rect(surface, color, tile_rect, border_radius=8)
        
        font_size = min(scaled_size // 3, 40)
        font = get_font(font_size)
        text_surface = font.render(str(self.value), True, text_color)
        text_rect = text_surface.get_rect(center=tile_rect.center)
        surface.blit(text_surface, text_rect)


class ProgressBar:
    """Progress bar component"""
    
    def __init__(self, screen: pygame.Surface, x: int, y: int, width: int, height: int,
                 max_value: float = 100.0, value: float = 0.0,
                 bg_color: Tuple[int, int, int] = (60, 60, 70),
                 fg_color: Tuple[int, int, int] = (100, 149, 237)):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.value = value
        self.bg_color = bg_color
        self.fg_color = fg_color
    
    def set_value(self, value: float):
        """Set progress value"""
        self.value = max(0, min(self.max_value, value))
    
    def update(self):
        """Update progress bar state"""
        pass
    
    def draw(self):
        """Draw the progress bar"""
        self.render(self.screen)
    
    def render(self, surface: pygame.Surface):
        """Render the progress bar"""
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=4)
        
        ratio = self.value / self.max_value
        fill_width = int(ratio * (self.rect.width - 4))
        
        if fill_width > 0:
            fill_rect = pygame.Rect(
                self.rect.x + 2, self.rect.y + 2,
                fill_width, self.rect.height - 4
            )
            pygame.draw.rect(surface, self.fg_color, fill_rect, border_radius=3)


class StarDisplay:
    """Star rating display component"""
    
    def __init__(self, screen: pygame.Surface, x: int, y: int, width: int, height: int,
                 stars: int = 0, max_stars: int = 3):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.size = height
        self.stars = stars
        self.max_stars = max_stars
    
    def update(self):
        """Update star display state"""
        pass
    
    def draw(self):
        """Draw the star display"""
        self.render(self.screen)
    
    def render(self, surface: pygame.Surface):
        """Render the stars"""
        font = get_font(self.size)
        
        total_width = self.max_stars * (self.size + 5) - 5
        start_x = self.x + (self.width - total_width) // 2
        
        for i in range(self.max_stars):
            star_x = start_x + i * (self.size + 5)
            if i < self.stars:
                text = "★"
                color = (255, 215, 0)
            else:
                text = "☆"
                color = (100, 100, 100)
            
            text_surface = font.render(text, True, color)
            surface.blit(text_surface, (star_x, self.y))
