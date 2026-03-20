"""
Unit tests for abbreviation helpers.

These tests verify the mapping between team abbreviations and their
corresponding location names, and vice versa.
"""

import unittest

from src.data import abbreviations

class TestAbbreviations(unittest.TestCase):
    """
    Tests for `get_location` and `get_abbreviation` helper functions.
    """

    def test_get_location(self):
        """
        Verify abbreviation-to-location mapping for valid and invalid inputs.
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
        Verify location-to-abbreviation mapping for valid and invalid inputs.
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
