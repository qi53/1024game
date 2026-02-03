"""
1024 Game - Pygame Version - Tests - UI Components
UI组件测试
"""

import unittest
import sys
import os

try:
    import pygame
    pygame.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_components import (
    UIComponent, Button, Label, Panel, ProgressBar,
    Slider, GridView, Theme, DarkTheme, UIState
)


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestUIComponent(unittest.TestCase):
    """测试UI组件基类"""
    
    def test_creation(self):
        """测试创建"""
        component = UIComponent(10, 20, 100, 200)
        self.assertEqual(component.rect.x, 10)
        self.assertEqual(component.rect.y, 20)
        self.assertEqual(component.rect.width, 100)
        self.assertEqual(component.rect.height, 200)
        self.assertTrue(component.visible)
        self.assertTrue(component.enabled)
    
    def test_contains_point(self):
        """测试点是否在组件内"""
        component = UIComponent(10, 20, 100, 200)
        self.assertTrue(component.contains_point((50, 100)))
        self.assertFalse(component.contains_point((5, 100)))
        self.assertFalse(component.contains_point((50, 300)))
    
    def test_add_remove_child(self):
        """测试添加和移除子组件"""
        parent = UIComponent(0, 0, 100, 100)
        child = UIComponent(10, 10, 50, 50)
        
        parent.add_child(child)
        self.assertEqual(len(parent.children), 1)
        self.assertEqual(child.parent, parent)
        
        parent.remove_child(child)
        self.assertEqual(len(parent.children), 0)
        self.assertIsNone(child.parent)


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestButton(unittest.TestCase):
    """测试按钮组件"""
    
    def test_creation(self):
        """测试创建"""
        button = Button(10, 20, 100, 50, "Test", 'normal')
        self.assertEqual(button.text, "Test")
        self.assertEqual(button.state, UIState.NORMAL)
    
    def test_click(self):
        """测试点击"""
        clicked = [False]
        
        def on_click():
            clicked[0] = True
        
        button = Button(10, 20, 100, 50, "Test", 'normal', on_click)
        
        # 模拟点击
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 40))
        button.handle_event(event)
        
        event = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(50, 40))
        button.handle_event(event)
        
        self.assertTrue(clicked[0])
    
    def test_disabled(self):
        """测试禁用状态"""
        button = Button(10, 20, 100, 50, "Test", 'normal')
        button.enabled = False
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 40))
        result = button.handle_event(event)
        
        self.assertFalse(result)


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestLabel(unittest.TestCase):
    """测试标签组件"""
    
    def test_creation(self):
        """测试创建"""
        label = Label(10, 20, "Test Text", 'normal')
        self.assertEqual(label.text, "Test Text")
    
    def test_set_text(self):
        """测试设置文字"""
        label = Label(10, 20, "Old", 'normal')
        label.set_text("New")
        self.assertEqual(label.text, "New")


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestPanel(unittest.TestCase):
    """测试面板组件"""
    
    def test_creation(self):
        """测试创建"""
        panel = Panel(10, 20, 100, 200)
        self.assertEqual(panel.rect.x, 10)
        self.assertEqual(panel.rect.y, 20)


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestProgressBar(unittest.TestCase):
    """测试进度条组件"""
    
    def test_creation(self):
        """测试创建"""
        bar = ProgressBar(10, 20, 100, 20, max_value=100, value=50)
        self.assertEqual(bar.max_value, 100)
        self.assertEqual(bar.value, 50)
    
    def test_set_value(self):
        """测试设置值"""
        bar = ProgressBar(10, 20, 100, 20, max_value=100, value=0)
        bar.set_value(75)
        self.assertEqual(bar.value, 75)
    
    def test_value_clamping(self):
        """测试值限制"""
        bar = ProgressBar(10, 20, 100, 20, max_value=100, value=50)
        bar.set_value(150)
        self.assertEqual(bar.value, 100)
        
        bar.set_value(-10)
        self.assertEqual(bar.value, 0)
    
    def test_set_progress(self):
        """测试设置进度"""
        bar = ProgressBar(10, 20, 100, 20, max_value=100, value=0)
        bar.set_progress(0.5)
        self.assertEqual(bar.value, 50)


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestSlider(unittest.TestCase):
    """测试滑块组件"""
    
    def test_creation(self):
        """测试创建"""
        slider = Slider(10, 20, 100, 30, min_value=0, max_value=1, value=0.5)
        self.assertEqual(slider.min_value, 0)
        self.assertEqual(slider.max_value, 1)
        self.assertEqual(slider.value, 0.5)
    
    def test_on_change_callback(self):
        """测试变化回调"""
        changed_value = [None]
        
        def on_change(value):
            changed_value[0] = value
        
        slider = Slider(10, 20, 100, 30, min_value=0, max_value=1, value=0, on_change=on_change)
        
        # 模拟拖动
        slider.dragging = True
        event = pygame.event.Event(pygame.MOUSEMOTION, pos=(60, 35))
        slider.handle_event(event)
        
        self.assertIsNotNone(changed_value[0])


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestTheme(unittest.TestCase):
    """测试主题"""
    
    def test_default_theme(self):
        """测试默认主题"""
        theme = Theme()
        self.assertIsNotNone(theme.background)
        self.assertIsNotNone(theme.primary)
        self.assertIsNotNone(theme.text)
    
    def test_dark_theme(self):
        """测试深色主题"""
        theme = DarkTheme()
        self.assertIsNotNone(theme.background)
        self.assertIsNotNone(theme.primary)


@unittest.skipUnless(HAS_PYGAME, "Pygame not available")
class TestUIState(unittest.TestCase):
    """测试UI状态"""
    
    def test_states(self):
        """测试状态枚举"""
        self.assertEqual(UIState.NORMAL.name, "NORMAL")
        self.assertEqual(UIState.HOVER.name, "HOVER")
        self.assertEqual(UIState.PRESSED.name, "PRESSED")
        self.assertEqual(UIState.DISABLED.name, "DISABLED")


if __name__ == '__main__':
    unittest.main()
