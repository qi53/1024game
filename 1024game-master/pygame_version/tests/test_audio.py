"""
1024 Game - Pygame Version - Tests - Audio System
音频系统测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio import SoundGenerator, AudioManager, SoundRequest


class TestSoundGenerator(unittest.TestCase):
    """测试音效生成器"""
    
    def setUp(self):
        """每个测试前执行"""
        try:
            import pygame
            pygame.init()
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.generator = SoundGenerator()
        except:
            self.skipTest("Pygame audio not available")
    
    def test_generate_tone(self):
        """测试生成音调"""
        sound = self.generator.generate_tone(440, 0.1)
        self.assertIsNotNone(sound)
    
    def test_generate_merge_sound(self):
        """测试生成合并音效"""
        sound = self.generator.generate_merge_sound(128)
        self.assertIsNotNone(sound)
    
    def test_generate_move_sound(self):
        """测试生成移动音效"""
        sound = self.generator.generate_move_sound()
        self.assertIsNotNone(sound)
    
    def test_generate_spawn_sound(self):
        """测试生成出现音效"""
        sound = self.generator.generate_spawn_sound()
        self.assertIsNotNone(sound)
    
    def test_generate_win_sound(self):
        """测试生成胜利音效"""
        sound = self.generator.generate_win_sound()
        self.assertIsNotNone(sound)
    
    def test_generate_lose_sound(self):
        """测试生成失败音效"""
        sound = self.generator.generate_lose_sound()
        self.assertIsNotNone(sound)
    
    def test_generate_button_sound(self):
        """测试生成按钮音效"""
        sound = self.generator.generate_button_sound()
        self.assertIsNotNone(sound)
    
    def test_generate_achievement_sound(self):
        """测试生成成就音效"""
        sound = self.generator.generate_achievement_sound()
        self.assertIsNotNone(sound)


class TestAudioManager(unittest.TestCase):
    """测试音频管理器"""
    
    def setUp(self):
        """每个测试前执行"""
        try:
            import pygame
            pygame.init()
            self.manager = AudioManager()
            self.manager.initialize()
        except:
            self.skipTest("Pygame audio not available")
    
    def tearDown(self):
        """每个测试后执行"""
        if hasattr(self, 'manager'):
            self.manager.cleanup()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertTrue(self.manager.initialized)
    
    def test_set_master_volume(self):
        """测试设置主音量"""
        self.manager.set_master_volume(0.5)
        self.assertEqual(self.manager.master_volume, 0.5)
    
    def test_set_sfx_volume(self):
        """测试设置音效音量"""
        self.manager.set_sfx_volume(0.7)
        self.assertEqual(self.manager.sfx_volume, 0.7)
    
    def test_set_music_volume(self):
        """测试设置音乐音量"""
        self.manager.set_music_volume(0.3)
        self.assertEqual(self.manager.music_volume, 0.3)
    
    def test_volume_clamping(self):
        """测试音量限制"""
        self.manager.set_master_volume(1.5)
        self.assertEqual(self.manager.master_volume, 1.0)
        
        self.manager.set_master_volume(-0.5)
        self.assertEqual(self.manager.master_volume, 0.0)
    
    def test_get_volumes(self):
        """测试获取音量设置"""
        self.manager.set_master_volume(0.5)
        self.manager.set_sfx_volume(0.7)
        self.manager.set_music_volume(0.3)
        
        volumes = self.manager.get_volumes()
        self.assertEqual(volumes[0], 0.5)
        self.assertEqual(volumes[1], 0.7)
        self.assertEqual(volumes[2], 0.3)


class TestSoundRequest(unittest.TestCase):
    """测试音效请求"""
    
    def test_default_values(self):
        """测试默认值"""
        request = SoundRequest("move")
        self.assertEqual(request.sound_type, "move")
        self.assertEqual(request.x, 0.5)
        self.assertEqual(request.y, 0.5)
        self.assertEqual(request.volume, 1.0)
        self.assertEqual(request.pitch, 1.0)
    
    def test_custom_values(self):
        """测试自定义值"""
        request = SoundRequest("merge", x=0.3, y=0.7, volume=0.8, pitch=1.2)
        self.assertEqual(request.sound_type, "merge")
        self.assertEqual(request.x, 0.3)
        self.assertEqual(request.y, 0.7)
        self.assertEqual(request.volume, 0.8)
        self.assertEqual(request.pitch, 1.2)


if __name__ == '__main__':
    unittest.main()
