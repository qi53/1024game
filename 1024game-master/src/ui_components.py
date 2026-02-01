#!/usr/bin/env python3
"""
1024 Game - UI Components
Base UI components for menus and interfaces
"""

import pygame
import math
from typing import Dict, List, Any, Tuple, Optional, Callable
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, TILE_SIZE, TILE_MARGIN


class Button:
    """Represents a clickable button"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, color: Tuple[int, int, int],
                 hover_color: Tuple[int, int, int], text_color: Tuple[int, int, int],
                 action: Callable = None, border_radius: int = 5):
        """Initialize a button"""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.border_radius = border_radius
        self.is_hovered = False
        self.is_pressed = False
        self.enabled = True
        
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> bool:
        """Update button state and check for clicks"""
        self.is_hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        
        if self.is_hovered and mouse_clicked and not self.is_pressed:
            self.is_pressed = True
            if self.action:
                self.action()
            return True
        elif not mouse_clicked:
            self.is_pressed = False
            
        return False
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button"""
        if not self.enabled:
            color = tuple(c // 2 for c in self.color)
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
            
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        
        # Draw button border
        pygame.draw.rect(surface, self.text_color, self.rect, 2, border_radius=self.border_radius)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Menu:
    """Base class for all menus"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager):
        """Initialize the menu"""
        self.screen = screen
        self.theme_manager = theme_manager
        self.audio_manager = audio_manager
        self.buttons: List[Button] = []
        self.running = True
        self.next_screen = None
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        pass
        
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        return None
        
    def draw(self) -> None:
        """Draw the menu"""
        pass