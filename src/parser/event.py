"""
This module handles parsing of the game's current state from JSON live feed data.
"""

from typing import Any, Optional

from src.data.event import Event
from src.parser.parser import Parser

class EventParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int, event_id : int):
        super().__init__(game_id, "/feed/live")
        self.event_id = event_id


    def parse(self) -> Optional[Event]:
        """
        Parse the static data for this game.
        """
        self.get_data()
        all_plays : Any = self.data["liveData"]["plays"]["allPlays"]
        for play in all_plays:
            event_type : str = play["result"]["event"]
            event_id   : int = int(play["about"]["eventId"])
            if event_type != "Goal":
                continue
            if event_id == self.event_id:
                if event_type == "Goal":
                    return Event(play)
                return None
        return None
