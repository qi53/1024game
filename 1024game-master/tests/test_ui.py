import unittest
import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.Surface((800, 600))
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_button_creation(self):
        from src.ui import Button
        
        clicked = [False]
        def on_click():
            clicked[0] = True
        
        btn = Button(100, 100, 150, 50, "测试", on_click)
        
        self.assertIsNotNone(btn)
        btn.render(self.screen)
    
    def test_button_click(self):
        from src.ui import Button
        
        clicked = [False]
        def on_click():
            clicked[0] = True
        
        btn = Button(100, 100, 150, 50, "测试", on_click)
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(120, 120), button=1)
        btn.handle_event(event)
        
        event = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(120, 120), button=1)
        result = btn.handle_event(event)
        
        self.assertTrue(result)
    
    def test_slider_creation(self):
        from src.ui import Slider
        
        slider = Slider(100, 100, 200, 20, 0.0, 1.0, 0.5, "测试")
        self.assertIsNotNone(slider)
    
    def test_slider_value_range(self):
        from src.ui import Slider
        
        slider = Slider(100, 100, 200, 20, 0.0, 1.0, 0.5, "测试")
        
        slider.value = 1.5
        self.assertEqual(slider.value, 1.0)
        
        slider.value = -0.5
        self.assertEqual(slider.value, 0.0)
    
    def test_toggle_creation(self):
        from src.ui import Toggle
        
        toggle = Toggle(100, 100, 60, 30, "测试", True)
        self.assertTrue(toggle.value)
    
    def test_toggle_switch(self):
        from src.ui import Toggle
        
        toggle = Toggle(100, 100, 60, 30, "测试", True)
        
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(110, 110), button=1)
        toggle.handle_event(event)
        
        self.assertFalse(toggle.value)
    
    def test_progress_bar(self):
        from src.ui import ProgressBar
        
        pb = ProgressBar(100, 100, 200, 20, 100.0, 50.0)
        self.assertEqual(pb.value, 50)
        pb.render(self.screen)
    
    def test_progress_bar_percentage(self):
        from src.ui import ProgressBar
        
        pb = ProgressBar(100, 100, 200, 20, 100.0, 50.0)
        self.assertEqual(pb.value / pb.max_value, 0.5)
    
    def test_star_display(self):
        from src.ui import StarDisplay
        
        sd = StarDisplay(100, 100, 30, 2, 3)
        self.assertEqual(sd.stars, 2)
        sd.render(self.screen)


if __name__ == "__main__":
    unittest.main()
