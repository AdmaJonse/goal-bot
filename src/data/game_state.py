"""
This module defines the enumeration for game states.
"""

from enum import Enum

class GameState(Enum):
    """
    Enumerated type capturing the possible states of a game.
    """
    SCHEDULED = 1
    LIVE = 2
    END = 3
    OFFICIAL = 4
