"""
1024 Game - Screen Modules
All game screens: menu, level select, game, settings, achievements, etc.
"""

import pygame
import math
from typing import Optional, List, Callable, Tuple
from enum import Enum, auto
import config
from ui_components import (
    Button, ButtonStyle, Slider, Toggle, ProgressBar,
    StarRating, AnimatedTile, Notification
)
from game_engine import GameEngine, GameState, MoveResult
from particles import ParticleSystem
from audio import AudioManager, SoundType
from data_manager import DataManager


class ScreenType(Enum):
    """Screen type enumeration"""
    MAIN_MENU = auto()
    LEVEL_SELECT = auto()
    GAME = auto()
    SETTINGS = auto()
    ACHIEVEMENTS = auto()
    TUTORIAL = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    PAUSE = auto()
    STATS = auto()


class BaseScreen:
    """Base class for all screens"""
    
    def __init__(
        self,
        screen: pygame.Surface,
        fonts: dict,
        theme: dict,
        audio: AudioManager,
        data: DataManager
    ):
        self.screen = screen
        self.fonts = fonts
        self.theme = theme
        self.audio = audio
        self.data = data
        self.buttons: List[Button] = []
        self.notifications: List[Notification] = []
        self.running = True
        self.next_screen: Optional[ScreenType] = None
        self.screen_data: dict = {}
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event, return True if event was consumed"""
        return False
    
    def update(self) -> None:
        """Update screen state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for button in self.buttons:
            if button.update(mouse_pos, mouse_pressed):
                return
        
        # Update notifications
        for notification in self.notifications[:]:
            if not notification.update():
                self.notifications.remove(notification)
    
    def draw(self) -> None:
        """Draw the screen"""
        # Clear with background color
        self.screen.fill(self.theme.get("background", (250, 248, 239)))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw notifications
        for notification in self.notifications:
            notification.draw(self.screen)
    
    def add_notification(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Add a notification"""
        x = self.screen.get_width() // 2
        y = 100
        notification = Notification(
            text, x, y, self.fonts["medium"], color,
            self.theme.get("button", (0, 0, 0))
        )
        self.notifications.append(notification)
    
    def switch_to(self, screen_type: ScreenType, data: dict = None) -> None:
        """Switch to another screen"""
        self.next_screen = screen_type
        if data:
            self.screen_data = data
        self.running = False


class MainMenuScreen(BaseScreen):
    """Main menu screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_buttons()
        self.title_angle = 0.0
    
    def _create_buttons(self) -> None:
        """Create menu buttons"""
        center_x = self.screen.get_width() // 2
        start_y = 300
        button_width = 250
        button_height = 60
        spacing = 80
        
        style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=10
        )
        
        # 开始游戏按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y,
            button_width, button_height,
            "开始游戏", self.fonts["large"], style,
            lambda: self._on_play()
        ))
        
        # 关卡选择按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y + spacing,
            button_width, button_height,
            "关卡选择", self.fonts["large"], style,
            lambda: self._on_level_select()
        ))
        
        # 成就按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y + spacing * 2,
            button_width, button_height,
            "成就系统", self.fonts["large"], style,
            lambda: self._on_achievements()
        ))
        
        # 设置按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y + spacing * 3,
            button_width, button_height,
            "游戏设置", self.fonts["large"], style,
            lambda: self._on_settings()
        ))
        
        # 教程按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y + spacing * 4,
            button_width, button_height,
            "游戏教程", self.fonts["large"], style,
            lambda: self._on_tutorial()
        ))
        
        # 统计按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y + spacing * 5,
            button_width, button_height,
            "游戏统计", self.fonts["large"], style,
            lambda: self._on_stats()
        ))
        
        # 退出按钮
        self.buttons.append(Button(
            center_x - button_width // 2, start_y + spacing * 6,
            button_width, button_height,
            "退出游戏", self.fonts["large"], style,
            lambda: self._on_exit()
        ))
    
    def _on_play(self) -> None:
        """Handle play button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        highest = self.data.get_highest_unlocked_level()
        self.switch_to(ScreenType.GAME, {"level": highest})
    
    def _on_level_select(self) -> None:
        """Handle level select button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.LEVEL_SELECT)
    
    def _on_achievements(self) -> None:
        """Handle achievements button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.ACHIEVEMENTS)
    
    def _on_settings(self) -> None:
        """Handle settings button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.SETTINGS)
    
    def _on_tutorial(self) -> None:
        """Handle tutorial button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.TUTORIAL)
    
    def _on_stats(self) -> None:
        """Handle stats button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.STATS)
    
    def _on_exit(self) -> None:
        """Handle exit button"""
        self.audio.play(SoundType.MENU_BACK)
        self.running = False
        self.next_screen = None
    
    def update(self) -> None:
        """Update menu animations"""
        super().update()
        self.title_angle += 0.02
    
    def draw(self) -> None:
        """Draw main menu"""
        super().draw()
        
        # Draw animated title
        center_x = self.screen.get_width() // 2
        title_y = 150
        
        # 标题阴影
        shadow_offset = 4
        title_shadow = self.fonts["title"].render("1024", True, (100, 100, 100))
        shadow_rect = title_shadow.get_rect(center=(center_x + shadow_offset, title_y + shadow_offset))
        self.screen.blit(title_shadow, shadow_rect)
        
        # 主标题颜色循环
        hue = (math.sin(self.title_angle) + 1) / 2
        r = int(200 + 55 * hue)
        g = int(150 + 50 * math.sin(self.title_angle + 2))
        b = int(100 + 50 * math.sin(self.title_angle + 4))
        title_color = (r, g, b)
        
        title_surface = self.fonts["title"].render("1024", True, title_color)
        title_rect = title_surface.get_rect(center=(center_x, title_y))
        self.screen.blit(title_surface, title_rect)
        
        # 副标题
        subtitle = self.fonts["medium"].render("数字益智挑战", True,
                                               self.theme.get("text_dark", (100, 100, 100)))
        subtitle_rect = subtitle.get_rect(center=(center_x, title_y + 60))
        self.screen.blit(subtitle, subtitle_rect)


