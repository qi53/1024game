#!/usr/bin/env python3
"""
1024 Game - Animation System
Handles smooth animations for tiles and UI elements
"""

import pygame
import math
from typing import List, Dict, Any, Callable, Optional, Tuple
from src.constants import ANIMATION_TILE_MOVE, ANIMATION_TILE_APPEAR, ANIMATION_TILE_MERGE, ANIMATION_BUTTON_HOVER


class Animation:
    """Base class for animations"""
    
    def __init__(self, duration: float, easing: str = 'linear'):
        """Initialize animation"""
        self.duration = duration
        self.elapsed = 0.0
        self.easing = easing
        self.running = True
        self.complete = False
        
    def update(self, dt: float) -> bool:
        """Update animation progress"""
        if not self.running:
            return False
            
        self.elapsed += dt
        
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.complete = True
            self.running = False
            return True
            
        return False
        
    def get_progress(self) -> float:
        """Get animation progress (0.0 to 1.0)"""
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)
        
    def apply_easing(self, t: float) -> float:
        """Apply easing function to progress value"""
        if t <= 0:
            return 0
        elif t >= 1:
            return 1
            
        if self.easing == 'linear':
            return t
        elif self.easing == 'ease_in':
            return t * t
        elif self.easing == 'ease_out':
            return 1 - (1 - t) * (1 - t)
        elif self.easing == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif self.easing == 'bounce':
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:
            return t
            
    def is_complete(self) -> bool:
        """Check if animation is complete"""
        return self.complete
        
    def is_running(self) -> bool:
        """Check if animation is running"""
        return self.running
        
    def stop(self) -> None:
        """Stop the animation"""
        self.running = False
        
    def reset(self) -> None:
        """Reset the animation"""
        self.elapsed = 0.0
        self.complete = False
        self.running = True


class PositionAnimation(Animation):
    """Animation for position changes"""
    
    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                 duration: float, easing: str = 'ease_out'):
        """Initialize position animation"""
        super().__init__(duration, easing)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        
    def update(self, dt: float) -> bool:
        """Update position"""
        super().update(dt)
        
        progress = self.apply_easing(self.get_progress())
        
        self.current_pos = (
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress,
            self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        )
        
        return self.is_complete()
        
    def get_position(self) -> Tuple[float, float]:
        """Get current position"""
        return self.current_pos


class ScaleAnimation(Animation):
    """Animation for scale changes"""
    
    def __init__(self, start_scale: float, end_scale: float, 
                 duration: float, easing: str = 'ease_out'):
        """Initialize scale animation"""
        super().__init__(duration, easing)
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.current_scale = start_scale
        
    def update(self, dt: float) -> bool:
        """Update scale"""
        super().update(dt)
        
        progress = self.apply_easing(self.get_progress())
        
        self.current_scale = self.start_scale + (self.end_scale - self.start_scale) * progress
        
        return self.is_complete()
        
    def get_scale(self) -> float:
        """Get current scale"""
        return self.current_scale


class AlphaAnimation(Animation):
    """Animation for alpha/transparency changes"""
    
    def __init__(self, start_alpha: int, end_alpha: int, 
                 duration: float, easing: str = 'ease_out'):
        """Initialize alpha animation"""
        super().__init__(duration, easing)
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.current_alpha = start_alpha
        
    def update(self, dt: float) -> bool:
        """Update alpha"""
        super().update(dt)
        
        progress = self.apply_easing(self.get_progress())
        
        self.current_alpha = int(self.start_alpha + (self.end_alpha - self.start_alpha) * progress)
        
        return self.is_complete()
        
    def get_alpha(self) -> int:
        """Get current alpha"""
        return self.current_alpha


class RotationAnimation(Animation):
    """Animation for rotation changes"""
    
    def __init__(self, start_angle: float, end_angle: float, 
                 duration: float, easing: str = 'ease_out'):
        """Initialize rotation animation"""
        super().__init__(duration, easing)
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.current_angle = start_angle
        
    def update(self, dt: float) -> bool:
        """Update rotation"""
        super().update(dt)
        
        progress = self.apply_easing(self.get_progress())
        
        self.current_angle = self.start_angle + (self.end_angle - self.start_angle) * progress
        
        return self.is_complete()
        
    def get_angle(self) -> float:
        """Get current angle"""
        return self.current_angle


