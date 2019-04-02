import os
import sys
import unittest


def additional_tests():
    setup_file = sys.modules['__main__'].__file__
    setup_dir = os.path.abspath(os.path.dirname(setup_file))
    tests_dir = os.path.join(setup_dir, "_Tests")
    return unittest.defaultTestLoader.discover(start_dir=tests_dir, pattern='*_test.py')
