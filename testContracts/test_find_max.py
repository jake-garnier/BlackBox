#!/usr/bin/env python3
"""
Test file for Find Maximum challenge.
This file contains unit tests that will verify if the submitted solution is correct.
"""

import unittest
import sys
import os

# Add the current directory to path so we can import the solution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestFindMax(unittest.TestCase):
    """Test cases for the find_max function."""
    
    def setUp(self):
        """Import the test_func from the submitted solution."""
        try:
            from solution import test_func as find_max
            self.find_max = find_max
        except ImportError:
            self.fail("Could not import test_func from solution.py")
    
    def test_basic_positive_numbers(self):
        """Test with basic positive numbers."""
        self.assertEqual(self.find_max([1, 3, 2]), 3)
        self.assertEqual(self.find_max([5, 1, 9, 3]), 9)
    
    def test_negative_numbers(self):
        """Test with negative numbers."""
        self.assertEqual(self.find_max([-1, -5, -2]), -1)
        self.assertEqual(self.find_max([-10, -3, -7]), -3)
    
    def test_mixed_numbers(self):
        """Test with mixed positive and negative numbers."""
        self.assertEqual(self.find_max([-1, 5, -3, 2]), 5)
        self.assertEqual(self.find_max([0, -1, 1]), 1)
    
    def test_single_element(self):
        """Test with single element list."""
        self.assertEqual(self.find_max([42]), 42)
        self.assertEqual(self.find_max([-5]), -5)
    
    def test_duplicates(self):
        """Test with duplicate maximum values."""
        self.assertEqual(self.find_max([3, 3, 1, 3]), 3)
        self.assertEqual(self.find_max([5, 5, 5]), 5)
    
    def test_zeros(self):
        """Test with zeros."""
        self.assertEqual(self.find_max([0, 0, 0]), 0)
        self.assertEqual(self.find_max([0, -1, -2]), 0)
    
    def test_large_numbers(self):
        """Test with large numbers."""
        self.assertEqual(self.find_max([1000000, 999999, 1000001]), 1000001)
    
    def test_floating_point(self):
        """Test with floating point numbers."""
        self.assertEqual(self.find_max([1.5, 2.7, 1.9]), 2.7)
        self.assertEqual(self.find_max([0.1, 0.01, 0.001]), 0.1)

def test_func():
    """
    Main test function that runs all unit tests.
    Returns True if all tests pass, False otherwise.
    """
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFindMax)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Return True if all tests passed
    return result.wasSuccessful()

if __name__ == '__main__':
    success = test_func()
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)