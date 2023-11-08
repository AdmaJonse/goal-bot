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

    def __init__(self, game_id : int, goal_id : int):
        super().__init__(game_id, "/landing")
        self.goal_id = goal_id


    def get_event(self) -> Optional[Any]:
        """
        Parse the game feed for the ID of the scoring play.
        """


    def parse(self) -> Optional[Event]:
        """
        Parse the static data for this game.
        """
        self.get_data()
        if self.data:
            periods : Any = self.data["summary"]["scoring"]
            for period in periods:
                descriptor : Any = period["periodDescriptor"]
                if "goals" in period:
                    for goal in period["goals"]:
                        goal_id : int = int(goal["homeScore"]) + int(goal["awayScore"])
                        if self.goal_id == goal_id:
                            return Event(descriptor, goal)
        return None
