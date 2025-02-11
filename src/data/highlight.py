"""
This module defines a highlight object.
"""

from typing import Dict, Optional

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

    def __init__(self, game_id, data) -> None:
        self.id        : int                 = int(data["highlightClip"])
        self.video     : str                 = VIDEO_URL + str(self.id)
        self.game_id   : int                 = game_id
        self.game_data : Optional[GameData]  = GameDataParser(self.game_id).parse()
        self.event     : Optional[Event]     = None
        self.goal_id   : int                 = int(data["homeScore"]) + int(data["awayScore"])
        self.post_id   : Dict[str, Optional[Dict[str, str]]] = {}

        if self.game_data:
            self.event = EventParser(self.game_id, self.goal_id).parse()
        else:
            log.error("Game data is null for game: " + str(game_id))


    def __str__(self) -> str:
        """
        Return a string representing the highlight.
        """
        return "Highlight: "  + str(self.id)


    def get_footer(self) -> Optional[str]:
        """
        Return the score string only for a goal event. We use this as an identifier for searching
        previous tweets of this goal.
        """

        if self.event is None:
            log.error("Could not find corresponding event.")
            return None

        if self.game_data is None:
            log.error("There is no game data for this game.")
            return None

        event_values = {
            "home_team":  self.game_data.home.location,
            "away_team":  self.game_data.away.location,
            "home_goals": self.event.score.home_goals,
            "away_goals": self.event.score.away_goals,
        }
        return templates.SCORE_TEMPLATE.format(**event_values)


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

        if self.event.team is None:
            log.error("There is no team for this event.")
            return None

        goal_string   : str = ""
        assist_string : str = ""
        footer        : str = ""

        event_values = {
            "team":             self.game_data.get_team_string(self.event.team),
            "scorer":           self.event.scorer,
            "primary_assist":   self.event.primary_assist,
            "secondary_assist": self.event.secondary_assist,
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
        elif self.event.strength == "pp":
            goal_string = templates.POWER_PLAY_GOAL_TEMPLATE.format(**event_values)
        elif self.event.strength == "sh":
            goal_string = templates.SHORT_HANDED_GOAL_TEMPLATE.format(**event_values)
        else:
            goal_string = templates.GOAL_TEMPLATE.format(**event_values)

        if self.event.secondary_assist is not None:
            assist_string = templates.TWO_ASSIST_TEMPLATE.format(**event_values)
        elif self.event.primary_assist is not None:
            assist_string = templates.ONE_ASSIST_TEMPLATE.format(**event_values)

        footer = templates.GOAL_FOOTER_TEMPLATE.format(**event_values)

        return goal_string + assist_string + footer


    def get_reply(self, previous : 'Event') -> Optional[str]:
        """
        Return the reply string for a goal event.
        """

        # Sometimes the NHL will remove all the data from a goal event after it's been posted.
        # When that happens, we want to avoid posting a reply so that we don't spam tweets.
        if self.event is None or self.game_data is None or self.event.scorer is None:
            return None

        event_values = {
            "team":             self.game_data.get_team_string(self.event.team),
            "scorer":           self.event.scorer,
            "primary_assist":   self.event.primary_assist,
            "secondary_assist": self.event.secondary_assist,
            "time":             self.event.time,
            "period":           self.event.period.ordinal,
            "home_team":        self.game_data.home.location,
            "away_team":        self.game_data.away.location,
            "home_goals":       self.event.score.home_goals,
            "away_goals":       self.event.score.away_goals,
            "hashtags":         self.game_data.hashtags
        }

        scorer_modified           : bool = self.event.is_scorer_modified(previous)
        primary_assist_added      : bool = self.event.is_primary_assist_added(previous)
        secondary_assist_added    : bool = self.event.is_secondary_assist_added(previous)
        primary_assist_modified   : bool = self.event.is_primary_assist_modified(previous)
        secondary_assist_modified : bool = self.event.is_secondary_assist_modified(previous)

        update_text : Optional[str] = None

        # Time of goal has been changed
        if previous.time != self.event.time:
            update_text = templates.GOAL_TIME_UPDATE_TEMPLATE.format(**event_values)

        # Assists have been changed
        if primary_assist_modified and secondary_assist_modified:
            update_text = templates.ASSIST_UPDATE_TEMPLATE.format(**event_values)
        elif primary_assist_modified:
            update_text = templates.PRIMARY_ASSIST_UPDATE_TEMPLATE.format(**event_values)
        elif secondary_assist_modified:
            update_text = templates.SECONDARY_ASSIST_UPDATE_TEMPLATE.format(**event_values)

        # Assists have been added
        if primary_assist_added and secondary_assist_added:
            update_text = templates.ASSIST_ADD_BOTH_TEMPLATE.format(**event_values)
        elif primary_assist_added:
            update_text = templates.ASSIST_ADD_PRIMARY_TEMPLATE.format(**event_values)
        elif secondary_assist_added:
            update_text = templates.ASSIST_ADD_SECONDARY_TEMPLATE.format(**event_values)

        # Goal scorer has been changed
        if scorer_modified:
            update_text = templates.SCORER_UPDATE_TEMPLATE.format(**event_values)

        return update_text
