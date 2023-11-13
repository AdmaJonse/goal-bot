"""
TODO
"""

import unittest
from typing import Any, Optional

from src.data import event

class TestAbbreviations(unittest.TestCase):
    """
    TODO
    """

    def test_to_name(self):
        """
        TODO
        """
        data : Any = {
            "playerId": 8477942,
            "firstName": "Kevin",
            "lastName": "Fiala",
            "assistToDate": 1
        }
        expected : Optional[str] = "Kevin Fiala"
        actual   : Optional[str] = event.to_name(data)
        assert expected == actual
 
    def test_get_primary_assist(self):
        """
        TODO
        """
        data : Any = {
            "assists": [
                {
                    "playerId": 8477942,
                    "firstName": "Kevin",
                    "lastName": "Fiala",
                    "assistToDate": 1
                },
                {
                    "playerId": 8481606,
                    "firstName": "Jordan",
                    "lastName": "Spence",
                    "assistToDate": 1
                }
            ]
        }
        expected : str           = "Kevin Fiala"
        actual   : Optional[str] = event.get_primary_assist(data)
        assert expected == actual


    def test_get_invalid_primary_assist(self):
        """
        TODO
        """
        data     : Any           = {}
        expected : Optional[str] = None
        actual   : Optional[str] = event.get_primary_assist(data)
        assert expected == actual


    def test_get_secondary_assist(self):
        """
        TODO
        """
        data : Any = {
            "assists": [
                {
                    "playerId": 8477942,
                    "firstName": "Kevin",
                    "lastName": "Fiala",
                    "assistToDate": 1
                },
                {
                    "playerId": 8481606,
                    "firstName": "Jordan",
                    "lastName": "Spence",
                    "assistToDate": 1
                }
            ]
        }
        expected : str           = "Jordan Spence"
        actual   : Optional[str] = event.get_secondary_assist(data)
        assert expected == actual


    def test_get_invalid_secondary_assist(self):
        """
        TODO
        """
        data     : Any           = {}
        expected : Optional[str] = None
        actual   : Optional[str] = event.get_secondary_assist(data)
        assert expected == actual


    def test_get_missing_secondary_assist(self):
        """
        TODO
        """
        data : Any = {
            "assists": [
                {
                    "playerId": 8477942,
                    "firstName": "Kevin",
                    "lastName": "Fiala",
                    "assistToDate": 1
                }
            ]
        }
        expected : Optional[str] = None
        actual   : Optional[str] = event.get_secondary_assist(data)
        assert expected == actual
