"""
This module defines the Post Highlight command.
"""

from typing import Optional

from src.command.command import Command, Priority
from src.data.highlight import Highlight
from src.logger import log
from src.output import output

# pylint: disable=too-few-public-methods
class PostHighlight(Command):
    """
    This class defines the Post Highlight command.
    """

    def __init__(self, highlight : Highlight):
        self.highlight : Highlight = highlight
        super().__init__("Post Highlight", Priority.NORMAL)


    def execute(self) -> None:
        """
        Execute the command.
        """
        self.highlight.is_pending = True

        try:
            text    : Optional[str] = self.highlight.get_post()
            footer  : Optional[str] = self.highlight.get_footer()

            if text is None:
                log.error("Could not post highlight - no post text.")
                self.highlight.post_id = {}
                return

            if footer is None:
                log.error("Could not post highlight - no footer text")
                self.highlight.post_id = {}
                return

            duplicate_status = output.has_posted_today(text)
            all_outputs_duplicate = len(duplicate_status) > 0 and all(duplicate_status.values())
            any_output_duplicate = any(duplicate_status.values())
            result = output.post_with_media(
                text,
                self.highlight.video,
                duplicate_status,
            )

            if any(post_id is not None for post_id in result.values()):
                self.highlight.post_id = result
                return

            if all_outputs_duplicate:
                # Terminal duplicate for this day; keep sentinel to avoid retries.
                terminal_duplicate_result = dict(result)
                terminal_duplicate_result["_duplicate"] = None
                self.highlight.post_id = terminal_duplicate_result
                return

            if any_output_duplicate:
                # At least one output already posted this highlight for the day.
                # Avoid retry loops when remaining outputs are unavailable (for example 429).
                terminal_duplicate_result = dict(result)
                terminal_duplicate_result["_duplicate"] = None
                self.highlight.post_id = terminal_duplicate_result
                return

            # Transient failure (for example, media temporarily unavailable). Allow retry.
            self.highlight.post_id = {}
        finally:
            self.highlight.is_pending = False
