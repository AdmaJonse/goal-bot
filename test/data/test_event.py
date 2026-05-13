"""
Unit tests for src.data.event
"""

import unittest
from typing import Any, Optional

from src.data import event
from src.data.game_type import GameType
from src.data.period import Period
from src.data.highlight import Highlight


def make_period(number: int = 1) -> Period:
    """
    Create a minimal valid Period instance for tests.
    """
    return Period(GameType.REGULAR_SEASON, {
        "periodType": "REG",
        "number": number,
    })


def base_event_data(**overrides) -> dict:
    """
    Minimal valid event payload for Event construction.
    """
    data = {
        "timeInPeriod": "01:00",
        "homeScore": 0,
        "awayScore": 0,
    }
    data.update(overrides)
    return data


class TestEvent(unittest.TestCase):
    """
    Tests for play-by-play event parsing helpers and Event behavior.
    """

    # ---------- to_name ----------

    def test_to_name(self):
        data: Any = {
            "playerId": 8477942,
            "firstName": {"default": "Kevin"},
            "lastName": {"default": "Fiala"},
            "assistToDate": 1,
        }
        expected: Optional[str] = "Kevin Fiala"
        actual: Optional[str] = event.to_name(data)
        self.assertEqual(expected, actual)

    def test_to_name_missing_fields(self):
        self.assertIsNone(event.to_name({"firstName": {"default": "Kevin"}}))
        self.assertIsNone(event.to_name({"lastName": {"default": "Fiala"}}))
        self.assertIsNone(event.to_name({}))

    # ---------- primary assist ----------

    def test_get_primary_assist(self):
        data: Any = {
            "assists": [
                {
                    "playerId": 8477942,
                    "firstName": {"default": "Kevin"},
                    "lastName": {"default": "Fiala"},
                },
                {
                    "playerId": 8481606,
                    "firstName": {"default": "Jordan"},
                    "lastName": {"default": "Spence"},
                },
            ]
        }
        expected: str = "Kevin Fiala"
        actual: Optional[str] = event.get_primary_assist(data)
        self.assertEqual(expected, actual)

    def test_get_invalid_primary_assist(self):
        self.assertIsNone(event.get_primary_assist({}))

    # ---------- secondary assist ----------

    def test_get_secondary_assist(self):
        data: Any = {
            "assists": [
                {
                    "playerId": 8477942,
                    "firstName": {"default": "Kevin"},
                    "lastName": {"default": "Fiala"},
                },
                {
                    "playerId": 8481606,
                    "firstName": {"default": "Jordan"},
                    "lastName": {"default": "Spence"},
                },
            ]
        }
        expected: str = "Jordan Spence"
        actual: Optional[str] = event.get_secondary_assist(data)
        self.assertEqual(expected, actual)

    def test_get_invalid_secondary_assist(self):
        self.assertIsNone(event.get_secondary_assist({}))

    def test_get_missing_secondary_assist(self):
        data: Any = {
            "assists": [
                {
                    "firstName": {"default": "Kevin"},
                    "lastName": {"default": "Fiala"},
                }
            ]
        }
        self.assertIsNone(event.get_secondary_assist(data))

    # ---------- team ----------

    def test_get_team_valid(self):
        data = {"teamAbbrev": {"default": "EDM"}}
        self.assertEqual("Edmonton", event.get_team(data))

    def test_get_team_invalid(self):
        self.assertIsNone(event.get_team({"teamAbbrev": {"default": "XXX"}}))

    def test_get_team_missing(self):
        self.assertIsNone(event.get_team({}))

    # ---------- strength ----------

    def test_get_strength(self):
        self.assertEqual("powerPlay", event.get_strength({"strength": "powerPlay"}))

    def test_get_strength_missing(self):
        self.assertIsNone(event.get_strength({}))

    # ---------- empty net ----------

    def test_is_empty_net_true(self):
        self.assertTrue(event.is_empty_net({"goalModifier": "empty-net"}))

    def test_is_empty_net_false(self):
        self.assertFalse(event.is_empty_net({"goalModifier": "deflected"}))

    def test_is_empty_net_missing(self):
        self.assertFalse(event.is_empty_net({}))

    # ---------- time remaining ----------

    def test_get_time_remaining(self):
        period = make_period(1)
        data = {"timeInPeriod": "05:30"}
        self.assertEqual("14:30", event.get_time_remaining(period, data))

    # ---------- Event comparison logic ----------

    def test_is_scorer_modified(self):
        period = make_period(1)

        prev = event.Event(period, base_event_data(
            firstName={"default": "Connor"},
            lastName={"default": "McDavid"},
        ))

        curr = event.Event(period, base_event_data(
            firstName={"default": "Leon"},
            lastName={"default": "Draisaitl"},
        ))

        self.assertTrue(curr.is_scorer_modified(prev))

    def test_primary_assist_added(self):
        period = make_period(1)

        prev = event.Event(period, base_event_data())

        curr = event.Event(period, base_event_data(
            assists=[
                {
                    "firstName": {"default": "Kevin"},
                    "lastName": {"default": "Fiala"},
                }
            ]
        ))

        self.assertTrue(curr.is_primary_assist_added(prev))

    def test_secondary_assist_added(self):
        period = make_period(1)

        prev = event.Event(period, base_event_data(
            assists=[
                {
                    "firstName": {"default": "Kevin"},
                    "lastName": {"default": "Fiala"},
                }
            ]
        ))

        curr = event.Event(period, base_event_data(
            assists=[
                {
                    "firstName": {"default": "Kevin"},
                    "lastName": {"default": "Fiala"},
                },
                {
                    "firstName": {"default": "Jordan"},
                    "lastName": {"default": "Spence"},
                },
            ]
        ))

        self.assertTrue(curr.is_secondary_assist_added(prev))


class DummyTeam:
    def __init__(self, location, abbreviation="", hashtag="", playoff_hashtag=""):
        self.location = location
        self.abbreviation = abbreviation
        self.hashtag = hashtag
        self.playoff_hashtag = playoff_hashtag


class DummyGameData:
    def __init__(self, home_location, away_location):
        self.home = DummyTeam(home_location, "HOME", "#Home")
        self.away = DummyTeam(away_location, "AWAY", "#Away")

    def get_team_string(self, team):
        if team == self.home.location:
            return self.home.location
        if team == self.away.location:
            return self.away.location
        return ""

    @property
    def hashtags(self):
        return f"#{self.away.abbreviation}vs{self.home.abbreviation} {self.home.hashtag} {self.away.hashtag}"


class TestHighlightShootout(unittest.TestCase):
    """
    Tests for formatting of highlight posts during special periods.
    """

    def test_shootout_goal_uses_shootout_template(self):
        # Create a shootout period
        period = Period(None, {"periodType": "SO", "number": 0})

        # Minimal event data for a shootout goal
        data = {
            "timeInPeriod": "00:00",
            "homeScore": 0,
            "awayScore": 1,
            "teamAbbrev": {"default": "EDM"},
            "firstName": {"default": "John"},
            "lastName": {"default": "Doe"},
        }

        evt = event.Event(period, data)

        # Construct a dummy GameData-like object
        game_data = DummyGameData("Edmonton", "Calgary")

        # Create a Highlight instance without running __init__ (avoids network calls)
        hl = Highlight.__new__(Highlight)
        hl.event = evt
        hl.game_data = game_data

        post = hl.get_post()

        # Ensure shootout wording appears in the generated post
        self.assertIn(f"Scored by {evt.scorer} in the shootout.", post)
