#!/usr/bin/env python3
"""
1024 Game - Achievements System
Handles achievements tracking and display
"""

import pygame
import datetime
from typing import Dict, List, Any, Tuple, Optional
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui_components import Menu, Button


class Achievement:
    """Represents a single achievement"""
    
    def __init__(self, key: str, name: str, description: str, icon: str = None,
                 hidden: bool = False, target: int = 1, reward_type: str = None,
                 reward_value: Any = None):
        """Initialize an achievement"""
        self.key = key
        self.name = name
        self.description = description
        self.icon = icon
        self.hidden = hidden
        self.target = target
        self.reward_type = reward_type
        self.reward_value = reward_value
        
        # Runtime state
        self.unlocked = False
        self.progress = 0
        self.unlock_date = None
        
    def update_progress(self, progress: int) -> bool:
        """Update achievement progress and check if unlocked"""
        if self.unlocked:
            return False
            
        old_progress = self.progress
        self.progress = min(progress, self.target)
        
        # Check if achievement should be unlocked
        if self.progress >= self.target:
            self.unlocked = True
            self.unlock_date = datetime.datetime.now().isoformat()
            return True
            
        return self.progress > old_progress
        
    def get_progress_percentage(self) -> float:
        """Get progress as a percentage"""
        if self.target <= 0:
            return 100.0 if self.unlocked else 0.0
        return min(100.0, (self.progress / self.target) * 100.0)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary for saving"""
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'hidden': self.hidden,
            'target': self.target,
            'reward_type': self.reward_type,
            'reward_value': self.reward_value,
            'unlocked': self.unlocked,
            'progress': self.progress,
            'unlock_date': self.unlock_date
        }
        
    @classmethod
    def from_dict(cls, key: str, data: Dict[str, Any]) -> 'Achievement':
        """Create achievement from dictionary"""
        achievement = cls(
            key=key,
            name=data.get('name', ''),
            description=data.get('description', ''),
            icon=data.get('icon'),
            hidden=data.get('hidden', False),
            target=data.get('target', 1),
            reward_type=data.get('reward_type'),
            reward_value=data.get('reward_value')
        )
        
        achievement.unlocked = data.get('unlocked', False)
        achievement.progress = data.get('progress', 0)
        achievement.unlock_date = data.get('unlock_date')
        
        return achievement


class AchievementManager:
    """Manages all achievements"""
    
    def __init__(self, data_manager):
        """Initialize the achievement manager"""
        self.data_manager = data_manager
        self.achievements: Dict[str, Achievement] = {}
        self.notification_queue: List[Achievement] = []
        
        # Create achievements
        self._create_achievements()
        
        # Load achievement progress
        self.load_achievements()
        
    def _create_achievements(self) -> None:
        """Create all achievements"""
        # Gameplay achievements
        self.achievements['first_win'] = Achievement(
            'first_win', 'First Victory', 'Win your first game', 'trophy'
        )
        
        self.achievements['speed_runner'] = Achievement(
            'speed_runner', 'Speed Runner', 'Complete a level in under 2 minutes', 'clock'
        )
        
        self.achievements['perfect_game'] = Achievement(
            'perfect_game', 'Perfect Game', 'Win a game without using undo', 'star'
        )
        
        self.achievements['high_scorer'] = Achievement(
            'high_scorer', 'High Scorer', 'Score over 10,000 points in a single game', 'score'
        )
        
        # Progress achievements
        self.achievements['explorer'] = Achievement(
            'explorer', 'Explorer', 'Complete 10 different levels', 'compass'
        )
        
        self.achievements['master'] = Achievement(
            'master', '1024 Master', 'Complete all 20 levels', 'crown'
        )
        
        self.achievements['persistent'] = Achievement(
            'persistent', 'Persistent', 'Play 50 games', 'repeat'
        )
        
        self.achievements['dedicated'] = Achievement(
            'dedicated', 'Dedicated', 'Play for 10 hours total', 'clock'
        )
        
        # Challenge achievements
        self.achievements['noob_to_pro'] = Achievement(
            'noob_to_pro', 'Noob to Pro', 'Win 5 games in a row', 'arrow_up'
        )
        
        self.achievements['unstoppable'] = Achievement(
            'unstoppable', 'Unstoppable', 'Win 10 games in a row', 'fire'
        )
        
        self.achievements['tile_master'] = Achievement(
            'tile_master', 'Tile Master', 'Create a 1024 tile', 'tile'
        )
        
        self.achievements['tile_legend'] = Achievement(
            'tile_legend', 'Tile Legend', 'Create a 2048 tile', 'legend'
        )
        
        # Special achievements
        self.achievements['perfectionist'] = Achievement(
            'perfectionist', 'Perfectionist', 'Get 3 perfect games', 'gem'
        )
        
        self.achievements['collector'] = Achievement(
            'collector', 'Collector', 'Unlock all other achievements', 'collection', hidden=True
        )
        
    def load_achievements(self) -> None:
        """Load achievement progress from data manager"""
        saved_achievements = self.data_manager.get_achievements()
        
        for key, achievement in self.achievements.items():
            if key in saved_achievements:
                achievement.unlocked = saved_achievements[key].get('unlocked', False)
                achievement.progress = saved_achievements[key].get('progress', 0)
                achievement.unlock_date = saved_achievements[key].get('unlock_date')
                
    def save_achievements(self) -> None:
        """Save achievement progress to data manager"""
        achievements_dict = {}
        
        for key, achievement in self.achievements.items():
            achievements_dict[key] = achievement.to_dict()
            
        self.data_manager.save_achievements(achievements_dict)
        
    def update_achievement_progress(self, key: str, progress: int) -> bool:
        """Update achievement progress and check if unlocked"""
        if key not in self.achievements:
            return False
            
        achievement = self.achievements[key]
        
        if achievement.update_progress(progress):
            # Achievement unlocked
            self.notification_queue.append(achievement)
            self.save_achievements()
            
            # Check for collector achievement
            self.check_collector_achievement()
            
            return True
            
        # Save progress even if not unlocked
        self.save_achievements()
        return False
        
    def check_collector_achievement(self) -> None:
        """Check if collector achievement should be unlocked"""
        if 'collector' not in self.achievements or self.achievements['collector'].unlocked:
            return
            
        # Count unlocked achievements (excluding collector itself)
        unlocked_count = sum(1 for key, achievement in self.achievements.items() 
                           if achievement.unlocked and key != 'collector')
        
        # Total achievements (excluding collector itself)
        total_count = len(self.achievements) - 1
        
        # Update progress
        self.update_achievement_progress('collector', unlocked_count)
        
    def get_achievement(self, key: str) -> Optional[Achievement]:
        """Get an achievement by key"""
        return self.achievements.get(key)
        
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements"""
        return list(self.achievements.values())
        
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [achievement for achievement in self.achievements.values() if achievement.unlocked]
        
    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements"""
        return [achievement for achievement in self.achievements.values() if not achievement.unlocked]
        
    def get_hidden_achievements(self) -> List[Achievement]:
        """Get all hidden achievements"""
        return [achievement for achievement in self.achievements.values() 
                if achievement.hidden and not achievement.unlocked]
                
    def get_progress_percentage(self) -> float:
        """Get overall achievement progress as a percentage"""
        if not self.achievements:
            return 0.0
            
        unlocked_count = sum(1 for achievement in self.achievements.values() if achievement.unlocked)
        total_count = len(self.achievements)
        
        return (unlocked_count / total_count) * 100.0
        
    def get_next_notifications(self) -> List[Achievement]:
        """Get and clear the notification queue"""
        notifications = self.notification_queue.copy()
        self.notification_queue.clear()
        return notifications
        
    def reset_achievements(self) -> None:
        """Reset all achievements"""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.progress = 0
            achievement.unlock_date = None
            
        self.save_achievements()


class AchievementsMenu(Menu):
    """Achievements menu screen"""
    
    def __init__(self, screen: pygame.Surface, theme_manager, audio_manager, achievement_manager):
        """Initialize the achievements menu"""
        super().__init__(screen, theme_manager, audio_manager)
        self.achievement_manager = achievement_manager
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.section_font = pygame.font.Font(None, 36)
        self.name_font = pygame.font.Font(None, 28)
        self.desc_font = pygame.font.Font(None, 22)
        self.progress_font = pygame.font.Font(None, 20)
        
        # UI elements
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 20
        
        # Create back button
        self.back_button = Button(
            20, 20, 100, 40,
            "Back", self.section_font,
            self.theme_manager.get_color('button'),
            self.theme_manager.get_color('button_hover'),
            self.theme_manager.get_color('text_light'),
            action=lambda: self.set_next_screen('main_menu')
        )
        
        # Calculate layout
        self.achievement_height = 100
        self.achievement_spacing = 20
        self.achievements_per_row = 2
        self.achievement_width = (SCREEN_WIDTH - 100 - (self.achievements_per_row - 1) * 20) // self.achievements_per_row
        
        # Calculate max scroll
        achievements = self.achievement_manager.get_achievements()
        total_rows = (len(achievements) + self.achievements_per_row - 1) // self.achievements_per_row
        total_height = total_rows * (self.achievement_height + self.achievement_spacing)
        visible_height = SCREEN_HEIGHT - 150
        self.max_scroll = max(0, total_height - visible_height)
        
    def set_next_screen(self, screen: str) -> None:
        """Set the next screen to transition to"""
        self.next_screen = screen
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.set_next_screen('main_menu')
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - self.scroll_speed)
            elif event.button == 5:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.scroll_speed)
                
    def update(self, dt: float) -> Optional[str]:
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Update back button
        if self.back_button.update(mouse_pos, mouse_clicked):
            self.audio_manager.play_sound('button_click')
            
        return self.next_screen
        
    def draw(self) -> None:
        """Draw the achievements menu"""
        # Fill background
        self.screen.fill(self.theme_manager.get_color('background'))
        
        # Draw title
        title_text = self.title_font.render("Achievements", True, self.theme_manager.get_color('text_dark'))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Draw progress
        progress = self.achievement_manager.get_progress_percentage()
        progress_text = self.section_font.render(f"Progress: {progress:.1f}%", True, self.theme_manager.get_color('text_dark'))
        progress_rect = progress_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(progress_text, progress_rect)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Create a clipping region for achievements
        clip_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)
        self.screen.set_clip(clip_rect)
        
        # Draw achievements
        achievements = self.achievement_manager.get_all_achievements()
        unlocked_achievements = self.achievement_manager.get_unlocked_achievements()
        
        for i, achievement in enumerate(achievements):
            row = i // self.achievements_per_row
            col = i % self.achievements_per_row
            
            x = 50 + col * (self.achievement_width + 20)
            y = 150 + row * (self.achievement_height + self.achievement_spacing) - self.scroll_offset
            
            # Skip if outside visible area
            if y + self.achievement_height < 150 or y > SCREEN_HEIGHT:
                continue
                
            # Draw achievement card
            self._draw_achievement_card(achievement, x, y, self.achievement_width, self.achievement_height)
            
        # Reset clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            self._draw_scroll_indicator()
            
    def _draw_achievement_card(self, achievement: Achievement, x: int, y: int, width: int, height: int) -> None:
        """Draw an achievement card"""
        # Card background
        if achievement.unlocked:
            bg_color = self.theme_manager.get_color('button')
            border_color = self.theme_manager.get_color('button_hover')
        elif achievement.hidden:
            bg_color = tuple(c // 2 for c in self.theme_manager.get_color('button'))
            border_color = tuple(c // 2 for c in self.theme_manager.get_color('button_hover'))
        else:
            bg_color = self.theme_manager.get_color('empty_cell')
            border_color = self.theme_manager.get_color('button')
            
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=10)
        
        # Achievement content
        if achievement.unlocked:
            # Name
            name_text = self.name_font.render(achievement.name, True, self.theme_manager.get_color('text_dark'))
            name_rect = name_text.get_rect(topleft=(x + 15, y + 15))
            self.screen.blit(name_text, name_rect)
            
            # Description
            desc_text = self.desc_font.render(achievement.description, True, self.theme_manager.get_color('text_dark'))
            desc_rect = desc_text.get_rect(topleft=(x + 15, y + 45))
            self.screen.blit(desc_text, desc_rect)
            
            # Unlock date
            if achievement.unlock_date:
                try:
                    unlock_date = datetime.datetime.fromisoformat(achievement.unlock_date)
                    date_text = self.progress_font.render(f"Unlocked: {unlock_date.strftime('%Y-%m-%d')}", 
                                                         True, self.theme_manager.get_color('text_dark'))
                    date_rect = date_text.get_rect(bottomright=(x + width - 15, y + height - 15))
                    self.screen.blit(date_text, date_rect)
                except:
                    pass
        elif achievement.hidden:
            # Hidden achievement
            name_text = self.name_font.render("???", True, self.theme_manager.get_color('text_dark'))
            name_rect = name_text.get_rect(topleft=(x + 15, y + 15))
            self.screen.blit(name_text, name_rect)
            
            desc_text = self.desc_font.render("Complete other achievements to unlock", True, self.theme_manager.get_color('text_dark'))
            desc_rect = desc_text.get_rect(topleft=(x + 15, y + 45))
            self.screen.blit(desc_text, desc_rect)
        else:
            # Locked achievement
            name_text = self.name_font.render(achievement.name, True, self.theme_manager.get_color('text_dark'))
            name_rect = name_text.get_rect(topleft=(x + 15, y + 15))
            self.screen.blit(name_text, name_rect)
            
            desc_text = self.desc_font.render(achievement.description, True, self.theme_manager.get_color('text_dark'))
            desc_rect = desc_text.get_rect(topleft=(x + 15, y + 45))
            self.screen.blit(desc_text, desc_rect)
            
            # Progress bar
            progress = achievement.get_progress_percentage()
            if progress > 0:
                # Progress bar background
                bar_rect = pygame.Rect(x + 15, y + height - 30, width - 30, 10)
                pygame.draw.rect(self.screen, self.theme_manager.get_color('empty_cell'), bar_rect, border_radius=5)
                
                # Progress bar fill
                fill_width = int(bar_rect.width * progress / 100)
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
                pygame.draw.rect(self.screen, self.theme_manager.get_color('button_hover'), fill_rect, border_radius=5)
                
                # Progress text
                progress_text = self.progress_font.render(f"{progress:.0f}%", True, self.theme_manager.get_color('text_dark'))
                progress_rect = progress_text.get_rect(midright=(x + width - 15, y + height - 25))
                self.screen.blit(progress_text, progress_rect)
                
    def _draw_scroll_indicator(self) -> None:
        """Draw scroll indicator"""
        # Calculate indicator size and position
        indicator_height = 60
        indicator_width = 10
        indicator_x = SCREEN_WIDTH - 30
        
        # Calculate indicator position based on scroll
        visible_height = SCREEN_HEIGHT - 150
        total_height = visible_height + self.max_scroll
        indicator_y = 150 + (self.scroll_offset / self.max_scroll) * (visible_height - indicator_height) if self.max_scroll > 0 else 150
        
        # Draw indicator
        indicator_rect = pygame.Rect(indicator_x, indicator_y, indicator_width, indicator_height)
        pygame.draw.rect(self.screen, self.theme_manager.get_color('button'), indicator_rect, border_radius=5)