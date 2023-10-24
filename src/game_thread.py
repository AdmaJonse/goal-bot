"""
This module defines the GameThread class.
"""

from datetime import datetime, timedelta, timezone
from threading import Thread
from typing import Optional
import pause

from src.data.game_data import GameData
from src.data.game_state import GameState
from src.parser.content import ContentParser
from src.parser.game_data import GameDataParser
from src.parser.game_state import GameStateParser
from src.logger import log

class GameThread(Thread):
    """
    This class extends the Thread class to provide a custom thread used to track a game that is
    currently in progress.
    """

    def __init__(self, game_id : int):
        self.game_id    : int                = game_id
        self.game_data  : Optional[GameData] = GameDataParser(self.game_id).parse()
        self.start_time : datetime           = datetime.now(timezone.utc)
        self.parser     : ContentParser      = ContentParser(self.game_id, self.start_time)
        Thread.__init__(self)


    def __str__(self) -> str:
        return "GameThread(" + str(self.game_id) + ")"


    def is_game_over(self) -> bool:
        """
        Return a boolean indicating whether or not the game is over.
        """
        state     : GameState = GameStateParser(self.game_id).parse()
        game_over : bool = state == GameState.OFFICIAL
        return game_over


    def run(self):
        """
        Continuously parse the highlights for this game while it is in progress.
        """
        if self.game_data is not None:
            log.info("Game " + str(self.game_id) + ": Pausing until " + str(self.game_data.date))
            pause.until(self.game_data.date)
            log.info("Game " + str(self.game_id) + ": The game is live.")
            while not self.is_game_over():
                self.parser.parse()
                pause.seconds(5)
            log.info("Game " + str(self.game_id) + ": The game is over.")

            # Continue checking for events for another 30 minutes after the game has ended
            end_time : datetime = datetime.now() + timedelta(minutes = 30)
            log.info("Game " + str(self.game_id) + ": Continuing to parse until " + str(end_time))

            while datetime.now() < end_time:
                self.parser.parse()
                pause.seconds(5)
            log.info("Game " + str(self.game_id) + ": Parsing complete.")

        else:
            log.error("Could not retrieve game data for game: " + str(self.game_id))
