"""
Unit tests for src.parser.content
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from unittest.mock import MagicMock

from src.parser.content import ContentParser


class TestContentParser(unittest.TestCase):
    """
    Tests for robust content parsing behavior.
    """

    @patch("src.parser.content.Highlight")
    @patch("src.parser.content.command_queue")
    def test_parse_skips_malformed_highlight_payload(self, mock_queue, mock_highlight):
        parser = ContentParser(123, datetime.now(timezone.utc))

        parser.get_data = lambda: None
        parser.data = {
            "summary": {
                "scoring": [
                    {
                        "goals": [
                            {
                                "highlightClip": "999",
                                "homeScore": "3",
                                "awayScore": "3",
                            }
                        ]
                    }
                ]
            }
        }

        mock_highlight.side_effect = KeyError("homeTeam")

        parser.parse()

        mock_queue.enqueue.assert_not_called()

    @patch("src.parser.content.output.has_posted_today")
    @patch("src.parser.content.Highlight")
    @patch("src.parser.content.command_queue")
    def test_parse_does_not_retry_when_now_duplicate(self,
                                                     mock_queue,
                                                     mock_highlight,
                                                     mock_has_posted_today):
        parser = ContentParser(123, datetime.now(timezone.utc))

        event_obj = object()
        existing = MagicMock()
        existing.id = 999
        existing.event = event_obj
        existing.post_id = {}
        existing.is_pending = False
        existing.get_post.return_value = "Goal text\n\nColorado: 1 Minnesota: 0"
        parser.highlight_list.add(existing)

        incoming = MagicMock()
        incoming.id = 999
        incoming.event = event_obj
        mock_highlight.return_value = incoming

        mock_has_posted_today.return_value = {"bluesky": True, "twitter": True}

        parser.get_data = lambda: None
        parser.data = {
            "summary": {
                "scoring": [
                    {
                        "goals": [
                            {
                                "highlightClip": "999",
                                "homeScore": "1",
                                "awayScore": "0",
                            }
                        ]
                    }
                ]
            }
        }

        parser.parse()

        mock_queue.enqueue.assert_not_called()
        self.assertEqual(existing.post_id, {"_duplicate": None})

    @patch("src.parser.content.Highlight")
    @patch("src.parser.content.command_queue")
    def test_parse_does_not_retry_while_already_queued(self,
                                                       mock_queue,
                                                       mock_highlight):
        parser = ContentParser(123, datetime.now(timezone.utc))

        event_obj = object()
        existing = MagicMock()
        existing.id = 999
        existing.event = event_obj
        existing.post_id = {"_queued": None}
        existing.is_pending = False
        parser.highlight_list.add(existing)

        incoming = MagicMock()
        incoming.id = 999
        incoming.event = event_obj
        mock_highlight.return_value = incoming

        parser.get_data = lambda: None
        parser.data = {
            "summary": {
                "scoring": [
                    {
                        "goals": [
                            {
                                "highlightClip": "999",
                                "homeScore": "1",
                                "awayScore": "0",
                            }
                        ]
                    }
                ]
            }
        }

        parser.parse()

        mock_queue.enqueue.assert_not_called()
        self.assertEqual(existing.post_id, {"_queued": None})


if __name__ == "__main__":
    unittest.main()
