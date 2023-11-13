"""
This module defines constants relating to team abbreviations.
"""

abbreviation_to_location = {
    "ANA": "Anaheim",
    "ARI": "Arizona",
    "BOS": "Boston",
    "BUF": "Buffalo",
    "CGY": "Calgary",
    "CAR": "Carolina",
    "CHI": "Chicago",
    "COL": "Colorado",
    "CBJ": "Columbus",
    "DAL": "Dallas",
    "DET": "Detroit",
    "EDM": "Edmonton",
    "FLA": "Florida",
    "LAK": "Los Angeles",
    "MIN": "Minnesota",
    "MTL": "Montreal",
    "NSH": "Nashville",
    "NJD": "New Jersey",
    "NYI": "New York",
    "NYR": "New York",
    "OTT": "Ottawa",
    "PHI": "Philadelphia",
    "PIT": "Pittsburgh",
    "SJS": "San Jose",
    "SEA": "Seattle",
    "STL": "St. Louis",
    "TBL": "Tampa Bay",
    "TOR": "Toronto",
    "VAN": "Vancouver",
    "VGK": "Vegas",
    "WSH": "Washington",
    "WPG": "Winnipeg"
}

location_to_abbreviation = {
    "Anaheim":      "ANA",
    "Arizona":      "ARI",
    "Boston":       "BOS",
    "Buffalo":      "BUF",
    "Calgary":      "CGY",
    "Carolina":     "CAR",
    "Chicago":      "CHI",
    "Colorado":     "COL",
    "Columbus":     "CBJ",
    "Dallas":       "DAL",
    "Detroit":      "DET",
    "Edmonton":     "EDM",
    "Florida":      "FLA",
    "Los Angeles":  "LAK",
    "Minnesota":    "MIN",
    "Montreal":     "MTL",
    "Nashville":    "NSH",
    "New Jersey":   "NJD",
    "New York (I)": "NYI",
    "New York (R)": "NYR",
    "Ottawa":       "OTT",
    "Philadelphia": "PHI",
    "Pittsburgh":   "PIT",
    "San Jose":     "SJS",
    "Seattle":      "SEA",
    "St. Louis":    "STL",
    "Tampa Bay":    "TBL",
    "Toronto":      "TOR",
    "Vancouver":    "VAN",
    "Vegas":        "VGK",
    "Washington":   "WSH",
    "Winnipeg":     "WPG"
}


def get_location(abbreviation : str) -> str:
    """
    Return the location for the given abbreviation. Return an empty string if the abbreviation does
    not exist.
    """
    return abbreviation_to_location.get(abbreviation, "")


def get_abbreviation(location : str) -> str:
    """
    Return the abbreviation for the given location. Return an empty string if the abbreviation does
    not exist.
    """
    return location_to_abbreviation.get(location, "")
