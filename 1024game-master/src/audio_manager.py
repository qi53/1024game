#!/usr/bin/env python3
"""
1024 Game - Audio Manager
Handles 3D sound effects and background music
"""

import pygame
import pygame.mixer
import math
import os
import random
from typing import Dict, List, Optional, Tuple
from src.constants import SFX_VOLUME, MUSIC_VOLUME, AUDIO_CHANNELS


class Sound3D:
    """Represents a 3D positioned sound"""
    
    def __init__(self, sound: pygame.mixer.Sound, x: float = 0, y: float = 0, z: float = 0):
        """Initialize 3D sound"""
        self.sound = sound
        self.x = x
        self.y = y
        self.z = z
        self.base_volume = 1.0
        self.max_distance = 500  # Maximum distance for sound attenuation
        
    def set_position(self, x: float, y: float, z: float = 0) -> None:
        """Set the 3D position of the sound"""
        self.x = x
        self.y = y
        self.z = z
        
    def calculate_volume(self, listener_x: float = 0, listener_y: float = 0, 
                        listener_z: float = 0) -> float:
        """Calculate volume based on distance from listener"""
        # Calculate distance
        dx = self.x - listener_x
        dy = self.y - listener_y
        dz = self.z - listener_z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Calculate volume based on distance (inverse square law)
        if distance >= self.max_distance:
            return 0.0
            
        # Volume decreases with distance
        volume = self.base_volume * (1.0 - (distance / self.max_distance))
        return max(0.0, min(1.0, volume))
        
    def calculate_pan(self, listener_x: float = 0, listener_y: float = 0) -> float:
        """Calculate stereo panning based on position relative to listener"""
        # Calculate horizontal distance
        dx = self.x - listener_x
        dy = self.y - listener_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:
            return 0.0  # Centered
            
        # Calculate pan (-1.0 for left, 1.0 for right)
        pan = dx / distance
        return max(-1.0, min(1.0, pan))
        
    def play(self, listener_x: float = 0, listener_y: float = 0, 
            listener_z: float = 0, volume_multiplier: float = 1.0) -> None:
        """Play the sound with 3D positioning"""
        # Calculate volume and pan
        volume = self.calculate_volume(listener_x, listener_y, listener_z) * volume_multiplier
        pan = self.calculate_pan(listener_x, listener_y)
        
        if volume <= 0:
            return
            
        # Set volume
        self.sound.set_volume(volume)
        
        # For true 3D sound, we would need a more advanced audio library
        # For now, we'll simulate it with volume and basic panning
        self.sound.play()


