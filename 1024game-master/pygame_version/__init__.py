"""
1024 Game - Pygame Version
Pygame图形版1024游戏

功能特性：
- 20个关卡，每5关难度递增
- 60帧流畅运行
- 粒子特效系统
- 3D音效系统
- 多线程支持
- 完整UI系统（主菜单、关卡选择、设置、成就）
- 数据持久化
- 主题定制
- 教程系统
"""

__version__ = "2.0.0"
__author__ = "1024 Game Team"

from .main_game import MainGame, main

__all__ = ['MainGame', 'main']
