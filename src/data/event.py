"""
TODO
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from dateutil import parser

from src.data.period import Period
from src.data.score import Score
from src.logger import log

def get_player_name(event : Any, player_type : str, index : int = 1):
    """
    Return the name of the player with the given type from the event.
    """
    count = 0
    try:
        for player in event["players"]:
            if player["playerType"].lower() == player_type.lower():
                count += 1
                if count == index:
                    return player["player"]["fullName"]
    except KeyError:
        return None

    return None


def get_team(event : Any):
    """
    Return the name of the team in the given event. Log an error
    and return None if no team was found.
    """
    try:
        return event["team"]["name"]
    except KeyError:
        log.info("Could not find team.")
        return None

def get_value(data : Any, *args):
    """
    Helper function for retrieving values from multi-level dictionaries.
    If the key is not found, return an empty string.
    """
    for key in args:
        try:
            value = data.get(key)
            data = value
        except KeyError:
            log.error("Could not find key: " + key)
            return None
        except AttributeError:
            log.error("Could not find key: " + key)
            return None
    return value


# pylint: disable=too-many-instance-attributes
@dataclass
class Event:
    """
    The base event class.
    """

    null_post : Optional[Any] = None

    def __init__(self, data : Any):
        self.event_id         : int           = int(data["about"]["eventId"])
        self.description      : str           = data["result"]["description"]
        self.period           : Period        = Period(data["about"])
        self.time             : str           = data["about"]["periodTimeRemaining"]
        self.timestamp        : datetime      = parser.parse(data["about"]["dateTime"])
        self.score            : Score         = Score(data["about"])
        self.team             : Optional[str] = get_team(data)
        self.scorer           : Optional[str] = get_player_name(data, "Scorer")
        self.primary_assist   : Optional[str] = get_player_name(data, "Assist", 1)
        self.secondary_assist : Optional[str] = get_player_name(data, "Assist", 2)
        self.goalie           : Optional[str] = get_player_name(data, "Goalie")
        self.strength         : Optional[str] = get_value(data, "result", "strength", "code")
        self.is_empty_net     : bool          = get_value(data, "result", "emptyNet")
