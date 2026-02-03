"""
1024 Game - Pygame Version - Game Engine
核心游戏引擎，支持关卡系统和60帧流畅运行
"""

import pygame
import random
import copy
import time
from typing import List, Tuple, Optional, Dict
from enum import Enum, auto
from dataclasses import dataclass, field

from config import (
    GRID_SIZE, LEVEL_CONFIGS, LevelConfig, 
    Direction, GameState, ACHIEVEMENTS, Achievement
)


@dataclass
class GameStats:
    """游戏统计"""
    total_score: int = 0
    total_moves: int = 0
    total_merges: int = 0
    max_tile_achieved: int = 0
    start_time: float = field(default_factory=time.time)
    elapsed_time: float = 0
    combo_count: int = 0
    max_combo: int = 0
    undo_count: int = 0
    
    def update_time(self) -> None:
        """更新经过时间"""
        self.elapsed_time = time.time() - self.start_time


class LevelGame:
    """关卡游戏类 - 扩展原有Game类支持关卡系统"""
    
    def __init__(self, level: int = 1):
        self.level = level
        self.config = LEVEL_CONFIGS[level - 1] if 1 <= level <= 20 else LEVEL_CONFIGS[0]
        
        # 游戏网格
        self.grid: List[List[int]] = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.obstacles: List[Tuple[int, int]] = []  # 障碍物位置
        
        # 分数
        self.score = 0
        self.target_score = self.config.target_score
        
        # 游戏状态
        self.is_won = False
        self.is_over = False
        self.is_paused = False
        
        # 时间限制
        self.time_limit = self.config.time_limit
        self.start_time = time.time()
        
        # 统计
        self.stats = GameStats()
        
        # 历史记录（用于撤销）
        self.history: List[Tuple[List[List[int]], int]] = []
        self.max_history = 10
        
        # 初始化
        self._init_obstacles()
        self._add_initial_tiles()
    
    def _init_obstacles(self) -> None:
        """初始化障碍物"""
        if self.config.obstacle_count > 0:
            positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
            self.obstacles = random.sample(positions, min(self.config.obstacle_count, len(positions)))
            for r, c in self.obstacles:
                self.grid[r][c] = -1  # -1表示障碍物
    
    def _add_initial_tiles(self) -> None:
        """添加初始方块"""
        self._spawn_tile()
        self._spawn_tile()
    
    def _get_empty_cells(self) -> List[Tuple[int, int]]:
        """获取空单元格"""
        empty = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == 0:
                    empty.append((i, j))
        return empty
    
    def _spawn_tile(self) -> bool:
        """生成新方块"""
        empty_cells = self._get_empty_cells()
        if not empty_cells:
            return False
        
        row, col = random.choice(empty_cells)
        
        # 根据关卡配置选择数值
        values = self.config.spawn_values
        weights = self.config.spawn_weights
        
        # 特殊方块概率
        if random.random() < self.config.special_tile_chance:
            # 生成双倍数值
            value = random.choices(values, weights=weights)[0] * 2
        else:
            value = random.choices(values, weights=weights)[0]
        
        self.grid[row][col] = value
        return True
    
    def _save_state(self) -> None:
        """保存当前状态"""
        self.history.append((copy.deepcopy(self.grid), self.score))
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def undo(self) -> bool:
        """撤销上一步"""
        if not self.history or self.is_won or self.is_over:
            return False
        
        self.grid, self.score = self.history.pop()
        self.stats.undo_count += 1
        return True
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return len(self.history) > 0 and not self.is_won and not self.is_over
    
    def move(self, direction: Direction) -> bool:
        """移动方块"""
        if self.is_won or self.is_over or self.is_paused:
            return False
        
        # 保存状态
        self._save_state()
        
        original_grid = copy.deepcopy(self.grid)
        moved = False
        merge_count = 0
        
        if direction == Direction.LEFT:
            moved, merge_count = self._move_left()
        elif direction == Direction.RIGHT:
            moved, merge_count = self._move_right()
        elif direction == Direction.UP:
            moved, merge_count = self._move_up()
        elif direction == Direction.DOWN:
            moved, merge_count = self._move_down()
        
        if moved:
            self._spawn_tile()
            self.stats.total_moves += 1
            self.stats.total_merges += merge_count
            
            # 更新连击
            if merge_count > 0:
                self.stats.combo_count += 1
                self.stats.max_combo = max(self.stats.max_combo, self.stats.combo_count)
            else:
                self.stats.combo_count = 0
            
            # 检查胜利条件
            self._check_win_condition()
            
            # 检查失败条件
            if not self.is_won:
                self._check_game_over()
        else:
            # 没有移动，恢复状态
            if self.history:
                self.history.pop()
        
        return moved
    
    def _move_left(self) -> Tuple[bool, int]:
        """向左移动"""
        moved = False
        merge_count = 0
        
        for i in range(GRID_SIZE):
            row = self.grid[i][:]
            new_row, row_moved, row_merges = self._process_line(row)
            if row_moved:
                moved = True
                merge_count += row_merges
                self.grid[i] = new_row
        
        return moved, merge_count
    
    def _move_right(self) -> Tuple[bool, int]:
        """向右移动"""
        moved = False
        merge_count = 0
        
        for i in range(GRID_SIZE):
            row = self.grid[i][::-1]
            new_row, row_moved, row_merges = self._process_line(row)
            if row_moved:
                moved = True
                merge_count += row_merges
                self.grid[i] = new_row[::-1]
        
        return moved, merge_count
    
    def _move_up(self) -> Tuple[bool, int]:
        """向上移动"""
        moved = False
        merge_count = 0
        
        for j in range(GRID_SIZE):
            col = [self.grid[i][j] for i in range(GRID_SIZE)]
            new_col, col_moved, col_merges = self._process_line(col)
            if col_moved:
                moved = True
                merge_count += col_merges
                for i in range(GRID_SIZE):
                    self.grid[i][j] = new_col[i]
        
        return moved, merge_count
    
    def _move_down(self) -> Tuple[bool, int]:
        """向下移动"""
        moved = False
        merge_count = 0
        
        for j in range(GRID_SIZE):
            col = [self.grid[i][j] for i in range(GRID_SIZE)][::-1]
            new_col, col_moved, col_merges = self._process_line(col)
            if col_moved:
                moved = True
                merge_count += col_merges
                for i in range(GRID_SIZE):
                    self.grid[GRID_SIZE - 1 - i][j] = new_col[i]
        
        return moved, merge_count
    
    def _process_line(self, line: List[int]) -> Tuple[List[int], bool, int]:
        """处理一行/列的移动和合并"""
        # 过滤掉0和障碍物
        non_zero = [x for x in line if x > 0]
        
        new_line = [0] * GRID_SIZE
        score_gained = 0
        merge_count = 0
        
        if not non_zero:
            return new_line, False, 0
        
        # 合并相同的数字
        i = 0
        pos = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                # 合并
                merged_value = non_zero[i] * 2
                new_line[pos] = merged_value
                score_gained += merged_value
                merge_count += 1
                i += 2
            else:
                new_line[pos] = non_zero[i]
                i += 1
            pos += 1
        
        # 恢复障碍物
        for idx, val in enumerate(line):
            if val == -1:
                new_line[idx] = -1
        
        moved = new_line != line
        self.score += score_gained
        self.stats.total_score += score_gained
        
        # 更新最大方块
        max_in_line = max(new_line) if new_line else 0
        self.stats.max_tile_achieved = max(self.stats.max_tile_achieved, max_in_line)
        
        return new_line, moved, merge_count
    
    def _check_win_condition(self) -> None:
        """检查是否达成胜利条件"""
        # 达到目标分数
        if self.score >= self.target_score:
            self.is_won = True
            return
        
        # 或者合成目标数值
        target_tile = self.config.target_score
        for row in self.grid:
            if target_tile in row:
                self.is_won = True
                return
    
    def _check_game_over(self) -> None:
        """检查游戏是否结束"""
        # 检查是否有空格
        if self._get_empty_cells():
            return
        
        # 检查是否可以合并
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE - 1):
                # 水平检查
                if self.grid[i][j] > 0 and self.grid[i][j] == self.grid[i][j + 1]:
                    return
                # 垂直检查
                if self.grid[j][i] > 0 and self.grid[j][i] == self.grid[j + 1][i]:
                    return
        
        self.is_over = True
    
    def check_time_limit(self) -> bool:
        """检查是否超时"""
        if self.time_limit <= 0:
            return False
        
        elapsed = time.time() - self.start_time
        return elapsed > self.time_limit
    
    def get_remaining_time(self) -> int:
        """获取剩余时间"""
        if self.time_limit <= 0:
            return -1
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        return int(remaining)
    
    def pause(self) -> None:
        """暂停游戏"""
        self.is_paused = True
        self.stats.update_time()
    
    def resume(self) -> None:
        """恢复游戏"""
        if self.is_paused:
            self.is_paused = False
            # 调整开始时间以补偿暂停
            self.start_time = time.time() - self.stats.elapsed_time
    
    def restart(self) -> None:
        """重新开始当前关卡"""
        self.__init__(self.level)
    
    def get_grid(self) -> List[List[int]]:
        """获取当前网格"""
        return copy.deepcopy(self.grid)
    
    def get_score(self) -> int:
        """获取当前分数"""
        return self.score
    
    def get_max_tile(self) -> int:
        """获取当前最大方块"""
        max_tile = 0
        for row in self.grid:
            for val in row:
                if val > max_tile:
                    max_tile = val
        return max_tile


