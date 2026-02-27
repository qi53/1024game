from typing import Optional, Dict, Any, List, Tuple
import pygame
import sys
import random

from .storage import GameData
from .audio import AudioManager
from .theme import ThemeManager
from .particles import ParticleSystem
from .game_logic import GameLogic, LevelSystem
from .renderer import GameRenderer
from .ui_widgets import Button, Slider, Label, Panel, Toast, ProgressBar
from .font_utils import get_font


class Scene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.data = game.data
        self.audio = game.audio
        self.theme = game.theme
        self.particles = game.particles
        self.font_cache: Dict[int, pygame.font.Font] = {}
    
    def get_font(self, size: int) -> pygame.font.Font:
        return get_font(size)
    
    def handle_event(self, event: pygame.event.Event):
        pass
    
    def update(self, dt: int):
        pass
    
    def draw(self):
        pass


class SceneManager:
    def __init__(self, game):
        self.game = game
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.fade_alpha = 0
        self.is_fading = False
        self.next_scene_name: Optional[str] = None
    
    def register_scene(self, name: str, scene_class):
        self.scenes[name] = scene_class
    
    def set_scene(self, name: str, fade: bool = True):
        if fade and self.current_scene is not None:
            self.is_fading = True
            self.fade_alpha = 0
            self.next_scene_name = name
        else:
            self._switch_to_scene(name)
    
    def _switch_to_scene(self, name: str):
        scene_class = self.scenes.get(name)
        if scene_class:
            self.current_scene = scene_class(self.game)
    
    def handle_event(self, event: pygame.event.Event):
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def update(self, dt: int):
        if self.is_fading:
            self.fade_alpha += dt * 0.5
            if self.fade_alpha >= 255:
                self._switch_to_scene(self.next_scene_name)
                self.fade_alpha = 255
                self.is_fading = False
        elif self.fade_alpha > 0:
            self.fade_alpha -= dt * 0.5
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
        
        if self.current_scene:
            self.current_scene.update(dt)
    
    def draw(self):
        if self.current_scene:
            self.current_scene.draw()
        
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(self.fade_alpha)))
            self.game.screen.blit(fade_surface, (0, 0))


class MainMenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        title_font = get_font(64)
        button_font = get_font(32)
        
        center_x = game.width // 2
        button_width = 280
        button_height = 55
        button_x = center_x - button_width // 2
        start_y = 280
        spacing = 70
        
        self.title_label = Label(center_x, 120, "1024 游戏", title_font, self.theme, center=True)
        
        self.buttons = [
            Button(button_x, start_y, button_width, button_height, "开始游戏", button_font, self.theme,
                   on_click=lambda: self.play_game(), icon="▶"),
            Button(button_x, start_y + spacing, button_width, button_height, "关卡选择", button_font, self.theme,
                   on_click=lambda: game.scene_manager.set_scene("level_select"), icon="🎯"),
            Button(button_x, start_y + spacing * 2, button_width, button_height, "成就", button_font, self.theme,
                   on_click=lambda: game.scene_manager.set_scene("achievements"), icon="🏆"),
            Button(button_x, start_y + spacing * 3, button_width, button_height, "设置", button_font, self.theme,
                   on_click=lambda: game.scene_manager.set_scene("settings"), icon="⚙"),
            Button(button_x, start_y + spacing * 4, button_width, button_height, "教程", button_font, self.theme,
                   on_click=lambda: game.scene_manager.set_scene("tutorial"), icon="📖"),
        ]
        
        self.title_particles = []
        self.spawn_title_particles()
    
    def play_game(self):
        if self.data.highest_unlocked_level > 1:
            self.game.current_level = self.data.last_played_level or 1
        else:
            self.game.current_level = 1
        self.game.scene_manager.set_scene("game")
    
    def spawn_title_particles(self):
        center_x = self.game.width // 2
        for _ in range(15):
            self.particles.spawn_button_particles(
                center_x + random.randint(-100, 100),
                120 + random.randint(-20, 20),
                self.theme.get_accent_color()
            )
    
    def handle_event(self, event: pygame.event.Event):
        for button in self.buttons:
            button.handle_event(event)
    
    def update(self, dt: int):
        for button in self.buttons:
            button.update(dt)
        
        if random.random() < 0.02:
            center_x = self.game.width // 2
            self.particles.spawn_button_particles(
                center_x + random.randint(-80, 80),
                120 + random.randint(-10, 10),
                self.theme.get_accent_color()
            )
    
    def draw(self):
        self.screen.fill(self.theme.get_background_color())
        
        self.title_label.draw(self.screen)
        
        for button in self.buttons:
            button.draw(self.screen)
        
        version_font = self.get_font(18)
        version_text = version_font.render("v2.0 - Pygame Edition", True, (100, 100, 110))
        self.screen.blit(version_text, (self.game.width - version_text.get_width() - 20, 
                                        self.game.height - 30))


class LevelSelectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level_system = LevelSystem()
        self.scroll_offset = 0
        self.max_scroll = 0
        self.is_scrolling = False
        
        title_font = self.get_font(48)
        level_font = self.get_font(24)
        button_font = self.get_font(28)
        
        self.title_label = Label(game.width // 2, 50, "关卡选择", title_font, self.theme, center=True)
        
        self.back_button = Button(30, 30, 100, 45, "返回", self.get_font(24), self.theme,
                                  on_click=lambda: game.scene_manager.set_scene("main_menu"))
        
        self.level_buttons: List[Button] = []
        self.setup_level_buttons(level_font)
    
    def setup_level_buttons(self, font):
        cols = 4
        button_size = 130
        padding = 20
        start_x = (self.game.width - (cols * button_size + (cols - 1) * padding)) // 2
        start_y = 130
        
        total_levels = self.level_system.get_total_levels()
        
        for i in range(total_levels):
            level_num = i + 1
            col = i % cols
            row = i // cols
            x = start_x + col * (button_size + padding)
            y = start_y + row * (button_size + padding)
            
            is_unlocked = level_num <= self.data.highest_unlocked_level
            level_info = self.level_system.get_level(level_num)
            
            btn = Button(x, y, button_size, button_size, f"{level_num}", font, self.theme,
                        on_click=lambda l=level_num: self.select_level(l),
                        corner_radius=12)
            btn.level_num = level_num
            btn.is_unlocked = is_unlocked
            btn.level_info = level_info
            self.level_buttons.append(btn)
        
        last_btn = self.level_buttons[-1]
        self.max_scroll = max(0, last_btn.rect.bottom + 50 - self.game.height)
    
    def select_level(self, level_num: int):
        self.game.current_level = level_num
        self.game.scene_manager.set_scene("game")
    
    def handle_event(self, event: pygame.event.Event):
        self.back_button.handle_event(event)
        
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
            self._update_button_positions()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for btn in self.level_buttons:
                    if btn.rect.collidepoint(event.pos[0], event.pos[1] + self.scroll_offset):
                        if btn.is_unlocked:
                            btn.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONUP:
            for btn in self.level_buttons:
                btn.handle_event(event)
        
        for btn in self.level_buttons:
            orig_y = btn.rect.y
            btn.rect.y -= self.scroll_offset
            btn.handle_event(event)
            btn.rect.y = orig_y
    
    def _update_button_positions(self):
        pass
    
    def update(self, dt: int):
        self.back_button.update(dt)
        for btn in self.level_buttons:
            btn.update(dt)
    
    def draw(self):
        self.screen.fill(self.theme.get_background_color())
        
        self.title_label.draw(self.screen)
        self.back_button.draw(self.screen)
        
        clip_rect = pygame.Rect(0, 100, self.game.width, self.game.height - 100)
        self.screen.set_clip(clip_rect)
        
        for btn in self.level_buttons:
            draw_rect = btn.rect.copy()
            draw_rect.y -= self.scroll_offset
            
            if btn.is_unlocked:
                btn.draw(self.screen)
                btn.rect.y -= self.scroll_offset
                info_font = self.get_font(16)
                target = info_font.render(f"目标: {btn.level_info['target']}", True, (150, 150, 160))
                self.screen.blit(target, target.get_rect(midtop=(draw_rect.centerx, draw_rect.bottom + 5)))
            else:
                lock_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(lock_surf, (50, 50, 60, 230), lock_surf.get_rect(), border_radius=12)
                lock_font = self.get_font(40)
                lock_text = lock_font.render("🔒", True, (100, 100, 110))
                lock_surf.blit(lock_text, lock_text.get_rect(center=lock_surf.get_rect().center))
                self.screen.blit(lock_surf, draw_rect)
            
            btn.rect.y += self.scroll_offset
        
        self.screen.set_clip(None)


class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        title_font = self.get_font(48)
        label_font = self.get_font(28)
        
        self.title_label = Label(game.width // 2, 50, "设置", title_font, self.theme, center=True)
        self.back_button = Button(30, 30, 100, 45, "返回", self.get_font(24), self.theme,
                                  on_click=lambda: game.scene_manager.set_scene("main_menu"))
        
        panel_x = game.width // 2 - 300
        panel_y = 130
        
        self.volume_slider = Slider(panel_x + 50, panel_y + 60, 500, 30, 0, 100, 
                                    self.data.get_setting('music_volume', 70), self.theme,
                                    label="音量", on_change=self.on_volume_change)
        
        theme_names = list(self.theme.get_unlocked_themes().keys())
        self.theme_buttons: List[Button] = []
        theme_start_y = panel_y + 150
        
        btn_font = self.get_font(22)
        for i, name in enumerate(theme_names):
            btn_x = panel_x + 50 + (i % 3) * 180
            btn_y = theme_start_y + (i // 3) * 60
            btn = Button(btn_x, btn_y, 160, 45, name.capitalize(), btn_font, self.theme,
                        on_click=lambda n=name: self.set_theme(n))
            if name == self.theme.current_theme_name:
                btn.bg_color = self.theme.get_accent_color()
            self.theme_buttons.append(btn)
        
        self.theme_label = Label(panel_x + 60, theme_start_y - 30, "主题:", label_font, self.theme)
        
        self.reset_button = Button(panel_x + 50, panel_y + 320, 200, 45, "重置进度", btn_font, self.theme,
                                   on_click=self.confirm_reset)
        
        self.confirm_dialog = None
    
    def on_volume_change(self, value: float):
        self.audio.set_volume(value / 100)
        self.data.set_setting('music_volume', int(value))
        self.data.save_all()
    
    def set_theme(self, name: str):
        self.theme.set_theme(name)
        for btn in self.theme_buttons:
            if btn.text.lower() == name:
                btn.bg_color = self.theme.get_accent_color()
            else:
                btn.bg_color = self.theme.get_button_color()
    
    def confirm_reset(self):
        self.confirm_dialog = {
            'showing': True,
            'panel': Panel(self.game.width // 2 - 200, self.game.height // 2 - 80, 400, 160, self.theme),
        }
        font = self.get_font(24)
        self.confirm_dialog['yes'] = Button(self.game.width // 2 - 150, self.game.height // 2 + 20, 120, 40, 
                                            "确定", font, self.theme, on_click=self.do_reset)
        self.confirm_dialog['no'] = Button(self.game.width // 2 + 30, self.game.height // 2 + 20, 120, 40, 
                                           "取消", font, self.theme, on_click=lambda: setattr(self, 'confirm_dialog', None))
    
    def do_reset(self):
        self.data.reset_all_data()
        self.confirm_dialog = None
        self.game.toast = Toast("数据已重置", 2000, self.theme)
    
    def handle_event(self, event: pygame.event.Event):
        if self.confirm_dialog:
            self.confirm_dialog['yes'].handle_event(event)
            self.confirm_dialog['no'].handle_event(event)
            return
        
        self.back_button.handle_event(event)
        self.volume_slider.handle_event(event)
        for btn in self.theme_buttons:
            btn.handle_event(event)
        self.reset_button.handle_event(event)
    
    def update(self, dt: int):
        self.back_button.update(dt)
        for btn in self.theme_buttons:
            btn.update(dt)
        self.reset_button.update(dt)
        if self.confirm_dialog:
            self.confirm_dialog['yes'].update(dt)
            self.confirm_dialog['no'].update(dt)
    
    def draw(self):
        self.screen.fill(self.theme.get_background_color())
        
        self.title_label.draw(self.screen)
        self.back_button.draw(self.screen)
        
        pygame.draw.rect(self.screen, (40, 40, 50, 240), 
                        (self.game.width // 2 - 320, 120, 640, 380), border_radius=12)
        
        self.volume_slider.draw(self.screen)
        self.theme_label.draw(self.screen)
        for btn in self.theme_buttons:
            btn.draw(self.screen)
        self.reset_button.draw(self.screen)
        
        if self.confirm_dialog:
            overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            self.confirm_dialog['panel'].draw(self.screen)
            
            msg_font = self.get_font(24)
            msg = msg_font.render("确定要重置所有进度吗？", True, self.theme.get_text_light())
            self.screen.blit(msg, msg.get_rect(center=(self.game.width // 2, self.game.height // 2 - 20)))
            
            self.confirm_dialog['yes'].draw(self.screen)
            self.confirm_dialog['no'].draw(self.screen)


class AchievementsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        from .constants import ACHIEVEMENTS
        self.achievements_list = ACHIEVEMENTS
        
        title_font = self.get_font(48)
        self.title_label = Label(game.width // 2, 50, "成就", title_font, self.theme, center=True)
        self.back_button = Button(30, 30, 100, 45, "返回", self.get_font(24), self.theme,
                                  on_click=lambda: game.scene_manager.set_scene("main_menu"))
        
        self.scroll_offset = 0
        self.item_height = 90
        self.max_scroll = max(0, len(self.achievements_list) * self.item_height + 180 - game.height)
    
    def handle_event(self, event: pygame.event.Event):
        self.back_button.handle_event(event)
        
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 40))
    
    def update(self, dt: int):
        self.back_button.update(dt)
    
    def draw(self):
        self.screen.fill(self.theme.get_background_color())
        
        self.title_label.draw(self.screen)
        self.back_button.draw(self.screen)
        
        clip_rect = pygame.Rect(0, 100, self.game.width, self.game.height - 100)
        self.screen.set_clip(clip_rect)
        
        panel_x = self.game.width // 2 - 300
        panel_width = 600
        
        unlocked_count = sum(1 for a in self.achievements_list 
                            if a['id'] in self.data.unlocked_achievements)
        progress_font = self.get_font(24)
        progress_text = progress_font.render(f"已解锁: {unlocked_count} / {len(self.achievements_list)}", 
                                              True, self.theme.get_text_light())
        self.screen.blit(progress_text, (panel_x, 110 - self.scroll_offset))
        
        for i, achievement in enumerate(self.achievements_list):
            y = 150 + i * self.item_height - self.scroll_offset
            if y < 100 or y > self.game.height:
                continue
            
            is_unlocked = achievement['id'] in self.data.unlocked_achievements
            
            item_rect = pygame.Rect(panel_x, y, panel_width, self.item_height - 10)
            
            if is_unlocked:
                bg_color = (50, 60, 70)
                border_color = self.theme.get_accent_color()
            else:
                bg_color = (35, 35, 45)
                border_color = (60, 60, 70)
            
            pygame.draw.rect(self.screen, bg_color, item_rect, border_radius=8)
            if is_unlocked:
                pygame.draw.rect(self.screen, border_color, item_rect, width=2, border_radius=8)
            
            icon_font = self.get_font(36)
            icon_text = icon_font.render(achievement['icon'] if is_unlocked else "🔒", True, 
                                         (255, 255, 255) if is_unlocked else (80, 80, 90))
            self.screen.blit(icon_text, (item_rect.x + 20, item_rect.y + 18))
            
            name_font = self.get_font(26)
            desc_font = self.get_font(20)
            text_color = self.theme.get_text_light() if is_unlocked else (100, 100, 110)
            
            name_text = name_font.render(achievement['name'], True, text_color)
            self.screen.blit(name_text, (item_rect.x + 70, item_rect.y + 12))
            
            desc_text = desc_font.render(achievement['description'], True, 
                                        (150, 150, 160) if is_unlocked else (70, 70, 80))
            self.screen.blit(desc_text, (item_rect.x + 70, item_rect.y + 42))
        
        self.screen.set_clip(None)


class TutorialScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.current_page = 0
        
        title_font = self.get_font(48)
        content_font = self.get_font(28)
        self.title_label = Label(game.width // 2, 50, "游戏教程", title_font, self.theme, center=True)
        
        self.back_button = Button(30, 30, 100, 45, "返回", self.get_font(24), self.theme,
                                  on_click=lambda: game.scene_manager.set_scene("main_menu"))
        
        self.pages = [
            {
                'title': "游戏目标",
                'content': [
                    "通过滑动方块，使相同数字的方块合并。",
                    "最终目标是达到每关指定的目标数字！",
                    "",
                    "例如：第一关目标是达到 32",
                ],
                'demo': 'goal'
            },
            {
                'title': "基本操作",
                'content': [
                    "使用方向键 (↑↓←→) 或 WASD 来移动所有方块。",
                    "也可以在触摸屏上滑动。",
                    "",
                    "每次移动后会随机出现新方块。",
                ],
                'demo': 'controls'
            },
            {
                'title': "合并规则",
                'content': [
                    "相同数字的方块碰撞时会合并为一个。",
                    "2 + 2 = 4",
                    "4 + 4 = 8",
                    "8 + 8 = 16 ...依此类推",
                    "",
                    "每次合并都会增加分数！",
                ],
                'demo': 'merge'
            },
            {
                'title': "挑战与成就",
                'content': [
                    "游戏共有 20 个关卡，难度逐渐提升。",
                    "完成关卡解锁新主题和后续关卡。",
                    "部分关卡有时间限制，需要在规定时间内完成。",
                    "",
                    "完成各种挑战解锁成就！",
                ],
                'demo': 'challenge'
            },
        ]
        
        btn_font = self.get_font(26)
        self.prev_button = Button(game.width // 2 - 250, game.height - 80, 120, 45, "< 上一页", btn_font, self.theme,
                                  on_click=self.prev_page)
        self.next_button = Button(game.width // 2 + 130, game.height - 80, 120, 45, "下一页 >", btn_font, self.theme,
                                  on_click=self.next_page)
        
        self.demo_grid = [[2, 4, 0, 0], [2, 8, 4, 0], [0, 0, 2, 0], [0, 0, 0, 0]]
        self.demo_animation = 0
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
    
    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
    
    def handle_event(self, event: pygame.event.Event):
        self.back_button.handle_event(event)
        self.prev_button.handle_event(event)
        self.next_button.handle_event(event)
    
    def update(self, dt: int):
        self.back_button.update(dt)
        self.prev_button.update(dt)
        self.next_button.update(dt)
        
        self.prev_button.bg_color = self.theme.get_button_color() if self.current_page > 0 else (60, 60, 70)
        self.next_button.bg_color = self.theme.get_button_color() if self.current_page < len(self.pages) - 1 else (60, 60, 70)
    
    def draw(self):
        self.screen.fill(self.theme.get_background_color())
        
        self.title_label.draw(self.screen)
        self.back_button.draw(self.screen)
        
        page = self.pages[self.current_page]
        
        page_title_font = self.get_font(36)
        page_title = page_title_font.render(page['title'], True, self.theme.get_accent_color())
        self.screen.blit(page_title, page_title.get_rect(midtop=(self.game.width // 2, 120)))
        
        content_font = self.get_font(26)
        y = 180
        for line in page['content']:
            text = content_font.render(line, True, self.theme.get_text_light())
            self.screen.blit(text, text.get_rect(midtop=(self.game.width // 2, y)))
            y += 38
        
        page_indicator_font = self.get_font(20)
        indicator = page_indicator_font.render(f"{self.current_page + 1} / {len(self.pages)}", True, (120, 120, 130))
        self.screen.blit(indicator, indicator.get_rect(midbottom=(self.game.width // 2, self.game.height - 95)))
        
        self.prev_button.draw(self.screen)
        self.next_button.draw(self.screen)


class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level_system = LevelSystem()
        
        level_info = self.level_system.get_level(game.current_level)
        grid_size = level_info['grid_size']
        target = level_info['target']
        time_limit = level_info['time_limit']
        
        self.game_logic = GameLogic(grid_size)
        self.renderer = GameRenderer(grid_size, self.theme, self.audio, self.particles)
        
        button_font = self.get_font(24)
        self.back_button = Button(20, self.game.height - 60, 110, 45, "返回", button_font, self.theme,
                                  on_click=self.go_back)
        self.restart_button = Button(self.game.width - 130, self.game.height - 60, 110, 45, "重开", button_font, self.theme,
                                     on_click=self.restart_level)
        
        self.target = target
        self.level_info = level_info
        self.time_remaining = time_limit if time_limit > 0 else None
        self.is_timed = time_limit > 0
        
        self.game_over = False
        self.victory = False
        self.paused = False
        
        self.result_dialog: Optional[dict] = None
        
        grid_x = (self.game.width - self.renderer.grid_width) // 2
        grid_y = 170
        self.grid_offset = (grid_x, grid_y)
        
        self.data.update_stats(games_started=1)
    
    def go_back(self):
        self.game.scene_manager.set_scene("level_select")
    
    def restart_level(self):
        level_info = self.level_system.get_level(self.game.current_level)
        grid_size = level_info['grid_size']
        self.game_logic.set_grid_size(grid_size)
        self.renderer.set_grid_size(grid_size)
        self.time_remaining = level_info['time_limit'] if level_info['time_limit'] > 0 else None
        self.is_timed = level_info['time_limit'] > 0
        self.game_over = False
        self.victory = False
        self.result_dialog = None
        
        grid_x = (self.game.width - self.renderer.grid_width) // 2
        grid_y = 170
        self.grid_offset = (grid_x, grid_y)
    
    def check_victory(self):
        if self.game_logic.has_won(self.target):
            self.victory = True
            self.game_over = True
            self.on_victory()
    
    def on_victory(self):
        score = self.game_logic.get_score()
        moves = self.game_logic.get_moves()
        elapsed_time = self.level_info['time_limit'] - (self.time_remaining or 0)
        
        self.data.complete_level(self.game.current_level, score, elapsed_time)
        
        new_themes = self.data.get_unlocked_themes()
        if len(new_themes) > self.game.current_level // 4:
            self.game.toast = Toast("解锁新主题！", 2500, self.theme)
        
        if self.game.current_level >= self.data.highest_unlocked_level and self.game.current_level < 20:
            self.data.unlock_level(self.game.current_level + 1)
            if self.game.current_level == 1:
                self.data.unlock_achievement('first_win')
            if self.game.current_level == 5:
                self.data.unlock_achievement('completed_tier_1')
            if self.game.current_level == 10:
                self.data.unlock_achievement('half_way')
            if self.game.current_level == 15:
                self.data.unlock_achievement('master')
            if self.game.current_level == 20:
                self.data.unlock_achievement('champion')
        
        if moves < 50 and self.game.current_level > 5:
            self.data.unlock_achievement('efficient')
        if score > 10000:
            self.data.unlock_achievement('high_score')
        if self.game_logic.max_tile >= 2048:
            self.data.unlock_achievement('reached_2048')
        if not self.is_timed or (self.time_remaining and self.time_remaining > 30):
            if self.game.current_level > 10:
                self.data.unlock_achievement('speedy')
        
        self.show_result_dialog()
    
    def show_result_dialog(self):
        font = self.get_font(24)
        self.result_dialog = {
            'victory': self.victory,
            'score': self.game_logic.score,
            'moves': self.game_logic.moves,
            'max_tile': self.game_logic.max_tile,
        }
        
        dialog_w, dialog_h = 400, 320
        x = self.game.width // 2 - dialog_w // 2
        y = self.game.height // 2 - dialog_h // 2
        
        self.result_dialog['next_button'] = Button(x + 50, y + 240, 130, 45, "下一关", font, self.theme,
                                                   on_click=self.next_level) if self.victory and self.game.current_level < 20 else None
        self.result_dialog['restart_button'] = Button(x + (220 if self.victory else 50), y + 240, 130, 45, "再玩一次", font, self.theme,
                                                      on_click=self.restart_level)
        self.result_dialog['menu_button'] = Button(x + dialog_w - 180 if self.result_dialog['next_button'] else x + 50, y + 240, 130, 45, "返回菜单", font, self.theme,
                                                   on_click=lambda: self.game.scene_manager.set_scene("main_menu"))
        
        for _ in range(30):
            if self.victory:
                self.particles.spawn_win_particles(self.game.width // 2 + random.randint(-150, 150), 
                                                   self.game.height // 2 + random.randint(-100, 100))
    
    def next_level(self):
        if self.game.current_level < 20:
            self.game.current_level += 1
            level_info = self.level_system.get_level(self.game.current_level)
            grid_size = level_info['grid_size']
            self.target = level_info['target']
            self.level_info = level_info
            self.time_remaining = level_info['time_limit'] if level_info['time_limit'] > 0 else None
            self.is_timed = level_info['time_limit'] > 0
            
            self.game_logic.set_grid_size(grid_size)
            self.renderer.set_grid_size(grid_size)
            
            self.game_over = False
            self.victory = False
            self.result_dialog = None
            
            grid_x = (self.game.width - self.renderer.grid_width) // 2
            grid_y = 170
            self.grid_offset = (grid_x, grid_y)
    
    def handle_event(self, event: pygame.event.Event):
        if self.result_dialog:
            if self.result_dialog.get('next_button'):
                self.result_dialog['next_button'].handle_event(event)
                if self.result_dialog is None:
                    return
            self.result_dialog['restart_button'].handle_event(event)
            self.result_dialog['menu_button'].handle_event(event)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()
                return
            
            if self.game_over:
                return
            
            moved = False
            score = 0
            merged = set()
            
            if event.key in [pygame.K_UP, pygame.K_w]:
                moved, score, merged = self.game_logic.move_up()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                moved, score, merged = self.game_logic.move_down()
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                moved, score, merged = self.game_logic.move_left()
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                moved, score, merged = self.game_logic.move_right()
            
            if moved:
                new_tile = self.game_logic.add_random_tile()
                if new_tile:
                    row, col, val = new_tile
                    self.renderer.add_spawn_animation(row, col)
                    
                    gx, gy = self.renderer.get_grid_position(col, row)
                    center_x = self.grid_offset[0] + gx + self.renderer.cell_size // 2
                    center_y = self.grid_offset[1] + gy + self.renderer.cell_size // 2
                    self.particles.spawn_spawn_particles(center_x, center_y, self.theme.get_accent_color())
                
                if merged:
                    self.renderer.add_merge_animation(merged)
                    max_merge = max([self.game_logic.grid[p[0]][p[1]] for p in merged]) if merged else 0
                    
                    for pos in merged:
                        gx, gy = self.renderer.get_grid_position(pos[1], pos[0])
                        center_x = self.grid_offset[0] + gx + self.renderer.cell_size // 2
                        center_y = self.grid_offset[1] + gy + self.renderer.cell_size // 2
                        self.audio.play_merge_sound(max_merge, (center_x, center_y))
                
                self.check_victory()
                
                if not self.victory and self.game_logic.is_game_over():
                    self.game_over = True
                    self.show_result_dialog()
        
        self.back_button.handle_event(event)
        self.restart_button.handle_event(event)
    
    def update(self, dt: int):
        self.back_button.update(dt)
        self.restart_button.update(dt)
        
        if self.is_timed and not self.game_over and self.time_remaining is not None:
            self.time_remaining -= dt / 1000
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.game_over = True
                self.victory = False
                self.show_result_dialog()
        
        if self.result_dialog:
            if self.result_dialog.get('next_button'):
                self.result_dialog['next_button'].update(dt)
            self.result_dialog['restart_button'].update(dt)
            self.result_dialog['menu_button'].update(dt)
    
    def draw(self):
        self.screen.fill(self.theme.get_background_color())
        
        level_font = self.get_font(32)
        level_text = level_font.render(f"关卡 {self.game.current_level}: {self.level_info['description']}", 
                                        True, self.theme.get_accent_color())
        self.screen.blit(level_text, level_text.get_rect(midtop=(self.game.width // 2, 12)))
        
        self.renderer.draw_game_info(
            self.screen,
            self.game_logic.score,
            self.game_logic.moves,
            self.game_logic.max_tile,
            self.target,
            self.time_remaining if self.is_timed else None
        )
        
        self.renderer.draw(
            self.screen,
            self.game_logic.grid,
            self.grid_offset[0],
            self.grid_offset[1]
        )
        
        self.back_button.draw(self.screen)
        self.restart_button.draw(self.screen)
        
        if self.result_dialog:
            overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            dialog_w, dialog_h = 400, 320
            x = self.game.width // 2 - dialog_w // 2
            y = self.game.height // 2 - dialog_h // 2
            
            pygame.draw.rect(self.screen, (45, 45, 55), (x, y, dialog_w, dialog_h), border_radius=12)
            pygame.draw.rect(self.screen, self.theme.get_accent_color() if self.victory else (180, 50, 50),
                           (x, y, dialog_w, 60), border_top_left_radius=12, border_top_right_radius=12)
            
            title_font = self.get_font(36)
            title = title_font.render("胜利！" if self.victory else "游戏结束", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(self.game.width // 2, y + 30)))
            
            stat_font = self.get_font(26)
            stats = [
                f"分数: {self.result_dialog['score']}",
                f"步数: {self.result_dialog['moves']}",
                f"最大方块: {self.result_dialog['max_tile']}",
            ]
            
            stat_y = y + 90
            for stat in stats:
                text = stat_font.render(stat, True, self.theme.get_text_light())
                self.screen.blit(text, text.get_rect(center=(self.game.width // 2, stat_y)))
                stat_y += 38
            
            if self.result_dialog.get('next_button'):
                self.result_dialog['next_button'].draw(self.screen)
            self.result_dialog['restart_button'].draw(self.screen)
            self.result_dialog['menu_button'].draw(self.screen)
