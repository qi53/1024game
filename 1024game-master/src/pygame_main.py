import pygame
import sys
from typing import Optional
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from .storage import GameStorage
from .audio import AudioManager
from .screens import (
    MainMenu,
    LevelSelect,
    SettingsScreen,
    AchievementsScreen,
    TutorialScreen,
    GameOverScreen,
    GamePlay
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1024 Game")
        
        self.clock = pygame.time.Clock()
        self.storage = GameStorage()
        self.audio = AudioManager()
        
        self.current_screen = None
        self.game_play = None
        self.screen_stack = []
        
        self._show_main_menu()
    
    def _show_main_menu(self):
        self.current_screen = MainMenu(
            self.screen,
            on_play=self._start_game,
            on_level_select=self._show_level_select,
            on_settings=self._show_settings,
            on_achievements=self._show_achievements,
            on_tutorial=self._show_tutorial,
            on_quit=self._quit
        )
    
    def _start_game(self):
        level_data = self.storage.get_levels_data()
        last_unlocked = 1
        for i in range(1, 21):
            if level_data.get(str(i), {}).get("completed", False):
                last_unlocked = i + 1
        start_level = min(last_unlocked, 20)
        self._start_level(start_level)
    
    def _start_level(self, level: int):
        self.game_play = GamePlay(
            self.screen,
            level,
            on_game_over=self._on_game_over,
            on_pause=self._on_pause
        )
        self.current_screen = self.game_play
    
    def _show_level_select(self):
        self.current_screen = LevelSelect(
            self.screen,
            on_back=self._show_main_menu,
            on_select_level=self._start_level
        )
    
    def _show_settings(self):
        self.current_screen = SettingsScreen(
            self.screen,
            on_back=self._show_main_menu
        )
    
    def _show_achievements(self):
        self.current_screen = AchievementsScreen(
            self.screen,
            on_back=self._show_main_menu
        )
    
    def _show_tutorial(self):
        self.current_screen = TutorialScreen(
            self.screen,
            on_back=self._show_main_menu
        )
    
    def _on_game_over(self, is_win: bool, stats: dict):
        self.game_play.cleanup()
        self.current_screen = GameOverScreen(
            self.screen,
            stats,
            on_restart=lambda: self._start_level(stats["level"]),
            on_next_level=lambda: self._start_level(min(stats["level"] + 1, 20)),
            on_menu=self._show_main_menu,
            is_win=is_win
        )
    
    def _on_pause(self):
        pass
    
    def _quit(self):
        pygame.quit()
        sys.exit()
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.current_screen:
                    self.current_screen.handle_event(event)
            
            if self.current_screen:
                self.current_screen.update(dt)
                self.current_screen.draw()
            
            pygame.display.flip()
        
        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
