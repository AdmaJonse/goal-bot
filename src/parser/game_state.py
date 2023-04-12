"""
This module handles parsing of the game's current state from JSON live feed data.
"""

from src.parser.parser import Parser

class GameStateParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int):
        super().__init__(game_id, "/feed/live")


    def parse(self) -> str:
        """
        Parse the static data for this game.
        """
        self.get_data()
        state : str = "Scheduled"
        for play in self.data["liveData"]["plays"]["allPlays"]:
            event : str = play["result"]["event"]
            if event == "Period Start":
                state = "Live"
            elif event == "Game End":
                state = "End"
            elif event == "Game Official":
                state = "Official"
        return state
