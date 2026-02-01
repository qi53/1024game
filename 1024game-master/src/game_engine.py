#!/usr/bin/env python3
"""
1024 Game - Game Engine
Main game engine that coordinates all game systems
"""

import pygame
import threading
import time
from typing import Dict, Any, Optional, List, Tuple

from src.game import Game
from src.constants import (
    GAME_STATE_MENU, GAME_STATE_PLAYING, GAME_STATE_PAUSED, 
    GAME_STATE_GAME_OVER, GAME_STATE_WIN, GAME_STATE_LEVEL_SELECT,
    GAME_STATE_SETTINGS, GAME_STATE_ACHIEVEMENTS, GAME_STATE_TUTORIAL,
    GAME_STATE_STATS, LEVEL_COUNT
)
from src.level_manager import LevelManager
from src.particle_system import ParticleSystem
from src.animation_system import AnimationSystem


class GameEngine:
    """Main game engine that coordinates all game systems"""
    
    def __init__(self, data_manager, audio_manager, theme_manager):
        """Initialize the game engine"""
        self.data_manager = data_manager
        self.audio_manager = audio_manager
        self.theme_manager = theme_manager
        
        # Game state
        self.state = GAME_STATE_MENU
        self.running = True
        
        # Game objects
        self.current_game = None
        self.level_manager = LevelManager()
        self.particle_system = ParticleSystem()
        self.animation_system = AnimationSystem()
        
        # Threading for smooth 60 FPS
        self.game_thread = None
        self.render_thread = None
        self.update_lock = threading.Lock()
        self.render_lock = threading.Lock()
        
        # Performance tracking
        self.fps = 60
        self.frame_times = []
        self.last_frame_time = time.time()
        
        # Initialize level manager
        self.level_manager.load_levels()
        
        # Statistics
        self.stats = {
            'games_played': 0,
            'total_score': 0,
            'high_score': 0,
            'total_moves': 0,
            'total_time': 0,
            'levels_completed': 0,
            'achievements_unlocked': 0
        }
        
        # Load saved stats
        self._load_stats()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            self.running = False
            return
        
        # Handle events based on current state
        if self.state == GAME_STATE_PLAYING:
            self._handle_game_events(event)
        elif self.state == GAME_STATE_MENU:
            self._handle_menu_events(event)
        elif self.state == GAME_STATE_PAUSED:
            self._handle_pause_events(event)
        elif self.state == GAME_STATE_LEVEL_SELECT:
            self._handle_level_select_events(event)
        elif self.state == GAME_STATE_SETTINGS:
            self._handle_settings_events(event)
        elif self.state == GAME_STATE_ACHIEVEMENTS:
            self._handle_achievements_events(event)
        elif self.state == GAME_STATE_TUTORIAL:
            self._handle_tutorial_events(event)
        elif self.state == GAME_STATE_STATS:
            self._handle_stats_events(event)
        elif self.state in [GAME_STATE_GAME_OVER, GAME_STATE_WIN]:
            self._handle_game_end_events(event)

    def _handle_game_events(self, event: pygame.event.Event) -> None:
        """Handle events during gameplay"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_state(GAME_STATE_PAUSED)
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Ctrl+Z for undo
                if self.current_game and self.current_game.undo():
                    self.audio_manager.play_sfx('undo')
            elif event.key == pygame.K_r:
                # Restart current level
                self._restart_level()
            elif self.current_game and not self.current_game.is_game_over() and not self.current_game.is_win():
                # Handle movement keys
                moved = False
                if event.key in [pygame.K_UP, pygame.K_w]:
                    moved = self.current_game.move('up')
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    moved = self.current_game.move('down')
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    moved = self.current_game.move('left')
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    moved = self.current_game.move('right')
                
                if moved:
                    self.audio_manager.play_sfx('move')
                    self.current_game.add_random_tile()
                    
                    # Create particle effect for move
                    self.particle_system.create_move_effect()
                    
                    # Check game state
                    if self.current_game.is_win():
                        self._on_level_complete()
                    elif self.current_game.is_game_over():
                        self._on_level_failed()

    def _handle_menu_events(self, event: pygame.event.Event) -> None:
        """Handle events in the main menu"""
        # This will be handled by UI manager
        pass

    def _handle_pause_events(self, event: pygame.event.Event) -> None:
        """Handle events in the pause menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_state(GAME_STATE_PLAYING)

    def _handle_level_select_events(self, event: pygame.event.Event) -> None:
        """Handle events in level select"""
        # This will be handled by UI manager
        pass

    def _handle_settings_events(self, event: pygame.event.Event) -> None:
        """Handle events in settings"""
        # This will be handled by UI manager
        pass

    def _handle_achievements_events(self, event: pygame.event.Event) -> None:
        """Handle events in achievements"""
        # This will be handled by UI manager
        pass

    def _handle_tutorial_events(self, event: pygame.event.Event) -> None:
        """Handle events in tutorial"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_state(GAME_STATE_MENU)

    def _handle_stats_events(self, event: pygame.event.Event) -> None:
        """Handle events in statistics"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_state(GAME_STATE_MENU)

    def _handle_game_end_events(self, event: pygame.event.Event) -> None:
        """Handle events at game end"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_state(GAME_STATE_LEVEL_SELECT)
            elif event.key == pygame.K_r:
                self._restart_level()

    def update(self, dt: float) -> None:
        """Update game logic"""
        with self.update_lock:
            # Update particle system
            self.particle_system.update(dt)
            
            # Update animation system
            self.animation_system.update(dt)
            
            # Update current game if playing
            if self.state == GAME_STATE_PLAYING and self.current_game:
                self.current_game.update_time(dt)
                
                # Check time limit
                if self.current_game.is_time_limit_exceeded():
                    self._on_level_failed()
                
                # Check move limit
                if self.current_game.is_move_limit_exceeded():
                    self._on_level_failed()
            
            # Track FPS
            current_time = time.time()
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 60:
                self.frame_times.pop(0)
            self.last_frame_time = current_time
            
            if len(self.frame_times) > 0:
                self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the game"""
        with self.render_lock:
            # Draw based on current state
            if self.state == GAME_STATE_PLAYING and self.current_game:
                self._draw_game(screen)
            
            # Draw particle effects
            self.particle_system.draw(screen)
            
            # Draw animations
            self.animation_system.draw(screen)

    def _draw_game(self, screen: pygame.Surface) -> None:
        """Draw the game board"""
        # This will be implemented in the game renderer
        pass

    def set_state(self, new_state: str) -> None:
        """Set the game state"""
        old_state = self.state
        self.state = new_state
        
        # Handle state transitions
        if new_state == GAME_STATE_PLAYING and old_state != GAME_STATE_PAUSED:
            # Starting a new game
            if self.current_game is None:
                level = self.level_manager.get_current_level()
                self.current_game = Game(level)
                self.audio_manager.play_sfx('start')
        elif new_state == GAME_STATE_MENU:
            # Returning to menu
            self.current_game = None
            self.audio_manager.play_background_music()

    def start_level(self, level: int) -> None:
        """Start a specific level"""
        if 1 <= level <= LEVEL_COUNT:
            self.level_manager.set_current_level(level)
            self.current_game = Game(level)
            self.set_state(GAME_STATE_PLAYING)
            self.audio_manager.play_sfx('start')

    def _restart_level(self) -> None:
        """Restart the current level"""
        if self.current_game:
            level = self.current_game.get_level()
            self.current_game = Game(level)
            self.audio_manager.play_sfx('restart')

    def _on_level_complete(self) -> None:
        """Handle level completion"""
        if self.current_game:
            level = self.current_game.get_level()
            score = self.current_game.get_score()
            
            # Update stats
            self.stats['games_played'] += 1
            self.stats['total_score'] += score
            self.stats['total_moves'] += self.current_game.get_moves()
            self.stats['total_time'] += self.current_game.get_time_elapsed()
            
            if score > self.stats['high_score']:
                self.stats['high_score'] = score
            
            # Mark level as completed
            self.level_manager.complete_level(level, score)
            
            # Check achievements
            self._check_achievements()
            
            # Save stats
            self._save_stats()
            
            # Play sound and create effect
            self.audio_manager.play_sfx('win')
            self.particle_system.create_win_effect()
            
            # Set state
            self.set_state(GAME_STATE_WIN)

    def _on_level_failed(self) -> None:
        """Handle level failure"""
        if self.current_game:
            # Update stats
            self.stats['games_played'] += 1
            self.stats['total_score'] += self.current_game.get_score()
            self.stats['total_moves'] += self.current_game.get_moves()
            self.stats['total_time'] += self.current_game.get_time_elapsed()
            
            # Save stats
            self._save_stats()
            
            # Play sound and create effect
            self.audio_manager.play_sfx('lose')
            self.particle_system.create_lose_effect()
            
            # Set state
            self.set_state(GAME_STATE_GAME_OVER)

    def _check_achievements(self) -> None:
        """Check and unlock achievements"""
        # This will be implemented with the achievement system
        pass

    def _load_stats(self) -> None:
        """Load statistics from data manager"""
        saved_stats = self.data_manager.get_stats()
        if saved_stats:
            self.stats.update(saved_stats)

    def _save_stats(self) -> None:
        """Save statistics to data manager"""
        self.data_manager.save_stats(self.stats)

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return self.stats.copy()

    def get_fps(self) -> float:
        """Get current FPS"""
        return self.fps

    def is_running(self) -> bool:
        """Check if the game is running"""
        return self.running

    def quit(self) -> None:
        """Quit the game"""
        self.running = False
        self._save_stats()