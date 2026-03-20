"""
Unit tests for utility helpers in `src.utils`.
"""

import unittest

from src.utils import strip_text


class TestUtils(unittest.TestCase):
    """
    Tests for `strip_text` behavior with matching and non-matching input.
    """

    def test_strip_text_matches_block(self):
        """
        When the text contains back-to-back score lines, they are returned combined.
        """
        text = "Header\nHome: 3\nAway: 2\nFooter"
        result = strip_text(text)
        self.assertEqual(result, "Home: 3 Away: 2")

    def test_strip_text_no_match(self):
        """
        If no two-line score block exists, empty string is returned.
        """
        text = "No scores here"
        result = strip_text(text)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
