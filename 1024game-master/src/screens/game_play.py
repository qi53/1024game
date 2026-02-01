import pygame
import threading
import time
from typing import Callable, Optional
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LEVEL_CONFIGS,
    TEXT_COLOR, BG_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR,
    TILE_COLORS, DIFFICULTY_COLORS
)
from ..game_core import GameCore, MoveResult
from ..storage import GameStorage
from ..particles import ParticleSystem
from ..audio import AudioManager
from ..ui import Button, ProgressBar, get_font


class GamePlay:
    def __init__(
        self,
        screen: pygame.Surface,
        level: int,
        on_game_over: Callable[[bool, dict], None],
        on_pause: Callable
    ):
        self.screen = screen
        self.level = level
        self.on_game_over = on_game_over
        self.on_pause = on_pause
        
        self.storage = GameStorage()
        self.game = GameCore()
        self.game.reset(level)
        
        self.particles = ParticleSystem()
        self.audio = AudioManager()
        
        self.running = True
        self.paused = False
        self.game_over = False
        
        self.start_time = time.time()
        self.game_time = 0
        self.moves = 0
        self.max_combo = 0
        self.current_combo = 0
        
        self.font_large = get_font(48)
        self.font_medium = get_font(36)
        self.font_small = get_font(24)
        
        self._setup_ui()
        
        self.game_thread = threading.Thread(target=self._game_update_loop, daemon=True)
        self.game_thread.start()
    
    def _setup_ui(self):
        config = LEVEL_CONFIGS[self.level]
        self.grid_size = config["grid_size"]
        self.target_value = config["target"]
        self.time_limit = config["time_limit"]
        self.difficulty = config["difficulty"]
        
        self.cell_size = min(500 // self.grid_size, 80)
        self.grid_padding = 10
        self.grid_width = self.cell_size * self.grid_size + self.grid_padding * (self.grid_size + 1)
        self.grid_x = (SCREEN_WIDTH - self.grid_width) // 2
        self.grid_y = 150
        
        self.time_bar = ProgressBar(
            self.screen, self.grid_x, self.grid_y - 50, self.grid_width, 20,
            self.time_limit, self.time_limit,
            bg_color=(50, 50, 50), fg_color=ACCENT_COLOR
        )
        
        self.pause_button = Button(
            self.screen, SCREEN_WIDTH - 100, 30, 70, 40,
            "暂停", self._toggle_pause,
            color=SECONDARY_COLOR, text_color=TEXT_COLOR
        )
    
    def _game_update_loop(self):
        while self.running:
            if not self.paused and not self.game_over:
                self.game_time = time.time() - self.start_time
            time.sleep(0.01)
    
    def _toggle_pause(self):
        self.paused = not self.paused
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.pause_button.handle_event(event):
            return True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._toggle_pause()
                return True
            
            if event.key == pygame.K_r:
                self.game.reset(self.level)
                self.start_time = time.time()
                self.moves = 0
                self.current_combo = 0
                self.max_combo = 0
                return True
            
            if not self.paused and not self.game_over:
                direction = None
                if event.key in (pygame.K_UP, pygame.K_w):
                    direction = "up"
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    direction = "down"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    direction = "left"
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    direction = "right"
                
                if direction:
                    self._make_move(direction)
                    return True
        
        return False
    
    def _make_move(self, direction: str):
        result = self.game.move(direction)
        
        if result == MoveResult.SUCCESS:
            self.moves += 1
            self.current_combo += 1
            if self.current_combo > self.max_combo:
                self.max_combo = self.current_combo
            
            merged = self.game.get_last_merged_positions()
            for pos in merged:
                x = self.grid_x + self.grid_padding + pos[1] * (self.cell_size + self.grid_padding) + self.cell_size // 2
                y = self.grid_y + self.grid_padding + pos[0] * (self.cell_size + self.grid_padding) + self.cell_size // 2
                self.particles.spawn_merge_effect(x, y, self.game.get_value_at(pos[0], pos[1]))
            
            self.audio.play_sound_3d("merge", x / SCREEN_WIDTH)
        
        elif result == MoveResult.NO_MOVE:
            self.current_combo = 0
        
        elif result == MoveResult.WIN:
            self.game_over = True
            self.audio.play_sound_3d("win", 0.5)
            
            elapsed = self.game_time
            stars = self._calculate_stars(elapsed)
            
            level_data = self.storage.get_levels_data()
            level_key = str(self.level)
            if level_key not in level_data:
                level_data[level_key] = {}
            
            current_best = level_data[level_key].get("best_time", float('inf'))
            if elapsed < current_best:
                level_data[level_key]["best_time"] = elapsed
            
            current_stars = level_data[level_key].get("stars", 0)
            if stars > current_stars:
                level_data[level_key]["stars"] = stars
            
            level_data[level_key]["completed"] = True
            self.storage.set_levels_data(level_data)
            self.storage.save()
            
            stats = {
                "level": self.level,
                "score": self.game.score,
                "max_tile": self.game.max_tile,
                "moves": self.moves,
                "time": elapsed,
                "max_combo": self.max_combo,
                "stars": stars
            }
            
            self._check_achievements(stats)
            self.on_game_over(True, stats)
        
        elif result == MoveResult.GAME_OVER:
            self.game_over = True
            self.audio.play_sound_3d("game_over", 0.5)
            
            stats = {
                "level": self.level,
                "score": self.game.score,
                "max_tile": self.game.max_tile,
                "moves": self.moves,
                "time": self.game_time,
                "max_combo": self.max_combo,
                "stars": 0
            }
            self.on_game_over(False, stats)
    
    def _calculate_stars(self, elapsed: float) -> int:
        if elapsed <= self.time_limit * 0.3:
            return 3
        elif elapsed <= self.time_limit * 0.6:
            return 2
        else:
            return 1
    
    def _check_achievements(self, stats: dict):
        stats_data = self.storage.get_stats()
        stats_data["total_games_played"] = stats_data.get("total_games_played", 0) + 1
        
        if stats["time"] < stats_data.get("fastest_win", float('inf')):
            stats_data["fastest_win"] = stats["time"]
        
        if stats["score"] > stats_data.get("highest_score", 0):
            stats_data["highest_score"] = stats["score"]
        
        if stats["max_combo"] > stats_data.get("max_combo", 0):
            stats_data["max_combo"] = stats["max_combo"]
        
        if stats["max_tile"] >= 2048:
            stats_data["reached_2048"] = True
        
        level_data = self.storage.get_levels_data()
        completed = sum(1 for v in level_data.values() if v.get("completed", False))
        stats_data["levels_completed"] = completed
        
        three_star = sum(1 for v in level_data.values() if v.get("stars", 0) >= 3)
        stats_data["total_3_star"] = three_star
        
        self.storage.set_stats(stats_data)
        self.storage.save()
    
    def update(self, dt: float):
        self.pause_button.update()
        self.particles.update(dt)
        
        if not self.paused and not self.game_over:
            remaining = self.time_limit - self.game_time
            self.time_bar.value = max(0, remaining)
            
            if remaining <= 0 and not self.game_over:
                self.game_over = True
                stats = {
                    "level": self.level,
                    "score": self.game.score,
                    "max_tile": self.game.max_tile,
                    "moves": self.moves,
                    "time": self.game_time,
                    "max_combo": self.max_combo,
                    "stars": 0
                }
                self.on_game_over(False, stats)
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        level_text = self.font_medium.render(f"关卡 {self.level}", True, TEXT_COLOR)
        self.screen.blit(level_text, (50, 30))
        
        target_text = self.font_small.render(f"目标: {self.target_value}", True, TEXT_COLOR)
        self.screen.blit(target_text, (50, 70))
        
        score_text = self.font_large.render(f"{self.game.score:,}", True, ACCENT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 30))
        
        moves_text = self.font_small.render(f"移动: {self.moves}", True, TEXT_COLOR)
        self.screen.blit(moves_text, (50, 100))
        
        if self.current_combo > 1:
            combo_text = self.font_medium.render(f"连击 x{self.current_combo}", True, (255, 100, 100))
            self.screen.blit(combo_text, (200, 95))
        
        self.time_bar.draw()
        
        diff_color = DIFFICULTY_COLORS.get(self.difficulty, SECONDARY_COLOR)
        pygame.draw.rect(self.screen, diff_color, 
                        (self.grid_x - 5, self.grid_y - 5, self.grid_width + 10, self.grid_width + 10), 
                        border_radius=10)
        
        pygame.draw.rect(self.screen, (30, 30, 30), 
                        (self.grid_x, self.grid_y, self.grid_width, self.grid_width), 
                        border_radius=8)
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                value = self.game.grid[row][col]
                x = self.grid_x + self.grid_padding + col * (self.cell_size + self.grid_padding)
                y = self.grid_y + self.grid_padding + row * (self.cell_size + self.grid_padding)
                
                color = TILE_COLORS.get(value, (60, 58, 50))
                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size), border_radius=6)
                
                if value > 0:
                    text_color = (249, 246, 242) if value >= 8 else (119, 110, 101)
                    font_size = 36 if value < 1000 else 28 if value < 10000 else 20
                    font = get_font(font_size)
                    text = font.render(str(value), True, text_color)
                    self.screen.blit(text, (x + self.cell_size // 2 - text.get_width() // 2,
                                           y + self.cell_size // 2 - text.get_height() // 2))
        
        self.particles.draw(self.screen)
        self.pause_button.draw()
        
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.font_large.render("游戏暂停", True, TEXT_COLOR)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            hint_text = self.font_small.render("按 ESC 或点击继续按钮继续游戏", True, (200, 200, 200))
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def cleanup(self):
        self.running = False
        if self.game_thread.is_alive():
            self.game_thread.join(timeout=1)
