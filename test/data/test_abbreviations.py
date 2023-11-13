"""
TODO
"""

import unittest

from src.data import abbreviations

class TestAbbreviations(unittest.TestCase):
    """
    TODO
    """

    def test_get_location(self):
        """
        TODO
        """
        expected : str = "Anaheim"
        actual   : str = abbreviations.get_location("ANA")
        assert expected == actual

        expected : str = "Vegas"
        actual   : str = abbreviations.get_location("VGK")
        assert expected == actual

        expected : str = ""
        actual   : str = abbreviations.get_location("Invalid")
        assert expected == actual

    def test_get_abbreviation(self):
        """
        TODO
        """
        expected : str = "ANA"
        actual   : str = abbreviations.get_abbreviation("Anaheim")
        assert expected == actual

        expected : str = "VGK"
        actual   : str = abbreviations.get_abbreviation("Vegas")
        assert expected == actual

        expected : str = ""
        actual   : str = abbreviations.get_abbreviation("Invalid")
        assert expected == actual
