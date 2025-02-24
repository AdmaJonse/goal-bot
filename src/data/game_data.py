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

    def __init__(self, data) -> None:
        self._home            : Team      = Team(data["homeTeam"])
        self._away            : Team      = Team(data["awayTeam"])
        self._date            : datetime  = parser.parse(data["startTimeUTC"])
        self._venue           : str       = data.get("venue", "")
        self._is_playoffs     : bool      = data.get("gameType", 0) == 3
        self._is_four_nations : bool      = data.get("gameType", 0) == 19 or data.get("gameType", 0) == 20


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
        team_string : str = ""
        if team == self.home.location:
            team_string = self.home.location
        elif team == self.away.location:
            team_string = self.away.location
        else:
            log.error("unknown team: " + str(team))
        return team_string


    def get_opposition(self, team : str) -> str:
        """
        Return the opposing team's location name.
        """
        team_string : str = ""
        if team == self.home.location:
            team_string = self.away.location
        elif team == self.away.location:
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
        if self._is_four_nations:
            hashtags.append("#4Nations")
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

    @property
    def is_four_nations(self) -> bool:
        """
        Getter for the is_four_nations field.
        """
        return self._is_four_nations
