"""
This module handles parsing of the JSON game data.
"""

from typing import Optional

from src.parser.parser import Parser
from src.data.game_data import GameData
from src.logger import log

class GameDataParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int):
        super().__init__(game_id, "/play-by-play")


    def parse(self) -> Optional[GameData]:
        """
        Parse the static data for this game.
        """
        self.get_data()
        if self.data:
            try:
                return GameData(self.data)
            except (KeyError, TypeError, ValueError) as exc:
                log.warning("Invalid game data: " + str(exc))
        return None
