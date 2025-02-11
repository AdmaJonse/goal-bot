"""
This module defines the Score class.
"""

class Score:
    """
    The score class. This class contains the score of the game and helper
    functions for using this data.
    """

    def __init__(self, data) -> None:
        self._home_goals  : int = data["homeScore"]
        self._away_goals  : int = data["awayScore"]

    @property
    def home_goals(self) -> int:
        """
        Getter for the home goals.
        """
        return self._home_goals

    @home_goals.setter
    def home_goals(self, home_goals : int):
        """
        Setter for the home goals.
        """
        self._home_goals = home_goals

    @property
    def away_goals(self) -> int:
        """
        Getter for the away goals.
        """
        return self._away_goals

    @away_goals.setter
    def away_goals(self, away_goals : int):
        """
        Setter for the away goals.
        """
        self._away_goals = away_goals