class CompositeAnimation(Animation):
    """Animation that combines multiple animations"""
    
    def __init__(self, animations: List[Animation], duration: float = None):
        """Initialize composite animation"""
        if duration is None:
            # Use the longest duration from child animations
            duration = max(anim.duration for anim in animations)
        super().__init__(duration)
        self.animations = animations
        
    def update(self, dt: float) -> bool:
        """Update all animations"""
        super().update(dt)
        
        all_complete = True
        for anim in self.animations:
            if anim.is_running():
                anim.update(dt)
                all_complete = False
                
        if all_complete:
            self.complete = True
            self.running = False
            
        return self.is_complete()


class AnimationSystem:
    """Manages all animations in the game"""
    
    def __init__(self):
        """Initialize the animation system"""
        self.animations: List[Animation] = []
        self.animation_queue: List[Animation] = []
        
    def add_animation(self, animation: Animation) -> None:
        """Add an animation to the system"""
        self.animations.append(animation)
        
    def queue_animation(self, animation: Animation) -> None:
        """Queue an animation to be added later"""
        self.animation_queue.append(animation)
        
    def remove_animation(self, animation: Animation) -> None:
        """Remove an animation from the system"""
        if animation in self.animations:
            self.animations.remove(animation)
            
    def clear_animations(self) -> None:
        """Clear all animations"""
        self.animations.clear()
        self.animation_queue.clear()
        
    def update(self, dt: float) -> None:
        """Update all animations"""
        # Add queued animations
        for animation in self.animation_queue:
            self.animations.append(animation)
        self.animation_queue.clear()
        
        # Update existing animations
        completed_animations = []
        for animation in self.animations:
            if animation.update(dt):
                completed_animations.append(animation)
                
        # Remove completed animations
        for animation in completed_animations:
            self.animations.remove(animation)
            
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all animations (if applicable)"""
        # Most animations don't directly draw, they just update properties
        # This method can be used for special effect animations
        pass
        
    def get_animation_count(self) -> int:
        """Get the current number of animations"""
        return len(self.animations)
        
    def create_tile_move_animation(self, start_pos: Tuple[float, float], 
                                  end_pos: Tuple[float, float]) -> PositionAnimation:
        """Create a tile move animation"""
        return PositionAnimation(start_pos, end_pos, ANIMATION_TILE_MOVE, 'ease_out')
        
    def create_tile_appear_animation(self, pos: Tuple[float, float]) -> CompositeAnimation:
        """Create a tile appear animation"""
        scale_anim = ScaleAnimation(0.0, 1.0, ANIMATION_TILE_APPEAR, 'bounce')
        alpha_anim = AlphaAnimation(0, 255, ANIMATION_TILE_APPEAR, 'ease_out')
        return CompositeAnimation([scale_anim, alpha_anim])
        
    def create_tile_merge_animation(self, pos: Tuple[float, float]) -> ScaleAnimation:
        """Create a tile merge animation"""
        return ScaleAnimation(1.0, 1.2, ANIMATION_TILE_MERGE / 2, 'ease_out')
        
    def create_button_hover_animation(self, start_scale: float = 1.0, 
                                    end_scale: float = 1.1) -> ScaleAnimation:
        """Create a button hover animation"""
        return ScaleAnimation(start_scale, end_scale, ANIMATION_BUTTON_HOVER, 'ease_out')
        
    def create_screen_transition_animation(self, duration: float = 0.5) -> AlphaAnimation:
        """Create a screen transition animation"""
        return AlphaAnimation(0, 255, duration, 'ease_in_out')
        
    def create_score_popup_animation(self, pos: Tuple[float, float]) -> CompositeAnimation:
        """Create a score popup animation"""
        pos_anim = PositionAnimation(pos, (pos[0], pos[1] - 50), 1.0, 'ease_out')
        alpha_anim = AlphaAnimation(255, 0, 1.0, 'ease_in')
        scale_anim = ScaleAnimation(1.0, 1.5, 0.5, 'ease_out')
        return CompositeAnimation([pos_anim, alpha_anim, scale_anim])