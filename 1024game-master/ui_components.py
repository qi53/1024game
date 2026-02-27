"""
1024 Game - UI Components Module
Reusable UI components for the game interface
"""

import pygame
import math
from typing import Tuple, Optional, Callable, List
from dataclasses import dataclass
import config


@dataclass
class ButtonStyle:
    """Button appearance style"""
    normal_color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    pressed_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    border_color: Optional[Tuple[int, int, int]] = None
    border_width: int = 0
    border_radius: int = 8


class Button:
    """Interactive button component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        style: ButtonStyle,
        on_click: Optional[Callable] = None,
        icon: Optional[str] = None
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.style = style
        self.on_click = on_click
        self.icon = icon
        
        self.is_hovered = False
        self.is_pressed = False
        self.animation_scale = 1.0
        self.target_scale = 1.0
        
        # Pre-render text
        self._update_text_surface()
    
    def _update_text_surface(self) -> None:
        """Update the text surface"""
        self.text_surface = self.font.render(self.text, True, self.style.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Update button state and return True if clicked"""
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Animate scale
        if self.is_hovered:
            self.target_scale = 1.05
        else:
            self.target_scale = 1.0
        
        self.animation_scale += (self.target_scale - self.animation_scale) * 0.2
        
        # Handle click
        clicked = False
        if self.is_hovered and mouse_pressed:
            if not self.is_pressed:
                self.is_pressed = True
        elif self.is_pressed and not mouse_pressed:
            self.is_pressed = False
            if self.is_hovered:
                clicked = True
                if self.on_click:
                    self.on_click()
        elif not mouse_pressed:
            self.is_pressed = False
        
        return clicked
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button"""
        # Determine color
        if self.is_pressed:
            color = self.style.pressed_color
        elif self.is_hovered:
            color = self.style.hover_color
        else:
            color = self.style.normal_color
        
        # Calculate scaled rect
        if self.animation_scale != 1.0:
            scale_diff = (self.animation_scale - 1.0)
            new_width = int(self.rect.width * self.animation_scale)
            new_height = int(self.rect.height * self.animation_scale)
            new_x = self.rect.centerx - new_width // 2
            new_y = self.rect.centery - new_height // 2
            draw_rect = pygame.Rect(new_x, new_y, new_width, new_height)
        else:
            draw_rect = self.rect
        
        # Draw button background
        pygame.draw.rect(
            surface,
            color,
            draw_rect,
            border_radius=self.style.border_radius
        )
        
        # Draw border
        if self.style.border_width > 0 and self.style.border_color:
            pygame.draw.rect(
                surface,
                self.style.border_color,
                draw_rect,
                width=self.style.border_width,
                border_radius=self.style.border_radius
            )
        
        # Draw text
        if self.animation_scale != 1.0:
            scaled_text = pygame.transform.scale(
                self.text_surface,
                (int(self.text_surface.get_width() * self.animation_scale),
                 int(self.text_surface.get_height() * self.animation_scale))
            )
            text_rect = scaled_text.get_rect(center=draw_rect.center)
            surface.blit(scaled_text, text_rect)
        else:
            surface.blit(self.text_surface, self.text_rect)


class Slider:
    """Volume/setting slider component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_value: float,
        max_value: float,
        initial_value: float,
        theme: dict
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.theme = theme
        
        self.handle_radius = height // 2
        self.track_height = height // 3
        self.dragging = False
        
        self._update_handle_position()
    
    def _update_handle_position(self) -> None:
        """Update handle position based on value"""
        value_ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        self.handle_x = self.rect.x + value_ratio * self.rect.width
        self.handle_y = self.rect.centery
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool, mouse_down: bool) -> bool:
        """Update slider and return True if value changed"""
        changed = False
        
        handle_rect = pygame.Rect(
            self.handle_x - self.handle_radius,
            self.handle_y - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2
        )
        
        if mouse_down and (handle_rect.collidepoint(mouse_pos) or self.dragging):
            self.dragging = True
        
        if self.dragging:
            if mouse_pressed:
                # Update value based on mouse position
                rel_x = max(0, min(mouse_pos[0] - self.rect.x, self.rect.width))
                ratio = rel_x / self.rect.width
                new_value = self.min_value + ratio * (self.max_value - self.min_value)
                
                if abs(new_value - self.value) > 0.001:
                    self.value = new_value
                    changed = True
                    self._update_handle_position()
            else:
                self.dragging = False
        
        return changed
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the slider"""
        # Draw track
        track_rect = pygame.Rect(
            self.rect.x,
            self.handle_y - self.track_height // 2,
            self.rect.width,
            self.track_height
        )
        pygame.draw.rect(
            surface,
            self.theme.get("empty_cell", (200, 200, 200)),
            track_rect,
            border_radius=self.track_height // 2
        )
        
        # Draw filled portion
        filled_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        filled_rect = pygame.Rect(
            self.rect.x,
            self.handle_y - self.track_height // 2,
            filled_width,
            self.track_height
        )
        pygame.draw.rect(
            surface,
            self.theme.get("button", (100, 100, 100)),
            filled_rect,
            border_radius=self.track_height // 2
        )
        
        # Draw handle
        pygame.draw.circle(
            surface,
            self.theme.get("button_hover", (150, 150, 150)),
            (int(self.handle_x), int(self.handle_y)),
            self.handle_radius
        )


class Toggle:
    """Toggle switch component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        initial_state: bool,
        theme: dict
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state
        self.theme = theme
        self.animation_progress = 1.0 if initial_state else 0.0
        self.target_progress = self.animation_progress
    
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> bool:
        """Update toggle and return True if state changed"""
        changed = False
        
        if mouse_clicked and self.rect.collidepoint(mouse_pos):
            self.state = not self.state
            self.target_progress = 1.0 if self.state else 0.0
            changed = True
        
        # Animate
        diff = self.target_progress - self.animation_progress
        self.animation_progress += diff * 0.2
        
        return changed
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the toggle"""
        # Background
        bg_color = self._lerp_color(
            self.theme.get("empty_cell", (200, 200, 200)),
            self.theme.get("button", (100, 200, 100)),
            self.animation_progress
        )
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.rect.height // 2)
        
        # Handle
        handle_radius = self.rect.height // 2 - 4
        handle_x = self._lerp(
            self.rect.x + handle_radius + 4,
            self.rect.right - handle_radius - 4,
            self.animation_progress
        )
        handle_y = self.rect.centery
        
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(handle_x), int(handle_y)),
            handle_radius
        )
    
    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t
    
    @staticmethod
    def _lerp_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )


class ProgressBar:
    """Progress bar component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        theme: dict
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = 0.0  # 0.0 to 1.0
        self.theme = theme
    
    def set_progress(self, progress: float) -> None:
        """Set progress value (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the progress bar"""
        # Background
        pygame.draw.rect(
            surface,
            self.theme.get("empty_cell", (200, 200, 200)),
            self.rect,
            border_radius=self.rect.height // 2
        )
        
        # Progress fill
        if self.progress > 0:
            fill_width = int(self.rect.width * self.progress)
            fill_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                fill_width,
                self.rect.height
            )
            pygame.draw.rect(
                surface,
                self.theme.get("button", (100, 100, 100)),
                fill_rect,
                border_radius=self.rect.height // 2
            )


