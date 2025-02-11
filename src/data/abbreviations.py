"""
This module defines constants relating to team abbreviations.
"""

abbreviation_to_location = {
    "ANA": "Anaheim",
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
    "UTA": "Utah",
    "VAN": "Vancouver",
    "VGK": "Vegas",
    "WSH": "Washington",
    "WPG": "Winnipeg",
    "CAN": "Canada",
    "USA": "United States",
    "SWE": "Sweden",
    "FIN": "Finland"
}

location_to_abbreviation = {
    "Anaheim":       "ANA",
    "Boston":        "BOS",
    "Buffalo":       "BUF",
    "Calgary":       "CGY",
    "Carolina":      "CAR",
    "Chicago":       "CHI",
    "Colorado":      "COL",
    "Columbus":      "CBJ",
    "Dallas":        "DAL",
    "Detroit":       "DET",
    "Edmonton":      "EDM",
    "Florida":       "FLA",
    "Los Angeles":   "LAK",
    "Minnesota":     "MIN",
    "Montreal":      "MTL",
    "Nashville":     "NSH",
    "New Jersey":    "NJD",
    "New York (I)":  "NYI",
    "New York (R)":  "NYR",
    "Ottawa":        "OTT",
    "Philadelphia":  "PHI",
    "Pittsburgh":    "PIT",
    "San Jose":      "SJS",
    "Seattle":       "SEA",
    "St. Louis":     "STL",
    "Tampa Bay":     "TBL",
    "Toronto":       "TOR",
    "Utah":          "UTA",
    "Vancouver":     "VAN",
    "Vegas":         "VGK",
    "Washington":    "WSH",
    "Winnipeg":      "WPG",
    "Canada":        "CAN",
    "USA":           "USA",
    "Sweden":        "SWE",
    "Finland":       "FIN"
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
