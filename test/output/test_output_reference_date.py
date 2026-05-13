"""
Unit tests for duplicate reference date propagation in Output.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.output.output import Output


class _FakeConfiguredOutputter:
    def __init__(self, name: str) -> None:
        self._name = name
        self.reference_dates = []

    def name(self) -> str:
        return self._name

    def set_duplicate_reference_date(self, value) -> None:
        self.reference_dates.append(value)

    def post(self, _text: str):
        return None

    def reply(self, _parent, _text: str):
        return None

    def post_with_media(self, _text: str, _media: str):
        return None

    def reply_with_media(self, _parent, _text: str, _media: str):
        return None

    def has_posted(self, _text: str) -> bool:
        return False

    def has_posted_today(self, _query: str = "") -> bool:
        return False

    def clear_posts(self) -> None:
        return None


class TestOutputReferenceDate(unittest.TestCase):
    @patch("src.output.output.Tweeter")
    @patch("src.output.output.BlueSky")
    def test_set_duplicate_reference_date_reconfigures_outputters(self,
                                                                  mock_bluesky,
                                                                  mock_tweeter):
        bluesky_initial = _FakeConfiguredOutputter("bluesky")
        twitter_initial = _FakeConfiguredOutputter("twitter")
        bluesky_updated = _FakeConfiguredOutputter("bluesky")
        twitter_updated = _FakeConfiguredOutputter("twitter")

        mock_bluesky.side_effect = [bluesky_initial, bluesky_updated]
        mock_tweeter.side_effect = [twitter_initial, twitter_updated]

        output = Output()
        initial_reference_date = output._duplicate_reference_date
        target_date = datetime(2026, 5, 4, tzinfo=timezone.utc)

        output.set_duplicate_reference_date(target_date)

        self.assertEqual(bluesky_initial.reference_dates, [initial_reference_date])
        self.assertEqual(twitter_initial.reference_dates, [initial_reference_date])
        self.assertEqual(bluesky_updated.reference_dates, [target_date])
        self.assertEqual(twitter_updated.reference_dates, [target_date])
        self.assertIs(output.outputters[0], bluesky_updated)
        self.assertIs(output.outputters[1], twitter_updated)


if __name__ == "__main__":
    unittest.main()
