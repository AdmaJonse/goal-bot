"""
This module defines a highlight object.
"""

from typing import Optional

from src.data.event import Event
from src.data.game_data import GameData
from src.output import templates
from src.parser.event import EventParser
from src.parser.game_data import GameDataParser
from src.logger import log

BASE_URL      : str = "https://players.brightcove.net/"
BRIGHTCOVE_ID : str = "6415718365001"
VIDEO_FORMAT  : str = "EXtG1xJ7H_default"
VIDEO_URL     : str = BASE_URL + BRIGHTCOVE_ID + "/" + VIDEO_FORMAT + "/index.html?videoId="

class Highlight:
    """
    This class defines a Highlight.
    """

    def __init__(self, game_id, data):
        self.id        : int = int(data["highlightClip"])
        self.video     : str = ""
        self.game_id   : int = game_id
        self.game_data : Optional[GameData] = None
        self.event     : Optional[Event]    = None
        self.goal_id   : int = int(data["homeScore"]) + int(data["awayScore"])

        self.video = VIDEO_URL + str(self.id)

        self.game_data : Optional[GameData] = GameDataParser(self.game_id).parse()
        if self.game_data:
            self.event : Optional[Event] = EventParser(self.game_id, self.goal_id).parse()
        else:
            log.error("Game data is null for game: " + str(game_id))


    def __str__(self) -> str:
        """
        Return a string representing the highlight.
        """
        return "Highlight: "  + str(self.id)


    def get_post(self) -> Optional[str]:
        """
        Return the event string for a goal event.
        """

        if self.event is None:
            log.error("Could not find corresponding event. Delaying tweet.")
            return None

        if self.event.scorer is None:
            log.error("Could not determine goal scorer. Delaying tweet.")
            return None

        if self.game_data is None:
            log.error("There is no game data for this game.")
            return None

        goal_string   : str = ""
        assist_string : str = ""
        footer        : str = ""

        event_values = {
            "team":             self.game_data.get_team_string(self.event.team),
            "scorer":           self.event.scorer,
            "goalie":           self.event.goalie,
            "primary_assist":   self.event.primary_assist,
            "secondary_assist": self.event.secondary_assist,
            "description":      self.event.description,
            "time":             self.event.time,
            "period":           self.event.period.ordinal,
            "home_team":        self.game_data.home.location,
            "away_team":        self.game_data.away.location,
            "home_goals":       self.event.score.home_goals,
            "away_goals":       self.event.score.away_goals,
            "hashtags":         self.game_data.hashtags
        }

        if self.event.is_empty_net:
            goal_string = templates.EMPTY_NET_GOAL_TEMPLATE.format(**event_values)
        elif self.event.strength == "PPG":
            goal_string = templates.POWER_PLAY_GOAL_TEMPLATE.format(**event_values)
        elif self.event.strength == "SHG":
            goal_string = templates.SHORT_HANDED_GOAL_TEMPLATE.format(**event_values)
        else:
            goal_string = templates.GOAL_TEMPLATE.format(**event_values)

        if self.event.secondary_assist is not None:
            assist_string = templates.TWO_ASSIST_TEMPLATE.format(**event_values)
        elif self.event.primary_assist is not None:
            assist_string = templates.ONE_ASSIST_TEMPLATE.format(**event_values)

        footer = templates.GOAL_FOOTER_TEMPLATE.format(**event_values)

        return goal_string + assist_string + footer