class LevelSelectScreen(BaseScreen):
    """Level selection screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level_buttons: List[Button] = []
        self.scroll_offset = 0
        self.max_scroll = 0
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create level selection buttons"""
        # Back button
        back_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        self.buttons.append(Button(
            50, 30, 120, 40,
            "← 返回", self.fonts["medium"], back_style,
            lambda: self._on_back()
        ))
        
        # 关卡按钮
        level_style_locked = ButtonStyle(
            normal_color=(150, 150, 150),
            hover_color=(150, 150, 150),
            pressed_color=(150, 150, 150),
            text_color=(200, 200, 200),
            border_radius=8
        )
        
        level_style_unlocked = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        level_style_completed = ButtonStyle(
            normal_color=(100, 180, 100),
            hover_color=(120, 200, 120),
            pressed_color=(80, 160, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        cols = 5
        rows = 4
        button_size = 80
        spacing = 20
        start_x = (self.screen.get_width() - (cols * button_size + (cols - 1) * spacing)) // 2
        start_y = 120
        
        for level in range(1, config.MAX_LEVELS + 1):
            row = (level - 1) // cols
            col = (level - 1) % cols
            x = start_x + col * (button_size + spacing)
            y = start_y + row * (button_size + spacing)
            
            progress = self.data.get_level_progress(level)
            
            if progress.completed:
                style = level_style_completed
            elif self.data.is_level_unlocked(level):
                style = level_style_unlocked
            else:
                style = level_style_locked
            
            btn = Button(
                x, y, button_size, button_size,
                str(level), self.fonts["large"], style,
                lambda l=level: self._on_level_click(l)
            )
            self.level_buttons.append(btn)
    
    def _on_back(self) -> None:
        """Handle back button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def _on_level_click(self, level: int) -> None:
        """Handle level button click"""
        if not self.data.is_level_unlocked(level):
            self.audio.play(SoundType.MENU_BACK)
            self.add_notification("关卡未解锁!", (255, 100, 100))
            return
        
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.GAME, {"level": level})
    
    def update(self) -> None:
        """Update screen"""
        super().update()
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for button in self.level_buttons:
            button.update(mouse_pos, mouse_pressed)
    
    def draw(self) -> None:
        """Draw level select screen"""
        super().draw()
        
        # Draw level buttons
        for button in self.level_buttons:
            button.draw(self.screen)
        
        # 绘制标题
        title = self.fonts["xlarge"].render("选择关卡", True,
                                            self.theme.get("text_dark", (0, 0, 0)))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title, title_rect)


class GameScreen(BaseScreen):
    """Main game screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = self.screen_data.get("level", 1)
        self.game = GameEngine(self.level)
        self.particles = ParticleSystem()
        self.tiles: List[AnimatedTile] = []
        self.animating = False
        self.animation_timer = 0
        self.score_display = 0
        self.start_time = pygame.time.get_ticks()
        
        self._create_buttons()
        self._init_tiles()
    
    def _create_buttons(self) -> None:
        """Create game UI buttons"""
        button_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        # 暂停按钮
        self.buttons.append(Button(
            20, 20, 100, 40,
            "暂停", self.fonts["small"], button_style,
            lambda: self._on_pause()
        ))
        
        # 撤销按钮
        self.undo_button = Button(
            130, 20, 100, 40,
            "撤销", self.fonts["small"], button_style,
            lambda: self._on_undo()
        )
        self.buttons.append(self.undo_button)
        
        # 重新开始按钮
        self.buttons.append(Button(
            240, 20, 100, 40,
            "重开", self.fonts["small"], button_style,
            lambda: self._on_restart()
        ))
        
        # 菜单按钮
        self.buttons.append(Button(
            350, 20, 100, 40,
            "菜单", self.fonts["small"], button_style,
            lambda: self._on_menu()
        ))
    
    def _init_tiles(self) -> None:
        """Initialize tile display"""
        self.tiles.clear()
        for row in range(4):
            for col in range(4):
                x = config.GRID_OFFSET_X + col * (config.CELL_SIZE + config.CELL_PADDING)
                y = config.GRID_OFFSET_Y + row * (config.CELL_SIZE + config.CELL_PADDING)
                tile = self.game.get_tile(row, col)
                value = tile.value if tile else 0
                is_obstacle = tile.is_obstacle if tile else False
                
                if is_obstacle:
                    value = -1
                
                animated_tile = AnimatedTile(
                    value, x, y, config.CELL_SIZE,
                    self.theme, is_new=False
                )
                self.tiles.append(animated_tile)
    
    def _on_pause(self) -> None:
        """Handle pause button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.PAUSE, {"level": self.level, "game": self.game})
    
    def _on_undo(self) -> None:
        """Handle undo button"""
        if self.game.can_undo():
            self.audio.play(SoundType.MENU_BACK)
            self.game.undo()
            self._init_tiles()
        else:
            self.audio.play(SoundType.MENU_BACK)
            self.add_notification("撤销次数已用完!", (255, 100, 100))
    
    def _on_restart(self) -> None:
        """Handle restart button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.game.reset()
        self.score_display = 0
        self.start_time = pygame.time.get_ticks()
        self._init_tiles()
    
    def _on_menu(self) -> None:
        """Handle menu button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if self.game.state == GameState.IDLE:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self._make_move("up")
                    return True
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self._make_move("down")
                    return True
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    self._make_move("left")
                    return True
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self._make_move("right")
                    return True
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self._on_undo()
                    return True
        
        return False
    
    def _make_move(self, direction: str) -> None:
        """Execute a move"""
        result = self.game.move(direction)
        
        if result.moved:
            self.audio.play(SoundType.MOVE)
            
            # Play merge sounds
            for merge in result.merges:
                self.audio.play(SoundType.MERGE)
                # Add particle effect at merge position
                row, col, value = merge
                x = config.GRID_OFFSET_X + col * (config.CELL_SIZE + config.CELL_PADDING) + config.CELL_SIZE // 2
                y = config.GRID_OFFSET_Y + row * (config.CELL_SIZE + config.CELL_PADDING) + config.CELL_SIZE // 2
                tile_colors = self.theme.get("tile_colors", {})
                color = tile_colors.get(value, (255, 255, 255))
                self.particles.spawn_merge_effect(x, y, color, value)
            
            # Play spawn sounds
            for spawn in result.new_tiles:
                self.audio.play(SoundType.SPAWN)
            
            # Update tiles
            self._init_tiles()
            
            # Check game state
            if self.game.state == GameState.LEVEL_COMPLETE:
                self._on_level_complete()
            elif self.game.state == GameState.GAME_OVER:
                self._on_game_over()
    
    def _on_level_complete(self) -> None:
        """Handle level completion"""
        self.audio.play(SoundType.LEVEL_COMPLETE)

        # Calculate elapsed time
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0

        # Save progress
        stars = self.game.get_stars()
        self.data.update_level_progress(
            self.level, True, self.game.score, elapsed, stars
        )

        # Update statistics
        self.data.update_statistics(
            total_games_played=1,
            total_time_played=elapsed,
            highest_score=max(0, self.game.score - self.data.statistics.highest_score),
            total_moves=self.game.moves,
            total_merges=len(self.game.undo_stack),
        )

        # Check and unlock achievements
        self._check_achievements_on_complete(elapsed, stars)

        # Add celebration particles
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        self.particles.spawn_level_complete(center_x, center_y)

        # Switch to level complete screen
        self.switch_to(ScreenType.LEVEL_COMPLETE, {
            "level": self.level,
            "score": self.game.score,
            "time": elapsed,
            "stars": stars,
            "moves": self.game.moves,
        })

    def _check_achievements_on_complete(self, elapsed: float, stars: int) -> None:
        """Check and unlock achievements when level is completed"""
        # first_win - 完成第1关
        if self.level == 1:
            self.data.unlock_achievement("first_win")

        # level_5_master - 完成第5关
        if self.level >= 5:
            self.data.unlock_achievement("level_5_master")

        # level_10_master - 完成第10关
        if self.level >= 10:
            self.data.unlock_achievement("level_10_master")

        # level_15_master - 完成第15关
        if self.level >= 15:
            self.data.unlock_achievement("level_15_master")

        # grand_master - 完成全部20关
        if self.level >= 20:
            self.data.unlock_achievement("grand_master")

        # speed_demon - 在60秒内完成一关
        if elapsed <= 60:
            self.data.unlock_achievement("speed_demon")

        # perfectionist - 不使用撤销完成一关（3星评价）
        if stars >= 3:
            self.data.unlock_achievement("perfectionist")

        # millionaire - 分数超过1,000,000
        if self.game.score >= 1000000:
            self.data.unlock_achievement("millionaire")

        # persistent - 玩50局游戏（在update_statistics中已增加）
        self.data.check_achievement("persistent", 1)
    
    def _on_game_over(self) -> None:
        """Handle game over"""
        self.audio.play(SoundType.GAME_OVER)
        
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        
        # Save progress (attempt)
        self.data.update_level_progress(self.level, False)
        
        self.switch_to(ScreenType.GAME_OVER, {
            "level": self.level,
            "score": self.game.score,
            "time": elapsed,
            "moves": self.game.moves,
        })
    
    def update(self) -> None:
        """Update game screen"""
        super().update()
        
        # Update particles
        self.particles.update()
        
        # Update tiles
        for tile in self.tiles:
            tile.update()
        
        # Animate score display
        diff = self.game.score - self.score_display
        self.score_display += int(diff * 0.1)
    
    def draw(self) -> None:
        """Draw game screen"""
        self.screen.fill(self.theme.get("background", (250, 248, 239)))
        
        # Draw grid background
        grid_width = 4 * config.CELL_SIZE + 3 * config.CELL_PADDING
        grid_height = 4 * config.CELL_SIZE + 3 * config.CELL_PADDING
        grid_rect = pygame.Rect(
            config.GRID_OFFSET_X - config.CELL_PADDING,
            config.GRID_OFFSET_Y - config.CELL_PADDING,
            grid_width + 2 * config.CELL_PADDING,
            grid_height + 2 * config.CELL_PADDING
        )
        pygame.draw.rect(
            self.screen,
            self.theme.get("grid_background", (187, 173, 160)),
            grid_rect,
            border_radius=10
        )
        
        # Draw tiles
        for tile in self.tiles:
            tile.draw(self.screen, self.fonts["large"])
        
        # Draw particles
        self.particles.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw notifications
        for notification in self.notifications:
            notification.draw(self.screen)
    
    def _draw_ui(self) -> None:
        """Draw game UI"""
        # 关卡信息
        level_text = self.fonts["large"].render(f"第 {self.level} 关", True,
                                                self.theme.get("text_dark", (0, 0, 0)))
        self.screen.blit(level_text, (20, 70))
        
        # 目标
        target_text = self.fonts["medium"].render(f"目标: {self.game.target_value}", True,
                                                  self.theme.get("text_dark", (0, 0, 0)))
        self.screen.blit(target_text, (20, 110))
        
        # 分数
        score_text = self.fonts["xlarge"].render(f"分数: {self.score_display}", True,
                                                 self.theme.get("text_dark", (0, 0, 0)))
        self.screen.blit(score_text, (20, 150))
        
        # 步数
        moves_text = self.fonts["medium"].render(f"步数: {self.game.moves}", True,
                                                 self.theme.get("text_dark", (0, 0, 0)))
        self.screen.blit(moves_text, (20, 200))
        
        # 时间
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        time_text = self.fonts["medium"].render(f"时间: {minutes:02d}:{seconds:02d}", True,
                                                self.theme.get("text_dark", (0, 0, 0)))
        self.screen.blit(time_text, (20, 240))
        
        # 剩余撤销次数
        undos_left = self.game.max_undos - self.game.undos_used
        undo_text = self.fonts["small"].render(f"撤销: {undos_left}", True,
                                               self.theme.get("text_dark", (0, 0, 0)))
        self.screen.blit(undo_text, (130, 65))


class SettingsScreen(BaseScreen):
    """Settings screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sliders: List[Slider] = []
        self.toggles: List[Tuple[str, Toggle]] = []
        self._create_ui()
    
    def _create_ui(self) -> None:
        """Create settings UI"""
        center_x = self.screen.get_width() // 2
        start_y = 200
        
        # Back button
        back_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        self.buttons.append(Button(
            50, 30, 120, 40,
            "← 返回", self.fonts["medium"], back_style,
            lambda: self._on_back()
        ))

        # 音量调节条布局 - 标签在左，调节条在右
        slider_width = 250
        slider_height = 25
        label_width = 180
        start_x = center_x - 250  # 整体起始位置

        # 主音量
        self.sliders.append(Slider(
            start_x + label_width + 20, start_y,
            slider_width, slider_height,
            0.0, 1.0, self.data.audio_settings["master_volume"],
            self.theme
        ))

        # 音乐音量
        self.sliders.append(Slider(
            start_x + label_width + 20, start_y + 70,
            slider_width, slider_height,
            0.0, 1.0, self.data.audio_settings["music_volume"],
            self.theme
        ))

        # 音效音量
        self.sliders.append(Slider(
            start_x + label_width + 20, start_y + 140,
            slider_width, slider_height,
            0.0, 1.0, self.data.audio_settings["sfx_volume"],
            self.theme
        ))

        # 开关布局
        toggle_width = 60
        toggle_height = 30

        # 音乐开关
        self.toggles.append(("music_enabled", Toggle(
            start_x + label_width + 20, start_y + 210,
            toggle_width, toggle_height,
            self.data.audio_settings["music_enabled"],
            self.theme
        )))

        # 音效开关
        self.toggles.append(("sfx_enabled", Toggle(
            start_x + label_width + 20, start_y + 270,
            toggle_width, toggle_height,
            self.data.audio_settings["sfx_enabled"],
            self.theme
        )))
    
    def _on_back(self) -> None:
        """Handle back button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def update(self) -> None:
        """Update settings screen"""
        super().update()
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_down = pygame.mouse.get_pressed()[0]
        
        # Update sliders
        slider_names = ["master_volume", "music_volume", "sfx_volume"]
        for i, slider in enumerate(self.sliders):
            if slider.update(mouse_pos, mouse_pressed, mouse_down):
                self.data.set_audio_setting(slider_names[i], slider.value)
                if slider_names[i] == "master_volume":
                    self.audio.set_master_volume(slider.value)
                elif slider_names[i] == "music_volume":
                    self.audio.set_music_volume(slider.value)
                elif slider_names[i] == "sfx_volume":
                    self.audio.set_sfx_volume(slider.value)
        
        # Update toggles
        for name, toggle in self.toggles:
            if toggle.update(mouse_pos, mouse_pressed):
                self.data.set_audio_setting(name, toggle.state)
                if name == "music_enabled":
                    self.audio.toggle_music()
                elif name == "sfx_enabled":
                    self.audio.toggle_sfx()
    
    def draw(self) -> None:
        """Draw settings screen"""
        super().draw()
        
        center_x = self.screen.get_width() // 2
        
        # Title
        title = self.fonts["xlarge"].render("游戏设置", True,
                                            self.theme.get("text_dark", (0, 0, 0)))
        title_rect = title.get_rect(center=(center_x, 80))
        self.screen.blit(title, title_rect)

        # 标签位置 - 与调节条对齐
        label_x = center_x - 250  # 与_create_ui中的start_x一致
        label_width = 180

        # 标签列表 (标签文字, 对应的Y坐标)
        labels = [
            ("主音量", 200),
            ("音乐音量", 270),
            ("音效音量", 340),
            ("开启音乐", 420),
            ("开启音效", 480),
        ]

        for text, y in labels:
            label = self.fonts["medium"].render(text, True,
                                                self.theme.get("text_dark", (0, 0, 0)))
            # 文字右对齐到标签区域
            label_rect = label.get_rect(midright=(label_x + label_width - 10, y + 12))
            self.screen.blit(label, label_rect)
        
        # Draw sliders
        for slider in self.sliders:
            slider.draw(self.screen)
        
        # Draw toggles
        for name, toggle in self.toggles:
            toggle.draw(self.screen)


class AchievementsScreen(BaseScreen):
    """Achievements screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create buttons"""
        back_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        self.buttons.append(Button(
            50, 30, 120, 40,
            "← 返回", self.fonts["medium"], back_style,
            lambda: self._on_back()
        ))

    def _on_back(self) -> None:
        """Handle back button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)

    def draw(self) -> None:
        """Draw achievements screen"""
        super().draw()

        center_x = self.screen.get_width() // 2

        # 标题
        title = self.fonts["xlarge"].render("成就系统", True,
                                            self.theme.get("text_dark", (0, 0, 0)))
        title_rect = title.get_rect(center=(center_x, 80))
        self.screen.blit(title, title_rect)
        
        # Draw achievements
        y = 150
        for achievement_id, info in config.ACHIEVEMENTS.items():
            progress = self.data.achievements[achievement_id]
            
            # Background
            bg_color = (200, 255, 200) if progress.unlocked else (240, 240, 240)
            rect = pygame.Rect(100, y, self.screen.get_width() - 200, 70)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 150, 150), rect, 2, border_radius=8)
            
            # Icon
            icon = self.fonts["large"].render(info["icon"], True, (0, 0, 0))
            self.screen.blit(icon, (120, y + 15))
            
            # 成就名称（中文映射）
            achievement_names = {
                "first_win": "初次胜利",
                "level_5_master": "关卡5大师",
                "level_10_master": "关卡10大师",
                "level_15_master": "关卡15大师",
                "grand_master": "终极大师",
                "speed_demon": "速度之王",
                "perfectionist": "完美主义者",
                "combo_master": "连击大师",
                "millionaire": "百万富翁",
                "persistent": "坚持不懈",
            }
            name_text = achievement_names.get(achievement_id, info["name"])
            name = self.fonts["medium"].render(name_text, True,
                                               self.theme.get("text_dark", (0, 0, 0)))
            self.screen.blit(name, (170, y + 10))

            # 成就描述（中文映射）
            achievement_descs = {
                "first_win": "完成第1关",
                "level_5_master": "完成第5关",
                "level_10_master": "完成第10关",
                "level_15_master": "完成第15关",
                "grand_master": "完成全部20关",
                "speed_demon": "在60秒内完成一关",
                "perfectionist": "不使用撤销完成一关",
                "combo_master": "一次移动完成5次合并",
                "millionaire": "分数超过1,000,000",
                "persistent": "玩50局游戏",
            }
            desc_text = achievement_descs.get(achievement_id, info["description"])
            desc = self.fonts["small"].render(desc_text, True,
                                              self.theme.get("text_dark", (100, 100, 100)))
            self.screen.blit(desc, (170, y + 40))
            
            # Progress
            if not progress.unlocked and progress.target > 1:
                progress_text = f"{progress.progress}/{progress.target}"
                progress_surface = self.fonts["small"].render(progress_text, True,
                                                              (100, 100, 100))
                self.screen.blit(progress_surface, (rect.right - 80, y + 25))
            
            y += 85


