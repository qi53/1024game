"""
1024 Game - Pygame Version - Tutorial System
教程系统，帮助新玩家学习游戏规则
"""

import pygame
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum, auto

from config import SCREEN_WIDTH, SCREEN_HEIGHT, Colors, FONT_SIZES
from ui_components import UIComponent, Button, Label, Panel, UIManager, Theme


class TutorialStepType(Enum):
    """教程步骤类型"""
    TEXT = auto()           # 纯文字说明
    DEMONSTRATION = auto()  # 演示
    INTERACTIVE = auto()    # 交互练习
    HIGHLIGHT = auto()      # 高亮区域


@dataclass
class TutorialStep:
    """教程步骤"""
    title: str
    content: str
    step_type: TutorialStepType
    highlight_rect: Optional[pygame.Rect] = None
    expected_input: Optional[str] = None
    demonstration_grid: Optional[List[List[int]]] = None


class TutorialSystem:
    """教程系统"""
    
    def __init__(self, on_complete: Optional[Callable] = None):
        self.on_complete = on_complete
        self.current_step = 0
        self.completed = False
        self.ui = UIManager()
        self.theme = Theme()
        
        # 教程步骤
        self.steps: List[TutorialStep] = self._create_steps()
        
        # 创建UI
        self._create_ui()
        
        # 演示用的游戏状态
        self.demo_grid: List[List[int]] = [[0] * 4 for _ in range(4)]
        self.demo_animating = False
    
    def _create_steps(self) -> List[TutorialStep]:
        """创建教程步骤"""
        return [
            TutorialStep(
                title="Welcome to 1024!",
                content="""Welcome to 1024 - a number sliding puzzle game!

Your goal is to combine numbered tiles to reach the target value.

Let's learn the basics step by step.""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="The Game Board",
                content="""The game is played on a 4x4 grid.

Tiles with numbers appear on the board.
You can see an example on the right.""",
                step_type=TutorialStepType.DEMONSTRATION,
                demonstration_grid=[
                    [2, 0, 0, 4],
                    [0, 2, 0, 0],
                    [0, 0, 2, 0],
                    [0, 0, 0, 2]
                ]
            ),
            TutorialStep(
                title="How to Move",
                content="""Use arrow keys or WASD to move all tiles:

- UP (W) - Move tiles up
- DOWN (S) - Move tiles down
- LEFT (A) - Move tiles left
- RIGHT (D) - Move tiles right

All tiles slide as far as possible in the chosen direction.""",
                step_type=TutorialStepType.INTERACTIVE,
                expected_input="any"
            ),
            TutorialStep(
                title="Combining Tiles",
                content="""When two tiles with the same number touch,
they merge into one!

For example:
  2 + 2 = 4
  4 + 4 = 8

Try it yourself! Press any arrow key to move.""",
                step_type=TutorialStepType.DEMONSTRATION,
                demonstration_grid=[
                    [2, 2, 0, 0],
                    [4, 0, 4, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]
                ]
            ),
            TutorialStep(
                title="Scoring",
                content="""Every time you merge tiles, you earn points!

The score equals the value of the new tile created.

Example:
  Merging two 8 tiles gives you 16 and 16 points!""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="New Tiles",
                content="""After each move, a new tile (2 or 4) randomly
appears in an empty spot.

This makes the game progressively more challenging!""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="Goal of the Game",
                content="""Your goal is to create a tile with the target value!

Level 1-5: Target is 512 or 1024
Level 6-10: Target is 2048
Level 11-15: Target is 4096
Level 16-20: Target is 8192

Higher levels have time limits and obstacles!""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="Game Over",
                content="""The game ends when:

1. You reach the target (VICTORY!)
2. The board is full and no moves are possible
3. Time runs out (on timed levels)

Plan your moves carefully!""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="Special Features",
                content="""Here are some helpful features:

UNDO (Ctrl+Z) - Undo your last move
PAUSE (P) - Pause the game
Particles - Watch cool effects when merging!
3D Audio - Sound comes from where the action is!""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="Tips for Success",
                content="""Pro tips:

1. Keep your highest tile in a corner
2. Build chains of decreasing values
3. Don't rush - think ahead!
4. Use undo wisely
5. Practice makes perfect!""",
                step_type=TutorialStepType.TEXT
            ),
            TutorialStep(
                title="Ready to Play!",
                content="""You've learned the basics!

Now it's time to put your skills to the test.

Good luck and have fun playing 1024!""",
                step_type=TutorialStepType.TEXT
            )
        ]
    
    def _create_ui(self) -> None:
        """创建UI组件"""
        # 背景面板
        panel = Panel(100, 80, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 160,
                     border_radius=15, border_width=2)
        self.ui.add_component(panel)
        
        # 标题 - 居中顶部
        self.title_label = Label(SCREEN_WIDTH // 2, 110, "", 'large', center=True)
        self.ui.add_component(self.title_label)
        
        # 内容区域 - 使用多行标签
        self.content_labels: List[Label] = []
        for i in range(10):  # 最多10行
            label = Label(SCREEN_WIDTH // 2, 160 + i * 30, "", 'small', center=True)
            self.content_labels.append(label)
            self.ui.add_component(label)
        
        # 步骤指示器
        self.step_label = Label(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180, "", 'small', center=True)
        self.ui.add_component(self.step_label)
        
        # 上一步按钮
        self.prev_button = Button(300, SCREEN_HEIGHT - 140, 120, 40,
                                 "Previous", 'normal', self._prev_step)
        self.ui.add_component(self.prev_button)
        
        # 下一步按钮
        self.next_button = Button(SCREEN_WIDTH - 420, SCREEN_HEIGHT - 140, 120, 40,
                                 "Next", 'normal', self._next_step)
        self.ui.add_component(self.next_button)
        
        # 跳过按钮
        skip_button = Button(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT - 140, 80, 40,
                            "Skip", 'normal', self._skip_tutorial)
        self.ui.add_component(skip_button)
        
        # 更新显示
        self._update_display()
    
    def _update_display(self) -> None:
        """更新显示内容"""
        if not self.steps:
            return
        
        step = self.steps[self.current_step]
        
        # 更新标题
        self.title_label.set_text(step.title)
        
        # 更新内容 - 分割成多行
        content_lines = self._split_content(step.content)
        for i, label in enumerate(self.content_labels):
            if i < len(content_lines):
                label.set_text(content_lines[i])
                label.visible = True
            else:
                label.set_text("")
                label.visible = False
        
        # 更新步骤指示器
        self.step_label.set_text(f"Step {self.current_step + 1} of {len(self.steps)}")
        
        # 更新按钮状态
        self.prev_button.enabled = self.current_step > 0
        
        if self.current_step >= len(self.steps) - 1:
            self.next_button.text = "Finish"
        else:
            self.next_button.text = "Next"
        
        # 更新演示网格
        if step.demonstration_grid:
            self.demo_grid = [row[:] for row in step.demonstration_grid]
        else:
            self.demo_grid = [[0] * 4 for _ in range(4)]
    
    def _split_content(self, content: str) -> List[str]:
        """将内容分割成适合显示的行"""
        lines = []
        max_chars = 50  # 每行最大字符数
        
        for paragraph in content.split('\n'):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 如果段落较短，直接添加
            if len(paragraph) <= max_chars:
                lines.append(paragraph)
            else:
                # 长段落需要分割
                words = paragraph.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_chars:
                        if current_line:
                            current_line += " " + word
                        else:
                            current_line = word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
        
        return lines
    
    def _next_step(self) -> None:
        """下一步"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._update_display()
        else:
            self._complete_tutorial()
    
    def _prev_step(self) -> None:
        """上一步"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_display()
    
    def _skip_tutorial(self) -> None:
        """跳过教程"""
        self._complete_tutorial()
    
    def _complete_tutorial(self) -> None:
        """完成教程"""
        self.completed = True
        if self.on_complete:
            self.on_complete()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if self.completed:
            return False
        
        # 处理UI事件
        if self.ui.handle_event(event):
            return True
        
        # 处理键盘导航
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                self._next_step()
                return True
            elif event.key == pygame.K_LEFT:
                self._prev_step()
                return True
            elif event.key == pygame.K_ESCAPE:
                self._skip_tutorial()
                return True
        
        return False
    
    def update(self, dt: float) -> None:
        """更新教程"""
        self.ui.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染教程"""
        if self.completed:
            return
        
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # 渲染UI
        self.ui.render(screen)
        
        # 渲染演示网格
        step = self.steps[self.current_step]
        if step.step_type == TutorialStepType.DEMONSTRATION or \
           (step.step_type == TutorialStepType.INTERACTIVE and step.demonstration_grid):
            self._render_demo_grid(screen)
    
    def _render_demo_grid(self, screen: pygame.Surface) -> None:
        """渲染演示网格 - 使用小尺寸示例在右下角显示"""
        from config import TILE_COLORS, TEXT_COLORS
        
        # 使用更小的尺寸显示示例
        demo_cell_size = 40
        demo_padding = 5
        grid_x = SCREEN_WIDTH - 250
        grid_y = 450
        grid_size = 4
        
        # 绘制网格背景
        bg_rect = pygame.Rect(
            grid_x - demo_padding,
            grid_y - demo_padding,
            grid_size * (demo_cell_size + demo_padding) + demo_padding,
            grid_size * (demo_cell_size + demo_padding) + demo_padding
        )
        pygame.draw.rect(screen, Colors.GRID_BG, bg_rect, border_radius=6)
        
        # 绘制单元格
        font = pygame.font.SysFont("arial", 16)
        
        for row in range(grid_size):
            for col in range(grid_size):
                x = grid_x + col * (demo_cell_size + demo_padding)
                y = grid_y + row * (demo_cell_size + demo_padding)
                
                value = self.demo_grid[row][col]
                color = TILE_COLORS.get(value, TILE_COLORS[0])
                
                cell_rect = pygame.Rect(x, y, demo_cell_size, demo_cell_size)
                pygame.draw.rect(screen, color, cell_rect, border_radius=4)
                
                if value > 0:
                    text_color = TEXT_COLORS.get(value, (255, 255, 255))
                    text = font.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=cell_rect.center)
                    screen.blit(text, text_rect)
    
    def is_active(self) -> bool:
        """检查教程是否正在进行"""
        return not self.completed
    
    def reset(self) -> None:
        """重置教程"""
        self.current_step = 0
        self.completed = False
        self._update_display()


class InteractiveTutorial:
    """交互式教程，在游戏中实时指导"""
    
    def __init__(self):
        self.active = False
        self.current_tip = ""
        self.tip_timer = 0
        self.tip_duration = 5000  # 5秒
        
        # 提示列表
        self.tips = [
            "Try to keep your highest tile in a corner",
            "Build chains: 64 → 32 → 16 → 8",
            "Don't let small tiles get trapped",
            "Use undo (Ctrl+Z) if you make a mistake",
            "Plan ahead before making moves",
            "Merge from the edges toward the center",
        ]
        self.current_tip_index = 0
    
    def start(self) -> None:
        """开始显示提示"""
        self.active = True
        self.current_tip_index = 0
        self._show_next_tip()
    
    def stop(self) -> None:
        """停止显示提示"""
        self.active = False
        self.current_tip = ""
    
    def _show_next_tip(self) -> None:
        """显示下一个提示"""
        if self.current_tip_index < len(self.tips):
            self.current_tip = self.tips[self.current_tip_index]
            self.tip_timer = self.tip_duration
            self.current_tip_index += 1
    
    def update(self, dt: float) -> None:
        """更新提示"""
        if not self.active:
            return
        
        self.tip_timer -= dt
        
        if self.tip_timer <= 0:
            if self.current_tip_index < len(self.tips):
                self._show_next_tip()
            else:
                # 循环显示
                self.current_tip_index = 0
                self._show_next_tip()
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染提示"""
        if not self.active or not self.current_tip:
            return
        
        # 计算透明度
        alpha = 255
        if self.tip_timer < 500:  # 最后0.5秒淡出
            alpha = int(255 * (self.tip_timer / 500))
        
        # 创建提示表面
        font = pygame.font.SysFont("arial", 24)
        text = font.render(self.current_tip, True, Colors.GOLD)
        
        # 背景
        padding = 15
        bg_width = text.get_width() + padding * 2
        bg_height = text.get_height() + padding * 2
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        
        bg_color = (0, 0, 0, min(200, alpha))
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect(), border_radius=10)
        
        # 文字
        text_surface = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
        text_surface.blit(text, (0, 0))
        text_surface.set_alpha(alpha)
        bg_surface.blit(text_surface, (padding, padding))
        
        # 位置：屏幕底部中央
        x = (SCREEN_WIDTH - bg_width) // 2
        y = SCREEN_HEIGHT - 150
        
        screen.blit(bg_surface, (x, y))
    
    def show_tip(self, tip: str, duration: float = 3000) -> None:
        """显示特定提示"""
        self.current_tip = tip
        self.tip_timer = duration


def show_tutorial_dialog(screen: pygame.Surface, on_complete: Optional[Callable] = None) -> TutorialSystem:
    """显示教程对话框"""
    tutorial = TutorialSystem(on_complete)
    return tutorial
