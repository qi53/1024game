"""
1024 Game - Pygame Main Entry Point
Main game loop and screen management
"""

import pygame
import sys
import os
from typing import Optional, Dict, Type

import config
from audio import AudioManager
from data_manager import DataManager
from particles import ParticleSystem
from screens import (
    BaseScreen, ScreenType,
    MainMenuScreen, LevelSelectScreen, GameScreen,
    SettingsScreen, AchievementsScreen, TutorialScreen,
    GameOverScreen, LevelCompleteScreen, PauseScreen,
    StatsScreen
)


class Game:
    """Main game class"""
    
    def __init__(self):
        """Initialize the game"""
        pygame.init()
        pygame.mixer.init()
        
        # Set up display
        self.screen = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        pygame.display.set_caption(config.TITLE)
        
        # Set up clock
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize systems
        self.audio = AudioManager()
        self.data = DataManager()
        self.particles = ParticleSystem()
        
        # Load fonts
        self.fonts = self._load_fonts()
        
        # Current theme
        self.theme = config.THEMES[self.data.get_theme()]
        
        # Screen management
        self.current_screen: Optional[BaseScreen] = None
        self.screens: Dict[ScreenType, Type[BaseScreen]] = {
            ScreenType.MAIN_MENU: MainMenuScreen,
            ScreenType.LEVEL_SELECT: LevelSelectScreen,
            ScreenType.GAME: GameScreen,
            ScreenType.SETTINGS: SettingsScreen,
            ScreenType.ACHIEVEMENTS: AchievementsScreen,
            ScreenType.TUTORIAL: TutorialScreen,
            ScreenType.GAME_OVER: GameOverScreen,
            ScreenType.LEVEL_COMPLETE: LevelCompleteScreen,
            ScreenType.PAUSE: PauseScreen,
            ScreenType.STATS: StatsScreen,
        }
        
        # Start with main menu
        self._switch_screen(ScreenType.MAIN_MENU)
    
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Load game fonts with Chinese support"""
        fonts = {}
        
        # macOS system fonts with Chinese support
        chinese_fonts = [
            # macOS系统中文字体
            "/System/Library/Fonts/PingFang.ttc",  # 苹方字体
            "/System/Library/Fonts/STHeiti Light.ttc",  # 华文黑体
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",  # Arial Unicode
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑体
            # 备用字体
            "PingFang SC",
            "Heiti SC",
            "STHeiti",
            "Arial Unicode MS",
        ]
        
        font_name = None
        
        # 尝试找到支持中文的字体
        for font_path in chinese_fonts:
            try:
                if font_path.startswith("/"):
                    # 系统字体路径
                    if os.path.exists(font_path):
                        test_font = pygame.font.Font(font_path, 24)
                        font_name = font_path
                        break
                else:
                    # 字体名称，尝试使用
                    test_font = pygame.font.SysFont(font_path, 24)
                    if test_font:
                        font_name = font_path
                        break
            except:
                continue
        
        try:
            if font_name and font_name.startswith("/"):
                # 使用系统字体文件
                fonts["small"] = pygame.font.Font(font_name, config.FONT_SIZES["small"])
                fonts["medium"] = pygame.font.Font(font_name, config.FONT_SIZES["medium"])
                fonts["large"] = pygame.font.Font(font_name, config.FONT_SIZES["large"])
                fonts["xlarge"] = pygame.font.Font(font_name, config.FONT_SIZES["xlarge"])
                fonts["title"] = pygame.font.Font(font_name, config.FONT_SIZES["title"])
            elif font_name:
                # 使用系统字体名称
                fonts["small"] = pygame.font.SysFont(font_name, config.FONT_SIZES["small"])
                fonts["medium"] = pygame.font.SysFont(font_name, config.FONT_SIZES["medium"])
                fonts["large"] = pygame.font.SysFont(font_name, config.FONT_SIZES["large"])
                fonts["xlarge"] = pygame.font.SysFont(font_name, config.FONT_SIZES["xlarge"])
                fonts["title"] = pygame.font.SysFont(font_name, config.FONT_SIZES["title"])
            else:
                # 回退到默认字体（不支持中文）
                raise Exception("No Chinese font found")
        except Exception as e:
            print(f"Warning: Could not load Chinese font: {e}")
            # Fallback to default font (will show squares for Chinese)
            fonts["small"] = pygame.font.Font(None, config.FONT_SIZES["small"])
            fonts["medium"] = pygame.font.Font(None, config.FONT_SIZES["medium"])
            fonts["large"] = pygame.font.Font(None, config.FONT_SIZES["large"])
            fonts["xlarge"] = pygame.font.Font(None, config.FONT_SIZES["xlarge"])
            fonts["title"] = pygame.font.Font(None, config.FONT_SIZES["title"])
        
        return fonts
    
    def _switch_screen(self, screen_type: ScreenType, data: Dict = None) -> None:
        """Switch to a different screen"""
        if screen_type in self.screens:
            screen_class = self.screens[screen_type]
            self.current_screen = screen_class(
                self.screen,
                self.fonts,
                self.theme,
                self.audio,
                self.data
            )
            if data:
                self.current_screen.screen_data = data
                # 如果屏幕有 init_with_data 方法，调用它来初始化数据
                if hasattr(self.current_screen, 'init_with_data'):
                    self.current_screen.init_with_data(data)
            # Re-initialize if needed (for screens without init_with_data)
            if hasattr(self.current_screen, '_create_buttons') and not hasattr(self.current_screen, 'init_with_data'):
                self.current_screen.buttons.clear()
                self.current_screen._create_buttons()
    
    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if isinstance(self.current_screen, GameScreen):
                        self.current_screen._on_pause()
                    elif not isinstance(self.current_screen, MainMenuScreen):
                        self._switch_screen(ScreenType.MAIN_MENU)
            
            # Pass event to current screen
            if self.current_screen:
                self.current_screen.handle_event(event)
    
    def update(self) -> None:
        """Update game state"""
        if self.current_screen:
            self.current_screen.update()
            
            # Check for screen switch
            if not self.current_screen.running:
                if self.current_screen.next_screen:
                    self._switch_screen(
                        self.current_screen.next_screen,
                        self.current_screen.screen_data
                    )
                else:
                    self.running = False
    
    def draw(self) -> None:
        """Draw the game"""
        if self.current_screen:
            self.current_screen.draw()
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(config.FPS)
        except Exception as e:
            print(f"Error: {e}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.data.save_all()
        self.audio.cleanup()
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
