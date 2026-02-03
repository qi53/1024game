"""
1024 Game - Pygame Version - UI Components
UI组件系统，包含按钮、面板、菜单等
"""

import pygame
import math
from typing import Callable, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum, auto

from config import Colors, FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT


class UIState(Enum):
    """UI状态"""
    NORMAL = auto()
    HOVER = auto()
    PRESSED = auto()
    DISABLED = auto()


@dataclass
class Theme:
    """主题配置"""
    # 颜色
    background: Tuple[int, int, int] = Colors.BACKGROUND
    primary: Tuple[int, int, int] = Colors.BUTTON_BG
    secondary: Tuple[int, int, int] = (150, 140, 130)
    accent: Tuple[int, int, int] = Colors.GOLD
    text: Tuple[int, int, int] = Colors.TEXT_DARK
    text_light: Tuple[int, int, int] = Colors.TEXT_LIGHT
    disabled: Tuple[int, int, int] = (200, 200, 200)
    
    # 网格颜色
    grid_bg: Tuple[int, int, int] = Colors.GRID_BG
    empty_cell: Tuple[int, int, int] = Colors.EMPTY_CELL
    
    # 字体
    font_name: str = "arial"


class DarkTheme(Theme):
    """深色主题"""
    def __init__(self):
        super().__init__(
            background=Colors.BACKGROUND_DARK,
            primary=(100, 90, 80),
            secondary=(80, 70, 60),
            accent=Colors.GOLD,
            text=Colors.TEXT_DARK_THEME,
            text_light=Colors.TEXT_LIGHT,
            disabled=(80, 80, 80),
            grid_bg=Colors.GRID_BG_DARK,
            empty_cell=Colors.EMPTY_CELL_DARK
        )


class UIComponent:
    """UI组件基类"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.parent: Optional['UIComponent'] = None
        self.children: List['UIComponent'] = []
        self.theme = Theme()
    
    def set_theme(self, theme: Theme) -> None:
        """设置主题"""
        self.theme = theme
        for child in self.children:
            child.set_theme(theme)
    
    def add_child(self, child: 'UIComponent') -> None:
        """添加子组件"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'UIComponent') -> None:
        """移除子组件"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回是否已处理"""
        if not self.visible or not self.enabled:
            return False
        
        for child in self.children:
            if child.handle_event(event):
                return True
        
        return False
    
    def update(self, dt: float) -> None:
        """更新组件"""
        if not self.visible:
            return
        
        for child in self.children:
            child.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染组件"""
        if not self.visible:
            return
        
        self._render_self(screen)
        
        for child in self.children:
            child.render(screen)
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染自身（子类实现）"""
        pass
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """检查点是否在组件内"""
        return self.rect.collidepoint(point)


class Button(UIComponent):
    """按钮组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str = "", font_size: str = 'normal',
                 on_click: Optional[Callable] = None,
                 icon: Optional[pygame.Surface] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.on_click = on_click
        self.icon = icon
        self.state = UIState.NORMAL
        self.border_radius = 8
        self.text_color = self.theme.text_light
        self._cached_font: Optional[pygame.font.Font] = None
    
    def _get_font(self) -> pygame.font.Font:
        """获取字体"""
        if self._cached_font is None:
            size = FONT_SIZES.get(self.font_size, 28)
            self._cached_font = pygame.font.SysFont(self.theme.font_name, size)
        return self._cached_font
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            if self.contains_point(event.pos):
                if self.state != UIState.PRESSED:
                    self.state = UIState.HOVER
            else:
                self.state = UIState.NORMAL
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(event.pos):
                self.state = UIState.PRESSED
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.state == UIState.PRESSED:
                    self.state = UIState.HOVER if self.contains_point(event.pos) else UIState.NORMAL
                    if self.contains_point(event.pos) and self.on_click:
                        self.on_click()
                        return True
                else:
                    self.state = UIState.NORMAL
        
        return False
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染按钮"""
        # 选择颜色
        if self.state == UIState.DISABLED or not self.enabled:
            color = self.theme.disabled
        elif self.state == UIState.PRESSED:
            color = tuple(max(0, c - 40) for c in self.theme.primary)
        elif self.state == UIState.HOVER:
            color = tuple(min(255, c + 20) for c in self.theme.primary)
        else:
            color = self.theme.primary
        
        # 绘制背景
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        # 绘制边框
        border_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(screen, border_color, self.rect, 
                        width=2, border_radius=self.border_radius)
        
        # 绘制文字
        if self.text:
            font = self._get_font()
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        
        # 绘制图标
        if self.icon:
            icon_rect = self.icon.get_rect(center=self.rect.center)
            screen.blit(self.icon, icon_rect)