class AudioManager:
    """Manages all audio in the game"""
    
    def __init__(self):
        """Initialize the audio manager"""
        # Initialize mixer with more channels for better sound management
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        
        # Sound storage
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: List[str] = []
        
        # 3D sounds
        self.sounds_3d: Dict[str, Sound3D] = {}
        
        # Audio settings
        self.master_volume = 1.0
        self.sfx_volume = SFX_VOLUME
        self.music_volume = MUSIC_VOLUME
        self.sfx_enabled = True
        self.music_enabled = True
        
        # Listener position (for 3D audio)
        self.listener_x = 0
        self.listener_y = 0
        self.listener_z = 0
        
        # Current music
        self.current_music = None
        self.music_position = 0
        
        # Load sounds
        self._load_sounds()
        
        # Load music
        self._load_music()
        
    def _load_sounds(self) -> None:
        """Load all sound effects"""
        # Since we don't have actual audio files, we'll create placeholder sounds
        # In a real implementation, these would load from files
        
        # Create placeholder sounds using pygame's sound generation
        try:
            # Generate simple sounds programmatically
            self.sounds['move'] = self._generate_beep(frequency=440, duration=50)
            self.sounds['merge'] = self._generate_beep(frequency=880, duration=100)
            self.sounds['spawn'] = self._generate_beep(frequency=660, duration=80)
            self.sounds['win'] = self._generate_beep(frequency=1320, duration=500)
            self.sounds['lose'] = self._generate_beep(frequency=220, duration=800)
            self.sounds['start'] = self._generate_beep(frequency=550, duration=200)
            self.sounds['restart'] = self._generate_beep(frequency=550, duration=150)
            self.sounds['undo'] = self._generate_beep(frequency=330, duration=100)
            self.sounds['button_click'] = self._generate_beep(frequency=440, duration=30)
            self.sounds['achievement'] = self._generate_beep(frequency=1760, duration=300)
            self.sounds['level_complete'] = self._generate_beep(frequency=990, duration=400)
            
            # Create 3D versions of some sounds
            for name in ['move', 'merge', 'spawn']:
                if name in self.sounds:
                    self.sounds_3d[name] = Sound3D(self.sounds[name])
                    
        except Exception as e:
            print(f"Error loading sounds: {e}")
            
    def _load_music(self) -> None:
        """Load background music tracks"""
        # Since we don't have actual music files, we'll create placeholder tracks
        # In a real implementation, these would load from files
        try:
            # Generate simple background music
            self.music_tracks = ['background1', 'background2', 'background3']
        except Exception as e:
            print(f"Error loading music: {e}")
            
    def _generate_beep(self, frequency: int, duration: int) -> pygame.mixer.Sound:
        """Generate a simple beep sound"""
        sample_rate = 22050
        samples = int(sample_rate * duration / 1000)
        
        # Generate sine wave
        waves = [int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate)) 
                for i in range(samples)]
        
        # Apply envelope to avoid clicks
        envelope_length = min(samples // 10, 100)
        for i in range(envelope_length):
            waves[i] = int(waves[i] * i / envelope_length)
            waves[-(i+1)] = int(waves[-(i+1)] * i / envelope_length)
            
        # Create stereo sound
        stereo_waves = []
        for sample in waves:
            # Convert signed 16-bit integer to two bytes (little-endian)
            byte1 = sample & 0xFF
            byte2 = (sample >> 8) & 0xFF
            stereo_waves.extend([byte1, byte2, byte1, byte2])  # Left and right channels
            
        # Create sound from bytes
        sound_bytes = bytes(stereo_waves)
        sound = pygame.mixer.Sound(buffer=sound_bytes)
        
        return sound
        
    def play_sfx(self, name: str, x: float = None, y: float = None, z: float = 0) -> None:
        """Play a sound effect"""
        if not self.sfx_enabled or name not in self.sounds:
            return
            
        # If position is provided, use 3D sound
        if x is not None and y is not None and name in self.sounds_3d:
            sound_3d = self.sounds_3d[name]
            sound_3d.set_position(x, y, z)
            sound_3d.play(self.listener_x, self.listener_y, self.listener_z, self.sfx_volume)
        else:
            # Play regular 2D sound
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play()
            
    def play_sfx_3d(self, name: str, x: float, y: float, z: float = 0) -> None:
        """Play a 3D positioned sound effect"""
        if not self.sfx_enabled or name not in self.sounds_3d:
            return
            
        sound_3d = self.sounds_3d[name]
        sound_3d.set_position(x, y, z)
        sound_3d.play(self.listener_x, self.listener_y, self.listener_z, self.sfx_volume)
        
    def play_background_music(self, track_name: str = None) -> None:
        """Play background music"""
        if not self.music_enabled:
            return
            
        # Select a random track if none specified
        if track_name is None:
            track_name = random.choice(self.music_tracks) if self.music_tracks else None
            
        if track_name is None:
            return
            
        # In a real implementation, this would load and play the music file
        # For now, we'll just set the current music
        self.current_music = track_name
        
        # Since we don't have actual music files, we'll generate a simple background track
        try:
            # Generate a simple background melody
            melody = self._generate_melody()
            
            # Create a sound from the melody
            if melody:
                pygame.mixer.music.load(melody)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
        except Exception as e:
            print(f"Error playing background music: {e}")
            
    def _generate_melody(self) -> Optional[str]:
        """Generate a simple melody for background music"""
        # This is a placeholder - in a real implementation, this would load a music file
        return None
        
    def stop_background_music(self) -> None:
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def pause_background_music(self) -> None:
        """Pause background music"""
        pygame.mixer.music.pause()
        
    def resume_background_music(self) -> None:
        """Resume background music"""
        if self.music_enabled:
            pygame.mixer.music.unpause()
            
    def set_listener_position(self, x: float, y: float, z: float = 0) -> None:
        """Set the listener position for 3D audio"""
        self.listener_x = x
        self.listener_y = y
        self.listener_z = z
        
    def set_volume(self, volume: float) -> None:
        """Set master volume"""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
        
    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def set_music_volume(self, volume: float) -> None:
        """Set music volume"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        
    def set_sfx_enabled(self, enabled: bool) -> None:
        """Enable or disable sound effects"""
        self.sfx_enabled = enabled
        
    def set_music_enabled(self, enabled: bool) -> None:
        """Enable or disable music"""
        self.music_enabled = enabled
        if not enabled:
            self.stop_background_music()
            
    def _update_volumes(self) -> None:
        """Update all volumes based on master volume"""
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        
    def get_volume(self) -> float:
        """Get master volume"""
        return self.master_volume
        
    def get_sfx_volume(self) -> float:
        """Get sound effects volume"""
        return self.sfx_volume
        
    def get_music_volume(self) -> float:
        """Get music volume"""
        return self.music_volume
        
    def is_sfx_enabled(self) -> bool:
        """Check if sound effects are enabled"""
        return self.sfx_enabled
        
    def is_music_enabled(self) -> bool:
        """Check if music is enabled"""
        return self.music_enabled
        
    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy() > 0
        
    def get_current_music(self) -> Optional[str]:
        """Get the currently playing music track"""
        return self.current_music