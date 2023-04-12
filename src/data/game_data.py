"""
This module provides classes for storing and querying static game data. This data is
initialized once for a particular game and will never change over the course of play.
"""

from typing import Optional
from datetime import datetime
from dateutil import parser

from src.logger import log
from src.data.team import Team

class GameData:
    """
    The GameData class defines static data about the particular game, such as the teams
    that are playing and where the game is being played. This data will not change over the
    course of play.
    """

    def __init__(self, data):
        self._home        : Team      = Team(data["gameData"]["teams"]["home"])
        self._away        : Team      = Team(data["gameData"]["teams"]["away"])
        self._date        : datetime  = parser.parse(data["gameData"]["datetime"]["dateTime"])
        self._venue       : str       = data["gameData"]["venue"]["name"]
        self._is_playoffs : bool      = data["gameData"]["game"]["type"] == "P"


    def print_constants(self):
        """
        Log the class constants for the current game.
        """
        log.info("Home Location:     " + self.home.location)
        log.info("Home Team:         " + self.home.team_name)
        log.info("Home Abbreviation: " + self.home.abbreviation)
        log.info("Home Full Name:    " + self.home.full_name)
        log.info("Away Location:     " + self.away.location)
        log.info("Away Team:         " + self.away.team_name)
        log.info("Away Abbreviation: " + self.away.abbreviation)
        log.info("Away Full Name:    " + self.away.full_name)
        log.info("Date/Time:         " + self.date.strftime("%I:%M %p %Z"))
        log.info("Venue:             " + self.venue)
        log.info("Is Playoffs:       " + str(self.is_playoffs))
        log.info("Hashtags:          " + self.hashtags)


    def get_team_string(self, team : Optional[str]) -> str:
        """
        Return the name of the team from this event as a location name.
        """
        if team == self.home.full_name:
            team_string = self.home.location
        elif team == self.away.full_name:
            team_string = self.away.location
        else:
            log.error("unknown team: " + str(team))
        return team_string


    def get_opposition(self, team : str) -> str:
        """
        Return the opposing team's location name.
        """
        if team == self.home.full_name:
            team_string = self.away.location
        elif team == self.away.full_name:
            team_string = self.home.location
        else:
            log.error("unknown team: " + team)
        return team_string


    @property
    def hashtags(self) -> str:
        """
        Return the hashtags to append to all tweets.
        """
        hashtags = []
        hashtags.append("#" + self.away.abbreviation + "vs" + self.home.abbreviation)
        hashtags.append(self.home.hashtag)
        hashtags.append(self.away.hashtag)
        if self.is_playoffs:
            hashtags.append(self.home.playoff_hashtag)
            hashtags.append(self.away.playoff_hashtag)
        return " ".join(hashtags)


    @property
    def home(self) -> Team:
        """
        Getter for the home team field.
        """
        return self._home


    @property
    def away(self) -> Team:
        """
        Getter for the away team field.
        """
        return self._away


    @property
    def date(self) -> datetime:
        """
        Getter for the date field.
        """
        return self._date


    @property
    def venue(self) -> str:
        """
        Getter for the venue field.
        """
        return self._venue

    @property
    def is_playoffs(self) -> bool:
        """
        Getter for the is_playoffs field.
        """
        return self._is_playoffs
