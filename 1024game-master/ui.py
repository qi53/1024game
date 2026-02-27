#!/usr/bin/env python3
"""
1024 Game - User Interface Module
Contains the UI class for terminal-based interface
"""

import os
import sys
from typing import Optional


class UI:
    """User Interface class for terminal display"""

    def __init__(self):
        """Initialize UI"""
        self.cell_width = 6  # Width of each cell
        self.cell_height = 3  # Height of each cell

    def clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_welcome(self) -> None:
        """Show welcome message"""
        self.clear_screen()
        print("=" * 50)
        print("           Welcome to 1024 Game!")
        print("=" * 50)
        print()
        print("Rules:")
        print("- Use WASD or Arrow Keys to move tiles")
        print("- Combine same numbers to reach 1024!")
        print("- Press Q to quit, R to restart")
        print()
        input("Press Enter to start...")

    def draw_game(self, game) -> None:
        """Draw the complete game interface"""
        self.clear_screen()
        self._draw_header()
        self._draw_grid(game.get_grid())
        self._draw_score(game.get_score(), game.get_high_score())
        self._draw_controls()

    def _draw_header(self) -> None:
        """Draw game header"""
        print("┌" + "─" * 48 + "┐")
        print("│" + " " * 48 + "│")
        print("│" + "           1024 Game".center(48) + "│")
        print("│" + " " * 48 + "│")
        print("└" + "─" * 48 + "┘")
        print()

    def _draw_grid(self, grid: list) -> None:
        """Draw the 4x4 game grid"""
        print("┌" + "─────┬" * 3 + "─────┐")

        for i, row in enumerate(grid):
            # Top line of cells
            line = "│"
            for cell in row:
                if cell == 0:
                    line += "     │"
                else:
                    line += f" {cell:4d} │"
            print(line)

            # Separator line (except after last row)
            if i < len(grid) - 1:
                print("├" + "─────┼" * 3 + "─────┤")
            else:
                print("└" + "─────┴" * 3 + "─────┘")

        print()

    def _draw_score(self, score: int, high_score: int) -> None:
        """Draw score information"""
        print("┌" + "─" * 48 + "┐")
        score_str = f"Score: {score}"
        high_score_str = f"High Score: {high_score}"
        total_len = len(score_str) + len(high_score_str) + 2
        padding = 48 - total_len
        left_padding = padding // 2
        right_padding = padding - left_padding

        print("│" + " " * left_padding + score_str + "  " + high_score_str + " " * right_padding + "│")
        print("└" + "─" * 48 + "┘")
        print()

    def _draw_controls(self) -> None:
        """Draw control instructions"""
        print("┌" + "─" * 48 + "┐")
        print("│" + " " * 48 + "│")
        print("│" + "         Controls:".ljust(48) + "│")
        print("│" + "         W/↑ - Move Up".ljust(48) + "│")
        print("│" + "         S/↓ - Move Down".ljust(48) + "│")
        print("│" + "         A/← - Move Left".ljust(48) + "│")
        print("│" + "         D/→ - Move Right".ljust(48) + "│")
        print("│" + "         Q - Quit Game".ljust(48) + "│")
        print("│" + "         R - Restart Game".ljust(48) + "│")
        print("│" + " " * 48 + "│")
        print("└" + "─" * 48 + "┘")

    def get_input(self) -> Optional[str]:
        """Get user input and return move direction"""
        try:
            key = input("Enter move (WASD or Q to quit): ").strip().lower()

            key_map = {
                'w': 'up',
                's': 'down',
                'a': 'left',
                'd': 'right',
                'q': 'quit',
                'r': 'restart'
            }

            return key_map.get(key)

        except (KeyboardInterrupt, EOFError):
            return 'quit'

    def show_win_message(self, score: int) -> None:
        """Show victory message"""
        self.clear_screen()
        print("🎉" * 25)
        print()
        print("           CONGRATULATIONS!")
        print("         You reached 1024!")
        print()
        print(f"         Final Score: {score}")
        print()
        print("🎉" * 25)
        input("\nPress Enter to exit...")

    def show_game_over_message(self, score: int) -> None:
        """Show game over message"""
        self.clear_screen()
        print("💀" * 25)
        print()
        print("           GAME OVER!")
        print("       No more moves available!")
        print()
        print(f"         Final Score: {score}")
        print()
        print("💀" * 25)
        input("\nPress Enter to exit...")

    def show_quit_message(self) -> None:
        """Show quit message"""
        print("\nThanks for playing 1024 Game!")
        print("Goodbye! 👋")

    def show_message(self, message: str) -> None:
        """Show a custom message"""
        print(f"\n{message}")

    def show_error(self, error: str) -> None:
        """Show error message"""
        print(f"\n❌ Error: {error}")

    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for an action"""
        try:
            response = input(f"{message} (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return False
