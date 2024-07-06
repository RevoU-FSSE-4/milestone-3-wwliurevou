import unittest

# Define the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Add test modules or test cases
suite.addTests(loader.discover('tests', pattern='test_*.py'))

# Define a runner and run the suite
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)