class Label(UIComponent):
    """标签组件"""
    
    def __init__(self, x: int, y: int, text: str = "",
                 font_size: str = 'normal', color: Optional[Tuple[int, int, int]] = None,
                 center: bool = False):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font_size = font_size
        self.color = color or self.theme.text
        self.center = center
        self._cached_font: Optional[pygame.font.Font] = None
        self._update_rect()
    
    def _get_font(self) -> pygame.font.Font:
        """获取字体"""
        if self._cached_font is None:
            size = FONT_SIZES.get(self.font_size, 28)
            self._cached_font = pygame.font.SysFont(self.theme.font_name, size)
        return self._cached_font
    
    def set_text(self, text: str) -> None:
        """设置文字"""
        self.text = text
        self._update_rect()
    
    def _update_rect(self) -> None:
        """更新矩形区域"""
        if self.text:
            font = self._get_font()
            text_surface = font.render(self.text, True, self.color)
            self.rect.size = text_surface.get_size()
        else:
            self.rect.size = (0, 0)
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染标签"""
        if not self.text:
            return
        
        font = self._get_font()
        text_surface = font.render(self.text, True, self.color)
        
        if self.center:
            # 使用原始x,y作为中心点
            text_rect = text_surface.get_rect(center=(self.rect.x, self.rect.y))
        else:
            text_rect = text_surface.get_rect(topleft=self.rect.topleft)
        
        screen.blit(text_surface, text_rect)


class Panel(UIComponent):
    """面板组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 background_color: Optional[Tuple[int, int, int]] = None,
                 border_radius: int = 10, border_width: int = 0):
        super().__init__(x, y, width, height)
        self.background_color = background_color or self.theme.background
        self.border_radius = border_radius
        self.border_width = border_width
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染面板"""
        # 绘制背景
        pygame.draw.rect(screen, self.background_color, self.rect,
                        border_radius=self.border_radius)
        
        # 绘制边框
        if self.border_width > 0:
            border_color = tuple(min(255, c + 30) for c in self.background_color)
            pygame.draw.rect(screen, border_color, self.rect,
                           width=self.border_width, border_radius=self.border_radius)


class ProgressBar(UIComponent):
    """进度条组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 max_value: float = 100, value: float = 0,
                 bar_color: Optional[Tuple[int, int, int]] = None,
                 bg_color: Optional[Tuple[int, int, int]] = None):
        super().__init__(x, y, width, height)
        self.max_value = max_value
        self.value = value
        self.bar_color = bar_color or Colors.GOLD
        self.bg_color = bg_color or Colors.EMPTY_CELL
        self.border_radius = height // 2
    
    def set_value(self, value: float) -> None:
        """设置当前值"""
        self.value = max(0, min(self.max_value, value))
    
    def set_progress(self, progress: float) -> None:
        """设置进度（0-1）"""
        self.value = progress * self.max_value
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染进度条"""
        # 绘制背景
        pygame.draw.rect(screen, self.bg_color, self.rect,
                        border_radius=self.border_radius)
        
        # 计算进度宽度
        if self.max_value > 0:
            progress = self.value / self.max_value
            progress_width = int(self.rect.width * progress)
            
            if progress_width > 0:
                progress_rect = pygame.Rect(
                    self.rect.x, self.rect.y,
                    progress_width, self.rect.height
                )
                pygame.draw.rect(screen, self.bar_color, progress_rect,
                               border_radius=self.border_radius)


class Slider(UIComponent):
    """滑块组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int = 30,
                 min_value: float = 0, max_value: float = 1,
                 value: float = 0.5, on_change: Optional[Callable[[float], None]] = None):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change = on_change
        self.dragging = False
        self.slider_radius = height // 2
        self.track_height = 6
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(event.pos):
                self.dragging = True
                self._update_value_from_mouse(event.pos[0])
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value_from_mouse(event.pos[0])
                return True
        
        return False
    
    def _update_value_from_mouse(self, mouse_x: int) -> None:
        """根据鼠标位置更新值"""
        track_x = self.rect.x + self.slider_radius
        track_width = self.rect.width - self.slider_radius * 2
        
        relative_x = max(0, min(track_width, mouse_x - track_x))
        ratio = relative_x / track_width if track_width > 0 else 0
        
        new_value = self.min_value + ratio * (self.max_value - self.min_value)
        
        if new_value != self.value:
            self.value = new_value
            if self.on_change:
                self.on_change(self.value)
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染滑块"""
        # 绘制轨道
        track_y = self.rect.centery - self.track_height // 2
        track_rect = pygame.Rect(
            self.rect.x + self.slider_radius, track_y,
            self.rect.width - self.slider_radius * 2, self.track_height
        )
        pygame.draw.rect(screen, self.theme.secondary, track_rect,
                        border_radius=self.track_height // 2)
        
        # 计算滑块位置
        if self.max_value > self.min_value:
            ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        else:
            ratio = 0
        
        slider_x = self.rect.x + self.slider_radius + int(
            (self.rect.width - self.slider_radius * 2) * ratio
        )
        
        # 绘制滑块
        pygame.draw.circle(screen, self.theme.primary,
                         (slider_x, self.rect.centery), self.slider_radius)
        pygame.draw.circle(screen, self.theme.text,
                         (slider_x, self.rect.centery), self.slider_radius, 2)


class GridView(UIComponent):
    """网格视图组件"""
    
    def __init__(self, x: int, y: int, rows: int, cols: int,
                 cell_size: int, cell_padding: int = 10):
        width = cols * (cell_size + cell_padding) + cell_padding
        height = rows * (cell_size + cell_padding) + cell_padding
        super().__init__(x, y, width, height)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cell_padding = cell_padding
        self.grid_data: List[List[Any]] = [[None] * cols for _ in range(rows)]
        self.cell_renderer: Optional[Callable[[pygame.Surface, int, int, Any, pygame.Rect], None]] = None
    
    def set_cell_renderer(self, renderer: Callable) -> None:
        """设置单元格渲染器"""
        self.cell_renderer = renderer
    
    def set_data(self, data: List[List[Any]]) -> None:
        """设置网格数据"""
        self.grid_data = data
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染网格"""
        # 绘制背景
        pygame.draw.rect(screen, self.theme.grid_bg, self.rect, border_radius=10)
        
        # 绘制单元格
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.rect.x + self.cell_padding + col * (self.cell_size + self.cell_padding)
                y = self.rect.y + self.cell_padding + row * (self.cell_size + self.cell_padding)
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                # 绘制空单元格背景
                pygame.draw.rect(screen, self.theme.empty_cell, cell_rect, border_radius=8)
                
                # 调用自定义渲染器
                if self.cell_renderer and row < len(self.grid_data) and col < len(self.grid_data[row]):
                    self.cell_renderer(screen, row, col, self.grid_data[row][col], cell_rect)


