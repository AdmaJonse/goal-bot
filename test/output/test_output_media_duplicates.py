"""
Unit tests for media duplicate handling in output coordinator.
"""

import unittest
from unittest.mock import patch

from src.output import output as output_module


class _FakeOutputter:
    def __init__(self, name: str) -> None:
        self._name = name
        self.post_with_media_calls = 0
        self.reply_with_media_calls = 0
        self.duplicate = False

    def name(self) -> str:
        return self._name

    def has_posted(self, _text: str) -> bool:
        return self.duplicate

    def post_with_media(self, _text: str, _media: str):
        self.post_with_media_calls += 1
        return {"id": self._name + "-id"}

    def reply_with_media(self, _parent, _text: str, _media: str):
        self.reply_with_media_calls += 1
        return {"id": self._name + "-id"}

    def clear_posts(self) -> None:
        return None

    def set_duplicate_reference_date(self, _value) -> None:
        return None


class TestOutputMediaDuplicates(unittest.TestCase):
    def setUp(self) -> None:
        self.twitter_outputter = _FakeOutputter("twitter")
        self.bluesky_outputter = _FakeOutputter("bluesky")
        output_module.output._outputters = [self.bluesky_outputter, self.twitter_outputter]

    @patch("src.output.output._download_media_once", return_value="local.mp4")
    @patch("src.output.output._is_remote_media", return_value=False)
    def test_twitter_duplicate_skips_only_twitter(self, _remote_mock, download_mock):
        self.twitter_outputter.duplicate = True
        media = "https://players.brightcove.net/x/y/index.html?videoId=6394299474112"

        result = output_module.post_with_media("Minnesota goal", media)

        self.assertIsNone(result.get("twitter"))
        self.assertIsNotNone(result.get("bluesky"))
        self.assertEqual(self.twitter_outputter.post_with_media_calls, 0)
        self.assertEqual(self.bluesky_outputter.post_with_media_calls, 1)
        download_mock.assert_called_once()

    @patch("src.output.output._download_media_once", return_value="local.mp4")
    @patch("src.output.output._is_remote_media", return_value=False)
    def test_non_twitter_duplicate_skips_only_that_output(self, _remote_mock, download_mock):
        self.bluesky_outputter.duplicate = True
        media = "https://players.brightcove.net/x/y/index.html?videoId=6394299474112"

        result = output_module.post_with_media("Minnesota goal", media)

        self.assertIsNotNone(result.get("twitter"))
        self.assertIsNone(result.get("bluesky"))
        self.assertEqual(self.twitter_outputter.post_with_media_calls, 1)
        self.assertEqual(self.bluesky_outputter.post_with_media_calls, 0)
        download_mock.assert_called_once()

    @patch("src.output.output._download_media_once", return_value="local.mp4")
    @patch("src.output.output._is_remote_media", return_value=False)
    def test_reply_with_media_duplicate_skips_only_one_output(self, _remote_mock, download_mock):
        self.twitter_outputter.duplicate = True
        parents = {"twitter": {"id": "t1"}, "bluesky": {"uri": "u1", "cid": "c1"}}

        result = output_module.reply_with_media(
            parents,
            "Goal update\n\nColorado: 4 Minnesota: 3",
            "https://players.brightcove.net/x/y/index.html?videoId=6394299474112",
        )

        self.assertIsNone(result.get("twitter"))
        self.assertIsNotNone(result.get("bluesky"))
        self.assertEqual(self.twitter_outputter.reply_with_media_calls, 0)
        self.assertEqual(self.bluesky_outputter.reply_with_media_calls, 1)
        download_mock.assert_called_once()

    @patch("src.output.output._download_media_once")
    @patch("src.output.output._is_remote_media", return_value=False)
    def test_reply_with_media_all_duplicates_skips_download(self, _remote_mock, download_mock):
        self.twitter_outputter.duplicate = True
        self.bluesky_outputter.duplicate = True
        parents = {"twitter": {"id": "t1"}, "bluesky": {"uri": "u1", "cid": "c1"}}

        result = output_module.reply_with_media(
            parents,
            "Goal update\n\nColorado: 4 Minnesota: 3",
            "https://players.brightcove.net/x/y/index.html?videoId=6394299474112",
        )

        self.assertIsNone(result.get("twitter"))
        self.assertIsNone(result.get("bluesky"))
        self.assertEqual(self.twitter_outputter.reply_with_media_calls, 0)
        self.assertEqual(self.bluesky_outputter.reply_with_media_calls, 0)
        download_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
