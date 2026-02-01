#!/usr/bin/env python3
"""
1024 Game - Settings Menu
Handles game settings and configuration
"""

import pygame
from typing import Dict, List, Any, Tuple, Optional, Callable
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui_components import Menu, Button


class SettingsMenu(Menu):
    """Settings menu screen"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, data_manager):
        """Initialize the settings menu"""
        super().__init__(screen, theme_manager, audio_manager)
        self.data_manager = data_manager
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.section_font = pygame.font.Font(None, 36)
        self.option_font = pygame.font.Font(None, 28)
        self.value_font = pygame.font.Font(None, 24)
        
        # Settings categories
        self.settings_categories = {
            'audio': {
                'title': 'Audio Settings',
                'options': {
                    'master_volume': {'name': 'Master Volume', 'type': 'slider', 'min': 0, 'max': 100, 'default': 70},
                    'sfx_volume': {'name': 'SFX Volume', 'type': 'slider', 'min': 0, 'max': 100, 'default': 80},
                    'music_volume': {'name': 'Music Volume', 'type': 'slider', 'min': 0, 'max': 100, 'default': 50},
                    'sfx_enabled': {'name': 'Sound Effects', 'type': 'toggle', 'default': True},
                    'music_enabled': {'name': 'Background Music', 'type': 'toggle', 'default': True}
                }
            },
            'visual': {
                'title': 'Visual Settings',
                'options': {
                    'current_theme': {'name': 'Theme', 'type': 'selector', 'options': ['default', 'dark', 'ocean', 'forest', 'sunset'], 'default': 'default'},
                    'show_fps': {'name': 'Show FPS', 'type': 'toggle', 'default': False},
                    'show_grid': {'name': 'Show Grid', 'type': 'toggle', 'default': True},
                    'animation_speed': {'name': 'Animation Speed', 'type': 'slider', 'min': 0.5, 'max': 2.0, 'step': 0.1, 'default': 1.0},
                    'particle_effects': {'name': 'Particle Effects', 'type': 'toggle', 'default': True}
                }
            },
            'gameplay': {
                'title': 'Gameplay Settings',
                'options': {
                    'auto_save': {'name': 'Auto Save', 'type': 'toggle', 'default': True},
                    'undo_limit': {'name': 'Undo Limit', 'type': 'selector', 'options': ['3', '5', '10', 'unlimited'], 'default': '5'},
                    'show_hints': {'name': 'Show Hints', 'type': 'toggle', 'default': True},
                    'confirm_quit': {'name': 'Confirm Quit', 'type': 'toggle', 'default': True}
                }
            }
        }
        
        # Current settings values
        self.current_settings = self.data_manager.get_settings().copy()
        
        # UI elements
        self.buttons = []
        self.sliders = []
        self.toggles = []
        self.selectors = []
        
        # Create UI elements
        self._create_ui_elements()
        
    def _create_ui_elements(self) -> None:
        """Create UI elements for settings"""
        # Back button
        self.back_button = Button(
            20, 20, 100, 40,
            "Back", self.section_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('main_menu')
        )
        
        # Reset button
        self.reset_button = Button(
            SCREEN_WIDTH - 120, 20, 100, 40,
            "Reset", self.section_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=self.reset_settings
        )
        
        # Create settings elements
        y_offset = 100
        for category_key, category in self.settings_categories.items():
            # Category title
            y_offset += 20
            
            # Settings options
            for option_key, option in category['options'].items():
                option_y = y_offset
                option_name = option['name']
                option_type = option['type']
                
                if option_type == 'slider':
                    self._create_slider(option_key, option_name, option, option_y)
                    y_offset += 60
                elif option_type == 'toggle':
                    self._create_toggle(option_key, option_name, option, option_y)
                    y_offset += 50
                elif option_type == 'selector':
                    self._create_selector(option_key, option_name, option, option_y)
                    y_offset += 60
                    
            y_offset += 20  # Space between categories
            
    def _create_slider(self, key: str, name: str, option: Dict[str, Any], y: int) -> None:
        """Create a slider element"""
        x = SCREEN_WIDTH // 2 - 200
        width = 400
        height = 20
        
        # Get current value
        current_value = self.current_settings.get(key, option['default'])
        
        # Create slider
        slider = {
            'key': key,
            'name': name,
            'rect': pygame.Rect(x, y, width, height),
            'min': option['min'],
            'max': option['max'],
            'step': option.get('step', 1),
            'value': current_value,
            'dragging': False
        }
        
        self.sliders.append(slider)
        
    def _create_toggle(self, key: str, name: str, option: Dict[str, Any], y: int) -> None:
        """Create a toggle element"""
        x = SCREEN_WIDTH // 2 - 200
        width = 30
        height = 30
        
        # Get current value
        current_value = self.current_settings.get(key, option['default'])
        
        # Create toggle
        toggle = {
            'key': key,
            'name': name,
            'rect': pygame.Rect(x, y, width, height),
            'value': current_value
        }
        
        self.toggles.append(toggle)
        
    def _create_selector(self, key: str, name: str, option: Dict[str, Any], y: int) -> None:
        """Create a selector element"""
        x = SCREEN_WIDTH // 2 - 200
        width = 400
        height = 30
        
        # Get current value
        current_value = self.current_settings.get(key, option['default'])
        
        # Create selector
        selector = {
            'key': key,
            'name': name,
            'rect': pygame.Rect(x, y, width, height),
            'options': option['options'],
            'current_index': option['options'].index(current_value) if current_value in option['options'] else 0
        }
        
        self.selectors.append(selector)
        
    def reset_settings(self) -> None:
        """Reset all settings to defaults"""
        for category_key, category in self.settings_categories.items():
            for option_key, option in category['options'].items():
                self.current_settings[option_key] = option['default']
                
        # Update UI elements
        self._update_ui_elements()
        
        # Play sound
        self.audio_manager.play_sound('button_click')
        
    def _update_ui_elements(self) -> None:
        """Update UI elements to match current settings"""
        # Update sliders
        for slider in self.sliders:
            slider['value'] = self.current_settings.get(slider['key'], slider['min'])
            
        # Update toggles
        for toggle in self.toggles:
            toggle['value'] = self.current_settings.get(toggle['key'], False)
            
        # Update selectors
        for selector in self.selectors:
            current_value = self.current_settings.get(selector['key'], selector['options'][0])
            if current_value in selector['options']:
                selector['current_index'] = selector['options'].index(current_value)
                
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        # Save settings before transitioning
        self.data_manager.save_settings(self.current_settings)
        
        # Apply theme if changed
        if self.current_settings.get('current_theme') != self.theme_manager.current_theme_name:
            self.theme_manager.set_theme(self.current_settings.get('current_theme'))
            
        # Apply audio settings
        self.audio_manager.set_volume(self.current_settings.get('master_volume', 70) / 100)
        self.audio_manager.set_sfx_volume(self.current_settings.get('sfx_volume', 80) / 100)
        self.audio_manager.set_music_volume(self.current_settings.get('music_volume', 50) / 100)
        
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_next_screen('main_menu')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check back button
                if self.back_button.rect.collidepoint(mouse_pos):
                    self.back_button.update(mouse_pos, True)
                    return
                    
                # Check reset button
                if self.reset_button.rect.collidepoint(mouse_pos):
                    self.reset_button.update(mouse_pos, True)
                    return
                    
                # Check sliders
                for slider in self.sliders:
                    if slider['rect'].collidepoint(mouse_pos):
                        slider['dragging'] = True
                        return
                        
                # Check toggles
                for toggle in self.toggles:
                    if toggle['rect'].collidepoint(mouse_pos):
                        toggle['value'] = not toggle['value']
                        self.current_settings[toggle['key']] = toggle['value']
                        self.audio_manager.play_sound('button_click')
                        return
                        
                # Check selectors
                for selector in self.selectors:
                    if selector['rect'].collidepoint(mouse_pos):
                        # Calculate which option was clicked
                        option_width = selector['rect'].width / len(selector['options'])
                        relative_x = mouse_pos[0] - selector['rect'].x
                        clicked_index = int(relative_x / option_width)
                        
                        if 0 <= clicked_index < len(selector['options']):
                            selector['current_index'] = clicked_index
                            self.current_settings[selector['key']] = selector['options'][clicked_index]
                            self.audio_manager.play_sound('button_click')
                        return
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                # Stop dragging all sliders
                for slider in self.sliders:
                    slider['dragging'] = False
                    
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update buttons
        self.back_button.update(mouse_pos, mouse_clicked)
        self.reset_button.update(mouse_pos, mouse_clicked)
        
        # Update sliders
        for slider in self.sliders:
            if slider['dragging']:
                # Calculate new value based on mouse position
                relative_x = mouse_pos[0] - slider['rect'].x
                relative_x = max(0, min(relative_x, slider['rect'].width))
                
                # Calculate value
                value_range = slider['max'] - slider['min']
                new_value = slider['min'] + (relative_x / slider['rect'].width) * value_range
                
                # Apply step
                if slider['step'] >= 1:
                    new_value = int(new_value / slider['step']) * slider['step']
                else:
                    new_value = round(new_value / slider['step'] * 10) / 10 * slider['step']
                    
                slider['value'] = new_value
                self.current_settings[slider['key']] = new_value
                
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the settings menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Draw title
        title_text = self.title_font.render("Settings", True, self.theme_manager.get_color('text_dark'))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        self.back_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        
        # Draw settings elements
        y_offset = 100
        
        for category_key, category in self.settings_categories.items():
            # Category title
            y_offset += 20
            category_text = self.section_font.render(category['title'], True, self.theme_manager.get_color('text_dark'))
            category_rect = category_text.get_rect(midleft=(SCREEN_WIDTH // 2 - 250, y_offset))
            self.screen.blit(category_text, category_rect)
            y_offset += 40
            
            # Settings options
            for option_key, option in category['options'].items():
                option_name = option['name']
                option_type = option['type']
                
                # Draw option name
                name_text = self.option_font.render(option_name, True, self.theme_manager.get_color('text_dark'))
                name_rect = name_text.get_rect(midleft=(SCREEN_WIDTH // 2 - 250, y_offset + 15))
                self.screen.blit(name_text, name_rect)
                
                if option_type == 'slider':
                    # Draw slider
                    self._draw_slider(option_key, y_offset)
                    y_offset += 60
                elif option_type == 'toggle':
                    # Draw toggle
                    self._draw_toggle(option_key, y_offset)
                    y_offset += 50
                elif option_type == 'selector':
                    # Draw selector
                    self._draw_selector(option_key, y_offset)
                    y_offset += 60
                    
            y_offset += 20  # Space between categories
            
    def _draw_slider(self, key: str, y: int) -> None:
        """Draw a slider element"""
        # Find the slider
        slider = None
        for s in self.sliders:
            if s['key'] == key:
                slider = s
                break
                
        if not slider:
            return
            
        # Draw slider track
        pygame.draw.rect(self.screen, self.theme_manager.get_color('button'), slider['rect'], border_radius=10)
        
        # Calculate handle position
        value_range = slider['max'] - slider['min']
        value_percentage = (slider['value'] - slider['min']) / value_range
        handle_x = slider['rect'].x + value_percentage * slider['rect'].width
        handle_y = slider['rect'].centery
        handle_radius = 10
        
        # Draw handle
        pygame.draw.circle(self.screen, self.theme_manager.get_color('button_hover'), (handle_x, handle_y), handle_radius)
        
        # Draw value text
        value_text = self.value_font.render(str(slider['value']), True, self.theme_manager.get_color('text_dark'))
        value_rect = value_text.get_rect(midleft=(slider['rect'].right + 20, slider['rect'].centery))
        self.screen.blit(value_text, value_rect)
        
    def _draw_toggle(self, key: str, y: int) -> None:
        """Draw a toggle element"""
        # Find the toggle
        toggle = None
        for t in self.toggles:
            if t['key'] == key:
                toggle = t
                break
                
        if not toggle:
            return
            
        # Draw toggle background
        bg_color = self.theme_manager.get_color('button_hover') if toggle['value'] else self.theme_manager.get_color('button')
        pygame.draw.rect(self.screen, bg_color, toggle['rect'], border_radius=15)
        
        # Draw toggle handle
        if toggle['value']:
            handle_x = toggle['rect'].right - 10
        else:
            handle_x = toggle['rect'].x + 10
            
        handle_y = toggle['rect'].centery
        handle_radius = 8
        
        pygame.draw.circle(self.screen, self.theme_manager.get_color('text_light'), (handle_x, handle_y), handle_radius)
        
    def _draw_selector(self, key: str, y: int) -> None:
        """Draw a selector element"""
        # Find the selector
        selector = None
        for s in self.selectors:
            if s['key'] == key:
                selector = s
                break
                
        if not selector:
            return
            
        # Calculate option width
        option_width = selector['rect'].width / len(selector['options'])
        
        # Draw options
        for i, option in enumerate(selector['options']):
            option_x = selector['rect'].x + i * option_width
            option_rect = pygame.Rect(option_x, selector['rect'].y, option_width, selector['rect'].height)
            
            # Highlight selected option
            if i == selector['current_index']:
                pygame.draw.rect(self.screen, self.theme_manager.get_color('button_hover'), option_rect, border_radius=5)
            else:
                pygame.draw.rect(self.screen, self.theme_manager.get_color('button'), option_rect, border_radius=5)
                
            # Draw option text
            option_text = self.value_font.render(option, True, self.theme_manager.get_color('text_light'))
            option_text_rect = option_text.get_rect(center=option_rect.center)
            self.screen.blit(option_text, option_text_rect)