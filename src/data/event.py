"""
This module contains parsing of a play-by-play event.
"""

from dataclasses import dataclass
from typing import Any, Optional

from datetime import datetime, timedelta

from src.data.abbreviations import abbreviation_to_location
from src.data.period import Period
from src.data.score import Score


def get_primary_assist(data) -> Optional[str]:
    """
    Get the player credited with the primary assist from the given event.
    """
    player : Optional[str] = None
    if len(data.get("assists", [])) >= 1:
        assist = data["assists"][0]
        player = assist["firstName"] + " " + assist["lastName"]
    return player


def get_secondary_assist(data) -> Optional[str]:
    """
    Get the player credited with the secondary assist from the given event.
    """
    player : Optional[str] = None
    if len(data.get("assists", [])) >= 2:
        assist = data["assists"][1]
        player = assist["firstName"] + " " + assist["lastName"]
    return player


def get_team(data) -> Optional[str]:
    """
    Return the location string for the team in the given event.
    """
    return abbreviation_to_location.get(data["teamAbbrev"], None)


def get_time_remaining(data) -> str:
    """
    Calculate the time remaining in the period from the event time and return it as a string.
    """
    period_length : datetime  = datetime.strptime("20:00", "%M:%S")
    current_time  : datetime  = datetime.strptime(data["timeInPeriod"], "%M:%S")
    delta         : timedelta = period_length - current_time
    minutes, seconds = divmod(delta.seconds, 60)
    return f"{minutes:02}:{seconds:02}"


def get_strength(data) -> Optional[str]:
    """
    Return the strength (even strength, power play or shorthanded) from the given event.
    """
    return data.get("strength", None)


def is_empty_net(data) -> bool:
    """
    Return whether or not the goal was scored on an empty net from the given event.
    """
    return data.get("goalModifier", False) == "empty-net"


# pylint: disable=too-many-instance-attributes
@dataclass
class Event:
    """
    The base event class.
    """

    null_post : Optional[Any] = None

    def __init__(self, period : Any, data : Any):
        self.period           : Period        = Period(period)
        self.time             : str           = get_time_remaining(data)
        self.score            : Score         = Score(data)
        self.team             : Optional[str] = get_team(data)
        self.scorer           : Optional[str] = data["firstName"] + " " + data["lastName"]
        self.primary_assist   : Optional[str] = get_primary_assist(data)
        self.secondary_assist : Optional[str] = get_secondary_assist(data)
        self.strength         : Optional[str] = get_strength(data)
        self.is_empty_net     : bool          = is_empty_net(data)
