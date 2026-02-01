#!/usr/bin/env python3
"""
1024 Game - Particle System
Handles particle effects for visual enhancements
"""

import pygame
import random
import math
from typing import List, Tuple, Dict, Any
from src.constants import PARTICLE_COUNT, PARTICLE_LIFETIME, PARTICLE_SIZE_RANGE, PARTICLE_SPEED_RANGE


class Particle:
    """Represents a single particle"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 size: float, speed: float, direction: float, lifetime: float):
        """Initialize a particle"""
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.direction = direction
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = math.cos(direction) * speed
        self.vy = math.sin(direction) * speed
        self.gravity = 100  # Gravity effect
        self.alpha = 255  # Transparency

    def update(self, dt: float) -> bool:
        """Update particle position and properties"""
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Apply gravity
        self.vy += self.gravity * dt
        
        # Update lifetime
        self.lifetime -= dt
        
        # Update alpha based on lifetime
        if self.max_lifetime > 0:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Return False if particle should be removed
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the particle"""
        if self.alpha <= 0:
            return
        
        # Create a temporary surface for the particle with alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw the particle with alpha
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (int(self.size), int(self.size)), int(self.size))
        
        # Blit the particle to the main surface
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """Manages particle effects"""
    
    def __init__(self):
        """Initialize the particle system"""
        self.particles: List[Particle] = []
        self.effects_queue: List[Dict[str, Any]] = []
        
        # Predefined effect configurations
        self.effect_configs = {
            'tile_merge': {
                'count': 15,
                'colors': [(255, 215, 0), (255, 255, 0), (255, 165, 0)],
                'size_range': (2, 5),
                'speed_range': (100, 200),
                'lifetime': 0.8
            },
            'tile_spawn': {
                'count': 10,
                'colors': [(100, 200, 255), (150, 150, 255)],
                'size_range': (1, 3),
                'speed_range': (50, 100),
                'lifetime': 0.5
            },
            'win': {
                'count': 50,
                'colors': [(255, 215, 0), (255, 255, 0), (255, 165, 0), (255, 100, 0)],
                'size_range': (3, 8),
                'speed_range': (150, 300),
                'lifetime': 2.0
            },
            'lose': {
                'count': 30,
                'colors': [(100, 100, 100), (50, 50, 50)],
                'size_range': (2, 6),
                'speed_range': (100, 200),
                'lifetime': 1.5
            },
            'move': {
                'count': 5,
                'colors': [(200, 200, 200)],
                'size_range': (1, 2),
                'speed_range': (50, 100),
                'lifetime': 0.3
            },
            'level_complete': {
                'count': 40,
                'colors': [(0, 255, 0), (100, 255, 100), (150, 255, 150)],
                'size_range': (2, 6),
                'speed_range': (100, 250),
                'lifetime': 1.5
            }
        }

    def create_effect(self, effect_type: str, x: float, y: float, 
                     custom_config: Dict[str, Any] = None) -> None:
        """Create a particle effect at the specified position"""
        config = self.effect_configs.get(effect_type, self.effect_configs['move'])
        
        # Override with custom config if provided
        if custom_config:
            config = {**config, **custom_config}
        
        # Create particles
        for _ in range(config['count']):
            # Random position offset
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            
            # Random color from the config
            color = random.choice(config['colors'])
            
            # Random size
            size = random.uniform(*config['size_range'])
            
            # Random speed and direction
            speed = random.uniform(*config['speed_range'])
            direction = random.uniform(0, 2 * math.pi)
            
            # Random lifetime variation
            lifetime = config['lifetime'] * random.uniform(0.8, 1.2)
            
            # Create particle
            particle = Particle(
                x + offset_x, y + offset_y, color, size, speed, direction, lifetime
            )
            self.particles.append(particle)

    def create_tile_merge_effect(self, x: float, y: float, tile_value: int) -> None:
        """Create a particle effect for tile merging"""
        # Customize effect based on tile value
        intensity = min(1.0, tile_value / 1024)
        custom_config = {
            'count': int(10 + intensity * 20),
            'colors': self._get_tile_colors(tile_value),
            'size_range': (2 + intensity * 3, 5 + intensity * 5),
            'speed_range': (100 + intensity * 100, 200 + intensity * 200),
            'lifetime': 0.8 + intensity * 0.4
        }
        self.create_effect('tile_merge', x, y, custom_config)

    def create_tile_spawn_effect(self, x: float, y: float) -> None:
        """Create a particle effect for tile spawning"""
        self.create_effect('tile_spawn', x, y)

    def create_win_effect(self, x: float, y: float) -> None:
        """Create a particle effect for winning"""
        self.create_effect('win', x, y)

    def create_lose_effect(self, x: float, y: float) -> None:
        """Create a particle effect for losing"""
        self.create_effect('lose', x, y)

    def create_move_effect(self, x: float, y: float) -> None:
        """Create a particle effect for moving tiles"""
        self.create_effect('move', x, y)

    def create_level_complete_effect(self, x: float, y: float) -> None:
        """Create a particle effect for level completion"""
        self.create_effect('level_complete', x, y)

    def create_explosion(self, x: float, y: float, count: int = 30) -> None:
        """Create an explosion effect"""
        custom_config = {
            'count': count,
            'colors': [(255, random.randint(100, 255), 0) for _ in range(5)],
            'size_range': (2, 8),
            'speed_range': (200, 400),
            'lifetime': 1.0
        }
        self.create_effect('tile_merge', x, y, custom_config)

    def create_trail(self, x: float, y: float, direction: float, color: Tuple[int, int, int]) -> None:
        """Create a trail effect"""
        for i in range(5):
            offset = i * 10
            trail_x = x - math.cos(direction) * offset
            trail_y = y - math.sin(direction) * offset
            
            particle = Particle(
                trail_x, trail_y, color, 
                3 - i * 0.5, 50, direction, 0.3 - i * 0.05
            )
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        """Update all particles"""
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Process queued effects
        for effect in self.effects_queue[:]:
            self.create_effect(**effect)
            self.effects_queue.remove(effect)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)

    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
        self.effects_queue.clear()

    def get_particle_count(self) -> int:
        """Get the current number of particles"""
        return len(self.particles)

    def _get_tile_colors(self, tile_value: int) -> List[Tuple[int, int, int]]:
        """Get colors based on tile value"""
        if tile_value <= 4:
            return [(238, 228, 218), (237, 224, 200)]
        elif tile_value <= 16:
            return [(242, 177, 121), (245, 149, 99)]
        elif tile_value <= 64:
            return [(246, 124, 95), (246, 94, 59)]
        elif tile_value <= 256:
            return [(237, 207, 114), (237, 204, 97)]
        elif tile_value <= 1024:
            return [(237, 197, 63), (237, 194, 46)]
        else:
            return [(60, 58, 50), (100, 100, 100)]

    def queue_effect(self, effect_type: str, x: float, y: float, 
                    custom_config: Dict[str, Any] = None) -> None:
        """Queue an effect to be created in the next update"""
        effect_data = {
            'effect_type': effect_type,
            'x': x,
            'y': y,
            'custom_config': custom_config
        }
        self.effects_queue.append(effect_data)