class LevelCompleteScreen(BaseScreen):
    """Level complete screen"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 1
        self.score = 0
        self.time = 0
        self.stars = 0
        self.moves = 0

    def init_with_data(self, data: dict) -> None:
        """Initialize with screen data - called after screen_data is set"""
        self.level = data.get("level", 1)
        self.score = data.get("score", 0)
        self.time = data.get("time", 0)
        self.stars = data.get("stars", 0)
        self.moves = data.get("moves", 0)
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create buttons"""
        button_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        center_x = self.screen.get_width() // 2
        
        # 下一关按钮
        if self.level < config.MAX_LEVELS:
            self.buttons.append(Button(
                center_x - 125, 500, 250, 50,
                "下一关", self.fonts["large"], button_style,
                lambda: self._on_next()
            ))

        # 重试按钮
        self.buttons.append(Button(
            center_x - 125, 560, 250, 50,
            "重试", self.fonts["large"], button_style,
            lambda: self._on_retry()
        ))

        # 菜单按钮
        self.buttons.append(Button(
            center_x - 125, 620, 250, 50,
            "主菜单", self.fonts["large"], button_style,
            lambda: self._on_menu()
        ))
    
    def _on_next(self) -> None:
        """Handle next level button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.GAME, {"level": self.level + 1})
    
    def _on_retry(self) -> None:
        """Handle retry button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.GAME, {"level": self.level})
    
    def _on_menu(self) -> None:
        """Handle menu button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def draw(self) -> None:
        """Draw level complete screen"""
        super().draw()
        
        center_x = self.screen.get_width() // 2
        
        # 标题
        title = self.fonts["title"].render("关卡完成!", True, (100, 200, 100))
        title_rect = title.get_rect(center=(center_x, 120))
        self.screen.blit(title, title_rect)

        # 星星
        star_rating = StarRating(center_x - 75, 180, 50)
        star_rating.set_rating(self.stars)
        star_rating.draw(self.screen)

        # 统计
        y = 280
        stats = [
            (f"分数: {self.score}", y),
            (f"时间: {int(self.time // 60):02d}:{int(self.time % 60):02d}", y + 50),
            (f"步数: {self.moves}", y + 100),
        ]

        for text, stat_y in stats:
            stat_surface = self.fonts["large"].render(text, True,
                                                      self.theme.get("text_dark", (0, 0, 0)))
            stat_rect = stat_surface.get_rect(center=(center_x, stat_y))
            self.screen.blit(stat_surface, stat_rect)


class GameOverScreen(BaseScreen):
    """Game over screen"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 1
        self.score = 0
        self.time = 0
        self.moves = 0

    def init_with_data(self, data: dict) -> None:
        """Initialize with screen data - called after screen_data is set"""
        self.level = data.get("level", 1)
        self.score = data.get("score", 0)
        self.time = data.get("time", 0)
        self.moves = data.get("moves", 0)
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create buttons"""
        button_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        center_x = self.screen.get_width() // 2
        
        # 重试按钮
        self.buttons.append(Button(
            center_x - 125, 450, 250, 50,
            "再试一次", self.fonts["large"], button_style,
            lambda: self._on_retry()
        ))

        # 菜单按钮
        self.buttons.append(Button(
            center_x - 125, 520, 250, 50,
            "主菜单", self.fonts["large"], button_style,
            lambda: self._on_menu()
        ))
    
    def _on_retry(self) -> None:
        """Handle retry button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.GAME, {"level": self.level})
    
    def _on_menu(self) -> None:
        """Handle menu button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def draw(self) -> None:
        """Draw game over screen"""
        super().draw()
        
        center_x = self.screen.get_width() // 2
        
        # 标题
        title = self.fonts["title"].render("游戏结束", True, (200, 100, 100))
        title_rect = title.get_rect(center=(center_x, 150))
        self.screen.blit(title, title_rect)

        # 消息
        msg = self.fonts["medium"].render("没有可移动的步数了!", True,
                                          self.theme.get("text_dark", (0, 0, 0)))
        msg_rect = msg.get_rect(center=(center_x, 220))
        self.screen.blit(msg, msg_rect)

        # 统计
        y = 300
        stats = [
            (f"最终分数: {self.score}", y),
            (f"时间: {int(self.time // 60):02d}:{int(self.time % 60):02d}", y + 50),
            (f"步数: {self.moves}", y + 100),
        ]

        for text, stat_y in stats:
            stat_surface = self.fonts["large"].render(text, True,
                                                      self.theme.get("text_dark", (0, 0, 0)))
            stat_rect = stat_surface.get_rect(center=(center_x, stat_y))
            self.screen.blit(stat_surface, stat_rect)


class PauseScreen(BaseScreen):
    """Pause screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = self.screen_data.get("level", 1)
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create buttons"""
        button_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        center_x = self.screen.get_width() // 2
        
        # 继续按钮
        self.buttons.append(Button(
            center_x - 125, 300, 250, 50,
            "继续游戏", self.fonts["large"], button_style,
            lambda: self._on_resume()
        ))

        # 重新开始按钮
        self.buttons.append(Button(
            center_x - 125, 370, 250, 50,
            "重新开始", self.fonts["large"], button_style,
            lambda: self._on_restart()
        ))

        # 菜单按钮
        self.buttons.append(Button(
            center_x - 125, 440, 250, 50,
            "主菜单", self.fonts["large"], button_style,
            lambda: self._on_menu()
        ))
    
    def _on_resume(self) -> None:
        """Handle resume button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.GAME, {"level": self.level})
    
    def _on_restart(self) -> None:
        """Handle restart button"""
        self.audio.play(SoundType.MENU_CONFIRM)
        self.switch_to(ScreenType.GAME, {"level": self.level})
    
    def _on_menu(self) -> None:
        """Handle menu button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def draw(self) -> None:
        """Draw pause screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # 标题
        center_x = self.screen.get_width() // 2
        title = self.fonts["title"].render("游戏暂停", True, (255, 255, 255))
        title_rect = title.get_rect(center=(center_x, 200))
        self.screen.blit(title, title_rect)


