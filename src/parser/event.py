"""
This module handles parsing of the game's current state from JSON live feed data.
"""

from typing import Any, Optional

from src.data.event import Event
from src.data.period import Period
from src.data.game_type import GameType
from src.logger import log
from src.parser.parser import Parser

class EventParser(Parser):
    """
    This class defines the parser for game data.
    """

    def __init__(self, game_id : int, goal_id : int):
        super().__init__(game_id, "/landing")
        self.goal_id = goal_id

    def parse(self) -> Optional[Event]:
        """
        Parse the static data for this game.
        """
        self.get_data()
        if not self.data:
            log.error("Could not find goal " + str(self.goal_id) + " in game " + str(self.game_id))
            return None

        game_type      : GameType = GameType(self.data.get("gameType"))
        period_summary : Any = self.data["summary"]["scoring"]

        for per in period_summary:
            descriptor : Any    = per.get("periodDescriptor", {})
            period     : Period = Period(game_type, descriptor)

            if "goals" not in per:
                continue

            for goal in per["goals"]:
                goal_id : int = int(goal["homeScore"]) + int(goal["awayScore"])
                if self.goal_id == goal_id:
                    return Event(period, goal)

        log.error("Could not find goal " + str(self.goal_id) + " in game: " + str(self.game_id))
        return None
