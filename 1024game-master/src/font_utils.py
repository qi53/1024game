import pygame
import os
import sys
from typing import Optional

_FONT_CACHE = {}
_SYSTEM_FONT_PATH: Optional[str] = None

def _find_chinese_font() -> Optional[str]:
    if sys.platform == 'darwin':
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    elif sys.platform == 'win32':
        font_paths = [
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\simsun.ttc",
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    else:
        font_paths = [
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    return None

_SYSTEM_FONT_PATH = _find_chinese_font()

def get_font(size: int) -> pygame.font.Font:
    global _SYSTEM_FONT_PATH
    cache_key = (size, _SYSTEM_FONT_PATH)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]
    
    if _SYSTEM_FONT_PATH:
        try:
            font = pygame.font.Font(_SYSTEM_FONT_PATH, size)
            _FONT_CACHE[cache_key] = font
            return font
        except Exception:
            pass
    
    try:
        font = pygame.font.SysFont("Arial,Droid Sans,Helvetica", size)
        _FONT_CACHE[cache_key] = font
        return font
    except Exception:
        font = pygame.font.Font(None, size)
        _FONT_CACHE[cache_key] = font
        return font

def render_text(text: str, font: pygame.font.Font, color: tuple, background: tuple = None) -> pygame.Surface:
    try:
        if background:
            return font.render(text, True, color, background)
        return font.render(text, True, color)
    except Exception:
        return font.render(str(text), True, color)
