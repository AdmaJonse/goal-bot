"""
Unit tests for the `Score` simple data container.
"""

import unittest

from src.data.score import Score


class TestScore(unittest.TestCase):
    """
    Tests Score getters and setters.
    """

    def test_getters_and_setters(self):
        """
        Verify that home_goals and away_goals properties work.
        """
        data = {"homeScore": 2, "awayScore": 1}
        s = Score(data)
        self.assertEqual(s.home_goals, 2)
        self.assertEqual(s.away_goals, 1)

        s.home_goals = 5
        s.away_goals = 4
        self.assertEqual(s.home_goals, 5)
        self.assertEqual(s.away_goals, 4)


if __name__ == "__main__":
    unittest.main()