class StarRating:
    """Star rating display component"""
    
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        max_stars: int = 3
    ):
        self.x = x
        self.y = y
        self.size = size
        self.max_stars = max_stars
        self.filled_stars = 0
        self.spacing = size // 4
    
    def set_rating(self, rating: int) -> None:
        """Set the number of filled stars"""
        self.filled_stars = max(0, min(rating, self.max_stars))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the star rating"""
        for i in range(self.max_stars):
            x = self.x + i * (self.size + self.spacing)
            self._draw_star(surface, x, self.y, self.size, i < self.filled_stars)
    
    def _draw_star(self, surface: pygame.Surface, x: int, y: int, size: int, filled: bool) -> None:
        """Draw a single star"""
        color = (255, 215, 0) if filled else (150, 150, 150)  # Gold or gray
        
        points = []
        center_x = x + size // 2
        center_y = y + size // 2
        outer_radius = size // 2
        inner_radius = size // 4
        
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = center_x + radius * math.cos(angle)
            py = center_y - radius * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (100, 100, 100), points, 1)


class AnimatedTile:
    """Animated game tile component"""
    
    def __init__(
        self,
        value: int,
        x: int,
        y: int,
        size: int,
        theme: dict,
        is_new: bool = False,
        is_merging: bool = False
    ):
        self.value = value
        self.x = x
        self.y = y
        self.size = size
        self.theme = theme
        
        self.scale = 0.0 if is_new else 1.0
        self.target_scale = 1.0
        self.pulse = 0.0
        self.is_merging = is_merging
        
        # Colors
        tile_colors = theme.get("tile_colors", {})
        self.bg_color = tile_colors.get(value, (60, 58, 50))
        self.text_color = theme.get("text_light" if value > 4 else "text_dark", (0, 0, 0))
    
    def update(self) -> None:
        """Update animation"""
        # Scale animation
        diff = self.target_scale - self.scale
        self.scale += diff * 0.15
        
        # Pulse animation for merges
        if self.is_merging:
            self.pulse += 0.2
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the tile"""
        # Calculate draw size with animation
        draw_size = int(self.size * self.scale)
        
        # Add pulse effect
        if self.is_merging:
            pulse_size = int(draw_size + math.sin(self.pulse) * 5)
        else:
            pulse_size = draw_size
        
        # Center the tile
        offset = (self.size - pulse_size) // 2
        draw_x = self.x + offset
        draw_y = self.y + offset
        
        # Draw tile background
        rect = pygame.Rect(draw_x, draw_y, pulse_size, pulse_size)
        border_radius = 8
        pygame.draw.rect(surface, self.bg_color, rect, border_radius=border_radius)
        
        # Draw value text
        if self.value > 0:
            text = str(self.value)
            text_surface = font.render(text, True, self.text_color)
            
            # Scale text with tile
            if self.scale < 1.0:
                text_size = int(text_surface.get_width() * self.scale)
                text_surface = pygame.transform.scale(
                    text_surface,
                    (text_size, int(text_surface.get_height() * self.scale))
                )
            
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)


