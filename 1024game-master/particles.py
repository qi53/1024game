"""
1024 Game - Particle System Module
Handles all visual particle effects
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Particle:
    """Individual particle data"""
    x: float
    y: float
    vx: float
    vy: float
    lifetime: int
    max_lifetime: int
    size: float
    color: Tuple[int, int, int]
    alpha: int = 255
    
    @property
    def is_alive(self) -> bool:
        return self.lifetime > 0
    
    def update(self) -> None:
        """Update particle state"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.lifetime -= 1
        
        # Fade out
        progress = 1 - (self.lifetime / self.max_lifetime)
        self.alpha = int(255 * (1 - progress))
        self.size = max(1, self.size * 0.98)


class ParticleSystem:
    """Manages all particle effects"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.emitters: List['ParticleEmitter'] = []
    
    def update(self) -> None:
        """Update all particles"""
        # Update individual particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive:
                self.particles.remove(particle)
        
        # Update emitters
        for emitter in self.emitters[:]:
            emitter.update()
            if emitter.is_finished:
                self.emitters.remove(emitter)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles"""
        for particle in self.particles:
            if particle.alpha > 0:
                color_with_alpha = (*particle.color, particle.alpha)
                
                # Create a surface with per-pixel alpha
                temp_surface = pygame.Surface(
                    (int(particle.size * 2), int(particle.size * 2)),
                    pygame.SRCALPHA
                )
                
                pygame.draw.circle(
                    temp_surface,
                    color_with_alpha,
                    (int(particle.size), int(particle.size)),
                    int(particle.size)
                )
                
                surface.blit(
                    temp_surface,
                    (int(particle.x - particle.size), int(particle.y - particle.size))
                )
        
        for emitter in self.emitters:
            emitter.draw(surface)
    
    def spawn_explosion(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 20,
        speed: float = 5.0,
        size: float = 8.0
    ) -> None:
        """Create explosion effect at position"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            
            particle = Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                lifetime=random.randint(30, 60),
                max_lifetime=60,
                size=random.uniform(size * 0.5, size),
                color=color,
                alpha=255
            )
            self.particles.append(particle)
    
    def spawn_merge_effect(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        value: int
    ) -> None:
        """Create merge celebration effect"""
        # Main explosion
        self.spawn_explosion(x, y, color, count=30, speed=8.0, size=10.0)
        
        # Sparkles
        for _ in range(10):
            sparkle_color = (255, 255, 200) if value >= 1024 else (255, 255, 255)
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 50)
            sx = x + math.cos(angle) * distance
            sy = y + math.sin(angle) * distance
            self.spawn_explosion(sx, sy, sparkle_color, count=5, speed=3.0, size=4.0)
    
    def spawn_tile_spawn(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int]
    ) -> None:
        """Create tile spawn effect"""
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(1.0, 3.0)
            vx = math.cos(angle) * velocity
            vy = math.sin(angle) * velocity
            
            particle = Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                lifetime=random.randint(20, 40),
                max_lifetime=40,
                size=random.uniform(3, 6),
                color=color,
                alpha=200
            )
            self.particles.append(particle)
    
    def spawn_level_complete(
        self,
        x: float,
        y: float
    ) -> None:
        """Create level completion celebration"""
        colors = [
            (255, 215, 0),   # Gold
            (255, 100, 100), # Red
            (100, 255, 100), # Green
            (100, 100, 255), # Blue
            (255, 255, 100), # Yellow
        ]
        
        for i, color in enumerate(colors):
            angle = (i / len(colors)) * 2 * math.pi
            for j in range(5):
                distance = 30 + j * 20
                px = x + math.cos(angle) * distance
                py = y + math.sin(angle) * distance
                self.spawn_explosion(px, py, color, count=15, speed=6.0, size=6.0)
    
    def spawn_trail(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        intensity: float = 1.0
    ) -> None:
        """Create motion trail effect"""
        if random.random() < 0.3 * intensity:
            particle = Particle(
                x=x + random.uniform(-5, 5),
                y=y + random.uniform(-5, 5),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-0.5, 0.5),
                lifetime=random.randint(10, 25),
                max_lifetime=25,
                size=random.uniform(2, 4) * intensity,
                color=color,
                alpha=150
            )
            self.particles.append(particle)
    
    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
        self.emitters.clear()


class ParticleEmitter:
    """Continuous particle emitter"""
    
    def __init__(
        self,
        x: float,
        y: float,
        emission_rate: float,
        duration: int,
        color: Tuple[int, int, int]
    ):
        self.x = x
        self.y = y
        self.emission_rate = emission_rate
        self.duration = duration
        self.color = color
        self.timer = 0
        self.emission_timer = 0
        self.particles: List[Particle] = []
    
    @property
    def is_finished(self) -> bool:
        return self.duration <= 0 and len(self.particles) == 0
    
    def update(self) -> None:
        """Update emitter"""
        self.duration -= 1
        self.timer += 1
        
        # Emit new particles
        if self.duration > 0:
            self.emission_timer += self.emission_rate
            while self.emission_timer >= 1:
                self.emission_timer -= 1
                self._emit_particle()
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive:
                self.particles.remove(particle)
    
    def _emit_particle(self) -> None:
        """Emit a single particle"""
        angle = random.uniform(0, 2 * math.pi)
        velocity = random.uniform(0.5, 2.0)
        vx = math.cos(angle) * velocity
        vy = math.sin(angle) * velocity
        
        particle = Particle(
            x=self.x + random.uniform(-10, 10),
            y=self.y + random.uniform(-10, 10),
            vx=vx,
            vy=vy,
            lifetime=random.randint(20, 40),
            max_lifetime=40,
            size=random.uniform(2, 5),
            color=self.color,
            alpha=200
        )
        self.particles.append(particle)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw emitter particles"""
        for particle in self.particles:
            if particle.alpha > 0:
                color_with_alpha = (*particle.color, particle.alpha)
                temp_surface = pygame.Surface(
                    (int(particle.size * 2), int(particle.size * 2)),
                    pygame.SRCALPHA
                )
                pygame.draw.circle(
                    temp_surface,
                    color_with_alpha,
                    (int(particle.size), int(particle.size)),
                    int(particle.size)
                )
                surface.blit(
                    temp_surface,
                    (int(particle.x - particle.size), int(particle.y - particle.size))
                )
