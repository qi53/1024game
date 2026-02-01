#!/usr/bin/env python3
"""
1024 Game - Particle Effects System
Implements various particle effects for visual feedback
"""

import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

import pygame

from .config import MAX_PARTICLES, PARTICLE_LIFETIME


class ParticleType(Enum):
    MERGE = 1
    SPAWN = 2
    EXPLOSION = 3
    CONFETTI = 4
    TRAIL = 5
    STAR = 6


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: Tuple[int, int, int]
    type: ParticleType
    rotation: float = 0
    rotation_speed: float = 0
    gravity: float = 0.3
    drag: float = 0.98


class ParticleSystem:
    """Manages particle effects for visual feedback"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.enabled = True
    
    def spawn_merge_particles(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10):
        """Spawn particles when tiles merge"""
        if not self.enabled:
            return
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            self._add_particle(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=PARTICLE_LIFETIME,
                max_life=PARTICLE_LIFETIME,
                size=random.uniform(4, 8),
                color=color,
                type=ParticleType.MERGE,
                gravity=0.1,
                drag=0.95
            ))
    
    def spawn_spawn_particles(self, x: float, y: float, color: Tuple[int, int, int]):
        """Spawn particles when a new tile appears"""
        if not self.enabled:
            return
        
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self._add_particle(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=300,
                max_life=300,
                size=random.uniform(3, 6),
                color=color,
                type=ParticleType.SPAWN,
                gravity=0,
                drag=0.92
            ))
    
    def spawn_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 30):
        """Spawn explosion effect particles"""
        if not self.enabled:
            return
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 10)
            self._add_particle(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=600,
                max_life=600,
                size=random.uniform(3, 10),
                color=self._variate_color(color),
                type=ParticleType.EXPLOSION,
                gravity=0.2,
                drag=0.96
            ))
    
    def spawn_confetti(self, x: float, y: float, count: int = 50):
        """Spawn confetti particles for celebrations"""
        if not self.enabled:
            return
        
        colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255)
        ]
        
        for _ in range(count):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(5, 12)
            self._add_particle(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1500,
                max_life=1500,
                size=random.uniform(4, 8),
                color=random.choice(colors),
                type=ParticleType.CONFETTI,
                rotation=random.uniform(0, math.pi * 2),
                rotation_speed=random.uniform(-0.3, 0.3),
                gravity=0.15,
                drag=0.99
            ))
    
    def spawn_star_particles(self, x: float, y: float, count: int = 15):
        """Spawn star-shaped particles"""
        if not self.enabled:
            return
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            self._add_particle(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=800,
                max_life=800,
                size=random.uniform(2, 5),
                color=(255, 255, 200),
                type=ParticleType.STAR,
                gravity=0.05,
                drag=0.97
            ))
    
    def spawn_trail(self, x: float, y: float, color: Tuple[int, int, int]):
        """Spawn trail particles for moving objects"""
        if not self.enabled:
            return
        
        self._add_particle(Particle(
            x=x,
            y=y,
            vx=random.uniform(-0.5, 0.5),
            vy=random.uniform(-0.5, 0.5),
            life=200,
            max_life=200,
            size=random.uniform(2, 4),
            color=color,
            type=ParticleType.TRAIL,
            gravity=0,
            drag=0.95
        ))
    
    def _add_particle(self, particle: Particle):
        """Add a particle, removing old ones if at limit"""
        if len(self.particles) >= MAX_PARTICLES:
            self.particles.pop(0)
        self.particles.append(particle)
    
    def _variate_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Add slight variation to a color"""
        return (
            min(255, max(0, color[0] + random.randint(-20, 20))),
            min(255, max(0, color[1] + random.randint(-20, 20))),
            min(255, max(0, color[2] + random.randint(-20, 20)))
        )
    
    def update(self, delta_time: float):
        """Update all particles"""
        for particle in self.particles[:]:
            particle.life -= delta_time * 1000
            
            if particle.life <= 0:
                self.particles.remove(particle)
                continue
            
            particle.vy += particle.gravity
            particle.vx *= particle.drag
            particle.vy *= particle.drag
            particle.x += particle.vx
            particle.y += particle.vy
            particle.rotation += particle.rotation_speed
    
    def render(self, surface: pygame.Surface, offset: Tuple[int, int] = (0, 0)):
        """Render all particles"""
        for particle in self.particles:
            alpha = int((particle.life / particle.max_life) * 255)
            
            draw_x = int(particle.x + offset[0])
            draw_y = int(particle.y + offset[1])
            
            if particle.type == ParticleType.CONFETTI:
                self._draw_confetti(surface, particle, draw_x, draw_y, alpha)
            elif particle.type == ParticleType.STAR:
                self._draw_star(surface, particle, draw_x, draw_y, alpha)
            else:
                self._draw_circle_particle(surface, particle, draw_x, draw_y, alpha)
    
    def _draw_circle_particle(self, surface: pygame.Surface, particle: Particle, 
                               x: int, y: int, alpha: int):
        """Draw a circular particle"""
        size = int(particle.size * (particle.life / particle.max_life))
        if size < 1:
            return
        
        temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color = (*particle.color, alpha)
        pygame.draw.circle(temp_surface, color, (size, size), size)
        surface.blit(temp_surface, (x - size, y - size))
    
    def _draw_confetti(self, surface: pygame.Surface, particle: Particle,
                        x: int, y: int, alpha: int):
        """Draw a confetti particle"""
        size = int(particle.size)
        if size < 1:
            return
        
        temp_surface = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        color = (*particle.color, alpha)
        
        rotated = pygame.transform.rotate(temp_surface, math.degrees(particle.rotation))
        pygame.draw.rect(rotated, color, rotated.get_rect())
        surface.blit(rotated, (x - rotated.get_width() // 2, y - rotated.get_height() // 2))
    
    def _draw_star(self, surface: pygame.Surface, particle: Particle,
                    x: int, y: int, alpha: int):
        """Draw a star particle"""
        size = int(particle.size * (particle.life / particle.max_life))
        if size < 1:
            return
        
        color = (*particle.color, alpha)
        points = []
        for i in range(5):
            angle = i * math.pi * 2 / 5 - math.pi / 2
            outer_x = x + math.cos(angle) * size
            outer_y = y + math.sin(angle) * size
            points.append((outer_x, outer_y))
            
            inner_angle = angle + math.pi / 5
            inner_x = x + math.cos(inner_angle) * (size * 0.4)
            inner_y = y + math.sin(inner_angle) * (size * 0.4)
            points.append((inner_x, inner_y))
        
        temp_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        pygame.draw.polygon(temp_surface, color, [(p[0] - x + size * 1.5, p[1] - y + size * 1.5) for p in points])
        surface.blit(temp_surface, (x - size * 1.5, y - size * 1.5))
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable particles"""
        self.enabled = enabled
        if not enabled:
            self.clear()
    
    def get_particle_count(self) -> int:
        """Get current number of particles"""
        return len(self.particles)