class ScrollView(UIComponent):
    """滚动视图组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 content_height: int = 0):
        super().__init__(x, y, width, height)
        self.content_height = content_height
        self.scroll_y = 0
        self.scrollbar_width = 10
        self.dragging_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.visible or not self.enabled:
            return False
        
        # 处理子组件事件（考虑滚动偏移）
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # 检查是否点击滚动条
                scrollbar_rect = self._get_scrollbar_rect()
                if scrollbar_rect and scrollbar_rect.collidepoint(event.pos):
                    self.dragging_scrollbar = True
                    self.drag_start_y = event.pos[1]
                    self.drag_start_scroll = self.scroll_y
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_scrollbar = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_scrollbar:
                delta_y = event.pos[1] - self.drag_start_y
                max_scroll = max(0, self.content_height - self.rect.height)
                scrollbar_height = self._get_scrollbar_height()
                if scrollbar_height < self.rect.height:
                    scroll_ratio = delta_y / (self.rect.height - scrollbar_height)
                    self.scroll_y = max(0, min(max_scroll,
                                              self.drag_start_scroll + scroll_ratio * max_scroll))
                return True
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.contains_point(pygame.mouse.get_pos()):
                scroll_amount = event.y * 30
                max_scroll = max(0, self.content_height - self.rect.height)
                self.scroll_y = max(0, min(max_scroll, self.scroll_y - scroll_amount))
                return True
        
        # 调整鼠标位置后传递给子组件
        adjusted_event = self._adjust_event_for_scroll(event)
        for child in self.children:
            if child.handle_event(adjusted_event):
                return True
        
        return False
    
    def _adjust_event_for_scroll(self, event: pygame.event.Event) -> pygame.event.Event:
        """调整事件坐标以考虑滚动"""
        if hasattr(event, 'pos'):
            new_event = pygame.event.Event(event.type, **event.dict)
            new_event.dict['pos'] = (event.pos[0], event.pos[1] + self.scroll_y)
            return new_event
        return event
    
    def _get_scrollbar_height(self) -> int:
        """获取滚动条高度"""
        if self.content_height <= self.rect.height:
            return self.rect.height
        ratio = self.rect.height / self.content_height
        return max(30, int(self.rect.height * ratio))
    
    def _get_scrollbar_rect(self) -> Optional[pygame.Rect]:
        """获取滚动条矩形"""
        if self.content_height <= self.rect.height:
            return None
        
        scrollbar_height = self._get_scrollbar_height()
        max_scroll = self.content_height - self.rect.height
        scroll_ratio = self.scroll_y / max_scroll if max_scroll > 0 else 0
        
        scrollbar_y = self.rect.y + scroll_ratio * (self.rect.height - scrollbar_height)
        
        return pygame.Rect(
            self.rect.right - self.scrollbar_width - 2,
            int(scrollbar_y),
            self.scrollbar_width,
            scrollbar_height
        )
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染滚动视图"""
        if not self.visible:
            return
        
        # 创建裁剪区域
        clip_rect = screen.get_clip()
        screen.set_clip(self.rect)
        
        # 渲染内容（考虑滚动偏移）
        for child in self.children:
            # 临时调整子组件位置
            original_y = child.rect.y
            child.rect.y = original_y - int(self.scroll_y)
            child.render(screen)
            child.rect.y = original_y
        
        # 恢复裁剪区域
        screen.set_clip(clip_rect)
        
        # 渲染滚动条
        scrollbar_rect = self._get_scrollbar_rect()
        if scrollbar_rect:
            pygame.draw.rect(screen, self.theme.secondary, scrollbar_rect,
                           border_radius=self.scrollbar_width // 2)


class Dialog(UIComponent):
    """对话框组件"""
    
    def __init__(self, width: int = 400, height: int = 300,
                 title: str = "", modal: bool = True):
        x = (SCREEN_WIDTH - width) // 2
        y = (SCREEN_HEIGHT - height) // 2
        super().__init__(x, y, width, height)
        self.title = title
        self.modal = modal
        self.result: Any = None
        self.on_close: Optional[Callable] = None
        self.border_radius = 15
    
    def close(self, result: Any = None) -> None:
        """关闭对话框"""
        self.result = result
        self.visible = False
        if self.on_close:
            self.on_close(result)
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染对话框"""
        # 绘制半透明背景（模态）
        if self.modal:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
        
        # 绘制对话框背景
        pygame.draw.rect(screen, self.theme.background, self.rect,
                        border_radius=self.border_radius)
        pygame.draw.rect(screen, self.theme.primary, self.rect,
                        width=3, border_radius=self.border_radius)
        
        # 绘制标题
        if self.title:
            font = pygame.font.SysFont(self.theme.font_name, FONT_SIZES['medium'])
            title_surface = font.render(self.title, True, self.theme.text)
            title_rect = title_surface.get_rect(
                centerx=self.rect.centerx,
                top=self.rect.top + 20
            )
            screen.blit(title_surface, title_rect)
            
            # 标题分隔线
            line_y = title_rect.bottom + 10
            pygame.draw.line(screen, self.theme.secondary,
                           (self.rect.left + 20, line_y),
                           (self.rect.right - 20, line_y), 2)


class Toast(UIComponent):
    """提示消息组件"""
    
    def __init__(self, text: str, duration: float = 2.0,
                 x: int = SCREEN_WIDTH // 2, y: int = SCREEN_HEIGHT - 100):
        # 先计算文字大小
        font = pygame.font.SysFont("arial", FONT_SIZES['normal'])
        text_surface = font.render(text, True, Colors.TEXT_LIGHT)
        padding = 20
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding
        
        super().__init__(x - width // 2, y, width, height)
        self.text = text
        self.duration = duration
        self.elapsed = 0
        self.alpha = 255
    
    def update(self, dt: float) -> None:
        """更新提示"""
        super().update(dt)
        self.elapsed += dt / 1000  # 转换为秒
        
        # 淡出效果
        if self.elapsed > self.duration - 0.5:
            self.alpha = int(255 * (self.duration - self.elapsed) / 0.5)
        
        if self.elapsed >= self.duration:
            self.visible = False
    
    def _render_self(self, screen: pygame.Surface) -> None:
        """渲染提示"""
        if self.alpha <= 0:
            return
        
        # 创建带透明度的表面
        surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # 绘制背景
        bg_color = (*Colors.BUTTON_BG[:3], self.alpha)
        pygame.draw.rect(surface, bg_color, surface.get_rect(), border_radius=10)
        
        # 绘制文字
        font = pygame.font.SysFont("arial", FONT_SIZES['normal'])
        text_color = (*Colors.TEXT_LIGHT[:3], self.alpha)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        screen.blit(surface, self.rect.topleft)


class UIManager:
    """UI管理器"""
    
    def __init__(self):
        self.root = UIComponent(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.theme = Theme()
        self.toasts: List[Toast] = []
        self.modal_dialog: Optional[Dialog] = None
    
    def set_theme(self, dark: bool = False) -> None:
        """设置主题"""
        self.theme = DarkTheme() if dark else Theme()
        self.root.set_theme(self.theme)
    
    def add_component(self, component: UIComponent) -> None:
        """添加组件"""
        component.set_theme(self.theme)
        self.root.add_child(component)
    
    def remove_component(self, component: UIComponent) -> None:
        """移除组件"""
        self.root.remove_child(component)
    
    def show_toast(self, text: str, duration: float = 2.0) -> None:
        """显示提示"""
        # 调整现有提示位置
        for toast in self.toasts:
            toast.rect.y -= 60
        
        toast = Toast(text, duration)
        toast.set_theme(self.theme)
        self.toasts.append(toast)
    
    def show_dialog(self, dialog: Dialog) -> None:
        """显示对话框"""
        dialog.set_theme(self.theme)
        self.modal_dialog = dialog
        self.root.add_child(dialog)
    
    def close_dialog(self) -> None:
        """关闭对话框"""
        if self.modal_dialog:
            self.root.remove_child(self.modal_dialog)
            self.modal_dialog = None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        # 模态对话框优先
        if self.modal_dialog and self.modal_dialog.visible:
            return self.modal_dialog.handle_event(event)
        
        return self.root.handle_event(event)
    
    def update(self, dt: float) -> None:
        """更新UI"""
        self.root.update(dt)
        
        # 更新提示
        for toast in self.toasts[:]:
            toast.update(dt)
            if not toast.visible:
                self.toasts.remove(toast)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染UI"""
        self.root.render(screen)
        
        # 渲染提示
        for toast in self.toasts:
            toast.render(screen)
