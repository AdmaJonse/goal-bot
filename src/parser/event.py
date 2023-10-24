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
        super().__init__(game_id, "/feed/live")
        self.goal_id = goal_id


    def get_event_id(self) -> Optional[int]:
        """
        Parse the game feed for the ID of the scoring play.
        """
        event_id      : Optional[int] = None
        scoring_plays : Any = self.data["liveData"]["plays"]["scoringPlays"]
        # Plays are zero indexed, so the first goal of the game has ID = 0
        goal_id : int = int(self.goal_id - 1)
        if goal_id < len(scoring_plays):
            event_id = scoring_plays[goal_id]
        return event_id


    def parse(self) -> Optional[Event]:
        """
        Parse the static data for this game.
        """
        self.get_data()
        if self.data:
            event_id : Optional[int] = self.get_event_id()
            if event_id is not None:
                all_plays : Any = self.data["liveData"]["plays"]["allPlays"]
                for index, play in enumerate(all_plays):
                    event_type : str = play["result"]["event"]
                    if event_type != "Goal":
                        continue
                    if int(index) == int(event_id):
                        if event_type == "Goal":
                            event = Event(play)
                            return event
                        return None
        return None
