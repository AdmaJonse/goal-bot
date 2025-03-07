"""
This module handles parsing of the JSON content data.
"""

from datetime import datetime
from typing import Optional

from src.command.command_queue import command_queue
from src.command.post_highlight import PostHighlight
from src.command.post_reply import PostReply
from src.data.highlight import Highlight
from src.highlight_list import HighlightList
from src.logger import log
from src.parser.parser import Parser

GAME_CENTER_URL : str = "https://api-web.nhle.com/v1/gamecenter/"

class ContentParser(Parser):
    """
    This class defines the parser for the live feed data.
    """

    def __init__(self, game_id : int, start_time : datetime):
        super().__init__(game_id, "/landing", GAME_CENTER_URL)
        self.game_id        : int = game_id
        self.highlight_list : HighlightList = HighlightList()
        self.start_time     : datetime = start_time


    def parse(self) -> None:
        """
        Parse the content page for the current game to determine if there are any new
        highlights to post.
        """

        self.get_data()

        if self.data is None:
            return

        scoring_data = self.data.get("summary", {}).get("scoring", None)

        if scoring_data is None:
            return

        for period in scoring_data:
            for goal in period.get("goals", {}):

                if "highlightClip" not in goal:
                    continue

                highlight : Highlight = Highlight(self.game_id, goal)
                if not self.highlight_list.exists(highlight):
                    log.info("Adding highlight to list: " + str(highlight.id))
                    self.highlight_list.add(highlight)

                    if highlight.event is not None:
                        command_queue.enqueue(PostHighlight(highlight))
                    else:
                        log.error("Highlight event is none. Could not enqueue.")
                else:
                    previous : Optional[Highlight] = self.highlight_list.get(highlight.id)
                    if previous is not None and previous.event != highlight.event:
                        log.info("Updating existing highlight: " + str(highlight.id))
                        self.highlight_list.update(highlight)
                        command_queue.enqueue(PostReply(highlight, previous))
