#!/usr/bin/env python3
"""
1024 Game - Pygame Edition Launcher
Run this file to start the pygame version of the game
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pygame_main import main

if __name__ == "__main__":
    main()
