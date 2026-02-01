#!/usr/bin/env python3
"""
1024 Game - pygame Graphics Edition
A complete 20-level game with advanced features
"""

from .config import *
from .storage import GameStorage
from .engine import GameEngine, ThreadSafeState
from .particles import ParticleSystem, ParticleType
from .audio import AudioManager
from .game_core import GameCore, MoveResult
from .ui import Button, Slider, Toggle, Tile, ProgressBar, StarDisplay

__version__ = "1.0.0"
__all__ = [
    'GameStorage',
    'GameEngine',
    'ThreadSafeState',
    'ParticleSystem',
    'ParticleType',
    'AudioManager',
    'GameCore',
    'MoveResult',
    'Button',
    'Slider',
    'Toggle',
    'Tile',
    'ProgressBar',
    'StarDisplay',
]
