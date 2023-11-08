"""
This module handles parsing of the JSON game data.
"""

from typing import Optional

from src.parser.parser import Parser
from src.data.game_data import GameData

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
            return GameData(self.data)
        return None
