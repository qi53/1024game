import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    from tests import test_config
    from tests import test_storage
    from tests import test_game_core
    from tests import test_particles_audio
    from tests import test_ui
    
    suite.addTests(loader.loadTestsFromModule(test_config))
    suite.addTests(loader.loadTestsFromModule(test_storage))
    suite.addTests(loader.loadTestsFromModule(test_game_core))
    suite.addTests(loader.loadTestsFromModule(test_particles_audio))
    suite.addTests(loader.loadTestsFromModule(test_ui))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
