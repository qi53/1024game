#!/usr/bin/env python3
"""
1024 Game - Main Entry Point for Pygame Version
Main entry point for the pygame graphical version of the game
"""

import pygame
import sys
import os
from typing import Dict, Any

from src.game_engine import GameEngine
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.data_manager import DataManager
from src.audio_manager import AudioManager
from src.theme_manager import ThemeManager
from src.ui_manager import UIManager


def main():
    """Main game loop for pygame version"""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("1024 Game - Enhanced Edition")
    
    # Set up the clock for FPS control
    clock = pygame.time.Clock()
    
    # Initialize managers
    data_manager = DataManager()
    audio_manager = AudioManager()
    theme_manager = ThemeManager()
    
    # Initialize game engine
    game_engine = GameEngine(data_manager, audio_manager, theme_manager)
    
    # Initialize UI manager after game engine (which creates level_manager)
    ui_manager = UIManager(screen, theme_manager, audio_manager, game_engine.level_manager, data_manager)
    
    # Load saved data
    data_manager.load_all_data()
    
    # Set initial theme
    theme_manager.set_theme(data_manager.get_current_theme())
    
    # Set initial audio settings
    audio_manager.set_volume(data_manager.get_settings().get('volume', 0.7))
    audio_manager.set_sfx_enabled(data_manager.get_settings().get('sfx_enabled', True))
    audio_manager.set_music_enabled(data_manager.get_settings().get('music_enabled', True))
    
    # Play background music
    if data_manager.get_settings().get('music_enabled', True):
        audio_manager.play_background_music()
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle UI events
            ui_manager.handle_event(event)
            
            # Handle game events
            game_engine.handle_event(event)
        
        # Update
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        ui_result = ui_manager.update(dt)
        game_engine.update(dt)
        
        # Check if UI wants to exit
        if ui_result == 'exit':
            running = False
        
        # Draw
        screen.fill(theme_manager.get_color('background'))
        ui_manager.draw()
        game_engine.draw(screen)
        
        # Update display
        pygame.display.flip()
    
    # Save game data before exit
    data_manager.save_all_data()
    
    # Quit pygame
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()