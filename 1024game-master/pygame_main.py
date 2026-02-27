#!/usr/bin/env python3
"""
1024 Game - Pygame Main Entry Point
Main game loop with 60 FPS, multithreading, particles and 3D audio
"""

import pygame
import sys
import time
import threading
import os
from typing import Dict, Optional, Tuple, Any
from enum import Enum

from pygame_game import Game, LevelConfig
from pygame_ui import (
    GameState, MainMenuUI, LevelSelectUI, SettingsUI, 
    AchievementsUI, StatsUI, GameOverUI, TutorialUI, GameUI, PauseUI
)
from particles import ParticleSystem, FloatingTextManager
from audio import AudioManager, MusicManager, SoundType
from data_manager import DataManager
from themes import ThemeManager


class GameRenderer:
    """Handles game grid rendering"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = 80
        self.grid_offset_x = 0
        self.grid_offset_y = 0
        self.animation_progress = 0
        self.cell_animations: Dict[Tuple[int, int], Dict[str, Any]] = {}
    
    def calculate_grid_position(self, grid_size: int):
        total_size = grid_size * self.cell_size + (grid_size + 1) * 10
        self.grid_offset_x = (self.screen_width - total_size) // 2
        self.grid_offset_y = (self.screen_height - total_size) // 2 + 50
        self.cell_size = min(80, (min(self.screen_width, self.screen_height) - 200) // grid_size)
    
    def get_cell_position(self, row: int, col: int) -> Tuple[int, int]:
        x = self.grid_offset_x + 10 + col * (self.cell_size + 10)
        y = self.grid_offset_y + 10 + row * (self.cell_size + 10)
        return x, y
    
    def draw_grid(self, surface: pygame.Surface, grid: list, theme, fonts: Dict[str, pygame.font.Font]):
        grid_size = len(grid)
        total_size = grid_size * self.cell_size + (grid_size + 1) * 10
        
        bg_rect = pygame.Rect(
            self.grid_offset_x,
            self.grid_offset_y,
            total_size,
            total_size
        )
        pygame.draw.rect(surface, theme.grid_background, bg_rect, border_radius=10)
        
        for row in range(grid_size):
            for col in range(grid_size):
                x, y = self.get_cell_position(row, col)
                value = grid[row][col]
                
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                if value == 0:
                    pygame.draw.rect(surface, theme.grid_border, cell_rect, border_radius=5)
                else:
                    tile_color = ThemeManager.get_tile_color(theme.name.lower() if hasattr(theme, 'name') else 'classic', value)
                    text_color = ThemeManager.get_tile_text_color(theme.name.lower() if hasattr(theme, 'name') else 'classic', value)
                    
                    pygame.draw.rect(surface, tile_color, cell_rect, border_radius=5)
                    
                    font_size = self.cell_size // 2
                    if value >= 1000:
                        font_size = self.cell_size // 3
                    
                    font = pygame.font.Font(None, font_size)
                    text = str(value)
                    text_surface = font.render(text, True, text_color)
                    text_rect = text_surface.get_rect(center=cell_rect.center)
                    surface.blit(text_surface, text_rect)
    
    def draw_merge_effect(self, surface: pygame.Surface, positions: list, theme):
        for row, col, value in positions:
            x, y = self.get_cell_position(row, col)
            center_x = x + self.cell_size // 2
            center_y = y + self.cell_size // 2
            
            radius = int(self.cell_size * 0.6)
            color = ThemeManager.get_tile_color(theme.name.lower() if hasattr(theme, 'name') else 'classic', value)
            
            for i in range(3):
                alpha = 100 - i * 30
                r = radius + i * 5
                effect_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surface, (*color, alpha), (r, r), r)
                surface.blit(effect_surface, (center_x - r, center_y - r))


class GameApp:
    """Main game application"""
    
    TARGET_FPS = 60
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("1024 Game - Pygame Edition")
        
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()
        
        self.data_manager = DataManager()
        self.audio_manager = AudioManager()
        self.music_manager = MusicManager()
        self.particle_system = ParticleSystem()
        self.floating_text_manager = FloatingTextManager()
        self.renderer = GameRenderer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        self._init_fonts()
        self._init_ui()
        
        self.game: Optional[Game] = None
        self.state = GameState.MAIN_MENU
        self.previous_state: Optional[GameState] = None
        self.running = True
        self.game_start_time = 0
        self.last_frame_time = time.time()
        
        self.combo_count = 0
        self.last_move_had_merge = False
        
        self._apply_settings()
        
        if not self.data_manager.get_setting("tutorial_completed", False):
            self.state = GameState.TUTORIAL
    
    def _init_fonts(self):
        font_paths = []
        
        if sys.platform == 'darwin':
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
            ]
        elif sys.platform == 'win32':
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
            ]
        else:
            font_paths = [
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        if font_path:
            try:
                self.fonts = {
                    "title": pygame.font.Font(font_path, 72),
                    "large": pygame.font.Font(font_path, 48),
                    "medium": pygame.font.Font(font_path, 32),
                    "small": pygame.font.Font(font_path, 24),
                }
            except:
                self.fonts = {
                    "title": pygame.font.Font(None, 72),
                    "large": pygame.font.Font(None, 48),
                    "medium": pygame.font.Font(None, 32),
                    "small": pygame.font.Font(None, 24),
                }
        else:
            self.fonts = {
                "title": pygame.font.Font(None, 72),
                "large": pygame.font.Font(None, 48),
                "medium": pygame.font.Font(None, 32),
                "small": pygame.font.Font(None, 24),
            }
    
    def _init_ui(self):
        self.main_menu_ui = MainMenuUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.level_select_ui = LevelSelectUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.data_manager)
        self.settings_ui = SettingsUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.data_manager)
        self.achievements_ui = AchievementsUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.data_manager)
        self.stats_ui = StatsUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.data_manager)
        self.game_over_ui = GameOverUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.tutorial_ui = TutorialUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.game_ui = GameUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.pause_ui = PauseUI(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
    
    def _apply_settings(self):
        volume = self.data_manager.get_setting("volume", 0.7)
        self.audio_manager.set_volume(volume)
        
        music_volume = self.data_manager.get_setting("music_volume", 0.3)
        self.music_manager.set_volume(music_volume)
        
        particles_enabled = self.data_manager.get_setting("particles_enabled", True)
        self.particle_system.set_enabled(particles_enabled)
        
        if self.data_manager.get_setting("music_enabled", False):
            self.music_manager.play()
    
    def _get_current_theme(self):
        theme_name = self.data_manager.get_setting("theme", "classic")
        return ThemeManager.get_theme(theme_name)
    
    def run(self):
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            self._handle_events()
            self._update(delta_time)
            self._render()
            
            self.clock.tick(self.TARGET_FPS)
        
        self._cleanup()
    
    def _handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        mouse_down = False
        scroll_y = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_click = True
                    mouse_down = True
                elif event.button == 4:
                    scroll_y = -30
                elif event.button == 5:
                    scroll_y = 30
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)
            
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)
            
            if mouse_click:
                result = self._handle_ui_interaction(mouse_pos, mouse_click, mouse_down, scroll_y)
                if result:
                    break
        
        if not mouse_click:
            self._handle_ui_interaction(mouse_pos, mouse_click, mouse_down, scroll_y)
    
    def _handle_key_press(self, key):
        if self.state == GameState.PLAYING and self.game:
            direction = None
            
            if key in (pygame.K_UP, pygame.K_w):
                direction = "up"
            elif key in (pygame.K_DOWN, pygame.K_s):
                direction = "down"
            elif key in (pygame.K_LEFT, pygame.K_a):
                direction = "left"
            elif key in (pygame.K_RIGHT, pygame.K_d):
                direction = "right"
            elif key == pygame.K_ESCAPE:
                self.previous_state = self.state
                self.state = GameState.PAUSED
                return
            elif key == pygame.K_r:
                self._start_game(self.game.level_id)
                return
            
            if direction:
                self._make_move(direction)
        
        elif self.state == GameState.PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
        
        elif self.state == GameState.GAME_OVER:
            if key == pygame.K_RETURN:
                if self.game:
                    self._start_game(self.game.level_id)
    
    def _handle_ui_interaction(self, mouse_pos, mouse_click, mouse_down, scroll_y) -> bool:
        new_state = None
        handled = False
        
        if self.state == GameState.MAIN_MENU:
            new_state = self.main_menu_ui.update(mouse_pos, mouse_click)
            if new_state == GameState.PLAYING:
                self._start_game(1)
                handled = True
            elif new_state == GameState.LEVEL_SELECT:
                handled = True
        
        elif self.state == GameState.LEVEL_SELECT:
            new_state = self.level_select_ui.update(mouse_pos, mouse_click)
            if new_state == GameState.PLAYING:
                self._start_game(self.level_select_ui.get_selected_level())
                handled = True
        
        elif self.state == GameState.SETTINGS:
            new_state = self.settings_ui.update(mouse_pos, mouse_click, mouse_down)
            if new_state == GameState.MAIN_MENU:
                self._apply_settings()
                handled = True
        
        elif self.state == GameState.ACHIEVEMENTS:
            new_state = self.achievements_ui.update(mouse_pos, mouse_click, scroll_y)
            if new_state:
                handled = True
        
        elif self.state == GameState.STATS:
            new_state = self.stats_ui.update(mouse_pos, mouse_click)
            if new_state:
                handled = True
        
        elif self.state == GameState.TUTORIAL:
            new_state = self.tutorial_ui.update(mouse_pos, mouse_click)
            if new_state == GameState.MAIN_MENU:
                self.data_manager.set_setting("tutorial_completed", True)
                handled = True
        
        elif self.state == GameState.PAUSED:
            new_state = self.pause_ui.update(mouse_pos, mouse_click)
            if new_state == GameState.PLAYING:
                if self.pause_ui.buttons[1].hover:
                    self._start_game(self.game.level_id)
                handled = True
        
        elif self.state == GameState.GAME_OVER:
            new_state = self.game_over_ui.update(mouse_pos, mouse_click)
            if new_state == GameState.PLAYING:
                self._start_game(self.game.level_id)
                handled = True
        
        elif self.state == GameState.PLAYING:
            new_state = self.game_ui.update(mouse_pos, mouse_click)
            if new_state:
                handled = True
        
        if new_state:
            self.previous_state = self.state
            self.state = new_state
            
            if new_state is None:
                self.running = False
        
        return handled
    
    def _handle_resize(self, width, height):
        self.SCREEN_WIDTH = max(600, width)
        self.SCREEN_HEIGHT = max(400, height)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        
        self._init_ui()
        self.renderer = GameRenderer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
    
    def _start_game(self, level_id: int):
        self.game = Game(level_id)
        self.renderer.calculate_grid_position(self.game.grid_size)
        self.game_start_time = time.time()
        self.combo_count = 0
        self.last_move_had_merge = False
        self.particle_system.clear()
        self.floating_text_manager.clear()
        
        self.audio_manager.play(SoundType.BUTTON_CLICK)
    
    def _make_move(self, direction: str):
        if not self.game or self.game.is_over:
            return
        
        moved, score_gained, merge_positions = self.game.move(direction)
        
        if moved:
            self.audio_manager.play(SoundType.MOVE)
            
            if merge_positions:
                for row, col, value in merge_positions:
                    x, y = self.renderer.get_cell_position(row, col)
                    center_x = x + self.renderer.cell_size // 2
                    center_y = y + self.renderer.cell_size // 2
                    
                    self.particle_system.emit_merge(center_x, center_y, value)
                    self.audio_manager.play_merge(value, center_x, center_y)
                    
                    self.floating_text_manager.add_score(center_x, center_y, value)
                
                if self.last_move_had_merge:
                    self.combo_count += 1
                    if self.combo_count >= 2:
                        self.floating_text_manager.add_combo(
                            self.SCREEN_WIDTH // 2,
                            self.SCREEN_HEIGHT // 2 - 100,
                            self.combo_count
                        )
                        self.audio_manager.play_combo(self.combo_count)
                else:
                    self.combo_count = 1
                
                self.last_move_had_merge = True
            else:
                self.last_move_had_merge = False
                self.combo_count = 0
            
            if self.game.new_tile_position:
                row, col = self.game.new_tile_position
                x, y = self.renderer.get_cell_position(row, col)
                center_x = x + self.renderer.cell_size // 2
                center_y = y + self.renderer.cell_size // 2
                self.particle_system.emit_spawn(center_x, center_y)
            
            if self.game.is_over:
                self._handle_game_end()
        else:
            self.audio_manager.play(SoundType.ERROR)
    
    def _handle_game_end(self):
        time_elapsed = time.time() - self.game_start_time
        stats = self.game.get_stats()
        stats["time_elapsed"] = time_elapsed
        stats["max_combo"] = max(stats.get("max_combo", 0), self.combo_count)
        
        self.game_over_ui.set_result(self.game.is_won, self.game.score, stats)
        
        self.data_manager.update_level_progress(
            self.game.level_id,
            self.game.is_won,
            self.game.score,
            time_elapsed,
            stats["total_moves"],
            stats["max_tile"]
        )
        
        self.data_manager.add_session(
            self.game.level_id,
            self.game.score,
            stats["total_moves"],
            time_elapsed,
            stats["max_tile"],
            self.game.is_won,
            stats
        )
        
        unlocked = self.data_manager.check_and_unlock_achievements(
            self.game.level_id,
            self.game.score,
            stats["max_tile"],
            stats["max_combo"],
            time_elapsed
        )
        
        if self.game.is_won:
            self.audio_manager.play(SoundType.WIN)
            center_x = self.SCREEN_WIDTH // 2
            center_y = self.SCREEN_HEIGHT // 2
            self.particle_system.emit_win(center_x, center_y)
        else:
            self.audio_manager.play(SoundType.GAME_OVER)
        
        self.previous_state = self.state
        self.state = GameState.GAME_OVER
    
    def _update(self, delta_time: float):
        if self.state == GameState.PLAYING and self.game:
            self.game.stats.time_elapsed = time.time() - self.game_start_time
        
        self.particle_system.update()
        self.floating_text_manager.update()
    
    def _render(self):
        theme = self._get_current_theme()
        
        self.screen.fill(theme.background)
        
        if self.state == GameState.MAIN_MENU:
            self.main_menu_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.LEVEL_SELECT:
            self.level_select_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.SETTINGS:
            self.settings_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.ACHIEVEMENTS:
            self.achievements_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.STATS:
            self.stats_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.TUTORIAL:
            self.tutorial_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.PLAYING:
            self._render_game(theme)
        
        elif self.state == GameState.PAUSED:
            self._render_game(theme)
            self.pause_ui.draw(self.screen, theme, self.fonts)
        
        elif self.state == GameState.GAME_OVER:
            self._render_game(theme)
            self.game_over_ui.draw(self.screen, theme, self.fonts)
        
        self.particle_system.draw(self.screen)
        self.floating_text_manager.draw(self.screen)
        
        if self.data_manager.get_setting("show_fps", False):
            fps = self.clock.get_fps()
            fps_text = f"FPS: {fps:.1f}"
            fps_surface = self.fonts["small"].render(fps_text, True, theme.text_color)
            self.screen.blit(fps_surface, (self.SCREEN_WIDTH - 80, 10))
        
        pygame.display.flip()
    
    def _render_game(self, theme):
        if not self.game:
            return
        
        self.renderer.draw_grid(self.screen, self.game.grid, theme, self.fonts)
        
        if self.game.last_merge_positions:
            self.renderer.draw_merge_effect(
                self.screen,
                self.game.last_merge_positions,
                theme
            )
        
        level_info = self.game.get_level_info()
        self.game_ui.draw(
            self.screen, theme, self.fonts,
            self.game.score,
            self.game.moves_remaining,
            level_info
        )
    
    def _cleanup(self):
        self.data_manager.save_all()
        self.audio_manager.stop_all()
        self.music_manager.stop()
        pygame.quit()


def run_game():
    """Entry point for the game"""
    try:
        app = GameApp()
        app.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_game()
