"""
This module defines the enumeration for game types.
"""

from enum import Enum
from typing import Dict

class GameType(Enum):
    """
    Enumerated type capturing the possible states of a game.

    https://github.com/Zmalski/NHL-API-Reference/issues/23#issuecomment-2492925102

    1 - pre-season (1,998 games)
    2 - regular season (63,930)
    3 - playoffs (5,017)
    4 - all-star (84)
    6 - World Cup group stage (36)
    7 - World Cup knockout stage (18)
    8 - World Cup pre-tournament (12)
    9 - Olympics (168)
    10 - Young Stars (2)
    12 - Canadian All-Stars vs. American All-Stars (1) and Team King vs. Team Kloss (1) -> 2 total
    13 - games lost to the 2004 labor dispute (1,230)
    14 - Canada Cup (93)
    18 - appears to be exhibition games played overseas (36)
    19 - Four Nations Face-off (6)
    """
    EXHIBITION = 1
    REGULAR_SEASON = 2
    PLAYOFF = 3
    FOUR_NATIONS = 19
    FOUR_NATIONS_FINAL = 20

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
        Return a boolean indicating whether or not this is a Four Nations
        tournament game.
        """
        return self in (GameType.FOUR_NATIONS, GameType.FOUR_NATIONS_FINAL)

    def is_four_nations_final(self) -> bool:
        """
        Return a boolean indicating whether or not this is the Four Nations
        tournament final game.
        """
        return self == GameType.FOUR_NATIONS_FINAL


game_type_lookup : Dict[int, GameType] = {
    1:  GameType.EXHIBITION,
    2:  GameType.REGULAR_SEASON,
    3:  GameType.PLAYOFF,
    19: GameType.FOUR_NATIONS,
    20: GameType.FOUR_NATIONS_FINAL
}
