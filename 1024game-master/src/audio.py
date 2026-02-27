import pygame
import threading
import math
import array
import os
from typing import Dict, Optional, Tuple
from .storage import GameData


class AudioManager:
    _instance: Optional['AudioManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'AudioManager':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self._music_volume = 0.7
        self._sfx_volume = 0.8
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._listener_pos: Tuple[float, float, float] = (0, 0, 0)
        self._game_data: Optional[GameData] = None
        self._mixer_initialized = False
        self._music_thread: Optional[threading.Thread] = None
        self._music_playing = False
    
    def initialize(self, game_data: GameData = None):
        self._game_data = game_data
        if game_data:
            self._music_volume = game_data.get_setting('music_volume', 70) / 100.0
            self._sfx_volume = game_data.get_setting('sfx_volume', 80) / 100.0
        
        if not self._mixer_initialized:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
                pygame.mixer.set_num_channels(16)
                self._mixer_initialized = True
            except pygame.error:
                pass
        
        self._generate_sounds()
    
    def _generate_sounds(self):
        sound_params = {
            'move': (440, 0.1, 'sine'),
            'merge': (523, 0.15, 'sine'),
            'merge_big': (659, 0.2, 'sine'),
            'win': (523, 0.3, 'sine'),
            'lose': (200, 0.4, 'sine'),
            'click': (800, 0.05, 'square'),
            'pop': (700, 0.08, 'sine'),
            'achievement': (784, 0.25, 'sine'),
        }
        
        for name, (freq, dur, wave) in sound_params.items():
            sound = self._create_tone(freq, dur, wave)
            if sound:
                sound.set_volume(self._sfx_volume)
                self._sounds[name] = sound
    
    def _create_tone(self, frequency: float, duration: float, wave_type: str = 'sine') -> Optional[pygame.mixer.Sound]:
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            amplitude = 4096
            
            samples = array.array('h')
            
            for i in range(n_samples):
                t = float(i) / sample_rate
                phase = 2 * math.pi * frequency * t
                
                if wave_type == 'sine':
                    raw_value = math.sin(phase)
                elif wave_type == 'square':
                    raw_value = 1.0 if math.sin(phase) > 0 else -1.0
                elif wave_type == 'triangle':
                    saw = 2 * (t * frequency - int(t * frequency + 0.5))
                    raw_value = 2 * abs(saw) - 1
                elif wave_type == 'sawtooth':
                    raw_value = 2 * (t * frequency - int(t * frequency + 0.5))
                else:
                    raw_value = math.sin(phase)
                
                attack = min(i / (n_samples * 0.1), 1.0)
                decay_start = n_samples * 0.9
                if i > decay_start:
                    decay = 1.0 - (i - decay_start) / (n_samples * 0.1)
                else:
                    decay = 1.0
                envelope = min(attack, max(decay, 0.0))
                
                value = int(amplitude * raw_value * envelope)
                samples.append(value)
            
            sound_bytes = samples.tobytes()
            return pygame.mixer.Sound(buffer=sound_bytes)
        except Exception:
            return None
    
    def play_sound(self, name: str, position: Optional[Tuple[float, float]] = None):
        if name not in self._sounds:
            return
        
        sound = self._sounds[name]
        channel = sound.play()
        
        if channel and position:
            self._apply_3d_effect(channel, position)
    
    def _apply_3d_effect(self, channel, position: Tuple[float, float]):
        try:
            dx = position[0] - self._listener_pos[0]
            dy = position[1] - self._listener_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            max_distance = 1000.0
            
            volume = max(0.1, 1.0 - min(distance / max_distance, 1.0))
            pan = max(-1.0, min(dx / 500.0, 1.0))
            
            left_volume = volume * (0.5 - pan * 0.5)
            right_volume = volume * (0.5 + pan * 0.5)
            
            channel.set_volume(left_volume, right_volume)
        except Exception:
            pass
    
    def set_listener_position(self, x: float, y: float, z: float = 0):
        self._listener_pos = (x, y, z)
    
    def play_music_loop(self):
        if not self._mixer_initialized:
            return
        
        self._music_playing = True
        
        def music_thread_func():
            import time
            melody = [523, 587, 659, 698, 784, 698, 659, 587]
            note_duration = 0.5
            
            while self._music_playing:
                for freq in melody:
                    if not self._music_playing:
                        break
                    note = self._create_tone(freq * 0.25, note_duration * 0.9, 'sine')
                    if note:
                        note.set_volume(self._music_volume * 0.15)
                        note.play()
                    time.sleep(note_duration)
        
        self._music_thread = threading.Thread(target=music_thread_func, daemon=True)
        self._music_thread.start()
    
    def stop_music(self):
        self._music_playing = False
        if self._mixer_initialized:
            pygame.mixer.stop()
    
    def set_music_volume(self, volume: int):
        self._music_volume = volume / 100.0
        if self._game_data:
            self._game_data.set_setting('music_volume', volume)
    
    def set_sfx_volume(self, volume: int):
        self._sfx_volume = volume / 100.0
        for sound in self._sounds.values():
            sound.set_volume(self._sfx_volume)
        if self._game_data:
            self._game_data.set_setting('sfx_volume', volume)
    
    def play_merge_sound(self, merge_value: int, position: Optional[Tuple[float, float]] = None):
        if merge_value >= 128:
            self.play_sound('merge_big', position)
        else:
            self.play_sound('merge', position)
    
    def play_move_sound(self, position: Optional[Tuple[float, float]] = None):
        self.play_sound('move', position)
    
    def play_win_sound(self):
        self.play_sound('win')
    
    def play_lose_sound(self):
        self.play_sound('lose')
    
    def play_click_sound(self):
        self.play_sound('click')
    
    def play_achievement_sound(self):
        self.play_sound('achievement')
    
    def play_pop_sound(self, position: Optional[Tuple[float, float]] = None):
        self.play_sound('pop', position)
    
    def cleanup(self):
        self.stop_music()
        if self._mixer_initialized:
            pygame.mixer.quit()
