#!/usr/bin/env python3
"""
1024 Game - Game Over Screen
Displays game statistics and results
"""

import pygame
import datetime
from typing import Dict, List, Any, Tuple, Optional
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui_manager import Menu, Button


class GameOverMenu(Menu):
    """Game over menu screen"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, data_manager, game_result: Dict[str, Any]):
        """Initialize the game over menu"""
        super().__init__(screen, theme_manager, audio_manager)
        self.data_manager = data_manager
        self.game_result = game_result
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.section_font = pygame.font.Font(None, 36)
        self.stat_font = pygame.font.Font(None, 28)
        self.value_font = pygame.font.Font(None, 32)
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = SCREEN_HEIGHT - 150
        
        self.retry_button = Button(
            SCREEN_WIDTH // 2 - button_width - button_spacing // 2, start_y, 
            button_width, button_height,
            "Retry", self.section_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('retry')
        )
        
        self.menu_button = Button(
            SCREEN_WIDTH // 2 + button_spacing // 2, start_y, 
            button_width, button_height,
            "Menu", self.section_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('main_menu')
        )
        
        # Update statistics
        self._update_statistics()
        
    def _update_statistics(self) -> None:
        """Update player statistics based on game result"""
        stats = self.data_manager.get_stats()
        
        # Update basic stats
        stats['games_played'] = stats.get('games_played', 0) + 1
        stats['total_score'] = stats.get('total_score', 0) + self.game_result.get('score', 0)
        stats['total_moves'] = stats.get('total_moves', 0) + self.game_result.get('moves', 0)
        stats['total_time'] = stats.get('total_time', 0) + self.game_result.get('time', 0)
        
        # Update high score
        if self.game_result.get('score', 0) > stats.get('high_score', 0):
            stats['high_score'] = self.game_result.get('score', 0)
            
        # Update win/loss
        if self.game_result.get('won', False):
            stats['wins'] = stats.get('wins', 0) + 1
            stats['current_streak'] = stats.get('current_streak', 0) + 1
            stats['best_streak'] = max(stats.get('best_streak', 0), stats['current_streak'])
            
            # Update levels completed
            if 'level' in self.game_result:
                completed = max(stats.get('levels_completed', 0), self.game_result['level'])
                stats['levels_completed'] = completed
        else:
            stats['losses'] = stats.get('losses', 0) + 1
            stats['current_streak'] = 0
            
        # Update perfect games
        if self.game_result.get('perfect', False):
            stats['perfect_games'] = stats.get('perfect_games', 0) + 1
            
        # Update playtime
        now = datetime.datetime.now()
        if not stats.get('first_played'):
            stats['first_played'] = now.isoformat()
        stats['last_played'] = now.isoformat()
        
        # Calculate total playtime (simplified)
        if stats.get('games_played', 1) == 1:
            stats['total_playtime'] = self.game_result.get('time', 0)
        else:
            stats['total_playtime'] = stats.get('total_playtime', 0) + self.game_result.get('time', 0)
            
        # Save updated stats
        self.data_manager.save_stats(stats)
        
        # Check for achievements
        self._check_achievements()
        
    def _check_achievements(self) -> None:
        """Check for achievement unlocks"""
        # Import here to avoid circular imports
        from src.achievements import AchievementManager
        
        # Create achievement manager if not already available
        if not hasattr(self.data_manager, 'achievement_manager'):
            self.data_manager.achievement_manager = AchievementManager(self.data_manager)
            
        achievement_manager = self.data_manager.achievement_manager
        
        # Check first win
        if self.game_result.get('won', False):
            achievement_manager.update_achievement_progress('first_win', 1)
            
        # Check speed runner
        if self.game_result.get('won', False) and self.game_result.get('time', 0) < 120:
            achievement_manager.update_achievement_progress('speed_runner', 1)
            
        # Check perfect game
        if self.game_result.get('won', False) and self.game_result.get('perfect', False):
            achievement_manager.update_achievement_progress('perfect_game', 1)
            
        # Check high scorer
        if self.game_result.get('score', 0) >= 10000:
            achievement_manager.update_achievement_progress('high_scorer', self.game_result.get('score', 0))
            
        # Check explorer
        if 'level' in self.game_result:
            achievement_manager.update_achievement_progress('explorer', self.game_result['level'])
            
        # Check master
        if self.game_result.get('level', 0) >= 20:
            achievement_manager.update_achievement_progress('master', 20)
            
        # Check persistent
        stats = self.data_manager.get_stats()
        achievement_manager.update_achievement_progress('persistent', stats.get('games_played', 0))
        
        # Check dedicated
        total_hours = stats.get('total_playtime', 0) / 3600
        achievement_manager.update_achievement_progress('dedicated', int(total_hours))
        
        # Check noob to pro
        achievement_manager.update_achievement_progress('noob_to_pro', stats.get('current_streak', 0))
        
        # Check unstoppable
        achievement_manager.update_achievement_progress('unstoppable', stats.get('current_streak', 0))
        
        # Check tile master
        if self.game_result.get('max_tile', 0) >= 1024:
            achievement_manager.update_achievement_progress('tile_master', 1)
            
        # Check tile legend
        if self.game_result.get('max_tile', 0) >= 2048:
            achievement_manager.update_achievement_progress('tile_legend', 1)
            
        # Check perfectionist
        achievement_manager.update_achievement_progress('perfectionist', stats.get('perfect_games', 0))
        
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = 'main_menu'
                
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update buttons
        if self.retry_button.update(mouse_pos, mouse_clicked):
            self.audio_manager.play_sound('button_click')
            
        if self.menu_button.update(mouse_pos, mouse_clicked):
            self.audio_manager.play_sound('button_click')
            
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the game over menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Draw title based on game result
        if self.game_result.get('won', False):
            title_text = "Victory!"
            title_color = (0, 200, 0)
        else:
            title_text = "Game Over"
            title_color = (200, 0, 0)
            
        title_surface = self.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Draw level if available
        if 'level' in self.game_result:
            level_text = self.section_font.render(f"Level {self.game_result['level']}", True, self.theme_manager.get_color('text_dark'))
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
            self.screen.blit(level_text, level_rect)
        
        # Draw statistics
        self._draw_statistics()
        
        # Draw buttons
        self.retry_button.draw(self.screen)
        self.menu_button.draw(self.screen)
        
    def _draw_statistics(self) -> None:
        """Draw game statistics"""
        # Statistics to display
        stats_to_show = [
            ('Score', self.game_result.get('score', 0)),
            ('Moves', self.game_result.get('moves', 0)),
            ('Time', self._format_time(self.game_result.get('time', 0))),
            ('Max Tile', self.game_result.get('max_tile', 0))
        ]
        
        # Additional stats if won
        if self.game_result.get('won', False):
            stats_to_show.append(('Perfect Game', 'Yes' if self.game_result.get('perfect', False) else 'No'))
            
        # Calculate layout
        stats_per_row = 2
        stat_width = 300
        stat_height = 80
        stat_spacing_x = (SCREEN_WIDTH - stats_per_row * stat_width) // (stats_per_row + 1)
        stat_spacing_y = 20
        start_y = 200
        
        # Draw stat cards
        for i, (name, value) in enumerate(stats_to_show):
            row = i // stats_per_row
            col = i % stats_per_row
            
            x = stat_spacing_x + col * (stat_width + stat_spacing_x)
            y = start_y + row * (stat_height + stat_spacing_y)
            
            # Draw stat card
            card_rect = pygame.Rect(x, y, stat_width, stat_height)
            pygame.draw.rect(self.screen, self.theme_manager.get_color('button'), card_rect, border_radius=10)
            
            # Draw stat name
            name_text = self.stat_font.render(name, True, self.theme_manager.get_color('text_light'))
            name_rect = name_text.get_rect(center=(x + stat_width // 2, y + 25))
            self.screen.blit(name_text, name_rect)
            
            # Draw stat value
            value_text = self.value_font.render(str(value), True, self.theme_manager.get_color('text_light'))
            value_rect = value_text.get_rect(center=(x + stat_width // 2, y + 55))
            self.screen.blit(value_text, value_rect)
            
        # Draw high score notification if new high score
        stats = self.data_manager.get_stats()
        if self.game_result.get('score', 0) >= stats.get('high_score', 0) and self.game_result.get('score', 0) > 0:
            high_score_text = self.section_font.render("NEW HIGH SCORE!", True, (255, 215, 0))
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + len(stats_to_show) // 2 * (stat_height + stat_spacing_y) + 50))
            self.screen.blit(high_score_text, high_score_rect)
            
    def _format_time(self, seconds: int) -> str:
        """Format time in seconds to MM:SS format"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class StatisticsMenu(Menu):
    """Detailed statistics menu"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, data_manager):
        """Initialize the statistics menu"""
        super().__init__(screen, theme_manager, audio_manager)
        self.data_manager = data_manager
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.section_font = pygame.font.Font(None, 36)
        self.stat_font = pygame.font.Font(None, 28)
        self.value_font = pygame.font.Font(None, 32)
        
        # Create back button
        self.back_button = Button(
            20, 20, 100, 40,
            "Back", self.section_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('main_menu')
        )
        
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_next_screen('main_menu')
                
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update back button
        if self.back_button.update(mouse_pos, mouse_clicked):
            self.audio_manager.play_sound('button_click')
            
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the statistics menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Draw title
        title_text = self.title_font.render("Statistics", True, self.theme_manager.get_color('text_dark'))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Get statistics
        stats = self.data_manager.get_stats()
        
        # Statistics to display
        stats_sections = [
            ('General Statistics', [
                ('Games Played', stats.get('games_played', 0)),
                ('Total Score', stats.get('total_score', 0)),
                ('High Score', stats.get('high_score', 0)),
                ('Average Score', self._calculate_average_score(stats)),
                ('Total Moves', stats.get('total_moves', 0)),
                ('Average Moves', self._calculate_average_moves(stats)),
                ('Total Playtime', self._format_time(stats.get('total_playtime', 0))),
                ('Average Game Time', self._calculate_average_time(stats))
            ]),
            ('Win/Loss Statistics', [
                ('Wins', stats.get('wins', 0)),
                ('Losses', stats.get('losses', 0)),
                ('Win Rate', self._calculate_win_rate(stats)),
                ('Current Streak', stats.get('current_streak', 0)),
                ('Best Streak', stats.get('best_streak', 0)),
                ('Perfect Games', stats.get('perfect_games', 0))
            ]),
            ('Progress Statistics', [
                ('Levels Completed', stats.get('levels_completed', 0)),
                ('Achievements Unlocked', stats.get('achievements_unlocked', 0)),
                ('First Played', self._format_date(stats.get('first_played'))),
                ('Last Played', self._format_date(stats.get('last_played')))
            ])
        ]
        
        # Draw statistics sections
        y_offset = 100
        
        for section_title, section_stats in stats_sections:
            # Draw section title
            section_text = self.section_font.render(section_title, True, self.theme_manager.get_color('text_dark'))
            section_rect = section_text.get_rect(midleft=(50, y_offset))
            self.screen.blit(section_text, section_rect)
            y_offset += 40
            
            # Draw section stats
            for stat_name, stat_value in section_stats:
                # Draw stat name
                name_text = self.stat_font.render(stat_name, True, self.theme_manager.get_color('text_dark'))
                name_rect = name_text.get_rect(topleft=(100, y_offset))
                self.screen.blit(name_text, name_rect)
                
                # Draw stat value
                value_text = self.value_font.render(str(stat_value), True, self.theme_manager.get_color('text_dark'))
                value_rect = value_text.get_rect(topright=(SCREEN_WIDTH - 100, y_offset))
                self.screen.blit(value_text, value_rect)
                
                y_offset += 30
                
            y_offset += 20  # Space between sections
            
    def _calculate_average_score(self, stats: Dict[str, Any]) -> str:
        """Calculate average score"""
        games = stats.get('games_played', 0)
        if games <= 0:
            return "0"
        return str(stats.get('total_score', 0) // games)
        
    def _calculate_average_moves(self, stats: Dict[str, Any]) -> str:
        """Calculate average moves"""
        games = stats.get('games_played', 0)
        if games <= 0:
            return "0"
        return str(stats.get('total_moves', 0) // games)
        
    def _calculate_average_time(self, stats: Dict[str, Any]) -> str:
        """Calculate average game time"""
        games = stats.get('games_played', 0)
        if games <= 0:
            return "00:00"
        return self._format_time(stats.get('total_playtime', 0) // games)
        
    def _calculate_win_rate(self, stats: Dict[str, Any]) -> str:
        """Calculate win rate"""
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        total = wins + losses
        if total <= 0:
            return "0%"
        return f"{(wins / total) * 100:.1f}%"
        
    def _format_time(self, seconds: int) -> str:
        """Format time in seconds to readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
            
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string"""
        if not date_str:
            return "Never"
            
        try:
            date = datetime.datetime.fromisoformat(date_str)
            return date.strftime("%Y-%m-%d")
        except:
            return "Unknown"