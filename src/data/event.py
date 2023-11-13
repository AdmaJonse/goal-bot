"""
This module contains parsing of a play-by-play event.
"""

from dataclasses import dataclass
from typing import Any, List, Optional

from datetime import datetime, timedelta

from src.data.abbreviations import abbreviation_to_location
from src.data.period import Period
from src.data.score import Score


def to_name(data : Any) -> Optional[str]:
    """
    Generate a full name from a dict that contains a first and last name property.
    """
    first_name : str           = data.get("firstName", None)
    last_name  : str           = data.get("lastName", None)
    full_name  : Optional[str] = None
    if first_name is not None and last_name is not None:
        full_name = first_name + " " + last_name
    return full_name


def get_primary_assist(data : Any) -> Optional[str]:
    """
    Get the player credited with the primary assist from the given event.
    """
    player  : Optional[str] = None
    assists : List[Any]     = data.get("assists", [])
    if len(assists) >= 1:
        player = to_name(assists[0])
    return player


def get_secondary_assist(data : Any) -> Optional[str]:
    """
    Get the player credited with the secondary assist from the given event.
    """
    player  : Optional[str] = None
    assists : List[Any]     = data.get("assists", [])
    if len(assists) >= 2:
        player = to_name(assists[1])
    return player


def get_team(data : Any) -> Optional[str]:
    """
    Return the location string for the team in the given event.
    """
    return abbreviation_to_location.get(data["teamAbbrev"], None)


def get_time_remaining(period : Period, data : Any) -> str:
    """
    Calculate the time remaining in the period from the event time and return it as a string.
    """
    read_time      : datetime  = datetime.strptime(data["timeInPeriod"], "%M:%S")
    time_in_period : timedelta = timedelta(minutes = read_time.minute, seconds = read_time.second)
    delta          : timedelta = period.length() - time_in_period
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

    def __init__(self, period : Period, data : Any):
        self.period           : Period        = period
        self.time             : str           = get_time_remaining(period, data)
        self.score            : Score         = Score(data)
        self.team             : Optional[str] = get_team(data)
        self.scorer           : Optional[str] = data["firstName"] + " " + data["lastName"]
        self.primary_assist   : Optional[str] = get_primary_assist(data)
        self.secondary_assist : Optional[str] = get_secondary_assist(data)
        self.strength         : Optional[str] = get_strength(data)
        self.is_empty_net     : bool          = is_empty_net(data)
