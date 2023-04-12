"""
TODO
"""

from datetime import datetime, timezone
import pause

from src.data.game_data import GameData
from src.parser.content import ContentParser
from src.parser.game_data import GameDataParser
from src.parser.game_state import GameStateParser
from src.logger import log

class GameThread:
    """
    TODO
    """

    def __init__(self, game_id : int):
        self.game_id    : int      = game_id
        self.game_data  : GameData = GameDataParser(self.game_id).parse()
        self.start_time : datetime = datetime.now(timezone.utc)
        self.parser     : ContentParser = ContentParser(self.game_id, self.start_time)


    def is_game_over(self):
        """
        Return a boolean indicating whether or not the game is over.
        """
        state : str = GameStateParser(self.game_id).parse()
        return state.lower().strip() == "official"


    def run(self):
        """
        TODO
        """
        log.info("Game " + str(self.game_id) + ": Pausing until " + str(self.game_data.date))
        pause.until(self.game_data.date)
        log.info("Game " + str(self.game_id) + ": The game is live.")
        while not self.is_game_over():
            self.parser.parse()
            pause.seconds(5)
        log.info("Game " + str(self.game_id) + ": The game is over.")
