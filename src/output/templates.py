"""
Templates for the tweets that are posted by this bot. These container placeholder values which will
be replaced by actual values prior to posting.
"""

GOAL_TEMPLATE = """\
{team} goal!

Scored by {scorer} with {time} remaining in the {period} period.
"""

POWER_PLAY_GOAL_TEMPLATE = """\
Power play goal for {team}!

Scored by {scorer} with {time} remaining in the {period} period.
"""

SHORT_HANDED_GOAL_TEMPLATE = """\
Short-handed goal for {team}!

Scored by {scorer} with {time} remaining in the {period} period.
"""

EMPTY_NET_GOAL_TEMPLATE = """\
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

SCORER_UPDATE_TEMPLATE = """\
The goal is now being awarded to {scorer}.

{hashtags}
"""

ASSIST_ADD_PRIMARY_TEMPLATE = """\
A primary assist has been awarded to {primary_assist}.

{hashtags}
"""

ASSIST_ADD_SECONDARY_TEMPLATE = """\
A secondary assist has been awarded to {secondary_assist}.

{hashtags}
"""

ASSIST_ADD_BOTH_TEMPLATE = """\
Assists have been awarded to {primary_assist} and {secondary_assist}.

{hashtags}
"""

ASSIST_UPDATE_TEMPLATE = """\
The assists have been changed on this goal. Assists are now awarded to {primary_assist} and {secondary_assist}.

{hashtags}
"""

PRIMARY_ASSIST_UPDATE_TEMPLATE = """\
The assists have been changed on this goal. The primary assist has been awarded to {primary_assist}.

{hashtags}
"""

SECONDARY_ASSIST_UPDATE_TEMPLATE = """\
The assists have been changed on this goal. The secondary assist has been awarded to {secondary_assist}.

{hashtags}
"""

GOAL_TIME_UPDATE_TEMPLATE = """\
The time of this goal has been changed. The scoresheet now indicates this goal occurred with {time} remaining in the {period} period.

{hashtags}
"""
