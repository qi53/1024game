#!/usr/bin/env python3
"""
1024 Game - Tutorial System
Handles game tutorial and instructions
"""

import pygame
from typing import Dict, List, Any, Tuple, Optional
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, TILE_SIZE, TILE_MARGIN
from src.ui_manager import Menu, Button


class Tutorial:
    """Represents a single tutorial slide"""
    
    def __init__(self, title: str, content: str, highlight_elements: List[str] = None,
                 custom_draw_func: callable = None):
        """Initialize a tutorial slide"""
        self.title = title
        self.content = content
        self.highlight_elements = highlight_elements or []
        self.custom_draw_func = custom_draw_func


class TutorialMenu(Menu):
    """Tutorial menu screen"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager):
        """Initialize the tutorial menu"""
        super().__init__(screen, theme_manager, audio_manager)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.content_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # Tutorial slides
        self.tutorials = self._create_tutorials()
        self.current_slide = 0
        
        # UI elements
        self.prev_button = Button(
            50, SCREEN_HEIGHT - 100, 100, 40,
            "Previous", self.content_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=self.prev_slide
        )
        
        self.next_button = Button(
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 100, 40,
            "Next", self.content_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=self.next_slide
        )
        
        self.skip_button = Button(
            SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 40,
            "Skip", self.content_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('main_menu')
        )
        
        # Demo game state for interactive tutorials
        self.demo_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.demo_score = 0
        self.demo_moves = 0
        
        # Initialize demo grid for certain slides
        self._init_demo_grid()
        
    def _create_tutorials(self) -> List[Tutorial]:
        """Create all tutorial slides"""
        tutorials = [
            Tutorial(
                "Welcome to 1024",
                "1024 is a puzzle game where you combine tiles to reach the number 1024.\n\n"
                "Use arrow keys or WASD to move tiles in four directions.\n"
                "When two tiles with the same number touch, they merge into one!\n\n"
                "Let's learn how to play.",
                [],
                self._draw_welcome_slide
            ),
            Tutorial(
                "Basic Movement",
                "Press the arrow keys or WASD to move all tiles in that direction.\n\n"
                "When you move, all tiles slide as far as possible in that direction.\n"
                "If two tiles with the same number collide, they merge into one with double the value.\n\n"
                "Try pressing the arrow keys to see how tiles move!",
                ["arrows", "wasd"],
                self._draw_movement_slide
            ),
            Tutorial(
                "Tile Merging",
                "When two tiles with the same number touch, they merge into one.\n\n"
                "The new tile has the sum of the two original tiles.\n"
                "For example: 2 + 2 = 4, 4 + 4 = 8, and so on.\n\n"
                "Your goal is to create a tile with the value 1024!",
                ["tiles"],
                self._draw_merging_slide
            ),
            Tutorial(
                "New Tiles",
                "After each move, a new tile randomly appears in an empty space.\n\n"
                "There's a 90% chance it will be a 2, and a 10% chance it will be a 4.\n\n"
                "The game ends when you can't make any more moves!",
                ["new_tiles"],
                self._draw_new_tiles_slide
            ),
            Tutorial(
                "Strategy Tips",
                "Here are some tips to help you succeed:\n\n"
                "1. Keep your highest value tile in a corner\n"
                "2. Build chains of decreasing values toward that corner\n"
                "3. Try to keep your options open\n"
                "4. Plan ahead before making moves\n\n"
                "Practice makes perfect!",
                [],
                self._draw_strategy_slide
            ),
            Tutorial(
                "Levels and Difficulty",
                "The game has 20 levels with increasing difficulty:\n\n"
                "• Levels 1-5: Easy - More space and time\n"
                "• Levels 6-10: Medium - Standard gameplay\n"
                "• Levels 11-15: Hard - Limited space\n"
                "• Levels 16-20: Expert - Maximum challenge\n\n"
                "Each level has different target scores and time limits!",
                [],
                self._draw_levels_slide
            ),
            Tutorial(
                "Features",
                "The game includes many features to enhance your experience:\n\n"
                "• Particle effects for visual feedback\n"
                "• 3D positional audio for immersive sound\n"
                "• Multiple themes to customize the look\n"
                "• Achievements to unlock\n"
                "• Statistics to track your progress\n"
                "• Settings to customize your experience",
                [],
                self._draw_features_slide
            ),
            Tutorial(
                "Ready to Play!",
                "You're now ready to start your 1024 journey!\n\n"
                "Remember:\n"
                "• Use arrow keys or WASD to move tiles\n"
                "• Combine tiles with the same number\n"
                "• Reach 1024 to win\n"
                "• Have fun!\n\n"
                "Good luck!",
                [],
                self._draw_ready_slide
            )
        ]
        
        return tutorials
        
    def _init_demo_grid(self) -> None:
        """Initialize demo grid for tutorials"""
        # Slide 2: Movement
        self.demo_grid[1][1] = 2
        self.demo_grid[2][2] = 4
        self.demo_grid[3][3] = 8
        
    def _draw_welcome_slide(self, surface: pygame.Surface) -> None:
        """Draw welcome slide"""
        # Draw 1024 logo
        logo_font = pygame.font.Font(None, 120)
        logo_text = logo_font.render("1024", True, self.theme_manager.get_color('text_dark'))
        logo_rect = logo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(logo_text, logo_rect)
        
        # Draw subtitle
        subtitle_text = self.content_font.render("A Puzzle Game", True, self.theme_manager.get_color('text_dark'))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        surface.blit(subtitle_text, subtitle_rect)
        
    def _draw_movement_slide(self, surface: pygame.Surface) -> None:
        """Draw movement slide with demo grid"""
        # Draw demo grid
        self._draw_demo_grid(surface)
        
        # Draw arrow key indicators
        arrow_size = 40
        arrow_color = self.theme_manager.get_color('button_hover')
        
        # Up arrow
        up_x = SCREEN_WIDTH // 2
        up_y = SCREEN_HEIGHT // 2 - 150
        pygame.draw.polygon(surface, arrow_color, [
            (up_x, up_y - arrow_size // 2),
            (up_x - arrow_size // 2, up_y + arrow_size // 2),
            (up_x + arrow_size // 2, up_y + arrow_size // 2)
        ])
        
        # Down arrow
        down_x = SCREEN_WIDTH // 2
        down_y = SCREEN_HEIGHT // 2 + 150
        pygame.draw.polygon(surface, arrow_color, [
            (down_x, down_y + arrow_size // 2),
            (down_x - arrow_size // 2, down_y - arrow_size // 2),
            (down_x + arrow_size // 2, down_y - arrow_size // 2)
        ])
        
        # Left arrow
        left_x = SCREEN_WIDTH // 2 - 150
        left_y = SCREEN_HEIGHT // 2
        pygame.draw.polygon(surface, arrow_color, [
            (left_x - arrow_size // 2, left_y),
            (left_x + arrow_size // 2, left_y - arrow_size // 2),
            (left_x + arrow_size // 2, left_y + arrow_size // 2)
        ])
        
        # Right arrow
        right_x = SCREEN_WIDTH // 2 + 150
        right_y = SCREEN_HEIGHT // 2
        pygame.draw.polygon(surface, arrow_color, [
            (right_x + arrow_size // 2, right_y),
            (right_x - arrow_size // 2, right_y - arrow_size // 2),
            (right_x - arrow_size // 2, right_y + arrow_size // 2)
        ])
        
        # Draw WASD labels
        wasd_font = pygame.font.Font(None, 24)
        wasd_labels = ["W", "A", "S", "D"]
        wasd_positions = [
            (up_x, up_y - arrow_size // 2 - 20),
            (left_x - arrow_size // 2 - 20, left_y),
            (down_x, down_y + arrow_size // 2 + 20),
            (right_x + arrow_size // 2 + 20, right_y)
        ]
        
        for label, pos in zip(wasd_labels, wasd_positions):
            label_text = wasd_font.render(label, True, self.theme_manager.get_color('text_dark'))
            label_rect = label_text.get_rect(center=pos)
            surface.blit(label_text, label_rect)
            
    def _draw_merging_slide(self, surface: pygame.Surface) -> None:
        """Draw merging slide with example"""
        # Draw merging example
        example_y = SCREEN_HEIGHT // 2 - 50
        
        # Draw two 4 tiles
        tile1_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, example_y, TILE_SIZE, TILE_SIZE)
        tile2_rect = pygame.Rect(SCREEN_WIDTH // 2 - 40, example_y, TILE_SIZE, TILE_SIZE)
        
        pygame.draw.rect(surface, self.theme_manager.get_tile_color(4), tile1_rect, border_radius=5)
        pygame.draw.rect(surface, self.theme_manager.get_tile_color(4), tile2_rect, border_radius=5)
        
        # Draw tile values
        tile_font = pygame.font.Font(None, 36)
        tile1_text = tile_font.render("4", True, self.theme_manager.get_tile_text_color(4))
        tile2_text = tile_font.render("4", True, self.theme_manager.get_tile_text_color(4))
        
        tile1_text_rect = tile1_text.get_rect(center=tile1_rect.center)
        tile2_text_rect = tile2_text.get_rect(center=tile2_rect.center)
        
        surface.blit(tile1_text, tile1_text_rect)
        surface.blit(tile2_text, tile2_text_rect)
        
        # Draw plus sign
        plus_text = tile_font.render("+", True, self.theme_manager.get_color('text_dark'))
        plus_rect = plus_text.get_rect(center=(SCREEN_WIDTH // 2 + 40, example_y + TILE_SIZE // 2))
        surface.blit(plus_text, plus_rect)
        
        # Draw equals sign
        equals_text = tile_font.render("=", True, self.theme_manager.get_color('text_dark'))
        equals_rect = equals_text.get_rect(center=(SCREEN_WIDTH // 2 + 120, example_y + TILE_SIZE // 2))
        surface.blit(equals_text, equals_rect)
        
        # Draw result tile
        result_rect = pygame.Rect(SCREEN_WIDTH // 2 + 160, example_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.theme_manager.get_tile_color(8), result_rect, border_radius=5)
        
        result_text = tile_font.render("8", True, self.theme_manager.get_tile_text_color(8))
        result_text_rect = result_text.get_rect(center=result_rect.center)
        surface.blit(result_text, result_text_rect)
        
    def _draw_new_tiles_slide(self, surface: pygame.Surface) -> None:
        """Draw new tiles slide with example"""
        # Draw grid with empty spaces
        grid_x = SCREEN_WIDTH // 2 - (GRID_SIZE * (TILE_SIZE + TILE_MARGIN)) // 2
        grid_y = SCREEN_HEIGHT // 2 - (GRID_SIZE * (TILE_SIZE + TILE_MARGIN)) // 2
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = grid_x + col * (TILE_SIZE + TILE_MARGIN)
                y = grid_y + row * (TILE_SIZE + TILE_MARGIN)
                
                # Draw empty cell
                cell_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, self.theme_manager.get_color('empty_cell'), cell_rect, border_radius=5)
                
        # Add some tiles
        tiles = [(1, 1, 2), (2, 2, 4), (3, 3, 8)]
        
        for row, col, value in tiles:
            x = grid_x + col * (TILE_SIZE + TILE_MARGIN)
            y = grid_y + row * (TILE_SIZE + TILE_MARGIN)
            
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, self.theme_manager.get_tile_color(value), tile_rect, border_radius=5)
            
            tile_font = pygame.font.Font(None, 36)
            tile_text = tile_font.render(str(value), True, self.theme_manager.get_tile_text_color(value))
            tile_text_rect = tile_text.get_rect(center=tile_rect.center)
            surface.blit(tile_text, tile_text_rect)
            
        # Draw new tile appearing
        new_tile_rect = pygame.Rect(grid_x + 3 * (TILE_SIZE + TILE_MARGIN), 
                                   grid_y + 1 * (TILE_SIZE + TILE_MARGIN), 
                                   TILE_SIZE, TILE_SIZE)
        
        # Pulsing effect for new tile
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        new_tile_color = tuple(int(c + (255 - c) * pulse) for c in self.theme_manager.get_tile_color(2))
        
        pygame.draw.rect(surface, new_tile_color, new_tile_rect, border_radius=5)
        
        tile_font = pygame.font.Font(None, 36)
        tile_text = tile_font.render("2", True, self.theme_manager.get_tile_text_color(2))
        tile_text_rect = tile_text.get_rect(center=new_tile_rect.center)
        surface.blit(tile_text, tile_text_rect)
        
    def _draw_strategy_slide(self, surface: pygame.Surface) -> None:
        """Draw strategy tips slide"""
        # Draw example of good strategy
        grid_x = SCREEN_WIDTH // 2 - (GRID_SIZE * (TILE_SIZE + TILE_MARGIN)) // 2
        grid_y = SCREEN_HEIGHT // 2 - (GRID_SIZE * (TILE_SIZE + TILE_MARGIN)) // 2
        
        # Draw grid with strategic tile placement
        strategy_grid = [
            [512, 256, 128, 64],
            [32, 16, 8, 4],
            [2, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = grid_x + col * (TILE_SIZE + TILE_MARGIN)
                y = grid_y + row * (TILE_SIZE + TILE_MARGIN)
                
                value = strategy_grid[row][col]
                
                if value > 0:
                    tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, self.theme_manager.get_tile_color(value), tile_rect, border_radius=5)
                    
                    tile_font = pygame.font.Font(None, 36)
                    tile_text = tile_font.render(str(value), True, self.theme_manager.get_tile_text_color(value))
                    tile_text_rect = tile_text.get_rect(center=tile_rect.center)
                    surface.blit(tile_text, tile_text_rect)
                else:
                    # Draw empty cell
                    cell_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, self.theme_manager.get_color('empty_cell'), cell_rect, border_radius=5)
                    
        # Draw arrow pointing to highest tile
        arrow_x = grid_x - 50
        arrow_y = grid_y + TILE_SIZE // 2
        pygame.draw.polygon(surface, self.theme_manager.get_color('button_hover'), [
            (arrow_x + 30, arrow_y),
            (arrow_x, arrow_y - 15),
            (arrow_x, arrow_y + 15)
        ])
        
        # Draw label
        label_text = self.small_font.render("Highest tile in corner", True, self.theme_manager.get_color('text_dark'))
        label_rect = label_text.get_rect(midright=(arrow_x - 10, arrow_y))
        surface.blit(label_text, label_rect)
        
    def _draw_levels_slide(self, surface: pygame.Surface) -> None:
        """Draw levels slide"""
        # Draw level progression
        level_width = 150
        level_height = 60
        level_spacing = 20
        start_x = (SCREEN_WIDTH - (4 * level_width + 3 * level_spacing)) // 2
        start_y = SCREEN_HEIGHT // 2 - 30
        
        levels = [
            ("Easy", (0, 200, 0), "1-5"),
            ("Medium", (200, 200, 0), "6-10"),
            ("Hard", (200, 100, 0), "11-15"),
            ("Expert", (200, 0, 0), "16-20")
        ]
        
        for i, (name, color, range_str) in enumerate(levels):
            x = start_x + i * (level_width + level_spacing)
            
            # Draw level box
            level_rect = pygame.Rect(x, start_y, level_width, level_height)
            pygame.draw.rect(surface, color, level_rect, border_radius=5)
            
            # Draw level name
            level_text = self.content_font.render(name, True, (255, 255, 255))
            level_text_rect = level_text.get_rect(center=(x + level_width // 2, start_y + 20))
            surface.blit(level_text, level_text_rect)
            
            # Draw level range
            range_text = self.small_font.render(range_str, True, (255, 255, 255))
            range_text_rect = range_text.get_rect(center=(x + level_width // 2, start_y + 40))
            surface.blit(range_text, range_text_rect)
            
    def _draw_features_slide(self, surface: pygame.Surface) -> None:
        """Draw features slide"""
        # Draw feature icons
        feature_icons = [
            ("Particles", "✨"),
            ("3D Audio", "🔊"),
            ("Themes", "🎨"),
            ("Achievements", "🏆"),
            ("Statistics", "📊"),
            ("Settings", "⚙️")
        ]
        
        icon_size = 80
        icon_spacing = 20
        icons_per_row = 3
        start_x = (SCREEN_WIDTH - (icons_per_row * (icon_size + icon_spacing) - icon_spacing)) // 2
        start_y = SCREEN_HEIGHT // 2 - 100
        
        for i, (name, icon) in enumerate(feature_icons):
            row = i // icons_per_row
            col = i % icons_per_row
            
            x = start_x + col * (icon_size + icon_spacing)
            y = start_y + row * (icon_size + icon_spacing + 30)
            
            # Draw icon background
            icon_rect = pygame.Rect(x, y, icon_size, icon_size)
            pygame.draw.rect(surface, self.theme_manager.get_color('button'), icon_rect, border_radius=10)
            
            # Draw icon symbol
            icon_font = pygame.font.Font(None, 48)
            icon_text = icon_font.render(icon, True, self.theme_manager.get_color('text_light'))
            icon_text_rect = icon_text.get_rect(center=icon_rect.center)
            surface.blit(icon_text, icon_text_rect)
            
            # Draw feature name
            name_text = self.small_font.render(name, True, self.theme_manager.get_color('text_dark'))
            name_rect = name_text.get_rect(center=(x + icon_size // 2, y + icon_size + 15))
            surface.blit(name_text, name_rect)
            
    def _draw_ready_slide(self, surface: pygame.Surface) -> None:
        """Draw ready slide"""
        # Draw checkmark
        checkmark_size = 100
        checkmark_x = SCREEN_WIDTH // 2
        checkmark_y = SCREEN_HEIGHT // 2 - 50
        
        pygame.draw.circle(surface, (0, 200, 0), (checkmark_x, checkmark_y), checkmark_size // 2)
        
        # Draw checkmark symbol
        checkmark_font = pygame.font.Font(None, 72)
        checkmark_text = checkmark_font.render("✓", True, (255, 255, 255))
        checkmark_rect = checkmark_text.get_rect(center=(checkmark_x, checkmark_y))
        surface.blit(checkmark_text, checkmark_rect)
        
    def _draw_demo_grid(self, surface: pygame.Surface) -> None:
        """Draw demo grid"""
        grid_x = SCREEN_WIDTH // 2 - (GRID_SIZE * (TILE_SIZE + TILE_MARGIN)) // 2
        grid_y = SCREEN_HEIGHT // 2 - (GRID_SIZE * (TILE_SIZE + TILE_MARGIN)) // 2
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = grid_x + col * (TILE_SIZE + TILE_MARGIN)
                y = grid_y + row * (TILE_SIZE + TILE_MARGIN)
                
                value = self.demo_grid[row][col]
                
                if value > 0:
                    tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, self.theme_manager.get_tile_color(value), tile_rect, border_radius=5)
                    
                    tile_font = pygame.font.Font(None, 36)
                    tile_text = tile_font.render(str(value), True, self.theme_manager.get_tile_text_color(value))
                    tile_text_rect = tile_text.get_rect(center=tile_rect.center)
                    surface.blit(tile_text, tile_text_rect)
                else:
                    # Draw empty cell
                    cell_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, self.theme_manager.get_color('empty_cell'), cell_rect, border_radius=5)
                    
    def prev_slide(self) -> None:
        """Go to previous slide"""
        if self.current_slide > 0:
            self.current_slide -= 1
            self.audio_manager.play_sound('button_click')
            
    def next_slide(self) -> None:
        """Go to next slide"""
        if self.current_slide < len(self.tutorials) - 1:
            self.current_slide += 1
            self.audio_manager.play_sound('button_click')
        else:
            # Last slide, go to main menu
            self.set_next_screen('main_menu')
            self.audio_manager.play_sound('button_click')
            
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_next_screen('main_menu')
            elif event.key == pygame.K_LEFT:
                self.prev_slide()
            elif event.key == pygame.K_RIGHT:
                self.next_slide()
                
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update buttons
        self.prev_button.update(mouse_pos, mouse_clicked)
        self.next_button.update(mouse_pos, mouse_clicked)
        self.skip_button.update(mouse_pos, mouse_clicked)
        
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the tutorial menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Get current tutorial
        tutorial = self.tutorials[self.current_slide]
        
        # Draw title
        title_text = self.title_font.render(tutorial.title, True, self.theme_manager.get_color('text_dark'))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Draw custom content if available
        if tutorial.custom_draw_func:
            tutorial.custom_draw_func(self.screen)
        else:
            # Draw content as text
            content_lines = tutorial.content.split('\n')
            y_offset = 150
            
            for line in content_lines:
                if line.strip():
                    content_text = self.content_font.render(line, True, self.theme_manager.get_color('text_dark'))
                    content_rect = content_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                    self.screen.blit(content_text, content_rect)
                    
                y_offset += 30
                
        # Draw slide indicator
        indicator_y = SCREEN_HEIGHT - 150
        indicator_spacing = 15
        
        for i in range(len(self.tutorials)):
            indicator_x = SCREEN_WIDTH // 2 - (len(self.tutorials) * indicator_spacing) // 2 + i * indicator_spacing
            
            if i == self.current_slide:
                pygame.draw.circle(self.screen, self.theme_manager.get_color('button_hover'), 
                                 (indicator_x, indicator_y), 6)
            else:
                pygame.draw.circle(self.screen, self.theme_manager.get_color('button'), 
                                 (indicator_x, indicator_y), 4)
                
        # Draw buttons
        self.prev_button.draw(self.screen)
        self.next_button.draw(self.screen)
        self.skip_button.draw(self.screen)
        
        # Disable prev button on first slide
        if self.current_slide == 0:
            self.prev_button.enabled = False
        else:
            self.prev_button.enabled = True
            
        # Change next button text on last slide
        if self.current_slide == len(self.tutorials) - 1:
            self.next_button.text = "Finish"
        else:
            self.next_button.text = "Next"