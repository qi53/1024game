#!/usr/bin/env python3
"""
1024 Game - Utility Functions
Contains helper functions for the game
"""

import os
import sys
from typing import Any, Optional


def get_data_dir() -> str:
    """Get the data directory path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def format_number(num: int) -> str:
    """Format number for display in grid"""
    if num == 0:
        return ""
    return str(num)


def is_valid_move_input(input_str: str) -> bool:
    """Check if input string is a valid move"""
    valid_inputs = ['w', 'a', 's', 'd', 'up', 'down', 'left', 'right']
    return input_str.lower() in valid_inputs


def normalize_direction(direction: str) -> Optional[str]:
    """Normalize direction input to standard format"""
    direction = direction.lower().strip()

    direction_map = {
        'w': 'up',
        's': 'down',
        'a': 'left',
        'd': 'right',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right'
    }

    return direction_map.get(direction)


def safe_int_convert(value: Any, default: int = 0) -> int:
    """Safely convert value to int with default fallback"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def read_file_safe(file_path: str, default: str = "") -> str:
    """Safely read file content with default fallback"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except (IOError, OSError):
        return default


def write_file_safe(file_path: str, content: str) -> bool:
    """Safely write content to file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except (IOError, OSError):
        return False


def get_terminal_size() -> tuple:
    """Get terminal size (rows, columns)"""
    try:
        size = os.get_terminal_size()
        return size.lines, size.columns
    except OSError:
        # Default fallback
        return 24, 80


def center_text(text: str, width: int) -> str:
    """Center text within given width"""
    return text.center(width)


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def is_python_version_supported() -> bool:
    """Check if current Python version is supported"""
    return sys.version_info >= (3, 8)


def get_python_version() -> str:
    """Get current Python version string"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def validate_grid(grid: list) -> bool:
    """Validate grid structure and content"""
    if not isinstance(grid, list) or len(grid) != 4:
        return False

    for row in grid:
        if not isinstance(row, list) or len(row) != 4:
            return False
        for cell in row:
            if not isinstance(cell, int) or cell < 0:
                return False

    return True


def deep_copy_grid(grid: list) -> list:
    """Create a deep copy of the grid"""
    return [row[:] for row in grid]


def grid_to_string(grid: list) -> str:
    """Convert grid to string representation for debugging"""
    lines = []
    for row in grid:
        line = " ".join(f"{cell:4d}" if cell != 0 else "    " for cell in row)
        lines.append(line)
    return "\n".join(lines)