class Notification:
    """Floating notification component"""
    
    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: Tuple[int, int, int] = (255, 255, 255),
        bg_color: Tuple[int, int, int] = (0, 0, 0),
        duration: int = 120
    ):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.bg_color = bg_color
        self.duration = duration
        self.lifetime = duration
        
        # Pre-render
        self.text_surface = font.render(text, True, color)
        padding = 10
        self.bg_rect = self.text_surface.get_rect().inflate(padding * 2, padding * 2)
        self.bg_rect.center = (x, y)
    
    def update(self) -> bool:
        """Update notification and return True if still alive"""
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the notification"""
        # Calculate alpha
        alpha = int(255 * (self.lifetime / self.duration))
        if self.lifetime < 30:
            alpha = int(255 * (self.lifetime / 30))
        
        # Create surfaces with alpha
        bg_surface = pygame.Surface(self.bg_rect.size, pygame.SRCALPHA)
        bg_color_with_alpha = (*self.bg_color[:3], alpha)
        pygame.draw.rect(bg_surface, bg_color_with_alpha, bg_surface.get_rect(), border_radius=8)
        
        text_surface = self.text_surface.copy()
        text_surface.set_alpha(alpha)
        
        # Draw
        surface.blit(bg_surface, self.bg_rect)
        text_rect = text_surface.get_rect(center=self.bg_rect.center)
        surface.blit(text_surface, text_rect)
