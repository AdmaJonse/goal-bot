"""
Unit tests for Bluesky session and duplicate-history fetch behavior.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

from src.output.bluesky import BlueSky


def _make_feed_item(created_at: str, text: str) -> dict:
	return {
		"post": {
			"record": {
				"createdAt": created_at,
				"text": text,
			}
		}
	}


class TestBlueskySession:
	@patch("src.output.bluesky.schedule.get_current_date", return_value=datetime(2026, 5, 22, 12, 0, 0))
	@patch("src.output.bluesky.Authentication")
	@patch("src.output.bluesky.atproto.Client")
	def test_get_posts_for_reference_day_uses_bearer_token(self, _client_mock, _auth_mock, _date_mock):
		bluesky = BlueSky()
		bluesky.session = {"did": "did:plc:example"}
		bluesky._session_tokens = {"access": "token-123", "refresh": "refresh-123"}
		bluesky.duplicate_reference_date = datetime(2026, 5, 22, 12, 0, 0)

		response = MagicMock()
		response.json.return_value = {
			"feed": [
				_make_feed_item("2026-05-22T17:00:00Z", "Colorado: 1 Vegas: 0"),
				_make_feed_item("2026-05-23T01:00:00Z", "Colorado: 2 Vegas: 0"),
			]
		}
		response.raise_for_status.return_value = None

		with patch("src.output.bluesky.requests.get", return_value=response) as get_mock:
			posts = bluesky.get_posts_for_reference_day()

		assert posts == ["Colorado: 1 Vegas: 0", "Colorado: 2 Vegas: 0"]
		get_mock.assert_called_once()
		_, kwargs = get_mock.call_args
		assert kwargs["headers"]["Authorization"] == "Bearer token-123"
		assert kwargs["params"]["actor"] == "did:plc:example"

	@patch("src.output.bluesky.schedule.get_current_date", return_value=datetime(2026, 5, 22, 12, 0, 0))
	@patch("src.output.bluesky.Authentication")
	@patch("src.output.bluesky.atproto.Client")
	def test_get_posts_for_reference_day_skips_without_access_token(self, _client_mock, _auth_mock, _date_mock):
		bluesky = BlueSky()
		bluesky.session = {"did": "did:plc:example"}
		bluesky._session_tokens = {}

		with patch("src.output.bluesky.requests.get") as get_mock:
			posts = bluesky.get_posts_for_reference_day()

		assert posts == []
		get_mock.assert_not_called()
