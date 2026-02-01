#!/usr/bin/env python3
"""
1024 Game - Pygame Graphics Version
A feature-rich graphical implementation of the 1024 number sliding game
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()