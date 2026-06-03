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
from src.output import output
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


    def _process_new_highlight(self, highlight: Highlight) -> None:
        """
        Process a newly discovered highlight.
        """
        log.info("Adding highlight to list: " + str(highlight.id))
        self.highlight_list.add(highlight)

        if highlight.event is not None:
            highlight.post_id = {"_queued": None}
            command_queue.enqueue(PostHighlight(highlight))
        else:
            log.error("Highlight event is none. Could not enqueue.")


    def _process_existing_highlight(
        self, highlight: Highlight, previous: Optional[Highlight]
    ) -> None:
        """
        Process an existing highlight (retry or update).
        """
        if previous is None or self._is_post_terminal(previous):
            # Check for event update on terminal posts
            if previous is not None and previous.event != highlight.event:
                log.info("Updating existing highlight: " + str(highlight.id))
                self.highlight_list.update(highlight)
                command_queue.enqueue(PostReply(highlight, previous))
            return

        # Non-terminal: check for retry eligibility
        if previous.event != highlight.event:
            self.highlight_list.update(highlight)
            previous = highlight

        if previous.is_pending or "_queued" in previous.post_id:
            return  # Still pending or queued, no retry

        # Check if ready for retry
        retry_text: Optional[str] = previous.get_post()
        if retry_text is not None and self._is_duplicate_on_all_outputs(retry_text):
            previous.post_id = {"_duplicate": None}
            return

        log.info("Retrying highlight post: " + str(highlight.id))
        previous.post_id = {"_queued": None}
        command_queue.enqueue(PostHighlight(previous))


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

                try:
                    highlight : Highlight = Highlight(self.game_id, goal)
                except (KeyError, TypeError, ValueError) as exc:
                    log.warning("Skipping malformed goal payload: " + str(exc))
                    continue

                if not self.highlight_list.exists(highlight):
                    self._process_new_highlight(highlight)
                else:
                    previous = self.highlight_list.get(highlight.id)
                    self._process_existing_highlight(highlight, previous)


    @staticmethod
    def _is_post_terminal(highlight: Highlight) -> bool:
        """
        Return True when this highlight should not be retried.
        Successful posts and duplicate posts are terminal.
        """
        if "_duplicate" in highlight.post_id:
            return True

        if (
            len(highlight.post_id) > 0
            and all(not key.startswith("_") for key in highlight.post_id.keys())
            and all(post_id is None for post_id in highlight.post_id.values())
        ):
            return True

        for post_id in highlight.post_id.values():
            if post_id is not None:
                return True
        return False


    @staticmethod
    def _is_duplicate_on_all_outputs(text: str) -> bool:
        """
        Return True when all configured outputs already posted this text today.
        """
        duplicate_status = output.has_posted_today(text)
        return len(duplicate_status) > 0 and all(duplicate_status.values())
