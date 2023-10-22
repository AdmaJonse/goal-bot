"""
This module defines the Team class.
"""

hashtags = {
    "ANA": "#FlyTogether",
    "ARI": "#Yotes",
    "BOS": "#NHLBruins",
    "BUF": "#LetsGoBuffalo",
    "CGY": "#Flames",
    "CAR": "#CauseChaos",
    "CHI": "#Blackhawks",
    "COL": "#GoAvsGo",
    "CBJ": "#CBJ",
    "DAL": "#TexasHockey",
    "DET": "#LGRW",
    "EDM": "#LetsGoOilers",
    "FLA": "#TimeToHunt",
    "LAK": "#GoKingsGo",
    "MIN": "#MNWild",
    "MTL": "#GoHabsGo",
    "NSH": "#Preds",
    "NJD": "#NJDevils",
    "NYI": "#Isles",
    "NYR": "#NYR",
    "OTT": "#GoSensGo",
    "PHI": "#LetsGoFlyers",
    "PIT": "#LetsGoPens",
    "SJS": "#SJSharks",
    "SEA": "#SeaKraken",
    "STL": "#STLBlues",
    "TBL": "#GoBolts",
    "TOR": "#LeafsForever",
    "VAN": "#Canucks",
    "VGK": "#VegasBorn",
    "WSH": "#ALLCAPS",
    "WPG": "#GoJetsGo"
}

playoff_hashtags = {
    "ANA": "",
    "ARI": "",
    "BOS": "",
    "BUF": "",
    "CGY": "",
    "CAR": "",
    "CHI": "",
    "COL": "#FindAWay",
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
    "VAN": "",
    "VGK": "",
    "WSH": "",
    "WPG": "",
}

class Team:
    """
    The team class. This class contains the various names that can be used for a team and
    provides methods for querying these names.
    """

    def __init__(self, data):
        self._location        : str = data["locationName"]
        self._team_name       : str = data["teamName"]
        self._abbreviation    : str = data["abbreviation"]
        self._full_name       : str = data["name"]
        self._timezone        : str = data["venue"]["timeZone"]["id"]
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
