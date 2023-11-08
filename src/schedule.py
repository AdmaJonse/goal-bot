"""
This module provides an interface for querying the NHL API's schedule data.
"""

from typing import Any, Optional, List

from datetime import datetime, tzinfo
from datetime import timedelta
from dateutil import parser

import pytz
import requests

from src.logger import log

# NHL API URL
SCHEDULE_API : str = "https://api-web.nhle.com/v1/schedule"

# Date and Time formats
NHL_TIME_FORMAT : str    = "%Y-%m-%dT%H:%M:%SZ"
TIME_FORMAT     : str    = "%Y-%m-%d %H:%M:%S %Z%z"
DATE_FORMAT     : str    = "%Y-%m-%d"
TIME_ZONE       : tzinfo = pytz.timezone("US/Eastern")


def time_to_string(time : datetime) -> str:
    """
    Return the given datetime object as a time string formatted
    using the time format constant.
    """
    return time.astimezone(TIME_ZONE).strftime(TIME_FORMAT)


def date_to_string(date : datetime) -> str:
    """
    Return the given datetime object as a date string formatted
    using the time format constant.
    """
    return date.strftime(DATE_FORMAT)


def get_current_time() -> datetime:
    """
    Return the current time localized using the time zone constant.
    """
    current_time : datetime = datetime.now(TIME_ZONE)
    log.info("current time: " + time_to_string(current_time))
    return current_time


def get_current_date() -> datetime:
    """
    Return the current date localized using the time zone constant.
    """
    now          : datetime = datetime.now(TIME_ZONE)
    current_date : datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
    log.info("current date: " + date_to_string(current_date))
    return current_date


def get_tomorrow() -> datetime:
    """
    Return the tomorrow's date localized using the time zone constant.
    """
    tomorrow = get_current_date() + timedelta(days=1)
    log.info("tomorrow's date: " + date_to_string(tomorrow))
    return tomorrow


def get_noon() -> datetime:
    """
    Return noon for the current date.
    """
    now  : datetime = datetime.now(TIME_ZONE)
    noon : datetime = now.replace(hour=12, minute=0, second=0)
    return noon


def get_schedule_json() -> Any:
    """
    Return the JSON record describing the team's games that are
    scheduled today.
    """

    date   : datetime = get_current_date()
    url    : str      = SCHEDULE_API + "/" + date_to_string(date)
    params : str      = ""

    log.info("getting schedule JSON from: " + url)
    request = requests.get(url, params)
    return request.json()


def get_game_id() -> Optional[int]:
    """
    Return the game ID from the given JSON schedule record.
    """
    try:

        data    : Any = get_schedule_json()
        game_id : int = data["gameWeek"][0]["games"][0]["gamePk"]

        log.info("game id: " + str(game_id))
        return game_id

    except IndexError:
        return None

    except KeyError:
        return None


def get_start_time() -> Optional[datetime]:
    """
    Return the game start time from the given JSON schedule record.
    """
    try:

        data       : Any      = get_schedule_json()
        start_time : datetime = parser.parse(data["gameWeek"][0]["games"][0]["gameDate"])

        log.info("game start time: " + time_to_string(start_time))
        return start_time

    except IndexError:
        return None

    except KeyError:
        return None


def get_todays_games() -> Optional[List[int]]:
    """
    Return the list of games for today.
    """
    try:

        data  : Any       = get_schedule_json()
        games : List[int] = []

        for game in data["gameWeek"][0]["games"]:
            games.append(game["id"])

        log.info("Today's games: " + str(games))
        return games

    except IndexError:
        return None

    except KeyError:
        return None
