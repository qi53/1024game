#!/usr/bin/env python3
"""
1024 Game - Pygame GUI Version
Launch this file to run the pygame graphical version of 1024 game
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from src.pygame_main import main
    print("Starting 1024 Pygame Game...")
    main()
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Make sure all required files are in the src/ directory.")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nGame interrupted. Goodbye!")
    sys.exit(0)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
