"""
This module handles parsing of the JSON game data.
"""

from src.parser.parser import Parser
from src.data.game_data import GameData

class GameDataParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int):
        super().__init__(game_id, "/feed/live")


    def parse(self) -> GameData:
        """
        Parse the static data for this game.
        """
        self.get_data()
        return GameData(self.data)
