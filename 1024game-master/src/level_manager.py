#!/usr/bin/env python3
"""
1024 Game - Level Manager
Manages game levels and progression
"""

import json
import os
from typing import Dict, List, Any, Optional
from src.constants import LEVEL_COUNT, LEVELS_PER_DIFFICULTY, DIFFICULTY_SETTINGS


class LevelManager:
    """Manages game levels and progression"""
    
    def __init__(self):
        """Initialize the level manager"""
        self.current_level = 1
        self.unlocked_levels = {1}  # Start with level 1 unlocked
        self.level_scores = {}  # Store best scores for each level
        self.level_data = {}  # Store additional level data
        
        # Generate level configurations
        self._generate_levels()
        
        # Load saved progress
        self._load_progress()

    def _generate_levels(self) -> None:
        """Generate level configurations"""
        for level in range(1, LEVEL_COUNT + 1):
            difficulty = self._get_difficulty_for_level(level)
            settings = DIFFICULTY_SETTINGS[difficulty].copy()
            
            # Add level-specific settings
            self.level_data[level] = {
                'level': level,
                'difficulty': difficulty,
                'name': self._get_level_name(level, difficulty),
                'description': self._get_level_description(level, difficulty),
                'settings': settings,
                'unlocked': level == 1,  # Only level 1 is unlocked initially
                'completed': False,
                'best_score': 0,
                'stars': 0,  # 0-3 stars based on performance
                'first_time': True
            }

    def _get_difficulty_for_level(self, level: int) -> int:
        """Get difficulty setting based on level number"""
        if level <= 5:
            return 1  # Easy
        elif level <= 10:
            return 2  # Medium
        elif level <= 15:
            return 3  # Hard
        else:
            return 4  # Expert

    def _get_level_name(self, level: int, difficulty: int) -> str:
        """Get the name for a level"""
        difficulty_names = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
        difficulty_name = difficulty_names[difficulty]
        
        # Special names for certain levels
        special_levels = {
            1: "Getting Started",
            5: "Easy Complete",
            10: "Medium Master",
            15: "Hard Hero",
            20: "Expert Elite"
        }
        
        return special_levels.get(level, f"{difficulty_name} Level {level}")

    def _get_level_description(self, level: int, difficulty: int) -> str:
        """Get the description for a level"""
        descriptions = {
            1: "Learn the basics of 1024. Reach 512 to win!",
            2: "Getting warmer. Can you reach 512?",
            3: "The challenge increases. Keep going!",
            4: "Almost there with the easy levels.",
            5: "Final easy level. Prove your skills!",
            6: "Welcome to medium difficulty. Now you need to reach 1024!",
            7: "The tiles are appearing more frequently now.",
            8: "Strategy becomes more important.",
            9: "Can you handle the pressure?",
            10: "Master of medium levels. Almost to hard!",
            11: "Hard mode begins. Time and move limits apply!",
            12: "5 minutes to reach 1024. Can you do it?",
            13: "The clock is ticking. 200 moves max.",
            14: "Precision and speed are key.",
            15: "Final hard level. Are you ready for expert?",
            16: "Expert mode! 5x5 grid and 2048 target!",
            17: "The ultimate challenge begins.",
            18: "4 minutes to prove your mastery.",
            19: "Only the best will reach this far.",
            20: "The final challenge. Can you become the 1024 champion?"
        }
        
        return descriptions.get(level, f"Level {level} - Difficulty: {difficulty}")

    def load_levels(self) -> None:
        """Load level configurations"""
        # Levels are generated in __init__, this is for future loading from files
        pass

    def get_level_data(self, level: int) -> Optional[Dict[str, Any]]:
        """Get data for a specific level"""
        return self.level_data.get(level)

    def get_current_level(self) -> int:
        """Get the current level"""
        return self.current_level

    def set_current_level(self, level: int) -> None:
        """Set the current level"""
        if 1 <= level <= LEVEL_COUNT:
            self.current_level = level

    def is_level_unlocked(self, level: int) -> bool:
        """Check if a level is unlocked"""
        return level in self.unlocked_levels

    def unlock_level(self, level: int) -> None:
        """Unlock a level"""
        if 1 <= level <= LEVEL_COUNT:
            self.unlocked_levels.add(level)
            self.level_data[level]['unlocked'] = True

    def complete_level(self, level: int, score: int) -> None:
        """Mark a level as completed and update score"""
        if level in self.level_data:
            level_info = self.level_data[level]
            level_info['completed'] = True
            
            # Update best score
            if score > level_info['best_score']:
                level_info['best_score'] = score
            
            # Calculate stars based on performance
            stars = self._calculate_stars(level, score)
            level_info['stars'] = max(level_info['stars'], stars)
            
            # Mark as not first time anymore
            level_info['first_time'] = False
            
            # Unlock next level
            if level < LEVEL_COUNT:
                self.unlock_level(level + 1)
            
            # Save progress
            self._save_progress()

    def _calculate_stars(self, level: int, score: int) -> int:
        """Calculate stars earned for a level"""
        level_info = self.level_data[level]
        settings = level_info['settings']
        win_value = settings['win_value']
        
        # Base star on reaching the goal
        if score >= win_value * 2:
            return 3  # Excellent
        elif score >= win_value:
            return 2  # Good
        elif score >= win_value // 2:
            return 1  # Passed
        else:
            return 0  # Failed

    def get_level_progress(self) -> Dict[str, Any]:
        """Get overall level progress"""
        completed = sum(1 for level in self.level_data.values() if level['completed'])
        total_stars = sum(level['stars'] for level in self.level_data.values())
        max_stars = LEVEL_COUNT * 3
        
        return {
            'completed': completed,
            'total': LEVEL_COUNT,
            'completed_percentage': (completed / LEVEL_COUNT) * 100,
            'total_stars': total_stars,
            'max_stars': max_stars,
            'stars_percentage': (total_stars / max_stars) * 100
        }

    def get_levels_by_difficulty(self, difficulty: int) -> List[Dict[str, Any]]:
        """Get all levels of a specific difficulty"""
        return [level for level in self.level_data.values() 
                if level['difficulty'] == difficulty]

    def get_next_level(self, current_level: int) -> Optional[int]:
        """Get the next level after the current one"""
        next_level = current_level + 1
        return next_level if next_level <= LEVEL_COUNT else None

    def get_previous_level(self, current_level: int) -> Optional[int]:
        """Get the previous level before the current one"""
        prev_level = current_level - 1
        return prev_level if prev_level >= 1 else None

    def reset_progress(self) -> None:
        """Reset all level progress"""
        self.current_level = 1
        self.unlocked_levels = {1}
        self.level_scores = {}
        
        # Reset level data
        for level in self.level_data:
            self.level_data[level]['unlocked'] = (level == 1)
            self.level_data[level]['completed'] = False
            self.level_data[level]['best_score'] = 0
            self.level_data[level]['stars'] = 0
            self.level_data[level]['first_time'] = True
        
        # Save the reset progress
        self._save_progress()

    def _load_progress(self) -> None:
        """Load level progress from file"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            progress_file = os.path.join(data_dir, 'level_progress.json')
            
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                
                # Load current level
                self.current_level = progress_data.get('current_level', 1)
                
                # Load unlocked levels
                self.unlocked_levels = set(progress_data.get('unlocked_levels', [1]))
                
                # Load level data
                saved_level_data = progress_data.get('level_data', {})
                for level_str, level_info in saved_level_data.items():
                    level = int(level_str)
                    if level in self.level_data:
                        self.level_data[level].update(level_info)
        except (json.JSONDecodeError, IOError):
            # If loading fails, use default values
            pass

    def _save_progress(self) -> None:
        """Save level progress to file"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            progress_file = os.path.join(data_dir, 'level_progress.json')
            
            progress_data = {
                'current_level': self.current_level,
                'unlocked_levels': list(self.unlocked_levels),
                'level_data': {str(level): data for level, data in self.level_data.items()}
            }
            
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except IOError:
            # Silently fail if can't save
            pass