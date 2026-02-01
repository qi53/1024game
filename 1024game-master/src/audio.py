#!/usr/bin/env python3
"""
1024 Game - 3D Audio System
Implements spatial audio with pygame.mixer
"""

import os
import math
from typing import Dict, Optional, Tuple
from threading import Lock

import pygame

from .config import ASSETS_DIR, SOUND_EFFECTS, MUSIC_TRACKS


class AudioManager:
    """3D Audio manager for spatial sound effects"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.channels: Dict[str, pygame.mixer.Channel] = {}
        
        self._master_volume = 0.8
        self._music_volume = 0.5
        self._sfx_volume = 0.7
        
        self.current_music: Optional[str] = None
        self.music_playing = False
        
        self.listener_position = (0, 0)
        self.sound_enabled = True
        
        self._create_sound_files()
        self._load_sounds()
    
    def _create_sound_files(self):
        """Create placeholder sound files if they don't exist"""
        import wave
        import struct
        
        sound_dir = os.path.join(ASSETS_DIR, 'sounds')
        music_dir = os.path.join(ASSETS_DIR, 'music')
        os.makedirs(sound_dir, exist_ok=True)
        os.makedirs(music_dir, exist_ok=True)
        
        for effect in SOUND_EFFECTS:
            filepath = os.path.join(sound_dir, f"{effect}.wav")
            if not os.path.exists(filepath):
                self._generate_sound_wave(filepath, effect)
        
        for track in MUSIC_TRACKS:
            filepath = os.path.join(music_dir, f"{track}.wav")
            if not os.path.exists(filepath):
                self._generate_music_track(filepath, track)
    
    def _generate_sound_wave(self, filepath: str, effect_type: str):
        """Generate simple sound waves for effects"""
        import wave
        import struct
        import math
        
        sample_rate = 44100
        duration = 0.2
        frequency = 440
        amplitude = 4000
        
        if effect_type == "merge":
            frequency = 660
            duration = 0.15
        elif effect_type == "level_complete":
            frequency = 880
            duration = 0.5
        elif effect_type == "game_over":
            frequency = 220
            duration = 0.4
        elif effect_type == "button_click":
            frequency = 500
            duration = 0.05
        elif effect_type == "achievement":
            frequency = 1000
            duration = 0.3
        elif effect_type == "countdown":
            frequency = 300
            duration = 0.1
        elif effect_type == "tutorial":
            frequency = 440
            duration = 0.2
        
        num_samples = int(sample_rate * duration)
        
        with wave.open(filepath, 'w') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            
            for i in range(num_samples):
                t = i / sample_rate
                envelope = 1.0 - (t / duration)
                value = int(amplitude * envelope * math.sin(2 * math.pi * frequency * t))
                
                left = value
                right = value
                
                data = struct.pack('<hh', left, right)
                wav.writeframesraw(data)
    
    def _generate_music_track(self, filepath: str, track_type: str):
        """Generate simple ambient music tracks"""
        import wave
        import struct
        import math
        
        sample_rate = 44100
        duration = 10.0
        
        if track_type == "menu_theme":
            base_freq = 220
        elif track_type == "game_theme":
            base_freq = 330
        elif track_type == "victory_theme":
            base_freq = 440
        else:
            base_freq = 220
        
        num_samples = int(sample_rate * duration)
        
        with wave.open(filepath, 'w') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            
            for i in range(num_samples):
                t = i / sample_rate
                envelope = 0.5 * (1.0 + math.sin(2 * math.pi * t / duration))
                
                freq_mod = 1.0 + 0.05 * math.sin(2 * math.pi * 0.5 * t)
                value = int(2000 * envelope * math.sin(2 * math.pi * base_freq * freq_mod * t))
                
                left = value
                right = value
                
                data = struct.pack('<hh', left, right)
                wav.writeframesraw(data)
    
    def _load_sounds(self):
        """Load all sound effects"""
        sound_dir = os.path.join(ASSETS_DIR, 'sounds')
        
        for effect in SOUND_EFFECTS:
            filepath = os.path.join(sound_dir, f"{effect}.wav")
            if os.path.exists(filepath):
                try:
                    self.sounds[effect] = pygame.mixer.Sound(filepath)
                except pygame.error:
                    pass
    
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self._master_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self._music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self._sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self._master_volume * self._sfx_volume)
    
    def play_sound(self, name: str, position: Optional[Tuple[float, float]] = None):
        """Play a sound effect with optional 3D positioning"""
        if not self.sound_enabled or name not in self.sounds:
            return
        
        channel = pygame.mixer.find_channel()
        if channel:
            sound = self.sounds[name]
            sound.set_volume(self._master_volume * self._sfx_volume)
            
            if position:
                left, right = self._calculate_stereo_pan(position)
                channel.set_volume(left, right)
            
            channel.play(sound)
    
    def play_sound_3d(self, name: str, source_position: Tuple[float, float]):
        """Play a sound with 3D spatial positioning"""
        if not self.sound_enabled or name not in self.sounds:
            return
        
        left, right = self._calculate_stereo_pan(source_position)
        
        channel = pygame.mixer.find_channel()
        if channel:
            sound = self.sounds[name]
            sound.set_volume(self._master_volume * self._sfx_volume)
            channel.set_volume(left, right)
            channel.play(sound)
    
    def _calculate_stereo_pan(self, source_position: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate left/right channel volumes based on 3D position"""
        dx = source_position[0] - self.listener_position[0]
        distance = math.sqrt(dx ** 2)
        
        max_distance = 500.0
        distance_attenuation = max(0.1, 1.0 - (distance / max_distance))
        
        pan = (source_position[0] / max_distance) if abs(dx) > 0 else 0
        pan = max(-1.0, min(1.0, pan))
        
        left = distance_attenuation * (0.5 - pan * 0.5)
        right = distance_attenuation * (0.5 + pan * 0.5)
        
        return left, right
    
    def play_music(self, track_name: str, loops: int = -1):
        """Play background music"""
        if not self.sound_enabled:
            return
        
        music_dir = os.path.join(ASSETS_DIR, 'music')
        filepath = os.path.join(music_dir, f"{track_name}.wav")
        
        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
                pygame.mixer.music.play(loops)
                self.current_music = track_name
                self.music_playing = True
            except pygame.error:
                pass
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.music_playing = False
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def fade_out_music(self, duration: int = 1000):
        """Fade out music over duration (ms)"""
        pygame.mixer.music.fadeout(duration)
    
    def set_listener_position(self, position: Tuple[float, float]):
        """Set the listener's position for 3D audio"""
        self.listener_position = position
    
    def play_merge_sound(self, position: Tuple[float, float]):
        """Play merge sound at position"""
        self.play_sound_3d("merge", position)
    
    def play_spawn_sound(self, position: Tuple[float, float]):
        """Play spawn sound at position"""
        self.play_sound_3d("spawn", position)
    
    def play_level_complete(self):
        """Play level complete sound"""
        self.play_sound("level_complete")
    
    def play_game_over(self):
        """Play game over sound"""
        self.play_sound("game_over")
    
    def play_click(self):
        """Play button click sound"""
        self.play_sound("button_click")
    
    def play_achievement(self):
        """Play achievement unlock sound"""
        self.play_sound("achievement")
    
    def play_countdown(self):
        """Play countdown tick sound"""
        self.play_sound("countdown")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all audio"""
        self.sound_enabled = enabled
        if not enabled:
            self.stop_music()
    
    def get_master_volume(self) -> float:
        """Get current master volume"""
        return self._master_volume
    
    def get_music_volume(self) -> float:
        """Get current music volume"""
        return self._music_volume
    
    def get_sfx_volume(self) -> float:
        """Get current SFX volume"""
        return self._sfx_volume
