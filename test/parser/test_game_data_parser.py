"""
Unit tests for src.parser.game_data
"""

import unittest

from src.parser.game_data import GameDataParser


class TestGameDataParser(unittest.TestCase):
    """
    Tests for resilient game data parsing.
    """

    def test_parse_returns_none_when_home_team_missing(self):
        parser = GameDataParser(123)

        def _fake_get_data():
            parser.data = {
                "awayTeam": {
                    "abbrev": "MTL",
                    "commonName": {"default": "Canadiens"},
                },
                "startTimeUTC": "2026-04-19T20:00:00Z",
            }

        parser.get_data = _fake_get_data

        self.assertIsNone(parser.parse())

    def test_parse_returns_game_data_when_required_fields_exist(self):
        parser = GameDataParser(123)

        def _fake_get_data():
            parser.data = {
                "homeTeam": {
                    "abbrev": "TBL",
                    "commonName": {"default": "Lightning"},
                },
                "awayTeam": {
                    "abbrev": "MTL",
                    "commonName": {"default": "Canadiens"},
                },
                "startTimeUTC": "2026-04-19T20:00:00Z",
            }

        parser.get_data = _fake_get_data

        game_data = parser.parse()

        self.assertIsNotNone(game_data)
        self.assertEqual("Tampa Bay", game_data.home.location)
        self.assertEqual("Montreal", game_data.away.location)


if __name__ == "__main__":
    unittest.main()
