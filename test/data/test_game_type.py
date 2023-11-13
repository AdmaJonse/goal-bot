"""
TODO
"""

import unittest
from typing import Optional

from src.data import game_type

class TestGameType(unittest.TestCase):
    """
    TODO
    """

    def test_exhibition(self):
        """
        TODO
        """
        expected : game_type.GameType           = game_type.GameType.EXHIBITION
        actual   : Optional[game_type.GameType] = game_type.game_type_lookup.get(1)
        assert expected == actual

    def test_regular_season(self):
        """
        TODO
        """
        expected : game_type.GameType           = game_type.GameType.REGULAR_SEASON
        actual   : Optional[game_type.GameType] = game_type.game_type_lookup.get(2)
        assert expected == actual

    def test_playoffs(self):
        """
        TODO
        """
        expected : game_type.GameType           = game_type.GameType.PLAYOFF
        actual   : Optional[game_type.GameType] = game_type.game_type_lookup.get(3)
        assert expected == actual

    def test_is_exhibition(self):
        """
        TODO
        """
        value : game_type.GameType = game_type.GameType.EXHIBITION
        assert value.is_exhibition()

    def test_is_regular_season(self):
        """
        TODO
        """
        value : game_type.GameType = game_type.GameType.REGULAR_SEASON
        assert value.is_regular_season()

    def test_is_playoffs(self):
        """
        TODO
        """
        value : game_type.GameType = game_type.GameType.PLAYOFF
        assert value.is_playoff()
