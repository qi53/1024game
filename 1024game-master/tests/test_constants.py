import pytest

from src.constants import LEVELS, ACHIEVEMENTS, THEMES, BACKGROUND_COLORS


class TestConstants:
    def test_levels_count(self):
        assert len(LEVELS) == 20
    
    def test_levels_structure(self):
        for level in LEVELS:
            assert 'level' in level
            assert 'target' in level
            assert 'grid_size' in level
            assert 'time_limit' in level
            assert 'description' in level
    
    def test_difficulty_progression(self):
        for i in range(1, len(LEVELS)):
            prev = LEVELS[i - 1]
            curr = LEVELS[i]
            assert curr['target'] >= prev['target']
    
    def test_achievements_count(self):
        assert len(ACHIEVEMENTS) >= 10
    
    def test_achievements_structure(self):
        for achievement in ACHIEVEMENTS:
            assert 'id' in achievement
            assert 'name' in achievement
            assert 'description' in achievement
            assert 'icon' in achievement
    
    def test_themes_count(self):
        assert len(THEMES) >= 5
    
    def test_themes_structure(self):
        required_keys = ['name', 'background', 'grid_bg', 'cell_bg', 
                        'text_light', 'text_dark', 'ui_bg', 'ui_text']
        for theme_name, theme in THEMES.items():
            for key in required_keys:
                assert key in theme, f"Theme '{theme_name}' missing key '{key}'"
    
    def test_cell_bg_is_dict(self):
        for theme_name, theme in THEMES.items():
            cell_bg = theme.get('cell_bg')
            assert isinstance(cell_bg, dict), f"Theme '{theme_name}' cell_bg should be dict"
    
    def test_theme_colors_are_tuples(self):
        for theme_name, theme in THEMES.items():
            for key in ['background', 'grid_bg', 'text_light', 'text_dark', 'ui_bg', 'ui_text']:
                color = theme[key]
                assert isinstance(color, tuple), f"Theme '{theme_name}' {key} should be tuple"
                assert len(color) == 3, f"Theme '{theme_name}' {key} should have 3 components"
    
    def test_level_difficulty_tiers(self):
        tier1 = [l for l in LEVELS if l['level'] <= 5]
        tier2 = [l for l in LEVELS if 6 <= l['level'] <= 10]
        tier3 = [l for l in LEVELS if 11 <= l['level'] <= 15]
        tier4 = [l for l in LEVELS if l['level'] >= 16]
        
        avg_target_tier1 = sum(l['target'] for l in tier1) / len(tier1)
        avg_target_tier2 = sum(l['target'] for l in tier2) / len(tier2)
        avg_target_tier3 = sum(l['target'] for l in tier3) / len(tier3)
        avg_target_tier4 = sum(l['target'] for l in tier4) / len(tier4)
        
        assert avg_target_tier1 < avg_target_tier2
        assert avg_target_tier2 < avg_target_tier3
        assert avg_target_tier3 < avg_target_tier4
    
    def test_grid_size_increases(self):
        grid_sizes_by_tier = {
            1: set(),
            2: set(),
            3: set(),
            4: set()
        }
        for level in LEVELS:
            tier = (level['level'] - 1) // 5 + 1
            grid_sizes_by_tier[tier].add(level['grid_size'])
        
        for tier in range(2, 5):
            avg_prev = sum(grid_sizes_by_tier[tier-1]) / len(grid_sizes_by_tier[tier-1])
            avg_curr = sum(grid_sizes_by_tier[tier]) / len(grid_sizes_by_tier[tier])
            assert avg_curr >= avg_prev, f"Tier {tier} should have larger grids than tier {tier-1}"
    
    def test_background_colors_has_common_tiles(self):
        for value in [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
            assert value in BACKGROUND_COLORS
