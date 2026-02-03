"""
1024 Game - Pygame Version - Tests - Particle System
粒子系统测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from particles import Particle, ParticleSystem, AnimatedTile, AnimationManager
from config import Colors


class TestParticle(unittest.TestCase):
    """测试粒子"""
    
    def test_particle_creation(self):
        """测试粒子创建"""
        particle = Particle(
            x=100, y=100, vx=1, vy=1,
            life=1000, max_life=1000,
            color=(255, 0, 0), size=10,
            size_decay=0.1, alpha=255, alpha_decay=0.5
        )
        
        self.assertEqual(particle.x, 100)
        self.assertEqual(particle.y, 100)
        self.assertTrue(particle.is_alive)
    
    def test_particle_update(self):
        """测试粒子更新"""
        particle = Particle(
            x=100, y=100, vx=10, vy=5,
            life=1000, max_life=1000,
            color=(255, 0, 0), size=10,
            size_decay=1, alpha=255, alpha_decay=1
        )
        
        particle.update(16)  # 16ms
        
        # 检查位置变化（vx, vy 是每毫秒的速度）
        self.assertAlmostEqual(particle.x, 260, delta=1)  # 100 + 10 * 16
        self.assertAlmostEqual(particle.y, 180, delta=1)  # 100 + 5 * 16
        self.assertEqual(particle.life, 984)  # 1000 - 16
    
    def test_particle_death(self):
        """测试粒子死亡"""
        particle = Particle(
            x=100, y=100, vx=0, vy=0,
            life=10, max_life=100,
            color=(255, 0, 0), size=10,
            size_decay=0.1, alpha=255, alpha_decay=10
        )
        
        particle.update(20)  # 超过生命时间
        
        self.assertFalse(particle.is_alive)


class TestParticleSystem(unittest.TestCase):
    """测试粒子系统"""
    
    def setUp(self):
        """每个测试前执行"""
        self.system = ParticleSystem()
    
    def tearDown(self):
        """每个测试后执行"""
        self.system.stop()
    
    def test_spawn_explosion(self):
        """测试生成爆炸效果"""
        self.system.spawn_explosion(100, 100, count=10)
        self.assertEqual(self.system.get_count(), 10)
    
    def test_spawn_sparkle(self):
        """测试生成闪烁效果"""
        self.system.spawn_sparkle(100, 100, count=5)
        self.assertEqual(self.system.get_count(), 5)
    
    def test_spawn_merge_effect(self):
        """测试生成合并效果"""
        self.system.spawn_merge_effect(100, 100, value=128)
        self.assertGreater(self.system.get_count(), 0)
    
    def test_spawn_spawn_effect(self):
        """测试生成出现效果"""
        self.system.spawn_spawn_effect(100, 100)
        self.assertGreater(self.system.get_count(), 0)
    
    def test_clear(self):
        """测试清除粒子"""
        self.system.spawn_explosion(100, 100, count=10)
        self.assertEqual(self.system.get_count(), 10)
        
        self.system.clear()
        self.assertEqual(self.system.get_count(), 0)
    
    def test_update(self):
        """测试更新粒子"""
        self.system.spawn_explosion(100, 100, count=5)
        initial_count = self.system.get_count()
        
        # 更新很长时间使粒子死亡
        self.system.update(2000)
        
        # 粒子应该死亡
        self.assertLess(self.system.get_count(), initial_count)


class TestAnimatedTile(unittest.TestCase):
    """测试动画方块"""
    
    def test_creation(self):
        """测试创建"""
        tile = AnimatedTile(
            value=2, x=0, y=0,
            target_x=100, target_y=100
        )
        
        self.assertEqual(tile.value, 2)
        self.assertEqual(tile.scale, 1.0)
        self.assertTrue(tile.is_new)
    
    def test_new_tile_animation(self):
        """测试新方块动画"""
        tile = AnimatedTile(
            value=2, x=100, y=100,
            target_x=100, target_y=100
        )
        tile.scale = 0.1
        tile.target_scale = 1.0
        
        # 更新几帧
        for _ in range(10):
            tile.update(16)
        
        # 应该接近目标大小
        self.assertGreater(tile.scale, 0.5)
    
    def test_move_animation(self):
        """测试移动动画"""
        tile = AnimatedTile(
            value=2, x=0, y=0,
            target_x=100, target_y=100
        )
        
        # 更新几帧
        for _ in range(20):
            tile.update(16)
        
        # 应该接近目标位置
        self.assertGreater(tile.x, 50)
        self.assertGreater(tile.y, 50)
    
    def test_merge_animation(self):
        """测试合并动画"""
        tile = AnimatedTile(
            value=4, x=100, y=100,
            target_x=100, target_y=100
        )
        tile.is_merging = True
        tile.animation_progress = 0
        tile.is_new = False  # 确保不是新方块
        
        # 更新（在动画前半段）
        tile.update(30)  # 30ms < 75ms (150ms的一半)
        
        # 应该有缩放效果
        self.assertNotEqual(tile.scale, 1.0)


class TestAnimationManager(unittest.TestCase):
    """测试动画管理器"""
    
    def setUp(self):
        """每个测试前执行"""
        self.manager = AnimationManager()
        self.manager.start()
    
    def tearDown(self):
        """每个测试后执行"""
        self.manager.stop()
    
    def test_create_tile(self):
        """测试创建方块"""
        self.manager.create_tile(
            row=0, col=0, value=2,
            grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        self.assertEqual(len(self.manager.tiles), 1)
    
    def test_move_tile(self):
        """测试移动方块"""
        # 先创建方块
        self.manager.create_tile(
            row=0, col=0, value=2,
            grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        # 移动方块
        self.manager.move_tile(
            from_row=0, from_col=0,
            to_row=1, to_col=1,
            grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        # 检查位置更新
        tile = self.manager.tiles.get((1, 1))
        self.assertIsNotNone(tile)
    
    def test_merge_tiles(self):
        """测试合并方块"""
        # 创建方块
        self.manager.create_tile(
            row=0, col=0, value=2,
            grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        # 合并
        self.manager.merge_tiles(
            row=0, col=0, new_value=4,
            grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        tile = self.manager.tiles.get((0, 0))
        self.assertEqual(tile.value, 4)
        self.assertTrue(tile.is_merging)
    
    def test_sync_with_grid(self):
        """测试与网格同步"""
        grid = [
            [2, 0, 0, 0],
            [0, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 8]
        ]
        
        self.manager.sync_with_grid(
            grid, grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        # 应该创建3个方块
        self.assertEqual(len(self.manager.tiles), 3)
    
    def test_clear(self):
        """测试清除"""
        self.manager.create_tile(
            row=0, col=0, value=2,
            grid_offset_x=100, grid_offset_y=100,
            cell_size=80, cell_padding=10
        )
        
        self.manager.clear()
        
        self.assertEqual(len(self.manager.tiles), 0)
        self.assertEqual(self.manager.particles.get_count(), 0)


if __name__ == '__main__':
    unittest.main()
