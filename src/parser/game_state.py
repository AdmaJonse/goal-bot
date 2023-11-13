"""
This module handles parsing of the game's current state from JSON live feed data.
"""

from src.data.game_state import GameState, game_state_lookup
from src.parser.parser import Parser

class GameStateParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int):
        super().__init__(game_id, "/play-by-play")


    def parse(self) -> GameState:
        """
        Parse the static data for this game.
        """
        self.get_data()
        if self.data is not None:
            state : str = self.data.get("gameState", "")
            return game_state_lookup.get(state, GameState.FUTURE)
        return GameState.FUTURE
