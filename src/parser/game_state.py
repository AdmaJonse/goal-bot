"""
This module handles parsing of the game's current state from JSON live feed data.
"""

from typing import Any
from src.data.game_state import GameState
from src.parser.parser import Parser

class GameStateParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int):
        super().__init__(game_id, "/feed/live")


    def parse(self) -> GameState:
        """
        Parse the static data for this game.
        """
        self.get_data()

        is_live      : bool = False
        is_end       : bool = False
        is_official  : bool = False

        if self.data:
            plays : Any = self.data["liveData"]["plays"]["allPlays"]
            if plays:
                for play in plays:
                    event : str = play["result"]["event"]
                    if event == "Period Start":
                        is_live = True
                    elif event == "Game End":
                        is_end = True
                    elif event == "Game Official":
                        is_official = True

        if is_official:
            return GameState.OFFICIAL

        if is_end:
            return GameState.END

        if is_live:
            return GameState.LIVE

        return GameState.SCHEDULED
