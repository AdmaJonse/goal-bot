"""
This module defines the Team class.
"""

from src.data.abbreviations import abbreviation_to_location

hashtags = {
    "ANA": "#FlyTogether",
    "BOS": "#NHLBruins",
    "BUF": "#SabreHood",
    "CGY": "#Flames",
    "CAR": "#RaiseUp",
    "CHI": "#Blackhawks",
    "COL": "#GoAvsGo",
    "CBJ": "#CBJ",
    "DAL": "#TexasHockey",
    "DET": "#LGRW",
    "EDM": "#LetsGoOilers",
    "FLA": "#TimeToHunt",
    "LAK": "#GoKingsGo",
    "MIN": "#mnwild",
    "MTL": "#GoHabsGo",
    "NSH": "#Smashville",
    "NJD": "#NJDevils",
    "NYI": "#Isles",
    "NYR": "#NYR",
    "OTT": "#GoSensGo",
    "PHI": "#LetsGoFlyers",
    "PIT": "#LetsGoPens",
    "SJS": "#TheFutureIsTeal",
    "SEA": "#SeaKraken",
    "STL": "#stlblues",
    "TBL": "#GoBolts",
    "TOR": "#LeafsForever",
    "UTA": "#UtahHC",
    "VAN": "#Canucks",
    "VGK": "#VegasBorn",
    "WSH": "#ALLCAPS",
    "WPG": "#GoJetsGo",
    "CAN": "#TeamCanada",
    "USA": "#TeamUSA",
    "SWE": "#TeamSweden",
    "FIN": "#TeamFinland"
}

playoff_hashtags = {
    "ANA": "",
    "BOS": "",
    "BUF": "",
    "CGY": "",
    "CAR": "",
    "CHI": "",
    "COL": "",
    "CBJ": "",
    "DAL": "",
    "DET": "",
    "EDM": "",
    "FLA": "",
    "LAK": "",
    "MIN": "",
    "MTL": "",
    "NSH": "",
    "NJD": "",
    "NYI": "",
    "NYR": "",
    "OTT": "",
    "PHI": "",
    "PIT": "",
    "SJS": "",
    "SEA": "",
    "STL": "",
    "TBL": "",
    "TOR": "",
    "UTA": "",
    "VAN": "",
    "VGK": "",
    "WSH": "",
    "WPG": "",
    "CAN": "",
    "USA": "",
    "SWE": "",
    "FIN": ""
}

class Team:
    """
    The team class. This class contains the various names that can be used for a team and
    provides methods for querying these names.
    """

    def __init__(self, data) -> None:
        self._abbreviation    : str = data["abbrev"]
        self._location        : str = abbreviation_to_location.get(self._abbreviation, "")
        self._team_name       : str = data["commonName"]["default"]
        self._full_name       : str = self._location + " " + self._team_name
        self._hashtag         : str = hashtags[self._abbreviation]
        self._playoff_hashtag : str = playoff_hashtags[self._abbreviation]

    @property
    def location(self) -> str:
        """
        Getter for the team location.
        """
        return self._location

    @property
    def team_name(self) -> str:
        """
        Getter for the team name.
        """
        return self._team_name

    @property
    def abbreviation(self) -> str:
        """
        Getter for the team abbreviation.
        """
        return self._abbreviation

    @property
    def full_name(self) -> str:
        """
        Getter for the team full name.
        """
        return self._full_name

    @property
    def hashtag(self) -> str:
        """
        Getter for the team hashtag.
        """
        return self._hashtag

    @property
    def playoff_hashtag(self) -> str:
        """
        Getter for the team's playoff hashtag.
        """
        return self._playoff_hashtag