class StatsScreen(BaseScreen):
    """Statistics screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create buttons"""
        back_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        self.buttons.append(Button(
            50, 30, 120, 40,
            "← 返回", self.fonts["medium"], back_style,
            lambda: self._on_back()
        ))

    def _on_back(self) -> None:
        """Handle back button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)

    def draw(self) -> None:
        """Draw statistics screen"""
        super().draw()

        center_x = self.screen.get_width() // 2
        stats = self.data.statistics

        # 标题
        title = self.fonts["xlarge"].render("游戏统计", True,
                                            self.theme.get("text_dark", (0, 0, 0)))
        title_rect = title.get_rect(center=(center_x, 80))
        self.screen.blit(title, title_rect)

        # 统计列表
        y = 150
        stat_items = [
            ("总游戏次数", stats.total_games_played),
            ("总游戏时间", f"{int(stats.total_time_played // 3600)}小时 {int((stats.total_time_played % 3600) // 60)}分钟"),
            ("最高分数", stats.highest_score),
            ("总移动次数", stats.total_moves),
            ("总合并次数", stats.total_merges),
            ("最大方块", stats.biggest_tile),
            ("完成关卡数", stats.levels_completed),
            ("完美游戏数", stats.perfect_games),
        ]

        for label, value in stat_items:
            # 标签
            label_surface = self.fonts["medium"].render(label + ":", True,
                                                        self.theme.get("text_dark", (0, 0, 0)))
            self.screen.blit(label_surface, (center_x - 200, y))

            # 数值
            value_surface = self.fonts["medium"].render(str(value), True,
                                                        self.theme.get("text_dark", (0, 0, 0)))
            self.screen.blit(value_surface, (center_x + 50, y))

            y += 50


class TutorialScreen(BaseScreen):
    """Tutorial screen"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = 0
        self.max_pages = 4
        self._create_buttons()
    
    def _create_buttons(self) -> None:
        """Create buttons"""
        button_style = ButtonStyle(
            normal_color=self.theme.get("button", (143, 122, 102)),
            hover_color=self.theme.get("button_hover", (160, 140, 120)),
            pressed_color=(120, 100, 80),
            text_color=(255, 255, 255),
            border_radius=8
        )
        
        # 返回按钮
        self.buttons.append(Button(
            50, 30, 120, 40,
            "← 返回", self.fonts["medium"], button_style,
            lambda: self._on_back()
        ))

        # 下一页按钮
        self.next_button = Button(
            self.screen.get_width() - 170, self.screen.get_height() - 80,
            120, 40,
            "下一页 →", self.fonts["medium"], button_style,
            lambda: self._on_next()
        )
        self.buttons.append(self.next_button)

        # 上一页按钮
        self.prev_button = Button(
            50, self.screen.get_height() - 80,
            120, 40,
            "← 上一页", self.fonts["medium"], button_style,
            lambda: self._on_prev()
        )
        self.buttons.append(self.prev_button)
    
    def _on_back(self) -> None:
        """Handle back button"""
        self.audio.play(SoundType.MENU_BACK)
        self.switch_to(ScreenType.MAIN_MENU)
    
    def _on_next(self) -> None:
        """Handle next button"""
        self.audio.play(SoundType.MENU_SELECT)
        if self.page < self.max_pages - 1:
            self.page += 1
        else:
            self.switch_to(ScreenType.MAIN_MENU)
    
    def _on_prev(self) -> None:
        """Handle previous button"""
        self.audio.play(SoundType.MENU_SELECT)
        if self.page > 0:
            self.page -= 1
    
    def draw(self) -> None:
        """Draw tutorial screen"""
        super().draw()

        center_x = self.screen.get_width() // 2

        # 标题
        title = self.fonts["xlarge"].render("游戏教程", True,
                                            self.theme.get("text_dark", (0, 0, 0)))
        title_rect = title.get_rect(center=(center_x, 80))
        self.screen.blit(title, title_rect)

        # 页面内容（中文）
        pages = [
            [
                "欢迎来到1024!",
                "",
                "目标是将相同数字的方块合并，",
                "达到关卡目标值。",
                "",
                "使用方向键或WASD移动方块。",
            ],
            [
                "当两个相同数字的方块碰撞时，",
                "它们会合并成一个!",
                "",
                "2 + 2 = 4",
                "4 + 4 = 8",
                "8 + 8 = 16",
                "以此类推...",
            ],
            [
                "每个关卡都有一个目标值需要达到。",
                "",
                "完成关卡可以解锁新关卡。",
                "更高关卡有障碍物，",
                "并且会生成更高数值的方块。",
            ],
            [
                "游戏技巧:",
                "",
                "• 提前规划你的移动",
                "• 将高数值方块保持在角落",
                "• 明智地使用撤销功能（每关有限）",
                "• 注意障碍物（灰色方块）",
            ],
        ]

        y = 180
        for line in pages[self.page]:
            if line:
                text_surface = self.fonts["medium"].render(line, True,
                                                           self.theme.get("text_dark", (0, 0, 0)))
                text_rect = text_surface.get_rect(center=(center_x, y))
                self.screen.blit(text_surface, text_rect)
            y += 40

        # 页面指示器
        page_text = f"第 {self.page + 1}/{self.max_pages} 页"
        page_surface = self.fonts["small"].render(page_text, True,
                                                  self.theme.get("text_dark", (100, 100, 100)))
        page_rect = page_surface.get_rect(center=(center_x, self.screen.get_height() - 60))
        self.screen.blit(page_surface, page_rect)
