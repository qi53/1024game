import pygame
import random
import math
from typing import List, Tuple, Optional


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int], size: int, lifetime: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.15
    
    def update(self, dt: int) -> bool:
        self.x += self.vx * (dt / 16.0)
        self.y += self.vy * (dt / 16.0)
        self.vy += self.gravity * (dt / 16.0)
        self.lifetime -= dt
        
        if self.size > 1:
            self.size = max(1, self.size - 0.05 * (dt / 16.0))
        
        return self.lifetime > 0
    
    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            temp_surface = pygame.Surface((int(self.size) * 2 + 2, int(self.size) * 2 + 2), pygame.SRCALPHA)
            temp_color = self.color + (alpha,)
            pygame.draw.circle(temp_surface, temp_color, 
                             (int(self.size) + 1, int(self.size) + 1), 
                             max(1, int(self.size)))
            surface.blit(temp_surface, (int(self.x) - int(self.size), int(self.y) - int(self.size)))


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        self.enabled = True
    
    def spawn_merge_particles(self, x: float, y: float, color: Tuple[int, int, int], count: int = 15):
        if not self.enabled:
            return
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            size = random.randint(3, 8)
            lifetime = random.randint(400, 700)
            
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                color=color,
                size=size,
                lifetime=lifetime
            )
            self.particles.append(particle)
    
    def spawn_spawn_particles(self, x: float, y: float, color: Tuple[int, int, int]):
        if not self.enabled:
            return
        
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            size = random.randint(2, 5)
            lifetime = random.randint(300, 500)
            
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                size=size,
                lifetime=lifetime
            )
            particle.gravity = 0.05
            self.particles.append(particle)
    
    def spawn_win_particles(self, x: float, y: float):
        if not self.enabled:
            return
        
        colors = [(255, 215, 0), (255, 100, 100), (100, 255, 100), (100, 100, 255)]
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            size = random.randint(4, 10)
            lifetime = random.randint(600, 1200)
            color = random.choice(colors)
            
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 3,
                color=color,
                size=size,
                lifetime=lifetime
            )
            self.particles.append(particle)
    
    def spawn_trail_particles(self, x: float, y: float, color: Tuple[int, int, int]):
        if not self.enabled:
            return
        
        particle = Particle(
            x=x,
            y=y,
            vx=random.uniform(-0.5, 0.5),
            vy=random.uniform(-0.5, 0.5),
            color=color,
            size=random.randint(2, 4),
            lifetime=random.randint(200, 400)
        )
        particle.gravity = 0
        self.particles.append(particle)
    
    def spawn_button_particles(self, x: float, y: float, color: Tuple[int, int, int]):
        if not self.enabled:
            return
        
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 3.5)
            size = random.randint(2, 5)
            
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=color,
                size=size,
                lifetime=300
            )
            particle.gravity = 0.05
            self.particles.append(particle)
    
    def update(self, dt: int):
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, surface: pygame.Surface):
        for particle in self.particles:
            particle.draw(surface)
    
    def clear(self):
        self.particles.clear()
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.clear()


class GlowEffect:
    def __init__(self):
        self.glow_surfaces: dict = {}
        self.cache: dict = {}
    
    def create_glow_surface(self, size: int, color: Tuple[int, int, int], alpha: int = 100) -> pygame.Surface:
        cache_key = (size, color, alpha)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        surface = pygame.Surface((size * 2 + 10, size * 2 + 10), pygame.SRCALPHA)
        center = (size + 5, size + 5)
        
        for r in range(size, 0, -1):
            ratio = r / size
            current_alpha = int(alpha * ratio * ratio)
            glow_color = color + (current_alpha,)
            pygame.draw.circle(surface, glow_color, center, r + 5)
        
        self.cache[cache_key] = surface
        return surface
    
    def draw_glow(self, surface: pygame.Surface, rect: pygame.Rect, 
                   color: Tuple[int, int, int], strength: int = 3):
        glow_size = max(rect.width, rect.height) // 4
        glow_surf = self.create_glow_surface(glow_size * strength, color, 60)
        
        dest_x = rect.centerx - glow_surf.get_width() // 2
        dest_y = rect.centery - glow_surf.get_height() // 2
        surface.blit(glow_surf, (dest_x, dest_y), special_flags=pygame.BLEND_ALPHA_SDL2)
