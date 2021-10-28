"""
==============
test_noop.py
==============

No-op test to have at least one test result.
"""
import unittest


class TestNoop(unittest.TestCase):

    def test_noop(self):
        self.assertTrue(True)