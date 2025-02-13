"""
This module defines the enumeration for game types.
"""

from enum import Enum
from typing import Dict

class GameType(Enum):
    """
    Enumerated type capturing the possible states of a game.
    """
    EXHIBITION = 1
    REGULAR_SEASON = 2
    PLAYOFF = 3
    NATIONS = 19

    def is_exhibition(self) -> bool:
        """
        Return a boolean indicating whether or not this is an exhibition game.
        """
        return self == GameType.EXHIBITION

    def is_regular_season(self) -> bool:
        """
        Return a boolean indicating whether or not this is a regular season game.
        """
        return self == GameType.REGULAR_SEASON

    def is_playoff(self) -> bool:
        """
        Return a boolean indicating whether or not this is a playoff game.
        """
        return self == GameType.PLAYOFF

    def is_four_nations(self) -> bool:
        """
        
        """
        return self == GameType.NATIONS


game_type_lookup : Dict[int, GameType] = {
    1: GameType.EXHIBITION,
    2: GameType.REGULAR_SEASON,
    3: GameType.PLAYOFF,
    19: GameType.NATIONS
}
