"""
Templates for the tweets that are posted by this bot. These container placeholder values which will
be replaced by actual values prior to posting.
"""

GOAL_TEMPLATE = """
{team} goal!

Scored by {scorer} with {time} remaining in the {period} period.
"""

POWER_PLAY_GOAL_TEMPLATE = """
Power play goal for {team}!

Scored by {scorer} with {time} remaining in the {period} period.
"""

SHORT_HANDED_GOAL_TEMPLATE = """
Short-handed goal for {team}!

Scored by {scorer} with {time} remaining in the {period} period.
"""

EMPTY_NET_GOAL_TEMPLATE = """
Empty net goal for {team}!

Scored by {scorer} with {time} remaining in the {period} period.
"""

SCORE_TEMPLATE = """
{home_team}: {home_goals}
{away_team}: {away_goals}
"""

GOAL_FOOTER_TEMPLATE = """
{home_team}: {home_goals}
{away_team}: {away_goals}

{hashtags}
"""

ONE_ASSIST_TEMPLATE = """
Assisted by {primary_assist}.
"""

TWO_ASSIST_TEMPLATE = """
Assisted by {primary_assist} and {secondary_assist}.
"""
