"""
Unit tests for the `game_type` lookup and helper methods.

These tests validate that numeric game type codes map to the
correct `GameType` enum and that convenience predicates behave as expected.
"""

import unittest
from typing import Optional

from src.data import game_type

class TestGameType(unittest.TestCase):
    """
    Tests for `GameType` lookup and predicate helpers.
    """

    def test_exhibition(self):
        """
        Lookup for code 1 returns GameType.EXHIBITION.
        """
        expected : game_type.GameType           = game_type.GameType.EXHIBITION
        actual   : Optional[game_type.GameType] = game_type.game_type_lookup.get(1)
        assert expected == actual

    def test_regular_season(self):
        """
        Lookup for code 2 returns GameType.REGULAR_SEASON.
        """
        expected : game_type.GameType           = game_type.GameType.REGULAR_SEASON
        actual   : Optional[game_type.GameType] = game_type.game_type_lookup.get(2)
        assert expected == actual

    def test_playoffs(self):
        """
        Lookup for code 3 returns GameType.PLAYOFF.
        """
        expected : game_type.GameType           = game_type.GameType.PLAYOFF
        actual   : Optional[game_type.GameType] = game_type.game_type_lookup.get(3)
        assert expected == actual

    def test_is_exhibition(self):
        """
        `is_exhibition()` returns True for EXHIBITION game type.
        """
        value : game_type.GameType = game_type.GameType.EXHIBITION
        assert value.is_exhibition()

    def test_is_regular_season(self):
        """
        `is_regular_season()` returns True for REGULAR_SEASON game type.
        """
        value : game_type.GameType = game_type.GameType.REGULAR_SEASON
        assert value.is_regular_season()

    def test_is_playoffs(self):
        """
        `is_playoff()` returns True for PLAYOFF game type.
        """
        value : game_type.GameType = game_type.GameType.PLAYOFF
        assert value.is_playoff()
