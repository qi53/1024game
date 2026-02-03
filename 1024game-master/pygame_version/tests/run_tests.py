#!/usr/bin/env python3
"""
1024 Game - Pygame Version - Test Runner
测试运行器
"""

import unittest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有测试模块
from tests import (
    test_game_engine,
    test_data_manager,
    test_particles,
    test_audio,
    test_ui_components
)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试模块
    suite.addTests(loader.loadTestsFromModule(test_game_engine))
    suite.addTests(loader.loadTestsFromModule(test_data_manager))
    suite.addTests(loader.loadTestsFromModule(test_particles))
    suite.addTests(loader.loadTestsFromModule(test_audio))
    suite.addTests(loader.loadTestsFromModule(test_ui_components))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


def run_specific_test(test_name):
    """运行特定测试"""
    loader = unittest.TestLoader()
    
    test_modules = {
        'game_engine': test_game_engine,
        'data_manager': test_data_manager,
        'particles': test_particles,
        'audio': test_audio,
        'ui': test_ui_components,
    }
    
    if test_name in test_modules:
        suite = loader.loadTestsFromModule(test_modules[test_name])
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    else:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_modules.keys())}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        success = run_specific_test(sys.argv[1])
    else:
        # 运行所有测试
        print("=" * 60)
        print("Running all tests for 1024 Game - Pygame Edition")
        print("=" * 60)
        success = run_all_tests()
    
    # 退出代码
    sys.exit(0 if success else 1)
