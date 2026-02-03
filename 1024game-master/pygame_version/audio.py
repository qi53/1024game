"""
1024 Game - Pygame Version - 3D Audio System
3D音效系统，支持空间音效和多线程处理
"""

import pygame
import numpy as np
import threading
import queue
import math
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from config import SOUND_FREQUENCIES


@dataclass
class SoundRequest:
    """音效请求"""
    sound_type: str
    x: float = 0.5  # 0-1，声源位置
    y: float = 0.5
    volume: float = 1.0
    pitch: float = 1.0


class SoundGenerator:
    """音效生成器"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bit_depth = -16  # 16-bit signed
        self.channels = 2     # 立体声
    
    def generate_tone(self, frequency: float, duration: float, 
                     volume: float = 0.5, fade_in: float = 0.01,
                     fade_out: float = 0.05) -> pygame.mixer.Sound:
        """生成音调"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 生成正弦波
        wave = np.sin(2 * np.pi * frequency * t)
        
        # 应用ADSR包络
        envelope = np.ones(samples)
        
        # 淡入
        fade_in_samples = min(int(fade_in * self.sample_rate), samples)
        if fade_in_samples > 0:
            envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
        
        # 淡出
        fade_out_samples = min(int(fade_out * self.sample_rate), samples)
        if fade_out_samples > 0:
            envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)
        
        wave *= envelope * volume
        
        # 转换为16位整数
        audio = (wave * 32767).astype(np.int16)
        
        # 创建立体声
        stereo = np.column_stack((audio, audio))
        
        return pygame.mixer.Sound(buffer=stereo.tobytes())
    
    def generate_merge_sound(self, value: int) -> pygame.mixer.Sound:
        """根据合并数值生成音效"""
        # 数值越大，音调越高
        base_freq = SOUND_FREQUENCIES['merge']
        frequency = base_freq * (1 + math.log2(max(value, 2)) / 10)
        
        # 数值越大，音效越长
        duration = 0.1 + min(value / 2048, 0.3)
        
        return self.generate_tone(frequency, duration, volume=0.4)
    
    def generate_move_sound(self) -> pygame.mixer.Sound:
        """生成移动音效"""
        return self.generate_tone(
            SOUND_FREQUENCIES['move'], 
            0.05, 
            volume=0.2,
            fade_in=0.005,
            fade_out=0.02
        )
    
    def generate_spawn_sound(self) -> pygame.mixer.Sound:
        """生成新方块音效"""
        return self.generate_tone(
            SOUND_FREQUENCIES['spawn'],
            0.08,
            volume=0.3,
            fade_in=0.02,
            fade_out=0.03
        )
    
    def generate_win_sound(self) -> pygame.mixer.Sound:
        """生成胜利音效"""
        # 生成和弦
        frequencies = [440, 554, 659, 880]  # A大调和弦
        duration = 0.5
        samples = int(self.sample_rate * duration)
        
        wave = np.zeros(samples)
        for freq in frequencies:
            t = np.linspace(0, duration, samples, False)
            wave += np.sin(2 * np.pi * freq * t) * 0.25
        
        # 应用包络
        envelope = np.ones(samples)
        fade_in = int(0.1 * self.sample_rate)
        fade_out = int(0.2 * self.sample_rate)
        envelope[:fade_in] = np.linspace(0, 1, fade_in)
        envelope[-fade_out:] = np.linspace(1, 0, fade_out)
        
        wave *= envelope * 0.4
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        
        return pygame.mixer.Sound(buffer=stereo.tobytes())
    
    def generate_lose_sound(self) -> pygame.mixer.Sound:
        """生成失败音效"""
        frequencies = [440, 349, 330, 262]  # 下降音阶
        duration = 0.3
        samples_per_note = int(self.sample_rate * duration / len(frequencies))
        
        audio = np.array([], dtype=np.int16)
        
        for freq in frequencies:
            t = np.linspace(0, duration / len(frequencies), samples_per_note, False)
            wave = np.sin(2 * np.pi * freq * t)
            envelope = np.linspace(0.3, 0, samples_per_note)
            wave *= envelope
            note = (wave * 32767).astype(np.int16)
            audio = np.concatenate([audio, note])
        
        stereo = np.column_stack((audio, audio))
        return pygame.mixer.Sound(buffer=stereo.tobytes())
    
    def generate_button_sound(self) -> pygame.mixer.Sound:
        """生成按钮音效"""
        return self.generate_tone(
            SOUND_FREQUENCIES['button'],
            0.03,
            volume=0.15
        )
    
    def generate_achievement_sound(self) -> pygame.mixer.Sound:
        """生成成就解锁音效"""
        frequencies = [523, 659, 784, 1047]  # C大调上升
        duration = 0.4
        samples_per_note = int(self.sample_rate * duration / len(frequencies))
        
        audio = np.array([], dtype=np.int16)
        
        for i, freq in enumerate(frequencies):
            t = np.linspace(0, duration / len(frequencies), samples_per_note, False)
            wave = np.sin(2 * np.pi * freq * t)
            # 每个音符音量递增
            envelope = np.linspace(0.2, 0.4, samples_per_note)
            wave *= envelope
            note = (wave * 32767).astype(np.int16)
            audio = np.concatenate([audio, note])
        
        stereo = np.column_stack((audio, audio))
        return pygame.mixer.Sound(buffer=stereo.tobytes())


