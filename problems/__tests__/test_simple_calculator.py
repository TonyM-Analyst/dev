import unittest
import re

class StringCalculator:
    def add(self, numbers: str) -> int:
        if not numbers:
            return 0
        parts = re.split(r",|\n", numbers)
        return sum(int(part) for part in parts)

class TestStringCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = StringCalculator()

    def test_empty_string_returns_0(self):
        self.assertEqual(self.calc.add(""), 0)

    def test_single_number(self):
        self.assertEqual(self.calc.add("1"), 1)

    def test_two_numbers(self):
        self.assertEqual(self.calc.add("1,2"), 3)

    def test_newline_and_comma_delimiters(self):
        self.assertEqual(self.calc.add("1\n2,3"), 6)

if __name__ == "__main__":
    unittest.main()
