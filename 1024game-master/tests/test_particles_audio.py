import unittest
import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestParticleSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        from src.particles import ParticleSystem
        self.ps = ParticleSystem()
    
    def test_initial_empty(self):
        self.assertEqual(len(self.ps.particles), 0)
    
    def test_spawn_merge_effect(self):
        self.ps.spawn_merge_particles(400, 300, (255, 100, 100), 16)
        self.assertGreater(len(self.ps.particles), 0)
    
    def test_spawn_spawn_effect(self):
        self.ps.spawn_spawn_particles(400, 300, (100, 255, 100))
        self.assertGreater(len(self.ps.particles), 0)
    
    def test_spawn_explosion_effect(self):
        self.ps.spawn_explosion(400, 300, (100, 100, 255), 30)
        self.assertGreater(len(self.ps.particles), 0)
    
    def test_particle_lifecycle(self):
        self.ps.spawn_merge_particles(400, 300, (255, 100, 100), 16)
        initial_count = len(self.ps.particles)
        
        self.ps.update(0.5)
        self.assertLessEqual(len(self.ps.particles), initial_count)
        
        self.ps.update(5.0)
        self.assertEqual(len(self.ps.particles), 0)
    
    def test_render_no_crash(self):
        screen = pygame.Surface((800, 600))
        self.ps.spawn_merge_particles(400, 300, (255, 100, 100), 16)
        self.ps.render(screen)


class TestAudioManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.mixer.init()
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        from src.audio import AudioManager
        AudioManager._instance = None
        self.am = AudioManager()
    
    def test_singleton(self):
        from src.audio import AudioManager
        am2 = AudioManager()
        self.assertIs(self.am, am2)
    
    def test_play_sound(self):
        try:
            self.am.play_sound("merge")
        except Exception as e:
            self.fail(f"play_sound raised {e}")
    
    def test_play_sound_3d(self):
        try:
            self.am.play_sound_3d("merge", (400, 300))
        except Exception as e:
            self.fail(f"play_sound_3d raised {e}")
    
    def test_set_volume(self):
        self.am.set_music_volume(0.5)
        self.am.set_sfx_volume(0.8)


if __name__ == "__main__":
    unittest.main()
