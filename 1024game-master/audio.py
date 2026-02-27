#!/usr/bin/env python3
"""
1024 Game - Audio Manager with 3D Sound Effects
Contains audio system with spatial sound positioning
"""

import math
import threading
import wave
import struct
import os
from typing import Optional, Dict, Tuple
from enum import Enum
from io import BytesIO


class SoundType(Enum):
    """Types of sounds"""
    MOVE = "move"
    MERGE = "merge"
    SPAWN = "spawn"
    WIN = "win"
    GAME_OVER = "game_over"
    BUTTON_CLICK = "button_click"
    LEVEL_COMPLETE = "level_complete"
    ACHIEVEMENT = "achievement"
    COMBO = "combo"
    ERROR = "error"


class SoundGenerator:
    """Generate sound effects programmatically"""
    
    SAMPLE_RATE = 44100
    
    @classmethod
    def generate_tone(cls, frequency: float, duration: float, volume: float = 0.5,
                      wave_type: str = "sine") -> bytes:
        n_samples = int(cls.SAMPLE_RATE * duration)
        samples = []
        
        for i in range(n_samples):
            t = i / cls.SAMPLE_RATE
            
            if wave_type == "sine":
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == "square":
                value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == "triangle":
                value = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
            elif wave_type == "sawtooth":
                value = 2 * (t * frequency - math.floor(t * frequency)) - 1
            else:
                value = math.sin(2 * math.pi * frequency * t)
            
            envelope = 1.0
            attack = 0.01
            release = 0.1
            if t < attack:
                envelope = t / attack
            elif t > duration - release:
                envelope = (duration - t) / release
            
            sample = int(value * volume * envelope * 32767)
            sample = max(-32767, min(32767, sample))
            samples.append(sample)
        
        return struct.pack('<' + 'h' * len(samples), *samples)
    
    @classmethod
    def generate_merge_sound(cls, value: int) -> bytes:
        base_freq = 300 + min(value, 2048) / 4
        duration = 0.15
        
        tone1 = cls.generate_tone(base_freq, duration, 0.3, "sine")
        tone2 = cls.generate_tone(base_freq * 1.5, duration * 0.7, 0.2, "sine")
        
        combined = cls._mix_sounds(tone1, tone2, duration)
        return cls._create_wav(combined, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_move_sound(cls) -> bytes:
        duration = 0.08
        tone = cls.generate_tone(200, duration, 0.2, "sine")
        return cls._create_wav(tone, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_spawn_sound(cls) -> bytes:
        duration = 0.1
        tone = cls.generate_tone(400, duration, 0.15, "triangle")
        tone2 = cls.generate_tone(600, duration * 0.5, 0.1, "sine")
        combined = cls._mix_sounds(tone, tone2, duration)
        return cls._create_wav(combined, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_win_sound(cls) -> bytes:
        duration = 0.8
        notes = [523, 659, 784, 1047]
        
        samples = []
        note_duration = duration / len(notes)
        
        for freq in notes:
            tone = cls.generate_tone(freq, note_duration, 0.3, "sine")
            samples.extend(struct.unpack('<' + 'h' * (len(tone) // 2), tone))
        
        combined = struct.pack('<' + 'h' * len(samples), *samples)
        return cls._create_wav(combined, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_game_over_sound(cls) -> bytes:
        duration = 0.6
        tone = cls.generate_tone(200, duration, 0.3, "sawtooth")
        tone2 = cls.generate_tone(150, duration, 0.2, "sine")
        combined = cls._mix_sounds(tone, tone2, duration)
        return cls._create_wav(combined, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_button_click_sound(cls) -> bytes:
        duration = 0.05
        tone = cls.generate_tone(800, duration, 0.2, "sine")
        return cls._create_wav(tone, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_level_complete_sound(cls) -> bytes:
        duration = 0.5
        notes = [392, 523, 659, 784]
        
        samples = []
        note_duration = duration / len(notes)
        
        for freq in notes:
            tone = cls.generate_tone(freq, note_duration, 0.25, "sine")
            samples.extend(struct.unpack('<' + 'h' * (len(tone) // 2), tone))
        
        combined = struct.pack('<' + 'h' * len(samples), *samples)
        return cls._create_wav(combined, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_achievement_sound(cls) -> bytes:
        duration = 0.4
        tone1 = cls.generate_tone(880, duration, 0.25, "sine")
        tone2 = cls.generate_tone(1100, duration * 0.6, 0.2, "sine")
        combined = cls._mix_sounds(tone1, tone2, duration)
        return cls._create_wav(combined, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_combo_sound(cls, combo_count: int) -> bytes:
        base_freq = 400 + combo_count * 50
        duration = 0.12
        tone = cls.generate_tone(base_freq, duration, 0.25, "triangle")
        return cls._create_wav(tone, cls.SAMPLE_RATE)
    
    @classmethod
    def generate_error_sound(cls) -> bytes:
        duration = 0.15
        tone = cls.generate_tone(150, duration, 0.3, "square")
        return cls._create_wav(tone, cls.SAMPLE_RATE)
    
    @classmethod
    def _mix_sounds(cls, sound1: bytes, sound2: bytes, duration: float) -> bytes:
        samples1 = struct.unpack('<' + 'h' * (len(sound1) // 2), sound1)
        samples2 = struct.unpack('<' + 'h' * (len(sound2) // 2), sound2)
        
        max_len = max(len(samples1), len(samples2))
        mixed = []
        
        for i in range(max_len):
            s1 = samples1[i] if i < len(samples1) else 0
            s2 = samples2[i] if i < len(samples2) else 0
            mixed_sample = max(-32767, min(32767, (s1 + s2) // 2))
            mixed.append(mixed_sample)
        
        return struct.pack('<' + 'h' * len(mixed), *mixed)
    
    @classmethod
    def _create_wav(cls, samples: bytes, sample_rate: int) -> bytes:
        buffer = BytesIO()
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples)
        
        return buffer.getvalue()


class Sound3D:
    """3D positional sound"""
    
    def __init__(self, sound_data: bytes, x: float = 0, y: float = 0, 
                 listener_x: float = 0, listener_y: float = 0):
        self.sound_data = sound_data
        self.x = x
        self.y = y
        self.listener_x = listener_x
        self.listener_y = listener_y
    
    def calculate_volume_and_pan(self) -> Tuple[float, float]:
        dx = self.x - self.listener_x
        dy = self.y - self.listener_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        max_distance = 800
        min_volume = 0.1
        
        if distance >= max_distance:
            volume = min_volume
        else:
            volume = 1.0 - (distance / max_distance) * (1.0 - min_volume)
        
        pan = 0.5
        if abs(dx) > 10:
            pan = 0.5 + (dx / max_distance) * 0.4
            pan = max(0.1, min(0.9, pan))
        
        return volume, pan


class AudioManager:
    """Main audio manager with 3D sound support"""
    
    def __init__(self):
        self.enabled = True
        self.volume = 0.7
        self.sounds: Dict[SoundType, bytes] = {}
        self.sound_cache: Dict[str, bytes] = {}
        self.listener_position = (0, 0)
        self._pygame_mixer = None
        self._initialized = False
        self._lock = threading.Lock()
        
        self._initialize_pygame()
        self._generate_sounds()
    
    def _initialize_pygame(self):
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._pygame_mixer = pygame.mixer
            self._initialized = True
        except Exception:
            self._initialized = False
    
    def _generate_sounds(self):
        with self._lock:
            self.sounds[SoundType.MOVE] = SoundGenerator.generate_move_sound()
            self.sounds[SoundType.SPAWN] = SoundGenerator.generate_spawn_sound()
            self.sounds[SoundType.WIN] = SoundGenerator.generate_win_sound()
            self.sounds[SoundType.GAME_OVER] = SoundGenerator.generate_game_over_sound()
            self.sounds[SoundType.BUTTON_CLICK] = SoundGenerator.generate_button_click_sound()
            self.sounds[SoundType.LEVEL_COMPLETE] = SoundGenerator.generate_level_complete_sound()
            self.sounds[SoundType.ACHIEVEMENT] = SoundGenerator.generate_achievement_sound()
            self.sounds[SoundType.ERROR] = SoundGenerator.generate_error_sound()
    
    def play(self, sound_type: SoundType, x: float = None, y: float = None):
        if not self.enabled or not self._initialized:
            return
        
        with self._lock:
            sound_data = self.sounds.get(sound_type)
            if sound_data is None:
                return
            
            try:
                import pygame
                sound = pygame.mixer.Sound(buffer=sound_data)
                
                volume = self.volume
                if x is not None and y is not None:
                    sound_3d = Sound3D(sound_data, x, y, 
                                      self.listener_position[0], self.listener_position[1])
                    volume, _ = sound_3d.calculate_volume_and_pan()
                    volume *= self.volume
                
                sound.set_volume(volume)
                sound.play()
            except Exception:
                pass
    
    def play_merge(self, value: int, x: float = None, y: float = None):
        cache_key = f"merge_{value}"
        
        with self._lock:
            if cache_key not in self.sound_cache:
                self.sound_cache[cache_key] = SoundGenerator.generate_merge_sound(value)
            
            sound_data = self.sound_cache[cache_key]
        
        self._play_sound_data(sound_data, x, y)
    
    def play_combo(self, combo_count: int, x: float = None, y: float = None):
        cache_key = f"combo_{combo_count}"
        
        with self._lock:
            if cache_key not in self.sound_cache:
                self.sound_cache[cache_key] = SoundGenerator.generate_combo_sound(combo_count)
            
            sound_data = self.sound_cache[cache_key]
        
        self._play_sound_data(sound_data, x, y)
    
    def _play_sound_data(self, sound_data: bytes, x: float = None, y: float = None):
        if not self.enabled or not self._initialized:
            return
        
        try:
            import pygame
            sound = pygame.mixer.Sound(buffer=sound_data)
            
            volume = self.volume
            if x is not None and y is not None:
                sound_3d = Sound3D(sound_data, x, y,
                                  self.listener_position[0], self.listener_position[1])
                volume, _ = sound_3d.calculate_volume_and_pan()
                volume *= self.volume
            
            sound.set_volume(volume)
            sound.play()
        except Exception:
            pass
    
    def set_listener_position(self, x: float, y: float):
        self.listener_position = (x, y)
    
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
    
    def stop_all(self):
        if self._initialized and self._pygame_mixer:
            self._pygame_mixer.stop()
    
    def is_available(self) -> bool:
        return self._initialized
    
    def get_volume(self) -> float:
        return self.volume
    
    def is_enabled(self) -> bool:
        return self.enabled


class MusicManager:
    """Background music manager"""
    
    def __init__(self):
        self.enabled = True
        self.volume = 0.3
        self._pygame_mixer = None
        self._initialized = False
        self._playing = False
        
        self._initialize()
    
    def _initialize(self):
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self._pygame_mixer = pygame.mixer
            self._initialized = True
        except Exception:
            self._initialized = False
    
    def generate_background_music(self) -> bytes:
        duration = 8.0
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        samples = []
        base_freq = 220
        
        chord_progression = [
            [1.0, 1.25, 1.5],
            [1.0, 1.2, 1.5],
            [0.833, 1.0, 1.25],
            [0.75, 1.0, 1.5],
        ]
        
        chord_duration = duration / len(chord_progression)
        samples_per_chord = int(sample_rate * chord_duration)
        
        for chord in chord_progression:
            for i in range(samples_per_chord):
                t = i / sample_rate
                value = 0
                
                for ratio in chord:
                    freq = base_freq * ratio
                    value += math.sin(2 * math.pi * freq * t) * 0.2
                
                envelope = 0.3
                if t < 0.1:
                    envelope = t / 0.1 * 0.3
                elif t > chord_duration - 0.1:
                    envelope = (chord_duration - t) / 0.1 * 0.3
                
                sample = int(value * envelope * 32767)
                sample = max(-32767, min(32767, sample))
                samples.append(sample)
        
        samples_data = struct.pack('<' + 'h' * len(samples), *samples)
        return SoundGenerator._create_wav(samples_data, sample_rate)
    
    def play(self):
        if not self.enabled or not self._initialized or self._playing:
            return
        
        try:
            import pygame
            music_data = self.generate_background_music()
            
            temp_file = "/tmp/1024_bg_music.wav"
            with open(temp_file, 'wb') as f:
                f.write(music_data)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
            self._playing = True
        except Exception:
            pass
    
    def stop(self):
        if self._initialized and self._pygame_mixer:
            try:
                self._pygame_mixer.music.stop()
                self._playing = False
            except Exception:
                pass
    
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        if self._initialized and self._pygame_mixer:
            try:
                self._pygame_mixer.music.set_volume(self.volume)
            except Exception:
                pass
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.stop()
    
    def is_playing(self) -> bool:
        return self._playing
