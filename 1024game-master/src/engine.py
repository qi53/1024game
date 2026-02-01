#!/usr/bin/env python3
"""
1024 Game - Game Engine with Multi-threading
Implements smooth 60FPS game loop with separate rendering thread
"""

import threading
import time
from typing import Callable, Optional
from queue import Queue

from .config import FPS


class GameEngine:
    """Multi-threaded game engine for smooth 60FPS performance"""
    
    def __init__(self):
        self.running = False
        self.paused = False
        self.fps = FPS
        self.frame_time = 1.0 / self.fps
        
        self.update_queue = Queue()
        self.render_queue = Queue()
        
        self.game_thread: Optional[threading.Thread] = None
        self.render_thread: Optional[threading.Thread] = None
        
        self.update_callback: Optional[Callable] = None
        self.render_callback: Optional[Callable] = None
        
        self.last_time = 0
        self.delta_time = 0
        self.frame_count = 0
        self.fps_counter = 0
        self.fps_timer = 0
        self.current_fps = 0
        
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_start_time = 0
    
    def set_update_callback(self, callback: Callable):
        """Set the update logic callback"""
        self.update_callback = callback
    
    def set_render_callback(self, callback: Callable):
        """Set the render callback"""
        self.render_callback = callback
    
    def start(self):
        """Start the game engine"""
        self.running = True
        self.paused = False
        self.last_time = time.time()
        
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
        
        self.game_thread.start()
        self.render_thread.start()
    
    def stop(self):
        """Stop the game engine"""
        self.running = False
        if self.game_thread:
            self.game_thread.join(timeout=1.0)
        if self.render_thread:
            self.render_thread.join(timeout=1.0)
    
    def pause(self):
        """Pause the game"""
        self.paused = True
    
    def resume(self):
        """Resume the game"""
        self.paused = False
        self.last_time = time.time()
    
    def _game_loop(self):
        """Main game update loop running in separate thread"""
        accumulator = 0
        
        while self.running:
            current_time = time.time()
            frame_time = current_time - self.last_time
            self.last_time = current_time
            
            if frame_time > 0.25:
                frame_time = 0.25
            
            self.delta_time = frame_time
            
            if not self.paused:
                accumulator += frame_time
                
                while accumulator >= self.frame_time:
                    if self.update_callback:
                        self.update_callback(self.frame_time)
                    accumulator -= self.frame_time
            
            time.sleep(0.001)
    
    def _render_loop(self):
        """Render loop running at fixed FPS in separate thread"""
        while self.running:
            start_time = time.time()
            
            if self.render_callback and not self.paused:
                self.render_callback()
            
            elapsed = time.time() - start_time
            sleep_time = self.frame_time - elapsed
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            self._update_fps_counter()
    
    def _update_fps_counter(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.fps_timer >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.fps_timer = current_time
    
    def get_current_fps(self) -> int:
        """Get current FPS"""
        return self.current_fps
    
    def get_delta_time(self) -> float:
        """Get delta time since last frame"""
        return self.delta_time
    
    def apply_screen_shake(self, intensity: float = 5.0, duration: float = 0.2):
        """Apply screen shake effect"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_start_time = time.time()
    
    def get_shake_offset(self) -> tuple:
        """Get current screen shake offset"""
        if self.shake_intensity <= 0:
            return (0, 0)
        
        elapsed = time.time() - self.shake_start_time
        if elapsed >= self.shake_duration:
            self.shake_intensity = 0
            return (0, 0)
        
        import random
        progress = 1 - (elapsed / self.shake_duration)
        intensity = self.shake_intensity * progress
        
        return (
            random.uniform(-intensity, intensity),
            random.uniform(-intensity, intensity)
        )
    
    def is_running(self) -> bool:
        """Check if engine is running"""
        return self.running
    
    def is_paused(self) -> bool:
        """Check if game is paused"""
        return self.paused


class ThreadSafeState:
    """Thread-safe game state container"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._state = {}
    
    def set(self, key: str, value):
        """Set a state value thread-safely"""
        with self._lock:
            self._state[key] = value
    
    def get(self, key: str, default=None):
        """Get a state value thread-safely"""
        with self._lock:
            return self._state.get(key, default)
    
    def update(self, data: dict):
        """Update multiple state values thread-safely"""
        with self._lock:
            self._state.update(data)
    
    def get_all(self) -> dict:
        """Get copy of all state"""
        with self._lock:
            return self._state.copy()
