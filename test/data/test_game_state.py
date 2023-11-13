"""
TODO
"""

import unittest
from typing import Optional

from src.data import game_state

class TestGameState(unittest.TestCase):
    """
    TODO
    """

    def test_future(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.FUTURE
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("FUT")
        assert expected == actual

    def test_pregame(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.PREGAME
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("PRE")
        assert expected == actual

    def test_soft_final(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.SOFT_FINAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("OVER")
        assert expected == actual

    def test_hard_final(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.HARD_FINAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("FINAL")
        assert expected == actual

    def test_official(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.OFFICIAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("OFF")
        assert expected == actual

    def test_live(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.LIVE
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("LIVE")
        assert expected == actual

    def test_critical(self):
        """
        TODO
        """
        expected : game_state.GameState           = game_state.GameState.CRITICAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("CRIT")
        assert expected == actual
