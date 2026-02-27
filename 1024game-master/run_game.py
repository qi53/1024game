#!/usr/bin/env python3
"""
1024 Game Launcher
Simple launcher script for the 1024 game
"""

import sys
import os

def main():
    """Launch the 1024 game"""
    try:
        # Ensure we're in the correct directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        # Import and run the game
        from main import main as game_main
        game_main()

    except ImportError as e:
        print(f"Error importing game modules: {e}")
        print("Make sure all game files are in the same directory.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGame interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
