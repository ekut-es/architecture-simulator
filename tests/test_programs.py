import unittest

from tests.py_programs.fibonacci_recursive import (
    fibonacci_recursive,
    fibonacci_recursive_2,
)


class TestPrograms(unittest.TestCase):
    def test_fibonacci_recursive(self):
        self.assertEqual(int(fibonacci_recursive(-5)), 0)
        self.assertEqual(int(fibonacci_recursive(0)), 0)
        self.assertEqual(int(fibonacci_recursive(1)), 1)
        self.assertEqual(int(fibonacci_recursive(2)), 1)
        self.assertEqual(int(fibonacci_recursive(3)), 2)
        self.assertEqual(int(fibonacci_recursive(4)), 3)
        self.assertEqual(int(fibonacci_recursive(5)), 5)
        self.assertEqual(int(fibonacci_recursive(6)), 8)
        self.assertEqual(int(fibonacci_recursive(7)), 13)

    def test_fibonacci_recursive_2(self):
        self.assertEqual(int(fibonacci_recursive_2(0)), 0)
        self.assertEqual(int(fibonacci_recursive_2(1)), 1)
        self.assertEqual(int(fibonacci_recursive_2(2)), 1)
        self.assertEqual(int(fibonacci_recursive_2(3)), 2)
        self.assertEqual(int(fibonacci_recursive_2(4)), 3)
        self.assertEqual(int(fibonacci_recursive_2(5)), 5)
        self.assertEqual(int(fibonacci_recursive_2(6)), 8)
        self.assertEqual(int(fibonacci_recursive_2(7)), 13)
