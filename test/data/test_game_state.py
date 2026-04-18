"""
Unit tests for the `game_state` lookup mapping.

These tests verify that the string codes map to the correct
`GameState` enum values used throughout the application.
"""

import unittest
from typing import Optional

from src.data import game_state

class TestGameState(unittest.TestCase):
    """
    Tests mapping of game state codes to the `GameState` enum.
    """

    def test_future(self):
        """
        Lookup for the 'FUT' code returns GameState.FUTURE.
        """
        expected : game_state.GameState           = game_state.GameState.FUTURE
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("FUT")
        assert expected == actual

    def test_pregame(self):
        """
        Lookup for the 'PRE' code returns GameState.PREGAME.
        """
        expected : game_state.GameState           = game_state.GameState.PREGAME
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("PRE")
        assert expected == actual

    def test_soft_final(self):
        """
        Lookup for the 'OVER' code returns GameState.SOFT_FINAL.
        """
        expected : game_state.GameState           = game_state.GameState.SOFT_FINAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("OVER")
        assert expected == actual

    def test_hard_final(self):
        """
        Lookup for the 'FINAL' code returns GameState.HARD_FINAL.
        """
        expected : game_state.GameState           = game_state.GameState.HARD_FINAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("FINAL")
        assert expected == actual

    def test_official(self):
        """
        Lookup for the 'OFF' code returns GameState.OFFICIAL.
        """
        expected : game_state.GameState           = game_state.GameState.OFFICIAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("OFF")
        assert expected == actual

    def test_live(self):
        """
        Lookup for the 'LIVE' code returns GameState.LIVE.
        """
        expected : game_state.GameState           = game_state.GameState.LIVE
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("LIVE")
        assert expected == actual

    def test_critical(self):
        """
        Lookup for the 'CRIT' code returns GameState.CRITICAL.
        """
        expected : game_state.GameState           = game_state.GameState.CRITICAL
        actual   : Optional[game_state.GameState] = game_state.game_state_lookup.get("CRIT")
        assert expected == actual
