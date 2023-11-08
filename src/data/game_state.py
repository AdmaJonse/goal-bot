"""
This module defines the enumeration for game states.
"""

from enum import Enum

class GameState(Enum):
    """
    Enumerated type capturing the possible states of a game.
    """
    FUTURE = 1
    PREGAME = 2
    SOFT_FINAL = 3
    HARD_FINAL = 4
    OFFICIAL = 5
    LIVE = 6
    CRITICAL = 7  # Not sure what this one means

game_state_lookup = {
    "FUT": GameState.FUTURE,
    "PRE": GameState.PREGAME,
    "OVER": GameState.SOFT_FINAL,
    "FINAL": GameState.HARD_FINAL,
    "OFF": GameState.OFFICIAL,
    "LIVE": GameState.LIVE,
    "CRIT": GameState.CRITICAL
}
