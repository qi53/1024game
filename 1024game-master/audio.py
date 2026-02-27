"""
1024 Game - 3D Audio System Module
Handles all sound effects and music with 3D positioning
"""

import pygame
import numpy as np
import os
import random
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum


class SoundType(Enum):
    """Types of game sounds"""
    MOVE = "move"
    MERGE = "merge"
    SPAWN = "spawn"
    WIN = "win"
    GAME_OVER = "game_over"
    MENU_SELECT = "menu_select"
    MENU_CONFIRM = "menu_confirm"
    MENU_BACK = "menu_back"
    LEVEL_COMPLETE = "level_complete"
    ACHIEVEMENT = "achievement"
    BUTTON_HOVER = "button_hover"


@dataclass
class SoundConfig:
    """Configuration for a sound effect"""
    base_frequency: float
    harmonics: list
    duration: float
    volume: float
    fade_out: bool = True


class SoundGenerator:
    """Generates procedural sound effects"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def generate_tone(
        self,
        frequency: float,
        duration: float,
        volume: float = 0.5,
        waveform: str = "sine",
        fade_out: bool = True
    ) -> np.ndarray:
        """Generate a tone with specified parameters"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        if waveform == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif waveform == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == "sawtooth":
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif waveform == "triangle":
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope
        if fade_out:
            envelope = np.exp(-3 * t / duration)
            wave *= envelope
        
        # Apply volume
        wave *= volume
        
        # Convert to 16-bit integer
        wave = (wave * 32767).astype(np.int16)
        
        return wave
    
    def generate_chord(
        self,
        frequencies: list,
        duration: float,
        volume: float = 0.5
    ) -> np.ndarray:
        """Generate a chord from multiple frequencies"""
        samples = int(self.sample_rate * duration)
        combined = np.zeros(samples)
        
        for freq in frequencies:
            wave = self.generate_tone(freq, duration, volume / len(frequencies), fade_out=True)
            combined += wave.astype(np.float64)
        
        # Normalize
        max_val = np.max(np.abs(combined))
        if max_val > 0:
            combined = (combined / max_val * 32767 * volume).astype(np.int16)
        
        return combined.astype(np.int16)
    
    def generate_slide(
        self,
        start_freq: float,
        end_freq: float,
        duration: float,
        volume: float = 0.5
    ) -> np.ndarray:
        """Generate a frequency slide effect"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Exponential frequency sweep
        freq = start_freq * np.exp(np.log(end_freq / start_freq) * t / duration)
        
        # Generate wave with varying frequency
        phase = np.cumsum(2 * np.pi * freq / self.sample_rate)
        wave = np.sin(phase)
        
        # Apply envelope
        envelope = np.exp(-3 * t / duration)
        wave *= envelope
        wave *= volume
        
        return (wave * 32767).astype(np.int16)
    
    def generate_noise(
        self,
        duration: float,
        volume: float = 0.3,
        filter_freq: Optional[float] = None
    ) -> np.ndarray:
        """Generate filtered noise"""
        samples = int(self.sample_rate * duration)
        noise = np.random.uniform(-1, 1, samples)
        
        if filter_freq:
            # Simple low-pass filter
            alpha = filter_freq / self.sample_rate
            filtered = np.zeros_like(noise)
            filtered[0] = noise[0]
            for i in range(1, samples):
                filtered[i] = alpha * noise[i] + (1 - alpha) * filtered[i - 1]
            noise = filtered
        
        # Apply envelope
        t = np.linspace(0, duration, samples, False)
        envelope = np.exp(-5 * t / duration)
        noise *= envelope
        noise *= volume
        
        return (noise * 32767).astype(np.int16)
    
    def create_stereo(
        self,
        mono_sound: np.ndarray,
        pan: float = 0.5
    ) -> np.ndarray:
        """Convert mono sound to stereo with panning"""
        # Pan: 0 = left, 0.5 = center, 1 = right
        left_vol = np.cos(pan * np.pi / 2)
        right_vol = np.sin(pan * np.pi / 2)
        
        stereo = np.zeros((len(mono_sound), 2), dtype=np.int16)
        stereo[:, 0] = (mono_sound * left_vol).astype(np.int16)
        stereo[:, 1] = (mono_sound * right_vol).astype(np.int16)
        
        return stereo


class AudioManager:
    """Manages all game audio"""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.generator = SoundGenerator()
        self.sounds: Dict[SoundType, pygame.mixer.Sound] = {}
        self.music_enabled = True
        self.sfx_enabled = True
        self.master_volume = 0.7
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        self._generate_sounds()
    
    def _generate_sounds(self) -> None:
        """Generate all procedural sound effects"""
        # Move sound - soft click
        move_wave = self.generator.generate_tone(800, 0.1, 0.3, "sine")
        self.sounds[SoundType.MOVE] = self._create_sound(move_wave)
        
        # Merge sound - ascending chord
        merge_wave = self.generator.generate_chord([440, 554, 659], 0.3, 0.4)
        self.sounds[SoundType.MERGE] = self._create_sound(merge_wave)
        
        # Spawn sound - pop
        spawn_wave = self.generator.generate_slide(600, 1200, 0.15, 0.3)
        self.sounds[SoundType.SPAWN] = self._create_sound(spawn_wave)
        
        # Win sound - triumphant fanfare
        win_wave = self.generator.generate_chord([523, 659, 784, 1047], 0.8, 0.5)
        self.sounds[SoundType.WIN] = self._create_sound(win_wave)
        
        # Game over sound - descending
        game_over_wave = self.generator.generate_slide(400, 100, 1.0, 0.4)
        self.sounds[SoundType.GAME_OVER] = self._create_sound(game_over_wave)
        
        # Menu sounds
        menu_select_wave = self.generator.generate_tone(1000, 0.05, 0.2, "sine")
        self.sounds[SoundType.MENU_SELECT] = self._create_sound(menu_select_wave)
        
        menu_confirm_wave = self.generator.generate_chord([880, 1100], 0.15, 0.3)
        self.sounds[SoundType.MENU_CONFIRM] = self._create_sound(menu_confirm_wave)
        
        menu_back_wave = self.generator.generate_slide(600, 400, 0.1, 0.2)
        self.sounds[SoundType.MENU_BACK] = self._create_sound(menu_back_wave)
        
        # Level complete - celebration
        level_wave = self.generator.generate_chord([523, 659, 784, 1047, 1319], 1.0, 0.5)
        self.sounds[SoundType.LEVEL_COMPLETE] = self._create_sound(level_wave)
        
        # Achievement - sparkle
        achievement_wave = self.generator.generate_chord([880, 1109, 1319, 1760], 0.6, 0.4)
        self.sounds[SoundType.ACHIEVEMENT] = self._create_sound(achievement_wave)
        
        # Button hover - subtle tick
        hover_wave = self.generator.generate_tone(2000, 0.03, 0.1, "sine")
        self.sounds[SoundType.BUTTON_HOVER] = self._create_sound(hover_wave)
    
    def _create_sound(self, wave_data: np.ndarray) -> pygame.mixer.Sound:
        """Create pygame Sound from numpy array"""
        # Ensure stereo
        if len(wave_data.shape) == 1:
            stereo = np.zeros((len(wave_data), 2), dtype=np.int16)
            stereo[:, 0] = wave_data
            stereo[:, 1] = wave_data
            wave_data = stereo
        
        return pygame.mixer.Sound(buffer=wave_data.tobytes())
    
    def play(
        self,
        sound_type: SoundType,
        position: Optional[Tuple[float, float]] = None,
        volume_multiplier: float = 1.0
    ) -> None:
        """Play a sound effect with optional 3D positioning"""
        if not self.sfx_enabled or sound_type not in self.sounds:
            return
        
        sound = self.sounds[sound_type]
        
        # Calculate volume based on position (simple 3D effect)
        if position:
            # Position is (x, y) in screen coordinates
            # Center of screen is (0.5, 0.5)
            screen_center_x = 0.5
            pan = max(0, min(1, position[0]))
            
            # Calculate stereo volume
            left_vol = np.cos(pan * np.pi / 2)
            right_vol = np.sin(pan * np.pi / 2)
            
            # Apply master and sfx volume
            base_volume = self.master_volume * self.sfx_volume * volume_multiplier
            sound.set_volume(base_volume)
        else:
            sound.set_volume(self.master_volume * self.sfx_volume * volume_multiplier)
        
        sound.play()
    
    def play_music(self, track_name: str) -> None:
        """Play background music (procedural)"""
        if not self.music_enabled:
            return
        
        # Generate ambient background music
        # This is a placeholder - in a full implementation,
        # you would generate or load actual music tracks
        pass
    
    def stop_music(self) -> None:
        """Stop background music"""
        pygame.mixer.music.stop()
    
    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_music(self) -> bool:
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        return self.music_enabled
    
    def toggle_sfx(self) -> bool:
        """Toggle sound effects on/off"""
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled
    
    def get_volume_settings(self) -> Dict[str, float]:
        """Get current volume settings"""
        return {
            "master": self.master_volume,
            "music": self.music_volume,
            "sfx": self.sfx_volume,
        }
    
    def cleanup(self) -> None:
        """Clean up audio resources"""
        pygame.mixer.stop()
        for sound in self.sounds.values():
            sound.stop()
