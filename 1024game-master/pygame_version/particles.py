"""
1024 Game - Pygame Version - Particle System
粒子特效系统，支持多线程渲染
"""

import pygame
import random
import math
import threading
from typing import List, Tuple, Optional
from dataclasses import dataclass
from config import Colors, PARTICLE_LIFETIME


@dataclass
class Particle:
    """单个粒子"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    size_decay: float
    alpha: float
    alpha_decay: float
    gravity: float = 0.0
    
    @property
    def is_alive(self) -> bool:
        return self.life > 0 and self.alpha > 0
    
    def update(self, dt: float) -> None:
        """更新粒子状态"""
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.size = max(0, self.size - self.size_decay * dt)
        self.alpha = max(0, self.alpha - self.alpha_decay * dt)


class ParticleSystem:
    """粒子系统管理器"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.lock = threading.Lock()
        self._update_thread: Optional[threading.Thread] = None
        self._running = False
    
    def start(self) -> None:
        """启动更新线程"""
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def stop(self) -> None:
        """停止更新线程"""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=0.1)
    
    def _update_loop(self) -> None:
        """后台更新循环"""
        import time
        last_time = time.time()
        while self._running:
            current_time = time.time()
            dt = (current_time - last_time) * 1000  # 转换为毫秒
            last_time = current_time
            self.update(dt)
            time.sleep(1/120)  # 120Hz更新率
    
    def spawn_explosion(self, x: float, y: float, count: int = 30, 
                        color: Optional[Tuple[int, int, int]] = None,
                        speed: float = 5.0, size: float = 12.0) -> None:
        """生成爆炸效果 - 增强版"""
        if color is None:
            color = random.choice(Colors.PARTICLE_COLORS)
        
        with self.lock:
            for _ in range(count):
                angle = random.uniform(0, 2 * math.pi)
                speed_var = random.uniform(0.5, 1.5) * speed
                vx = math.cos(angle) * speed_var
                vy = math.sin(angle) * speed_var
                
                particle = Particle(
                    x=x,
                    y=y,
                    vx=vx,
                    vy=vy,
                    life=PARTICLE_LIFETIME * random.uniform(0.7, 1.0),
                    max_life=PARTICLE_LIFETIME,
                    color=color,
                    size=size * random.uniform(0.8, 1.2),
                    size_decay=size / PARTICLE_LIFETIME * 1.5,
                    alpha=255,
                    alpha_decay=255 / PARTICLE_LIFETIME * 1.2,
                    gravity=0.03
                )
                self.particles.append(particle)
    
    def spawn_sparkle(self, x: float, y: float, count: int = 10,
                      color: Optional[Tuple[int, int, int]] = None) -> None:
        """生成闪烁效果"""
        if color is None:
            color = Colors.GOLD
        
        with self.lock:
            for _ in range(count):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, 30)
                px = x + math.cos(angle) * distance
                py = y + math.sin(angle) * distance
                
                particle = Particle(
                    x=px,
                    y=py,
                    vx=0,
                    vy=-0.5,
                    life=800 * random.uniform(0.5, 1.0),
                    max_life=800,
                    color=color,
                    size=random.uniform(2, 5),
                    size_decay=0.01,
                    alpha=200,
                    alpha_decay=0.3
                )
                self.particles.append(particle)
    
    def spawn_merge_effect(self, x: float, y: float, value: int) -> None:
        """生成合并特效 - 增强版"""
        # 根据数值选择颜色
        if value < 128:
            color = (255, 200, 100)
        elif value < 512:
            color = (255, 150, 50)
        elif value < 2048:
            color = (255, 100, 50)
        else:
            color = (255, 50, 100)
        
        # 爆炸效果 - 更多粒子
        particle_count = min(50, value // 30 + 15)
        self.spawn_explosion(x, y, count=particle_count, 
                            color=color, speed=6.0, size=15.0)
        
        # 闪烁效果 - 更多闪烁
        self.spawn_sparkle(x, y, count=25, color=Colors.GOLD)
        
        # 添加光环效果
        self.spawn_ring_effect(x, y, color)
    
    def spawn_spawn_effect(self, x: float, y: float) -> None:
        """生成新方块出现特效"""
        self.spawn_explosion(x, y, count=8, 
                            color=(100, 255, 100), 
                            speed=2.0, size=5.0)
    
    def spawn_win_effect(self, x: float, y: float) -> None:
        """生成胜利特效"""
        colors = [Colors.GOLD, (255, 215, 0), (255, 255, 0), (255, 200, 50)]
        for i, color in enumerate(colors):
            offset_x = random.uniform(-50, 50)
            offset_y = random.uniform(-50, 50)
            self.spawn_explosion(x + offset_x, y + offset_y, 
                               count=25, color=color, speed=5.0, size=12.0)
    
    def spawn_trail(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """生成拖尾效果"""
        with self.lock:
            particle = Particle(
                x=x + random.uniform(-5, 5),
                y=y + random.uniform(-5, 5),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-0.5, 0.5),
                life=300,
                max_life=300,
                color=color,
                size=random.uniform(3, 6),
                size_decay=0.02,
                alpha=150,
                alpha_decay=0.5
            )
            self.particles.append(particle)
    
    def spawn_ring_effect(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """生成光环扩散效果"""
        with self.lock:
            # 创建多个环形粒子
            for ring in range(3):
                radius = 20 + ring * 15
                particle_count = 12 + ring * 4
                for i in range(particle_count):
                    angle = (2 * math.pi / particle_count) * i
                    px = x + math.cos(angle) * radius
                    py = y + math.sin(angle) * radius
                    
                    # 向外扩散的速度
                    vx = math.cos(angle) * (2.0 + ring * 0.5)
                    vy = math.sin(angle) * (2.0 + ring * 0.5)
                    
                    particle = Particle(
                        x=px,
                        y=py,
                        vx=vx,
                        vy=vy,
                        life=800 + ring * 200,
                        max_life=800 + ring * 200,
                        color=color,
                        size=8 - ring * 2,
                        size_decay=0.02,
                        alpha=200 - ring * 30,
                        alpha_decay=0.3
                    )
                    self.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """更新所有粒子"""
        with self.lock:
            for particle in self.particles[:]:
                particle.update(dt)
                if not particle.is_alive:
                    self.particles.remove(particle)
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染所有粒子"""
        with self.lock:
            for particle in self.particles:
                if particle.size > 0 and particle.alpha > 0:
                    # 创建带透明度的颜色
                    color = (*particle.color[:3], int(particle.alpha))
                    
                    # 绘制粒子
                    surface = pygame.Surface((int(particle.size * 2), int(particle.size * 2)), 
                                            pygame.SRCALPHA)
                    pygame.draw.circle(surface, color, 
                                     (int(particle.size), int(particle.size)), 
                                     int(particle.size))
                    screen.blit(surface, (int(particle.x - particle.size), 
                                         int(particle.y - particle.size)))
    
    def clear(self) -> None:
        """清除所有粒子"""
        with self.lock:
            self.particles.clear()
    
    def get_count(self) -> int:
        """获取当前粒子数量"""
        with self.lock:
            return len(self.particles)


class AnimatedTile:
    """带动画的方块"""
    
    def __init__(self, value: int, x: float, y: float, 
                 target_x: float, target_y: float):
        self.value = value
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.scale = 1.0
        self.target_scale = 1.0
        self.alpha = 255
        self.is_merging = False
        self.is_new = True
        self.animation_progress = 0.0
        
    def update(self, dt: float, animation_speed: float = 0.15) -> bool:
        """更新动画，返回是否还在动画中"""
        # 位置插值
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            self.x += dx * animation_speed
            self.y += dy * animation_speed
            return True
        else:
            self.x = self.target_x
            self.y = self.target_y
        
        # 缩放动画
        if self.is_new:
            # 新方块：从小到大
            self.scale += (self.target_scale - self.scale) * animation_speed * 2
            if abs(self.target_scale - self.scale) < 0.01:
                self.scale = self.target_scale
                self.is_new = False
            return True
        elif self.is_merging:
            # 合并：先放大再缩小
            self.animation_progress += dt / 150  # 150ms动画
            if self.animation_progress < 0.5:
                self.scale = 1.0 + 0.2 * math.sin(self.animation_progress * math.pi * 2)
                return True
            else:
                self.scale = 1.0
                self.is_merging = False
                return False
        
        return False
    
    def render(self, screen: pygame.Surface, colors: dict, text_colors: dict,
               cell_size: int, font: pygame.font.Font) -> None:
        """渲染方块"""
        size = int(cell_size * self.scale)
        offset = (cell_size - size) // 2
        
        rect = pygame.Rect(
            int(self.x) + offset,
            int(self.y) + offset,
            size,
            size
        )
        
        # 绘制圆角矩形
        color = colors.get(self.value, colors.get(0))
        pygame.draw.rect(screen, color, rect, border_radius=8)
        
        # 绘制数字
        if self.value > 0:
            text_color = text_colors.get(self.value, (255, 255, 255))
            text = font.render(str(self.value), True, text_color)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)


class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        self.tiles: dict = {}  # (row, col) -> AnimatedTile
        self.particles = ParticleSystem()
        self.lock = threading.Lock()
    
    def start(self) -> None:
        """启动动画系统"""
        self.particles.start()
    
    def stop(self) -> None:
        """停止动画系统"""
        self.particles.stop()
    
    def create_tile(self, row: int, col: int, value: int, 
                   grid_offset_x: int, grid_offset_y: int, 
                   cell_size: int, cell_padding: int) -> None:
        """创建新方块动画"""
        x = grid_offset_x + col * (cell_size + cell_padding)
        y = grid_offset_y + row * (cell_size + cell_padding)
        
        with self.lock:
            tile = AnimatedTile(value, x, y, x, y)
            tile.scale = 0.1
            tile.target_scale = 1.0
            self.tiles[(row, col)] = tile
        
        # 生成出现特效
        center_x = x + cell_size // 2
        center_y = y + cell_size // 2
        self.particles.spawn_spawn_effect(center_x, center_y)
    
    def move_tile(self, from_row: int, from_col: int, 
                 to_row: int, to_col: int,
                 grid_offset_x: int, grid_offset_y: int,
                 cell_size: int, cell_padding: int) -> None:
        """移动方块动画"""
        target_x = grid_offset_x + to_col * (cell_size + cell_padding)
        target_y = grid_offset_y + to_row * (cell_size + cell_padding)
        
        with self.lock:
            key = (from_row, from_col)
            if key in self.tiles:
                tile = self.tiles[key]
                tile.target_x = target_x
                tile.target_y = target_y
                self.tiles[(to_row, to_col)] = tile
                del self.tiles[key]
    
    def merge_tiles(self, row: int, col: int, new_value: int,
                   grid_offset_x: int, grid_offset_y: int,
                   cell_size: int, cell_padding: int) -> None:
        """合并方块动画"""
        x = grid_offset_x + col * (cell_size + cell_padding)
        y = grid_offset_y + row * (cell_size + cell_padding)
        
        with self.lock:
            key = (row, col)
            if key in self.tiles:
                tile = self.tiles[key]
                tile.value = new_value
                tile.is_merging = True
                tile.animation_progress = 0.0
        
        # 生成合并特效
        center_x = x + cell_size // 2
        center_y = y + cell_size // 2
        self.particles.spawn_merge_effect(center_x, center_y, new_value)
    
    def update(self, dt: float) -> bool:
        """更新所有动画，返回是否还有动画在进行"""
        with self.lock:
            animating = False
            for tile in self.tiles.values():
                if tile.update(dt):
                    animating = True
            return animating
    
    def render_tiles(self, screen: pygame.Surface, colors: dict, 
                    text_colors: dict, cell_size: int, 
                    font: pygame.font.Font) -> None:
        """渲染所有方块"""
        with self.lock:
            for tile in self.tiles.values():
                tile.render(screen, colors, text_colors, cell_size, font)
    
    def render_particles(self, screen: pygame.Surface) -> None:
        """渲染粒子效果"""
        self.particles.render(screen)
    
    def clear(self) -> None:
        """清除所有动画"""
        with self.lock:
            self.tiles.clear()
        self.particles.clear()
    
    def sync_with_grid(self, grid: list, grid_offset_x: int, grid_offset_y: int,
                      cell_size: int, cell_padding: int) -> None:
        """与游戏网格同步"""
        with self.lock:
            new_tiles = {}
            for row in range(len(grid)):
                for col in range(len(grid[row])):
                    value = grid[row][col]
                    x = grid_offset_x + col * (cell_size + cell_padding)
                    y = grid_offset_y + row * (cell_size + cell_padding)
                    
                    key = (row, col)
                    if key in self.tiles:
                        tile = self.tiles[key]
                        tile.value = value
                        tile.target_x = x
                        tile.target_y = y
                        new_tiles[key] = tile
                    elif value > 0:
                        tile = AnimatedTile(value, x, y, x, y)
                        new_tiles[key] = tile
            
            self.tiles = new_tiles
