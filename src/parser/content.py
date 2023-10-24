"""
This module handles parsing of the JSON content data.
"""

from datetime import datetime

from src.command.command_queue import command_queue
from src.command.post_highlight import PostHighlight
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


    def parse(self):
        """
        Parse the content page for the current game to determine if there are any new
        highlights to post.
        """

        self.get_data()

        if "summary" in self.data:
            if "scoring" in self.data["summary"]:
                for data in self.data["summary"]["scoring"]:
                    for goal in data["goals"]:
                        if "highlightClip" in goal:
                            highlight : Highlight = Highlight(self.game_id, goal)
                            if not self.highlight_list.exists(highlight):
                                log.info("Adding highlight to list: " + str(highlight.id))
                                self.highlight_list.add(highlight)

                                if (highlight.event is not None and
                                    highlight.event.timestamp > self.start_time):
                                    command_queue.enqueue(PostHighlight(highlight))
