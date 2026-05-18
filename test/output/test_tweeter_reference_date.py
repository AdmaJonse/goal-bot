"""
Unit tests for Twitter duplicate reference date refresh behavior.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.output.tweeter import Tweeter


class TestTweeterReferenceDate(unittest.TestCase):
    def test_set_duplicate_reference_date_skips_refresh_when_date_is_unchanged(self):
        tweeter = object.__new__(Tweeter)
        same_date = datetime(2026, 5, 13, tzinfo=timezone.utc)
        tweeter.duplicate_reference_date = same_date
        tweeter.posts = ["existing post"]

        with patch.object(tweeter, "get_posts_for_reference_day") as fetch_mock:
            tweeter.set_duplicate_reference_date(same_date)

        fetch_mock.assert_not_called()
        self.assertEqual(tweeter.duplicate_reference_date, same_date)
        self.assertEqual(tweeter.posts, ["existing post"])

    def test_set_duplicate_reference_date_refreshes_when_date_changes(self):
        tweeter = object.__new__(Tweeter)
        initial_date = datetime(2026, 5, 13, tzinfo=timezone.utc)
        target_date = datetime(2026, 5, 14, tzinfo=timezone.utc)
        tweeter.duplicate_reference_date = initial_date
        tweeter.posts = ["existing post"]

        with patch.object(tweeter, "get_posts_for_reference_day", return_value=["refreshed post"]) as fetch_mock:
            tweeter.set_duplicate_reference_date(target_date)

        fetch_mock.assert_called_once_with()
        self.assertEqual(tweeter.duplicate_reference_date, target_date)
        self.assertEqual(tweeter.posts, ["refreshed post"])


if __name__ == "__main__":
    unittest.main()
