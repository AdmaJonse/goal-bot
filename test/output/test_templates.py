"""
Unit tests for output templates formatting.
"""

import unittest

from src.output import templates


class TestTemplates(unittest.TestCase):
    """
    Ensure templates format and contain expected phrases.
    """

    def test_goal_template_contains_scorer(self):
        """
        GOAL_TEMPLATE should include 'Scored by {scorer}' after formatting.
        """
        values = {
            "team": "Edmonton",
            "scorer": "John Doe",
            "time": "05:00",
            "period": "1st",
        }
        text = templates.GOAL_TEMPLATE.format(**values)
        self.assertIn("Scored by John Doe", text)

    def test_shootout_template_wording(self):
        """
        SHOOTOUT_GOAL_TEMPLATE should mention the shootout.
        """
        values = {"team": "Edmonton", "scorer": "Jane", "time": "00:00", "period": "SO"}
        text = templates.SHOOTOUT_GOAL_TEMPLATE.format(**values)
        self.assertIn("in the shootout", text)


if __name__ == "__main__":
    unittest.main()