class GameEngine:
    """游戏引擎主类"""
    
    def __init__(self):
        pygame.init()
        
        # 屏幕设置
        from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1024 Game - Pygame Edition")
        
        # 时钟
        self.clock = pygame.time.Clock()
        self.fps = FPS
        
        # 游戏状态
        self.state = GameState.MENU
        self.running = True
        
        # 当前游戏
        self.current_game: Optional[LevelGame] = None
        self.current_level = 1
        self.unlocked_levels = 1
        
        # 主题
        self.dark_theme = False
        
        # 字体
        self._init_fonts()
        
        # 动画和音效管理器（稍后初始化）
        self.animation_manager = None
        self.audio_manager = None
        
        # 统计数据
        self.total_play_time = 0
        self.total_games_played = 0
        self.achievements: Dict[str, Achievement] = {}
        self._init_achievements()
    
    def _init_fonts(self) -> None:
        """初始化字体"""
        from config import FONT_SIZES
        self.fonts = {}
        for name, size in FONT_SIZES.items():
            try:
                self.fonts[name] = pygame.font.Font(None, size)
            except:
                self.fonts[name] = pygame.font.SysFont("arial", size)
    
    def _init_achievements(self) -> None:
        """初始化成就"""
        for ach in ACHIEVEMENTS:
            self.achievements[ach.id] = Achievement(
                ach.id, ach.name, ach.description, ach.icon,
                ach.condition_type, ach.condition_value
            )
    
    def start_game(self, level: int) -> None:
        """开始游戏"""
        self.current_level = level
        self.current_game = LevelGame(level)
        self.state = GameState.PLAYING
        self.total_games_played += 1
        
        # 播放开始音效
        if self.audio_manager:
            self.audio_manager.play_spawn()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.QUIT:
            self.running = False
            return True
        
        if self.state == GameState.PLAYING and self.current_game:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self._make_move(Direction.UP)
                    return True
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self._make_move(Direction.DOWN)
                    return True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self._make_move(Direction.LEFT)
                    return True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self._make_move(Direction.RIGHT)
                    return True
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self._undo()
                    return True
                elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self._pause_game()
                    return True
        
        return False
    
    def _make_move(self, direction: Direction) -> None:
        """执行移动"""
        if not self.current_game:
            return
        
        old_grid = self.current_game.get_grid()
        moved = self.current_game.move(direction)
        
        if moved:
            # 播放移动音效
            if self.audio_manager:
                self.audio_manager.play_move()
            
            # 检查合并并播放音效
            new_grid = self.current_game.get_grid()
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if new_grid[i][j] > old_grid[i][j] and old_grid[i][j] > 0:
                        # 计算声源位置
                        x = 0.3 + (j / GRID_SIZE) * 0.4
                        y = 0.2 + (i / GRID_SIZE) * 0.4
                        if self.audio_manager:
                            self.audio_manager.play_merge(new_grid[i][j], x, y)
            
            # 检查游戏结束
            if self.current_game.is_won:
                self._on_victory()
            elif self.current_game.is_over:
                self._on_game_over()
    
    def _undo(self) -> None:
        """撤销"""
        if self.current_game and self.current_game.undo():
            if self.audio_manager:
                self.audio_manager.play_button()
    
    def _pause_game(self) -> None:
        """暂停游戏"""
        if self.current_game:
            self.current_game.pause()
            self.state = GameState.PAUSED
    
    def _on_victory(self) -> None:
        """胜利处理"""
        if self.audio_manager:
            self.audio_manager.play_win()
        
        # 解锁下一关
        if self.current_level >= self.unlocked_levels and self.current_level < 20:
            self.unlocked_levels = self.current_level + 1
        
        # 检查成就
        self._check_achievements()
        
        self.state = GameState.VICTORY
    
    def _on_game_over(self) -> None:
        """失败处理"""
        if self.audio_manager:
            self.audio_manager.play_lose()
        
        self.state = GameState.GAME_OVER
    
    def _check_achievements(self) -> None:
        """检查成就"""
        if not self.current_game:
            return
        
        stats = self.current_game.stats
        
        for ach in self.achievements.values():
            if ach.unlocked:
                continue
            
            unlocked = False
            
            if ach.condition_type == "level_complete":
                if self.current_level >= ach.condition_value and self.current_game.is_won:
                    unlocked = True
            elif ach.condition_type == "score":
                if stats.total_score >= ach.condition_value:
                    unlocked = True
            elif ach.condition_type == "time":
                if stats.elapsed_time <= ach.condition_value and self.current_game.is_won:
                    unlocked = True
            elif ach.condition_type == "combo":
                if stats.max_combo >= ach.condition_value:
                    unlocked = True
            elif ach.condition_type == "max_tile":
                if stats.max_tile_achieved >= ach.condition_value:
                    unlocked = True
            elif ach.condition_type == "no_undo":
                if stats.undo_count == 0 and self.current_game.is_won:
                    unlocked = True
            
            if unlocked:
                ach.unlocked = True
                ach.unlocked_at = time.time()
                if self.audio_manager:
                    self.audio_manager.play_achievement()
    
    def update(self, dt: float) -> None:
        """更新游戏状态"""
        if self.state == GameState.PLAYING and self.current_game:
            # 更新时间
            self.current_game.stats.update_time()
            
            # 检查时间限制
            if self.current_game.check_time_limit():
                self.current_game.is_over = True
                self._on_game_over()
            
            # 更新动画
            if self.animation_manager:
                self.animation_manager.update(dt)
    
    def render(self) -> None:
        """渲染游戏画面"""
        from config import Colors
        
        # 清屏
        bg_color = Colors.BACKGROUND_DARK if self.dark_theme else Colors.BACKGROUND
        self.screen.fill(bg_color)
        
        # 根据状态渲染不同内容
        if self.state == GameState.MENU:
            self._render_menu()
        elif self.state == GameState.PLAYING:
            self._render_game()
        elif self.state == GameState.PAUSED:
            self._render_game()
            self._render_pause_overlay()
        elif self.state == GameState.VICTORY:
            self._render_game()
            self._render_victory_overlay()
        elif self.state == GameState.GAME_OVER:
            self._render_game()
            self._render_game_over_overlay()
        
        # 更新显示
        pygame.display.flip()
    
    def _render_menu(self) -> None:
        """渲染主菜单"""
        from config import Colors
        
        # 标题
        title = self.fonts['title'].render("1024", True, Colors.TEXT_DARK)
        title_rect = title.get_rect(center=(640, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.fonts['normal'].render("Pygame Edition", True, Colors.TEXT_DARK)
        subtitle_rect = subtitle.get_rect(center=(640, 220))
        self.screen.blit(subtitle, subtitle_rect)
    
    def _render_game(self) -> None:
        """渲染游戏画面"""
        if not self.current_game:
            return
        
        from config import (
            GRID_OFFSET_X, GRID_OFFSET_Y, CELL_SIZE, CELL_PADDING,
            TILE_COLORS, TILE_COLORS_DARK, TEXT_COLORS, Colors
        )
        
        colors = TILE_COLORS_DARK if self.dark_theme else TILE_COLORS
        
        # 绘制网格背景
        grid_bg_color = Colors.GRID_BG_DARK if self.dark_theme else Colors.GRID_BG
        grid_rect = pygame.Rect(
            GRID_OFFSET_X - CELL_PADDING,
            GRID_OFFSET_Y - CELL_PADDING,
            GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING,
            GRID_SIZE * (CELL_SIZE + CELL_PADDING) + CELL_PADDING
        )
        pygame.draw.rect(self.screen, grid_bg_color, grid_rect, border_radius=10)
        
        # 绘制方块
        grid = self.current_game.get_grid()
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = GRID_OFFSET_X + j * (CELL_SIZE + CELL_PADDING)
                y = GRID_OFFSET_Y + i * (CELL_SIZE + CELL_PADDING)
                
                value = grid[i][j]
                
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
        
        # 绘制UI信息
        self._render_game_ui()
    
    def _render_game_ui(self) -> None:
        """渲染游戏UI"""
        from config import Colors
        
        if not self.current_game:
            return
        
        # 分数
        score_text = self.fonts['medium'].render(f"Score: {self.current_game.score}", 
                                                True, Colors.TEXT_DARK)
        self.screen.blit(score_text, (50, 50))
        
        # 目标
        target_text = self.fonts['normal'].render(f"Target: {self.current_game.target_score}", 
                                                 True, Colors.TEXT_DARK)
        self.screen.blit(target_text, (50, 100))
        
        # 关卡
        level_text = self.fonts['normal'].render(f"Level: {self.current_level}", 
                                                True, Colors.TEXT_DARK)
        self.screen.blit(level_text, (50, 150))
        
        # 时间
        if self.current_game.time_limit > 0:
            remaining = self.current_game.get_remaining_time()
            time_color = Colors.TEXT_DARK if remaining > 30 else (255, 100, 100)
            time_text = self.fonts['normal'].render(f"Time: {remaining}s", 
                                                   True, time_color)
            self.screen.blit(time_text, (50, 200))
        
        # 操作提示
        hint_text = self.fonts['small'].render("WASD/Arrows: Move | Z: Undo | P: Pause", 
                                              True, Colors.TEXT_DARK)
        self.screen.blit(hint_text, (50, 650))
    
    def _render_pause_overlay(self) -> None:
        """渲染暂停覆盖层"""
        from config import Colors
        
        # 半透明背景
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文字
        text = self.fonts['xlarge'].render("PAUSED", True, Colors.TEXT_LIGHT)
        text_rect = text.get_rect(center=(640, 360))
        self.screen.blit(text, text_rect)
        
        hint = self.fonts['normal'].render("Press P to resume", True, Colors.TEXT_LIGHT)
        hint_rect = hint.get_rect(center=(640, 420))
        self.screen.blit(hint, hint_rect)
    
    def _render_victory_overlay(self) -> None:
        """渲染胜利覆盖层"""
        from config import Colors
        
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.fonts['xlarge'].render("VICTORY!", True, Colors.GOLD)
        text_rect = text.get_rect(center=(640, 300))
        self.screen.blit(text, text_rect)
        
        if self.current_game:
            score_text = self.fonts['normal'].render(f"Final Score: {self.current_game.score}", 
                                                    True, Colors.TEXT_LIGHT)
            score_rect = score_text.get_rect(center=(640, 380))
            self.screen.blit(score_text, score_rect)
    
    def _render_game_over_overlay(self) -> None:
        """渲染失败覆盖层"""
        from config import Colors
        
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.fonts['xlarge'].render("GAME OVER", True, (255, 100, 100))
        text_rect = text.get_rect(center=(640, 360))
        self.screen.blit(text, text_rect)
        
        if self.current_game:
            score_text = self.fonts['normal'].render(f"Final Score: {self.current_game.score}", 
                                                    True, Colors.TEXT_LIGHT)
            score_rect = score_text.get_rect(center=(640, 420))
            self.screen.blit(score_text, score_rect)
    
    def run(self) -> None:
        """主循环"""
        while self.running:
            dt = self.clock.tick(self.fps)
            
            # 处理事件
            for event in pygame.event.get():
                self.handle_event(event)
            
            # 更新
            self.update(dt)
            
            # 渲染
            self.render()
        
        pygame.quit()


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
