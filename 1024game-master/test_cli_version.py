#!/usr/bin/env python3
"""
1024 Game - Command Line Version
A simple command line version to test game logic
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game
from src.level_manager import LevelManager

def print_grid(game):
    """Print the game grid"""
    print("\n" + "="*25)
    print(f"Score: {game.score} | Moves: {game.moves} | Level: {game.level}")
    print("="*25)
    for row in game.grid:
        print("|", end="")
        for cell in row:
            if cell == 0:
                print("    |", end="")
            else:
                print(f"{cell:4} |", end="")
        print("\n" + "-"*25)
    print()

def get_move():
    """Get user input for move"""
    while True:
        move = input("Enter move (w/a/s/d for up/left/down/right, q to quit): ").lower()
        if move in ['w', 'a', 's', 'd', 'q']:
            return move
        print("Invalid input. Please try again.")

def main():
    """Main function for command line version"""
    print("Welcome to 1024 Game - Command Line Version!")
    print("Combine tiles with the same number to reach 1024!")
    print("Controls: w (up), a (left), s (down), d (right), q (quit)")
    
    # Initialize game
    game = Game()
    level_manager = LevelManager()
    
    # Set level based on user choice
    try:
        level = int(input(f"Select level (1-{len(level_manager.level_data)}): "))
        if 1 <= level <= len(level_manager.level_data):
            level_data = level_manager.get_level_data(level)
            game.set_level(level_data['settings'])
            print(f"Level {level} selected. Win value: {game.win_value}")
        else:
            print("Invalid level. Using level 1.")
    except ValueError:
        print("Invalid input. Using level 1.")
    
    # Add initial tiles
    game.add_random_tile()
    game.add_random_tile()
    
    # Game loop
    while True:
        print_grid(game)
        
        # Check win/lose conditions
        if game.is_win():
            print(f"Congratulations! You reached {game.win_value}!")
            print(f"Final score: {game.score} | Moves: {game.moves}")
            break
        elif game.is_game_over():
            print("Game Over! No more moves available.")
            print(f"Final score: {game.score} | Moves: {game.moves}")
            break
        
        # Get user input
        move = get_move()
        
        if move == 'q':
            print("Quitting game...")
            print(f"Final score: {game.score} | Moves: {game.moves}")
            break
        
        # Convert move to game direction
        direction_map = {'w': 'up', 'a': 'left', 's': 'down', 'd': 'right'}
        direction = direction_map[move]
        
        # Make move
        moved = game.move(direction)
        if moved:
            game.add_random_tile()
        else:
            print("Invalid move! Try a different direction.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()