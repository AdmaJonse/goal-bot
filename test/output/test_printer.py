"""
Unit tests for the `Printer` outputter.
"""

import unittest

from src.output.printer import Printer


class TestPrinter(unittest.TestCase):
    """
    Tests that Printer methods return an ID dict and do not raise.
    """

    def test_post_and_reply_return_ids(self):
        """
        post(), reply(), post_with_media(), reply_with_media() return dicts with 'id'.
        """
        p = Printer()
        post_id = p.post("Hello")
        self.assertIsInstance(post_id, dict)
        self.assertIn("id", post_id)

        reply_id = p.reply({"id": "123"}, "Hi")
        self.assertIsInstance(reply_id, dict)
        self.assertIn("id", reply_id)

        pm = p.post_with_media("Hello", "media")
        self.assertIsInstance(pm, dict)
        self.assertIn("id", pm)

        rm = p.reply_with_media({"id": "123"}, "Hi", "media")
        self.assertIsInstance(rm, dict)
        self.assertIn("id", rm)


if __name__ == "__main__":
    unittest.main()
