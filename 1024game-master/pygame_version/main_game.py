"""
1024 Game - Pygame Version - Main Game
主游戏类，整合所有系统
"""

import pygame
import sys
import time
from typing import Optional, List

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GRID_SIZE,
    CELL_SIZE, CELL_PADDING, GRID_OFFSET_X, GRID_OFFSET_Y,
    TILE_COLORS, TILE_COLORS_DARK, TEXT_COLORS,
    Colors, GameState, Direction, LEVEL_CONFIGS
)
from game_engine import LevelGame
from particles import AnimationManager, ParticleSystem
from audio import AudioManager
from data_manager import get_data_manager, DataManager
from ui_components import (
    UIManager, Button, Label, Panel, ProgressBar,
    Slider, Theme, DarkTheme, Toast, Dialog
)
from tutorial import TutorialSystem, InteractiveTutorial


class MainGame:
    """主游戏类"""
    
    def __init__(self):
        # 初始化Pygame
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # 创建窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1024 Game - Pygame Edition v2.0")
        
        # 时钟
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 数据管理器
        self.data_manager = get_data_manager()
        
        # 游戏状态
        self.state = GameState.MENU
        self.previous_state = None
        
        # 当前游戏
        self.current_game: Optional[LevelGame] = None
        self.current_level = 1
        
        # 动画和音效
        self.animation_manager = AnimationManager()
        self.audio_manager = AudioManager()
        
        # UI管理器
        self.ui_manager = UIManager()
        
        # 教程系统
        self.tutorial_system: Optional[TutorialSystem] = None
        self.interactive_tutorial = InteractiveTutorial()
        
        # 字体
        self._init_fonts()
        
        # 初始化系统
        self._init_systems()
        
        # 创建UI
        self._create_menu_ui()
        self._create_level_select_ui()
        self._create_settings_ui()
        self._create_achievements_ui()
        self._create_game_ui()
        self._create_pause_ui()
        self._create_victory_ui()
        self._create_game_over_ui()
        
        # 显示当前状态的UI
        self._show_current_state_ui()
    
    def _init_fonts(self) -> None:
        """初始化字体"""
        from config import FONT_SIZES
        self.fonts = {}
        for name, size in FONT_SIZES.items():
            try:
                self.fonts[name] = pygame.font.Font(None, size)
            except:
                self.fonts[name] = pygame.font.SysFont("arial", size)
    
    def _init_systems(self) -> None:
        """初始化系统"""
        # 应用主题
        dark_theme = self.data_manager.get_setting('dark_theme', False)
        self.ui_manager.set_theme(dark_theme)
        
        # 初始化音频
        self.audio_manager.initialize()
        volumes = self.data_manager.get_volumes()
        self.audio_manager.set_master_volume(volumes['master'])
        self.audio_manager.set_sfx_volume(volumes['sfx'])
        self.audio_manager.set_music_volume(volumes['music'])
        
        # 启动动画系统
        self.animation_manager.start()
        
        # 加载解锁关卡
        self.unlocked_levels = self.data_manager.get_unlocked_levels()
    
    def _create_menu_ui(self) -> None:
        """创建主菜单UI"""
        self.menu_ui = UIManager()
        
        # 标题
        title = Label(640, 120, "1024", 'title', center=True)
        self.menu_ui.add_component(title)
        
        subtitle = Label(640, 200, "Pygame Edition", 'normal', center=True)
        self.menu_ui.add_component(subtitle)
        
        # 按钮
        button_width, button_height = 200, 50
        start_x = 640 - button_width // 2
        start_y = 300
        gap = 70
        
        btn_play = Button(start_x, start_y, button_width, button_height,
                         "Play", 'normal', lambda: self._change_state(GameState.LEVEL_SELECT))
        self.menu_ui.add_component(btn_play)
        
        btn_achievements = Button(start_x, start_y + gap, button_width, button_height,
                                 "Achievements", 'normal', 
                                 lambda: self._change_state(GameState.ACHIEVEMENTS))
        self.menu_ui.add_component(btn_achievements)
        
        btn_settings = Button(start_x, start_y + gap * 2, button_width, button_height,
                             "Settings", 'normal',
                             lambda: self._change_state(GameState.SETTINGS))
        self.menu_ui.add_component(btn_settings)
        
        btn_tutorial = Button(start_x, start_y + gap * 3, button_width, button_height,
                             "Tutorial", 'normal', self._show_tutorial)
        self.menu_ui.add_component(btn_tutorial)
        
        btn_quit = Button(start_x, start_y + gap * 4, button_width, button_height,
                         "Quit", 'normal', self._quit_game)
        self.menu_ui.add_component(btn_quit)
    
    def _create_level_select_ui(self) -> None:
        """创建关卡选择UI"""
        self.level_select_ui = UIManager()
        
        # 标题
        title = Label(640, 50, "Select Level", 'large', center=True)
        self.level_select_ui.add_component(title)
        
        # 返回按钮
        btn_back = Button(50, 50, 100, 40, "Back", 'normal',
                         lambda: self._change_state(GameState.MENU))
        self.level_select_ui.add_component(btn_back)
        
        # 关卡按钮
        self.level_buttons = []
        cols = 5
        rows = 4
        button_size = 80
        gap = 20
        start_x = 640 - (cols * (button_size + gap)) // 2 + gap // 2
        start_y = 150
        
        for level in range(1, 21):
            row = (level - 1) // cols
            col = (level - 1) % cols
            x = start_x + col * (button_size + gap)
            y = start_y + row * (button_size + gap)
            
            btn = Button(x, y, button_size, button_size, str(level), 'normal',
                        lambda l=level: self._start_level(l))
            btn.enabled = level <= self.unlocked_levels
            self.level_buttons.append(btn)
            self.level_select_ui.add_component(btn)
        
        # 难度说明
        info_y = start_y + rows * (button_size + gap) + 30
        info_texts = [
            "Levels 1-5: Beginner (Target: 512-1024)",
            "Levels 6-10: Intermediate (Target: 2048, Time Limit)",
            "Levels 11-15: Advanced (Target: 4096, Obstacles)",
            "Levels 16-20: Expert (Target: 8192, Hard Mode)"
        ]
        
        for i, text in enumerate(info_texts):
            label = Label(640, info_y + i * 30, text, 'small', center=True)
            self.level_select_ui.add_component(label)
    
    def _create_settings_ui(self) -> None:
        """创建设置UI"""
        self.settings_ui = UIManager()
        
        # 标题
        title = Label(640, 50, "Settings", 'large', center=True)
        self.settings_ui.add_component(title)
        
        # 返回按钮
        btn_back = Button(50, 50, 100, 40, "Back", 'normal',
                         lambda: self._change_state(GameState.MENU))
        self.settings_ui.add_component(btn_back)
        
        # 设置项
        settings_y = 150
        gap = 80
        
        # 主音量
        lbl_master = Label(300, settings_y, "Master Volume:", 'normal')
        self.settings_ui.add_component(lbl_master)
        
        volumes = self.data_manager.get_volumes()
        slider_master = Slider(500, settings_y, 400, 30, 0, 1, volumes['master'],
                              lambda v: self._set_volume(master=v))
        self.settings_ui.add_component(slider_master)
        
        # 音效音量
        lbl_sfx = Label(300, settings_y + gap, "SFX Volume:", 'normal')
        self.settings_ui.add_component(lbl_sfx)
        
        slider_sfx = Slider(500, settings_y + gap, 400, 30, 0, 1, volumes['sfx'],
                           lambda v: self._set_volume(sfx=v))
        self.settings_ui.add_component(slider_sfx)
        
        # 音乐音量
        lbl_music = Label(300, settings_y + gap * 2, "Music Volume:", 'normal')
        self.settings_ui.add_component(lbl_music)
        
        slider_music = Slider(500, settings_y + gap * 2, 400, 30, 0, 1, volumes['music'],
                             lambda v: self._set_volume(music=v))
        self.settings_ui.add_component(slider_music)
        
        # 主题切换
        lbl_theme = Label(300, settings_y + gap * 3, "Dark Theme:", 'normal')
        self.settings_ui.add_component(lbl_theme)
        
        btn_theme = Button(500, settings_y + gap * 3, 150, 40,
                          "Toggle", 'normal', self._toggle_theme)
        self.settings_ui.add_component(btn_theme)
        
        # 重置数据
        btn_reset = Button(500, settings_y + gap * 4, 200, 40,
                          "Reset All Data", 'normal', self._reset_data)
        self.settings_ui.add_component(btn_reset)
    
    def _create_achievements_ui(self) -> None:
        """创建成就UI"""
        self.achievements_ui = UIManager()
        
        # 标题
        title = Label(640, 50, "Achievements", 'large', center=True)
        self.achievements_ui.add_component(title)
        
        # 返回按钮
        btn_back = Button(50, 50, 100, 40, "Back", 'normal',
                         lambda: self._change_state(GameState.MENU))
        self.achievements_ui.add_component(btn_back)
        
        # 成就列表
        from config import ACHIEVEMENTS
        start_y = 120
        gap = 55
        
        for i, ach in enumerate(ACHIEVEMENTS):
            y = start_y + i * gap
            
            # 图标
            icon = Label(100, y, ach.icon, 'large')
            self.achievements_ui.add_component(icon)
            
            # 名称
            name = Label(150, y, ach.name, 'normal')
            self.achievements_ui.add_component(name)
            
            # 描述
            desc = Label(150, y + 25, ach.description, 'small')
            self.achievements_ui.add_component(desc)
            
            # 状态
            is_unlocked = self.data_manager.is_achievement_unlocked(ach.id)
            status_text = "✓ Unlocked" if is_unlocked else "✗ Locked"
            status_color = (100, 200, 100) if is_unlocked else (200, 100, 100)
            status = Label(600, y + 10, status_text, 'small', color=status_color)
            self.achievements_ui.add_component(status)
    
    def _create_game_ui(self) -> None:
        """创建游戏UI"""
        self.game_ui = UIManager()
        
        # 分数面板
        score_panel = Panel(50, 50, 250, 150, border_radius=10)
        self.game_ui.add_component(score_panel)
        
        # 分数标签
        self.score_label = Label(70, 70, "Score: 0", 'normal')
        self.game_ui.add_component(self.score_label)
        
        self.target_label = Label(70, 110, "Target: 1024", 'normal')
        self.game_ui.add_component(self.target_label)
        
        self.level_label = Label(70, 150, "Level: 1", 'normal')
        self.game_ui.add_component(self.level_label)
        
        # 时间标签
        self.time_label = Label(70, 190, "Time: --", 'normal')
        self.game_ui.add_component(self.time_label)
        
        # 按钮
        btn_pause = Button(1050, 50, 100, 40, "Pause", 'normal', self._pause_game)
        self.game_ui.add_component(btn_pause)
        
        btn_undo = Button(1160, 50, 70, 40, "Undo", 'normal', self._undo_move)
        self.game_ui.add_component(btn_undo)
        
        btn_restart = Button(1050, 100, 100, 40, "Restart", 'normal', self._restart_level)
        self.game_ui.add_component(btn_restart)
        
        btn_quit = Button(1160, 100, 70, 40, "Quit", 'normal',
                         lambda: self._change_state(GameState.LEVEL_SELECT))
        self.game_ui.add_component(btn_quit)
        
        # 操作提示
        hint = Label(640, 680, "WASD/Arrows: Move | Z: Undo | P: Pause", 'small', center=True)
        self.game_ui.add_component(hint)
    
    def _create_pause_ui(self) -> None:
        """创建暂停UI"""
        self.pause_ui = UIManager()
        
        # 半透明背景
        overlay = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))
        self.pause_ui.add_component(overlay)
        
        # 暂停文字
        title = Label(640, 280, "PAUSED", 'xlarge', Colors.TEXT_LIGHT, center=True)
        self.pause_ui.add_component(title)
        
        # 按钮
        btn_resume = Button(540, 350, 200, 50, "Resume", 'normal', self._resume_game)
        self.pause_ui.add_component(btn_resume)
        
        btn_restart = Button(540, 420, 200, 50, "Restart", 'normal', self._restart_level)
        self.pause_ui.add_component(btn_restart)
        
        btn_quit = Button(540, 490, 200, 50, "Quit to Menu", 'normal',
                         lambda: self._change_state(GameState.MENU))
        self.pause_ui.add_component(btn_quit)
    
    def _create_victory_ui(self) -> None:
        """创建胜利UI"""
        self.victory_ui = UIManager()
        
        # 半透明背景
        overlay = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))
        self.victory_ui.add_component(overlay)
        
        # 胜利文字
        title = Label(640, 200, "VICTORY!", 'xlarge', Colors.GOLD, center=True)
        self.victory_ui.add_component(title)
        
        # 统计标签
        self.victory_stats_label = Label(640, 300, "", 'normal', Colors.TEXT_LIGHT, center=True)
        self.victory_ui.add_component(self.victory_stats_label)
        
        # 按钮
        btn_next = Button(440, 450, 200, 50, "Next Level", 'normal', self._next_level)
        self.victory_ui.add_component(btn_next)
        
        btn_retry = Button(660, 450, 200, 50, "Retry", 'normal', self._restart_level)
        self.victory_ui.add_component(btn_retry)
        
        btn_menu = Button(550, 520, 200, 50, "Level Select", 'normal',
                         lambda: self._change_state(GameState.LEVEL_SELECT))
        self.victory_ui.add_component(btn_menu)
    
    def _create_game_over_ui(self) -> None:
        """创建失败UI"""
        self.game_over_ui = UIManager()
        
        # 半透明背景
        overlay = Panel(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))
        self.game_over_ui.add_component(overlay)
        
        # 失败文字
        title = Label(640, 280, "GAME OVER", 'xlarge', (255, 100, 100), center=True)
        self.game_over_ui.add_component(title)
        
        # 统计标签
        self.game_over_stats_label = Label(640, 360, "", 'normal', Colors.TEXT_LIGHT, center=True)
        self.game_over_ui.add_component(self.game_over_stats_label)
        
        # 按钮
        btn_retry = Button(440, 450, 200, 50, "Try Again", 'normal', self._restart_level)
        self.game_over_ui.add_component(btn_retry)
        
        btn_menu = Button(660, 450, 200, 50, "Level Select", 'normal',
                         lambda: self._change_state(GameState.LEVEL_SELECT))
        self.game_over_ui.add_component(btn_menu)
    
    def _show_current_state_ui(self) -> None:
        """显示当前状态的UI"""
        pass  # UI在render中根据状态选择
    
    def _change_state(self, new_state: GameState) -> None:
        """改变游戏状态"""
        self.previous_state = self.state
        self.state = new_state
        
        if new_state == GameState.MENU:
            self.audio_manager.play_button()
        elif new_state == GameState.LEVEL_SELECT:
            self._update_level_buttons()
            self.audio_manager.play_button()
        elif new_state == GameState.SETTINGS:
            self.audio_manager.play_button()
        elif new_state == GameState.ACHIEVEMENTS:
            self._update_achievements_ui()
            self.audio_manager.play_button()
    
    def _start_level(self, level: int) -> None:
        """开始关卡"""
        self.current_level = level
        self.current_game = LevelGame(level)
        
        # 同步动画管理器
        self.animation_manager.sync_with_grid(
            self.current_game.get_grid(),
            GRID_OFFSET_X, GRID_OFFSET_Y,
            CELL_SIZE, CELL_PADDING
        )
        
        self.state = GameState.PLAYING
        self.audio_manager.play_spawn()
    
    def _update_level_buttons(self) -> None:
        """更新关卡按钮状态"""
        self.unlocked_levels = self.data_manager.get_unlocked_levels()
        for i, btn in enumerate(self.level_buttons):
            btn.enabled = (i + 1) <= self.unlocked_levels
    
    def _update_achievements_ui(self) -> None:
        """更新成就UI（重新创建以刷新状态）"""
        self._create_achievements_ui()
    
    def _set_volume(self, master: Optional[float] = None,
                   sfx: Optional[float] = None,
                   music: Optional[float] = None) -> None:
        """设置音量"""
        self.data_manager.set_volume(master, sfx, music)
        
        if master is not None:
            self.audio_manager.set_master_volume(master)
        if sfx is not None:
            self.audio_manager.set_sfx_volume(sfx)
        if music is not None:
            self.audio_manager.set_music_volume(music)
    
    def _toggle_theme(self) -> None:
        """切换主题"""
        new_theme = self.data_manager.toggle_dark_theme()
        self.ui_manager.set_theme(new_theme)
        self.menu_ui.set_theme(DarkTheme() if new_theme else Theme())
        self.level_select_ui.set_theme(DarkTheme() if new_theme else Theme())
        self.settings_ui.set_theme(DarkTheme() if new_theme else Theme())
        self.achievements_ui.set_theme(DarkTheme() if new_theme else Theme())
        self.game_ui.set_theme(DarkTheme() if new_theme else Theme())
    
    def _reset_data(self) -> None:
        """重置所有数据"""
        self.data_manager.reset_all_data()
        self.unlocked_levels = 1
        self._update_level_buttons()
        self.ui_manager.show_toast("All data has been reset!")
    
    def _show_tutorial(self) -> None:
        """显示教程"""
        self.tutorial_system = TutorialSystem(on_complete=self._on_tutorial_complete)
        self.state = GameState.TUTORIAL
        self.audio_manager.play_button()
    
    def _on_tutorial_complete(self) -> None:
        """教程完成回调"""
        self.tutorial_system = None
        self._change_state(GameState.MENU)
    
    def _quit_game(self) -> None:
        """退出游戏"""
        self.running = False
    
    def _pause_game(self) -> None:
        """暂停游戏"""
        if self.current_game:
            self.current_game.pause()
            self.state = GameState.PAUSED
            self.audio_manager.play_button()
    
    def _resume_game(self) -> None:
        """恢复游戏"""
        if self.current_game:
            self.current_game.resume()
            self.state = GameState.PLAYING
            self.audio_manager.play_button()
    
    def _undo_move(self) -> None:
        """撤销移动"""
        if self.current_game and self.current_game.undo():
            self.audio_manager.play_button()
            # 重新同步动画
            self.animation_manager.sync_with_grid(
                self.current_game.get_grid(),
                GRID_OFFSET_X, GRID_OFFSET_Y,
                CELL_SIZE, CELL_PADDING
            )
    
    def _restart_level(self) -> None:
        """重新开始关卡"""
        if self.current_game:
            self.current_game.restart()
            self.animation_manager.clear()
            self.animation_manager.sync_with_grid(
                self.current_game.get_grid(),
                GRID_OFFSET_X, GRID_OFFSET_Y,
                CELL_SIZE, CELL_PADDING
            )
            self.state = GameState.PLAYING
            self.audio_manager.play_button()
    
    def _next_level(self) -> None:
        """下一关"""
        if self.current_level < 20:
            self._start_level(self.current_level + 1)
        else:
            self._change_state(GameState.LEVEL_SELECT)
    
    def handle_events(self) -> None:
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # 教程事件优先处理
            if self.state == GameState.TUTORIAL and self.tutorial_system:
                if self.tutorial_system.handle_event(event):
                    continue
            
            # UI事件处理
            if self.state == GameState.MENU:
                if self.menu_ui.handle_event(event):
                    continue
            elif self.state == GameState.LEVEL_SELECT:
                if self.level_select_ui.handle_event(event):
                    continue
            elif self.state == GameState.SETTINGS:
                if self.settings_ui.handle_event(event):
                    continue
            elif self.state == GameState.ACHIEVEMENTS:
                if self.achievements_ui.handle_event(event):
                    continue
            elif self.state == GameState.PLAYING:
                if self.game_ui.handle_event(event):
                    continue
                self._handle_game_input(event)
            elif self.state == GameState.PAUSED:
                if self.pause_ui.handle_event(event):
                    continue
            elif self.state == GameState.VICTORY:
                if self.victory_ui.handle_event(event):
                    continue
            elif self.state == GameState.GAME_OVER:
                if self.game_over_ui.handle_event(event):
                    continue
    
    def _handle_game_input(self, event: pygame.event.Event) -> None:
        """处理游戏输入"""
        if not self.current_game or self.current_game.is_won or self.current_game.is_over:
            return
        
        if event.type == pygame.KEYDOWN:
            moved = False
            
            if event.key in (pygame.K_UP, pygame.K_w):
                moved = self.current_game.move(Direction.UP)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                moved = self.current_game.move(Direction.DOWN)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                moved = self.current_game.move(Direction.LEFT)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                moved = self.current_game.move(Direction.RIGHT)
            elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self._pause_game()
                return
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self._undo_move()
                return
            
            if moved:
                self.audio_manager.play_move()
                
                # 同步动画管理器与游戏网格
                self.animation_manager.sync_with_grid(
                    self.current_game.get_grid(),
                    GRID_OFFSET_X, GRID_OFFSET_Y,
                    CELL_SIZE, CELL_PADDING
                )
                
                # 检查游戏状态
                if self.current_game.is_won:
                    self._on_victory()
                elif self.current_game.is_over:
                    self._on_game_over()
    
    def _on_victory(self) -> None:
        """胜利处理"""
        self.audio_manager.play_win()
        
        # 解锁下一关
        if self.current_level >= self.unlocked_levels and self.current_level < 20:
            self.data_manager.unlock_level(self.current_level + 1)
        
        # 记录统计
        stats = self.current_game.stats
        self.data_manager.record_game_result(
            self.current_level, True, self.current_game.score,
            stats.total_moves, stats.elapsed_time, stats.max_tile_achieved
        )
        
        # 更新胜利统计标签
        stats_text = f"Score: {self.current_game.score} | Moves: {stats.total_moves} | Time: {int(stats.elapsed_time)}s"
        self.victory_stats_label.set_text(stats_text)
        
        # 隐藏下一关按钮如果是最后一关
        if self.current_level >= 20:
            for component in self.victory_ui.root.children:
                if isinstance(component, Button) and component.text == "Next Level":
                    component.visible = False
        
        self.state = GameState.VICTORY
    
    def _on_game_over(self) -> None:
        """失败处理"""
        self.audio_manager.play_lose()
        
        # 记录统计
        stats = self.current_game.stats
        self.data_manager.record_game_result(
            self.current_level, False, self.current_game.score,
            stats.total_moves, stats.elapsed_time, stats.max_tile_achieved
        )
        
        # 更新失败统计标签
        stats_text = f"Score: {self.current_game.score} | Moves: {stats.total_moves} | Max Tile: {stats.max_tile_achieved}"
        self.game_over_stats_label.set_text(stats_text)
        
        self.state = GameState.GAME_OVER
    
    def update(self) -> None:
        """更新游戏"""
        dt = self.clock.tick(FPS)
        
        # 更新UI
        if self.state == GameState.MENU:
            self.menu_ui.update(dt)
        elif self.state == GameState.LEVEL_SELECT:
            self.level_select_ui.update(dt)
        elif self.state == GameState.SETTINGS:
            self.settings_ui.update(dt)
        elif self.state == GameState.ACHIEVEMENTS:
            self.achievements_ui.update(dt)
        elif self.state == GameState.TUTORIAL and self.tutorial_system:
            self.tutorial_system.update(dt)
        elif self.state == GameState.PLAYING:
            self.game_ui.update(dt)
            self._update_game(dt)
            self.interactive_tutorial.update(dt)
        elif self.state == GameState.PAUSED:
            self.pause_ui.update(dt)
        elif self.state == GameState.VICTORY:
            self.victory_ui.update(dt)
        elif self.state == GameState.GAME_OVER:
            self.game_over_ui.update(dt)
        
        # 更新动画
        self.animation_manager.update(dt)
    
    def _update_game(self, dt: float) -> None:
        """更新游戏逻辑"""
        if not self.current_game:
            return
        
        # 更新时间
        self.current_game.stats.update_time()
        
        # 检查时间限制
        if self.current_game.check_time_limit():
            self.current_game.is_over = True
            self._on_game_over()
            return
        
        # 更新UI标签
        self.score_label.set_text(f"Score: {self.current_game.score}")
        self.target_label.set_text(f"Target: {self.current_game.target_score}")
        self.level_label.set_text(f"Level: {self.current_level}")
        
        if self.current_game.time_limit > 0:
            remaining = self.current_game.get_remaining_time()
            self.time_label.set_text(f"Time: {remaining}s")
        else:
            self.time_label.set_text(f"Time: {int(self.current_game.stats.elapsed_time)}s")
    
    def render(self) -> None:
        """渲染游戏"""
        # 获取主题颜色
        dark_theme = self.data_manager.get_setting('dark_theme', False)
        bg_color = Colors.BACKGROUND_DARK if dark_theme else Colors.BACKGROUND
        
        # 清屏
        self.screen.fill(bg_color)
        
        # 根据状态渲染
        if self.state == GameState.MENU:
            self.menu_ui.render(self.screen)
        elif self.state == GameState.LEVEL_SELECT:
            self.level_select_ui.render(self.screen)
        elif self.state == GameState.SETTINGS:
            self.settings_ui.render(self.screen)
        elif self.state == GameState.ACHIEVEMENTS:
            self.achievements_ui.render(self.screen)
        elif self.state == GameState.TUTORIAL and self.tutorial_system:
            # 教程使用独立的背景，不渲染游戏
            self.tutorial_system.render(self.screen)
        elif self.state == GameState.PLAYING:
            self._render_game()
            self.game_ui.render(self.screen)
            self.interactive_tutorial.render(self.screen)
        elif self.state == GameState.PAUSED:
            self._render_game()
            self.game_ui.render(self.screen)
            self.pause_ui.render(self.screen)
        elif self.state == GameState.VICTORY:
            self._render_game()
            self.game_ui.render(self.screen)
            self.victory_ui.render(self.screen)
        elif self.state == GameState.GAME_OVER:
            self._render_game()
            self.game_ui.render(self.screen)
            self.game_over_ui.render(self.screen)
        
        # 更新显示
        pygame.display.flip()
    
    def _render_game(self) -> None:
        """渲染游戏画面"""
        if not self.current_game:
            return
        
        colors = TILE_COLORS_DARK if self.data_manager.get_setting('dark_theme') else TILE_COLORS
        
        # 绘制网格背景
        grid_bg_color = Colors.GRID_BG_DARK if self.data_manager.get_setting('dark_theme') else Colors.GRID_BG
        grid_rect = pygame.Rect(
            GRID_OFFSET_X - CELL_PADDING,
            GRID_OFFSET_Y - CELL_PADDING,
            GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING,
            GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING
        )
        pygame.draw.rect(self.screen, grid_bg_color, grid_rect, border_radius=10)
        
        # 获取当前网格
        grid = self.current_game.get_grid()
        
        # 绘制空单元格和所有方块
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * (CELL_SIZE + CELL_PADDING)
                y = GRID_OFFSET_Y + row * (CELL_SIZE + CELL_PADDING)
                
                value = grid[row][col]
                
                if value == -1:  # 障碍物
                    pygame.draw.rect(self.screen, (80, 80, 80), 
                                   (x, y, CELL_SIZE, CELL_SIZE), border_radius=8)
                    # 绘制X标记
                    pygame.draw.line(self.screen, (150, 150, 150), 
                                   (x + 20, y + 20), (x + CELL_SIZE - 20, y + CELL_SIZE - 20), 4)
                    pygame.draw.line(self.screen, (150, 150, 150), 
                                   (x + CELL_SIZE - 20, y + 20), (x + 20, y + CELL_SIZE - 20), 4)
                else:
                    color = colors.get(value, colors.get(0))
                    pygame.draw.rect(self.screen, color, 
                                   (x, y, CELL_SIZE, CELL_SIZE), border_radius=8)
                    
                    if value > 0:
                        text_color = TEXT_COLORS.get(value, (255, 255, 255))
                        font_size = 'large' if value < 100 else 'medium' if value < 1000 else 'normal'
                        text = self.fonts[font_size].render(str(value), True, text_color)
                        text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                        self.screen.blit(text, text_rect)
        
        # 渲染粒子效果
        self.animation_manager.render_particles(self.screen)
    
    def run(self) -> None:
        """主循环"""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """清理资源"""
        # 保存数据
        self.data_manager.save_all()
        
        # 停止动画系统
        self.animation_manager.stop()
        
        # 清理音频
        self.audio_manager.cleanup()
        
        # 退出Pygame
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    game = MainGame()
    game.run()


if __name__ == "__main__":
    main()
