#!/usr/bin/env python3
"""
1024 Game - UI Manager
Handles all UI elements and screens
"""

import pygame
import math
from typing import Dict, List, Any, Tuple, Optional, Callable
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, TILE_SIZE, TILE_MARGIN
from src.ui_components import Menu, Button
from src.settings_menu import SettingsMenu
from src.achievements import AchievementsMenu


class MainMenu(Menu):
    """Main menu screen"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, data_manager):
        """Initialize the main menu"""
        super().__init__(screen, theme_manager, audio_manager)
        self.data_manager = data_manager
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2 - 150
        
        self.buttons.append(Button(
            button_x, start_y, button_width, button_height,
            "New Game", self.menu_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('level_select')
        ))
        
        self.buttons.append(Button(
            button_x, start_y + button_height + button_spacing, button_width, button_height,
            "Continue", self.menu_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('game') if self.data_manager.has_save() else None
        ))
        
        self.buttons.append(Button(
            button_x, start_y + 2 * (button_height + button_spacing), button_width, button_height,
            "Settings", self.menu_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('settings')
        ))
        
        self.buttons.append(Button(
            button_x, start_y + 3 * (button_height + button_spacing), button_width, button_height,
            "Achievements", self.menu_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('achievements')
        ))
        
        self.buttons.append(Button(
            button_x, start_y + 4 * (button_height + button_spacing), button_width, button_height,
            "Exit", self.menu_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('exit')
        ))
        
        # Disable continue button if no save
        if not self.data_manager.has_save():
            self.buttons[1].enabled = False
            
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = 'exit'
                
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        for button in self.buttons:
            if button.update(mouse_pos, mouse_clicked):
                self.audio_manager.play_sound('button_click')
                
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the main menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Draw title
        title_text = self.title_font.render("1024", True, self.theme_manager.get_color('text_dark'))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.small_font.render("A Puzzle Game", True, self.theme_manager.get_color('text_dark'))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
            
        # Draw version info
        version_text = self.small_font.render("v1.0", True, self.theme_manager.get_color('text_dark'))
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        self.screen.blit(version_text, version_rect)


class LevelSelectMenu(Menu):
    """Level selection menu"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, level_manager, data_manager):
        """Initialize the level select menu"""
        super().__init__(screen, theme_manager, audio_manager)
        self.level_manager = level_manager
        self.data_manager = data_manager
        self.title_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create back button
        button_width = 100
        button_height = 40
        self.back_button = Button(
            20, 20, button_width, button_height,
            "Back", self.menu_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('main_menu')
        )
        
        # Level grid settings
        self.levels_per_row = 5
        self.level_button_size = 80
        self.level_button_spacing = 20
        self.grid_start_x = (SCREEN_WIDTH - (self.levels_per_row * (self.level_button_size + self.level_button_spacing) - self.level_button_spacing)) // 2
        self.grid_start_y = 150
        
        # Create level buttons
        self.level_buttons = []
        for i in range(1, 21):  # 20 levels
            row = (i - 1) // self.levels_per_row
            col = (i - 1) % self.levels_per_row
            
            x = self.grid_start_x + col * (self.level_button_size + self.level_button_spacing)
            y = self.grid_start_y + row * (self.level_button_size + self.level_button_spacing)
            
            # Check if level is unlocked
            unlocked = i == 1 or self.data_manager.get_stats().get('levels_completed', 0) >= i - 1
            
            self.level_buttons.append({
                'rect': pygame.Rect(x, y, self.level_button_size, self.level_button_size),
                'level': i,
                'unlocked': unlocked
            })
            
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = 'main_menu'
                
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update back button
        if self.back_button.update(mouse_pos, mouse_clicked):
            self.audio_manager.play_sound('button_click')
            
        # Update level buttons
        for level_button in self.level_buttons:
            if level_button['unlocked'] and level_button['rect'].collidepoint(mouse_pos) and mouse_clicked:
                self.audio_manager.play_sound('button_click')
                self.level_manager.set_current_level(level_button['level'])
                self.next_screen = 'game'
                
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the level select menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Draw title
        title_text = self.title_font.render("Select Level", True, self.theme_manager.get_color('text_dark'))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Draw level buttons
        completed_levels = self.data_manager.get_stats().get('levels_completed', 0)
        
        for level_button in self.level_buttons:
            level = level_button['level']
            rect = level_button['rect']
            unlocked = level_button['unlocked']
            completed = level <= completed_levels
            
            # Determine button color
            if not unlocked:
                color = tuple(c // 2 for c in self.theme_manager.get_color('button'))
                text_color = tuple(c // 2 for c in self.theme_manager.get_color('text_light'))
            elif completed:
                color = self.theme_manager.get_color('button')
                text_color = self.theme_manager.get_color('text_light')
            else:
                color = self.theme_manager.get_color('button')
                text_color = self.theme_manager.get_color('text_light')
                
            # Check hover
            is_hovered = rect.collidepoint(pygame.mouse.get_pos()) and unlocked
            if is_hovered:
                color = self.theme_manager.get_color('button_hover')
                
            # Draw button
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # Draw level number
            level_text = self.menu_font.render(str(level), True, text_color)
            level_rect = level_text.get_rect(center=rect.center)
            self.screen.blit(level_text, level_rect)
            
            # Draw completion indicator
            if completed:
                pygame.draw.circle(self.screen, (0, 200, 0), (rect.right - 10, rect.top + 10), 5)
                
        # Draw difficulty indicators
        difficulty_y = self.grid_start_y + 4 * (self.level_button_size + self.level_button_spacing) + 40
        
        difficulties = [
            ("Easy (1-5)", self.theme_manager.get_color('text_dark')),
            ("Medium (6-10)", self.theme_manager.get_color('text_dark')),
            ("Hard (11-15)", self.theme_manager.get_color('text_dark')),
            ("Expert (16-20)", self.theme_manager.get_color('text_dark'))
        ]
        
        for i, (text, color) in enumerate(difficulties):
            diff_text = self.small_font.render(text, True, color)
            diff_x = self.grid_start_x + i * (SCREEN_WIDTH - 2 * self.grid_start_x) // 4
            diff_rect = diff_text.get_rect(midleft=(diff_x, difficulty_y))
            self.screen.blit(diff_text, diff_rect)


class UIManager:
    """Manages all UI screens and transitions"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, level_manager, data_manager):
        """Initialize the UI manager"""
        self.screen = screen
        self.theme_manager = theme_manager
        self.audio_manager = audio_manager
        self.level_manager = level_manager
        self.data_manager = data_manager
        
        self.current_screen = 'main_menu'
        self.screens = {
            'main_menu': MainMenu(screen, theme_manager, audio_manager, data_manager),
            'level_select': LevelSelectMenu(screen, theme_manager, audio_manager, level_manager, data_manager),
            'settings': SettingsMenu(screen, theme_manager, audio_manager, data_manager),
            'achievements': AchievementsMenu(screen, theme_manager, audio_manager, data_manager)
        }
        
    def set_screen(self, screen_name: str) -> None:
        """Set the current screen"""
        if screen_name in self.screens:
            self.current_screen = screen_name
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if self.current_screen in self.screens:
            self.screens[self.current_screen].handle_event(event)
            
    def update(self, dt: float) -> Optional[str]:
        """Update the current screen"""
        if self.current_screen in self.screens:
            next_screen = self.screens[self.current_screen].update(dt)
            
            if next_screen:
                if next_screen == 'exit':
                    return 'exit'
                elif next_screen in self.screens:
                    self.set_screen(next_screen)
                    
        return None
        
    def draw(self) -> None:
        """Draw the current screen"""
        if self.current_screen in self.screens:
            self.screens[self.current_screen].draw()