class AudioManager:
    """3D音效管理器"""
    
    def __init__(self):
        self.initialized = False
        self.generator = SoundGenerator()
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_queue: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self._audio_thread: Optional[threading.Thread] = None
        self._running = False
        
        # 音量设置
        self.master_volume = 1.0
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # 3D音效参数
        self.listener_pos = (0.5, 0.5)  # 听者位置（屏幕中心）
        self.max_distance = 1.0  # 最大距离
        
        # 缓存
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
    
    def initialize(self) -> bool:
        """初始化音频系统"""
        try:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512
            )
            self.initialized = True
            self._preload_sounds()
            self.start()
            return True
        except pygame.error as e:
            print(f"音频初始化失败: {e}")
            return False
    
    def _preload_sounds(self) -> None:
        """预加载音效"""
        self._sound_cache['move'] = self.generator.generate_move_sound()
        self._sound_cache['spawn'] = self.generator.generate_spawn_sound()
        self._sound_cache['win'] = self.generator.generate_win_sound()
        self._sound_cache['lose'] = self.generator.generate_lose_sound()
        self._sound_cache['button'] = self.generator.generate_button_sound()
        self._sound_cache['achievement'] = self.generator.generate_achievement_sound()
    
    def start(self) -> None:
        """启动音频线程"""
        self._running = True
        self._audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self._audio_thread.start()
    
    def stop(self) -> None:
        """停止音频线程"""
        self._running = False
        if self._audio_thread:
            self._audio_thread.join(timeout=0.5)
    
    def _audio_loop(self) -> None:
        """音频处理循环"""
        while self._running:
            try:
                request = self.sound_queue.get(timeout=0.1)
                self._play_sound(request)
            except queue.Empty:
                continue
    
    def _calculate_3d_volume(self, x: float, y: float, base_volume: float) -> Tuple[float, float]:
        """
        计算3D音量
        返回: (左声道音量, 右声道音量)
        """
        # 计算距离
        dx = x - self.listener_pos[0]
        dy = y - self.listener_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 距离衰减
        attenuation = max(0, 1 - distance / self.max_distance)
        volume = base_volume * attenuation * self.sfx_volume * self.master_volume
        
        # 声像（左右声道平衡）
        pan = (x - self.listener_pos[0]) / self.max_distance
        pan = max(-1, min(1, pan))  # 限制在-1到1之间
        
        left_volume = volume * (1 - pan) / 2
        right_volume = volume * (1 + pan) / 2
        
        return left_volume, right_volume
    
    def _play_sound(self, request: SoundRequest) -> None:
        """播放音效"""
        if not self.initialized:
            return
        
        with self.lock:
            sound = self._get_sound(request.sound_type)
            if sound:
                # 计算3D音量
                left_vol, right_vol = self._calculate_3d_volume(
                    request.x, request.y, request.volume
                )
                
                # 设置音量
                avg_volume = (left_vol + right_vol) / 2
                sound.set_volume(avg_volume)
                
                # 播放
                channel = sound.play()
                if channel:
                    # 设置立体声平衡
                    channel.set_volume(left_vol / avg_volume if avg_volume > 0 else 0,
                                     right_vol / avg_volume if avg_volume > 0 else 0)
    
    def _get_sound(self, sound_type: str) -> Optional[pygame.mixer.Sound]:
        """获取音效"""
        if sound_type in self._sound_cache:
            return self._sound_cache[sound_type]
        
        if sound_type.startswith('merge_'):
            # 动态生成合并音效
            try:
                value = int(sound_type.split('_')[1])
                return self.generator.generate_merge_sound(value)
            except (ValueError, IndexError):
                return self._sound_cache.get('move')
        
        return None
    
    def play(self, sound_type: str, x: float = 0.5, y: float = 0.5, 
             volume: float = 1.0) -> None:
        """
        播放音效
        
        Args:
            sound_type: 音效类型
            x: 声源x位置 (0-1)
            y: 声源y位置 (0-1)
            volume: 音量倍数
        """
        request = SoundRequest(sound_type, x, y, volume)
        self.sound_queue.put(request)
    
    def play_merge(self, value: int, x: float = 0.5, y: float = 0.5) -> None:
        """播放合并音效"""
        self.play(f'merge_{value}', x, y)
    
    def play_move(self, x: float = 0.5, y: float = 0.5) -> None:
        """播放移动音效"""
        self.play('move', x, y, volume=0.5)
    
    def play_spawn(self, x: float = 0.5, y: float = 0.5) -> None:
        """播放生成音效"""
        self.play('spawn', x, y)
    
    def play_win(self) -> None:
        """播放胜利音效"""
        self.play('win', volume=0.8)
    
    def play_lose(self) -> None:
        """播放失败音效"""
        self.play('lose', volume=0.8)
    
    def play_button(self) -> None:
        """播放按钮音效"""
        self.play('button', volume=0.6)
    
    def play_achievement(self) -> None:
        """播放成就音效"""
        self.play('achievement', volume=0.8)
    
    def set_master_volume(self, volume: float) -> None:
        """设置主音量"""
        self.master_volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        """设置音效音量"""
        self.sfx_volume = max(0, min(1, volume))
    
    def set_music_volume(self, volume: float) -> None:
        """设置音乐音量"""
        self.music_volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def get_volumes(self) -> Tuple[float, float, float]:
        """获取当前音量设置"""
        return self.master_volume, self.sfx_volume, self.music_volume
    
    def pause(self) -> None:
        """暂停所有音效"""
        if self.initialized:
            pygame.mixer.pause()
    
    def resume(self) -> None:
        """恢复所有音效"""
        if self.initialized:
            pygame.mixer.unpause()
    
    def stop_all(self) -> None:
        """停止所有音效"""
        if self.initialized:
            pygame.mixer.stop()
    
    def cleanup(self) -> None:
        """清理资源"""
        self.stop()
        self.stop_all()
        if self.initialized:
            pygame.mixer.quit()
            self.initialized = False
