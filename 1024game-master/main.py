#!/usr/bin/env python3
"""
1024 Game - Main Entry Point
A terminal-based 1024 number sliding game
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game
from ui import UI


def main():
    """Main game loop"""
    try:
        # Initialize game and UI
        game = Game()
        ui = UI()

        # Display welcome message
        ui.show_welcome()

        # Main game loop
        while True:
            # Draw current game state
            ui.draw_game(game)

            # Check game state
            if game.is_win():
                ui.show_win_message(game.score)
                break
            elif game.is_game_over():
                ui.show_game_over_message(game.score)
                break

            # Get user input
            move = ui.get_input()

            if move == 'quit':
                ui.show_quit_message()
                break
            elif move == 'restart':
                game.reset_game()
                continue

            # Process move
            if move in ['up', 'down', 'left', 'right']:
                if game.move(move):
                    # Move was successful, add new tile
                    game.add_random_tile()

        # Save high score before exit
        game.save_high_score()

    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
