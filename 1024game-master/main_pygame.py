import pygame
import sys
import os

from src.storage import GameData
from src.audio import AudioManager
from src.theme import ThemeManager
from src.particles import ParticleSystem
from src.scenes import SceneManager, MainMenuScene, LevelSelectScene, SettingsScene
from src.scenes import AchievementsScene, TutorialScene, GameScene
from src.ui_widgets import Toast


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.width = 800
        self.height = 750
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("1024 Game - Pygame Edition")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        
        self.data = GameData(data_dir)
        
        self.audio = AudioManager()
        self.audio.initialize(self.data)
        self.theme = ThemeManager(self.data)
        self.particles = ParticleSystem()
        
        self.scene_manager = SceneManager(self)
        self.scene_manager.register_scene("main_menu", MainMenuScene)
        self.scene_manager.register_scene("level_select", LevelSelectScene)
        self.scene_manager.register_scene("settings", SettingsScene)
        self.scene_manager.register_scene("achievements", AchievementsScene)
        self.scene_manager.register_scene("tutorial", TutorialScene)
        self.scene_manager.register_scene("game", GameScene)
        
        self.scene_manager.set_scene("main_menu", fade=False)
        
        self.current_level = self.data.last_played_level or 1
        
        self.toast: Toast = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            
            self.scene_manager.handle_event(event)
    
    def update(self, dt: int):
        self.scene_manager.update(dt)
        self.particles.update(dt)
        
        if self.toast:
            self.toast.update(dt)
            if self.toast.is_done():
                self.toast = None
    
    def draw(self):
        self.scene_manager.draw()
        self.particles.draw(self.screen)
        
        if self.toast:
            self.toast.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        import threading
        
        bgm_thread = threading.Thread(target=self.audio.play_music_loop, daemon=True)
        bgm_thread.start()
        
        frame_count = 0
        
        while self.running:
            dt = self.clock.tick(self.fps)
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            frame_count += 1
            
            if frame_count % 600 == 0:
                print(f"FPS: {self.clock.get_fps():.1f}")
    
    def quit(self):
        self.audio.stop_music()
        self.data.save_all()
        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
