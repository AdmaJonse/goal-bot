"""
Unit tests for `Period` behavior: string conversions, ordinals, and lengths.
"""

import unittest
from datetime import timedelta

from src.data.period import Period
from src.data.game_type import GameType


class TestPeriod(unittest.TestCase):
    """
    Tests for `Period.__str__`, `Period.ordinal`, and `Period.length()`.
    """

    def test_str_regulation_and_special(self):
        """
        Regulation periods (1/2/3), overtime and shootout produce expected strings.
        """
        p1 = Period(None, {"periodType": "REG", "number": 1})
        p2 = Period(None, {"periodType": "REG", "number": 2})
        p3 = Period(None, {"periodType": "REG", "number": 3})
        ot = Period(None, {"periodType": "OT", "number": 4})
        so = Period(None, {"periodType": "SO", "number": 0})

        self.assertEqual(str(p1), "The first period")
        self.assertEqual(str(p2), "The second period")
        self.assertEqual(str(p3), "The third period")
        self.assertEqual(str(ot), "The OT period")
        self.assertEqual(str(so), "The shootout")

    def test_ordinal_values(self):
        """
        Ordinal labels for regulation, overtime sequences and shootout.
        """
        r1 = Period(None, {"periodType": "REG", "number": 1})
        r2 = Period(None, {"periodType": "REG", "number": 2})
        r3 = Period(None, {"periodType": "REG", "number": 3})
        ot1 = Period(GameType.REGULAR_SEASON, {"periodType": "OT", "number": 4})
        ot2 = Period(GameType.REGULAR_SEASON, {"periodType": "OT", "number": 5})
        so = Period(None, {"periodType": "SO", "number": 0})

        self.assertEqual(r1.ordinal, "1st")
        self.assertEqual(r2.ordinal, "2nd")
        self.assertEqual(r3.ordinal, "3rd")
        self.assertEqual(ot1.ordinal, "OT")
        self.assertEqual(ot2.ordinal, "2OT")
        self.assertEqual(so.ordinal, "SO")

    def test_length_varies_by_game_type(self):
        """
        Period.length returns expected timedeltas for regulation, shootout and OT variants.
        """
        reg = Period(None, {"periodType": "REG", "number": 1})
        so = Period(None, {"periodType": "SO", "number": 0})

        ot_regular = Period(GameType.REGULAR_SEASON, {"periodType": "OT", "number": 4})
        ot_playoff = Period(GameType.PLAYOFF, {"periodType": "OT", "number": 4})
        ot_four = Period(GameType.FOUR_NATIONS, {"periodType": "OT", "number": 4})

        self.assertEqual(reg.length(), timedelta(minutes=20))
        self.assertEqual(so.length(), timedelta(minutes=0))
        self.assertEqual(ot_regular.length(), timedelta(minutes=5))
        self.assertEqual(ot_playoff.length(), timedelta(minutes=20))
        self.assertEqual(ot_four.length(), timedelta(minutes=10))


if __name__ == "__main__":
    unittest.main()
