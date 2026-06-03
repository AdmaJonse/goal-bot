"""
Unit tests for PostHighlight retry state handling.
"""

import unittest
from unittest.mock import patch
from typing import Dict, Optional

from src.command.post_highlight import PostHighlight


class _FakeHighlight:
    def __init__(self) -> None:
        self.video = "https://example.test/video"
        self.post_id: Dict[str, Optional[Dict[str, str]]] = {}
        self.is_pending = False

    def get_post(self):
        return "Goal text\n\nColorado: 3 Minnesota: 2"

    def get_footer(self):
        return "Colorado: 3 Minnesota: 2"


class TestPostHighlight(unittest.TestCase):
    @patch("src.command.post_highlight.output.post_with_media")
    @patch("src.command.post_highlight.output.has_posted_today")
    def test_transient_failure_resets_post_id_for_retry(self, has_posted_today_mock, post_with_media_mock):
        has_posted_today_mock.return_value = {"bluesky": False, "twitter": False}
        post_with_media_mock.return_value = {"bluesky": None, "twitter": None}

        highlight = _FakeHighlight()
        command = PostHighlight(highlight)
        command.execute()

        self.assertEqual(highlight.post_id, {})

    @patch("src.command.post_highlight.output.post_with_media")
    @patch("src.command.post_highlight.output.has_posted_today")
    def test_all_duplicate_keeps_terminal_state(self, has_posted_today_mock, post_with_media_mock):
        has_posted_today_mock.return_value = {"bluesky": True, "twitter": True}
        post_with_media_mock.return_value = {"bluesky": None, "twitter": None}

        highlight = _FakeHighlight()
        command = PostHighlight(highlight)
        command.execute()

        self.assertEqual(
            highlight.post_id,
            {"bluesky": None, "twitter": None, "_duplicate": None},
        )

    @patch("src.command.post_highlight.output.post_with_media")
    @patch("src.command.post_highlight.output.has_posted_today")
    def test_partial_duplicate_failure_stops_retry_loop(self, has_posted_today_mock, post_with_media_mock):
        has_posted_today_mock.return_value = {"bluesky": False, "twitter": True}
        post_with_media_mock.return_value = {"bluesky": None, "twitter": None}

        highlight = _FakeHighlight()
        command = PostHighlight(highlight)
        command.execute()

        self.assertEqual(
            highlight.post_id,
            {"bluesky": None, "twitter": None, "_duplicate": None},
        )

    @patch("src.command.post_highlight.output.post_with_media")
    @patch("src.command.post_highlight.output.has_posted_today")
    def test_duplicate_status_is_passed_to_post_with_media(self, has_posted_today_mock, post_with_media_mock):
        duplicate_status = {"bluesky": False, "twitter": True}
        has_posted_today_mock.return_value = duplicate_status
        post_with_media_mock.return_value = {"bluesky": None, "twitter": None}

        highlight = _FakeHighlight()
        command = PostHighlight(highlight)
        command.execute()

        post_with_media_mock.assert_called_once_with(
            highlight.get_post(),
            highlight.video,
            duplicate_status,
        )
        self.assertFalse(highlight.is_pending)


if __name__ == "__main__":
    unittest.main()
