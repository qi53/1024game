#!/usr/bin/env python3
"""
1024 Game - Particle System
Contains particle effects for visual feedback
"""

import random
import math
from typing import List, Tuple, Optional
from enum import Enum


class ParticleType(Enum):
    """Types of particles"""
    MERGE = "merge"
    SPAWN = "spawn"
    WIN = "win"
    GAME_OVER = "game_over"
    COMBO = "combo"
    LEVEL_UP = "level_up"


class Particle:
    """Single particle class"""
    
    def __init__(self, x: float, y: float, particle_type: ParticleType, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.type = particle_type
        self.color = color
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.size = random.uniform(3, 8)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        self.gravity = 0.1
        
        if particle_type == ParticleType.MERGE:
            self.vx *= 1.5
            self.vy *= 1.5
            self.decay = 0.02
        elif particle_type == ParticleType.SPAWN:
            self.vx *= 0.5
            self.vy *= 0.5
            self.decay = 0.025
        elif particle_type == ParticleType.WIN:
            self.vx *= 2
            self.vy *= 2
            self.decay = 0.005
            self.gravity = -0.05
        elif particle_type == ParticleType.COMBO:
            self.vx *= 2
            self.vy *= 2
            self.decay = 0.015
            self.gravity = 0.05
    
    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay
        self.size *= 0.98
        return self.life > 0
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0):
        if self.life <= 0:
            return
        
        alpha = int(self.life * 255)
        color_with_alpha = (*self.color, alpha)
        
        size = max(1, int(self.size))
        pygame = __import__('pygame')
        
        if self.type == ParticleType.WIN:
            rect = pygame.Rect(
                int(self.x + offset_x - size),
                int(self.y + offset_y - size),
                size * 2,
                size * 2
            )
            pygame.draw.rect(surface, color_with_alpha, rect)
        else:
            pygame.draw.circle(
                surface,
                color_with_alpha,
                (int(self.x + offset_x), int(self.y + offset_y)),
                size
            )


class ParticleSystem:
    """Particle system manager"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 500
        self.enabled = True
    
    def emit(self, x: float, y: float, particle_type: ParticleType, 
             color: Optional[Tuple[int, int, int]] = None, count: int = 10):
        if not self.enabled:
            return
        
        if color is None:
            color = self._get_default_color(particle_type)
        
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                self.particles.pop(0)
            
            particle = Particle(x, y, particle_type, color)
            self.particles.append(particle)
    
    def emit_merge(self, x: float, y: float, value: int):
        colors = [
            (255, 255, 255),
            (255, 215, 0),
            (255, 165, 0),
            (255, 69, 0),
            (255, 0, 0)
        ]
        color_index = min(len(colors) - 1, int(math.log2(value)) - 1)
        color = colors[color_index]
        self.emit(x, y, ParticleType.MERGE, color, count=15)
    
    def emit_spawn(self, x: float, y: float):
        self.emit(x, y, ParticleType.SPAWN, (100, 200, 255), count=8)
    
    def emit_win(self, x: float, y: float):
        colors = [(255, 215, 0), (255, 255, 0), (255, 165, 0), (255, 69, 0)]
        color = random.choice(colors)
        self.emit(x, y, ParticleType.WIN, color, count=30)
    
    def emit_game_over(self, x: float, y: float):
        self.emit(x, y, ParticleType.GAME_OVER, (128, 128, 128), count=20)
    
    def emit_combo(self, x: float, y: float, combo_count: int):
        colors = [(255, 255, 0), (255, 200, 0), (255, 150, 0), (255, 100, 0)]
        color_index = min(len(colors) - 1, combo_count - 1)
        color = colors[color_index]
        count = min(25, 10 + combo_count * 2)
        self.emit(x, y, ParticleType.COMBO, color, count=count)
    
    def emit_level_up(self, x: float, y: float):
        colors = [(0, 255, 0), (50, 255, 50), (100, 255, 100), (150, 255, 150)]
        color = random.choice(colors)
        self.emit(x, y, ParticleType.LEVEL_UP, color, count=25)
    
    def emit_explosion(self, x: float, y: float, color: Tuple[int, int, int]):
        self.emit(x, y, ParticleType.MERGE, color, count=40)
    
    def emit_trail(self, x: float, y: float, color: Tuple[int, int, int]):
        if len(self.particles) >= self.max_particles:
            self.particles.pop(0)
        particle = Particle(x, y, ParticleType.SPAWN, color)
        particle.vx *= 0.3
        particle.vy *= 0.3
        particle.decay = 0.04
        particle.size = random.uniform(2, 4)
        self.particles.append(particle)
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0):
        for particle in self.particles:
            particle.draw(surface, offset_x, offset_y)
    
    def clear(self):
        self.particles.clear()
    
    def get_count(self) -> int:
        return len(self.particles)
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
    
    def _get_default_color(self, particle_type: ParticleType) -> Tuple[int, int, int]:
        colors = {
            ParticleType.MERGE: (255, 215, 0),
            ParticleType.SPAWN: (100, 200, 255),
            ParticleType.WIN: (255, 215, 0),
            ParticleType.GAME_OVER: (128, 128, 128),
            ParticleType.COMBO: (255, 165, 0),
            ParticleType.LEVEL_UP: (0, 255, 0)
        }
        return colors.get(particle_type, (255, 255, 255))


class TextParticle(Particle):
    """Text-based particle for floating numbers"""
    
    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int], size: int = 24):
        super().__init__(x, y, ParticleType.MERGE, color)
        self.text = text
        self.font_size = size
        self.vx = 0
        self.vy = -2
        self.gravity = 0
        self.decay = 0.015
        self.size = size
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0):
        if self.life <= 0:
            return
        
        pygame = __import__('pygame')
        font = pygame.font.Font(None, self.font_size)
        alpha = int(self.life * 255)
        
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        
        surface.blit(
            text_surface,
            (int(self.x + offset_x - text_surface.get_width() // 2),
             int(self.y + offset_y - text_surface.get_height() // 2))
        )


class FloatingTextManager:
    """Manager for floating text effects"""
    
    def __init__(self):
        self.texts: List[TextParticle] = []
        self.max_texts = 50
    
    def add_score(self, x: float, y: float, score: int):
        if score > 0:
            text = f"+{score}"
            color = (255, 215, 0) if score < 100 else (255, 100, 0)
            self._add_text(x, y, text, color, size=28)
    
    def add_combo(self, x: float, y: float, combo: int):
        text = f"COMBO x{combo}!"
        colors = [(255, 255, 0), (255, 200, 0), (255, 150, 0), (255, 100, 0)]
        color = colors[min(len(colors) - 1, combo - 1)]
        self._add_text(x, y, text, color, size=32)
    
    def add_message(self, x: float, y: float, message: str, color: Tuple[int, int, int]):
        self._add_text(x, y, message, color, size=24)
    
    def _add_text(self, x: float, y: float, text: str, color: Tuple[int, int, int], size: int = 24):
        if len(self.texts) >= self.max_texts:
            self.texts.pop(0)
        text_particle = TextParticle(x, y, text, color, size)
        self.texts.append(text_particle)
    
    def update(self):
        self.texts = [t for t in self.texts if t.update()]
    
    def draw(self, surface, offset_x: int = 0, offset_y: int = 0):
        for text in self.texts:
            text.draw(surface, offset_x, offset_y)
    
    def clear(self):
        self.texts.clear()
