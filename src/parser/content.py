"""
This module handles parsing of the JSON content data.
"""

from datetime import datetime

from src.command.command_queue import command_queue
from src.command.post_highlight import PostHighlight
from src.data.highlight import Highlight
from src.highlight_list import HighlightList
from src.parser.parser import Parser


class ContentParser(Parser):
    """
    This class defines the parser for the live feed data.
    """

    def __init__(self, game_id : int, start_time : datetime):
        super().__init__(game_id, "/content")
        self.game_id        : int = game_id
        self.highlight_list : HighlightList = HighlightList()
        self.start_time     : datetime = start_time


    def parse(self):
        """
        Parse the content page for the current game to determine if there are any new
        highlights to post.
        """

        self.get_data()
        highlights = self.data["highlights"]["gameCenter"]["items"]
        if highlights:
            for data in highlights:
                highlight : Highlight = Highlight(self.game_id, data)
                if not self.highlight_list.exists(highlight.id):
                    self.highlight_list.add(highlight)

                    if highlight.event is not None and highlight.event.timestamp > self.start_time:
                        command_queue.enqueue(PostHighlight(highlight))
