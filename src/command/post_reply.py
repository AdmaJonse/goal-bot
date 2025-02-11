"""
This module defines the Post Highlight command.
"""

from typing import Dict, Optional

from src.command.command import Command, Priority
from src.data.highlight import Highlight
from src.logger import log
from src.output import output

# pylint: disable=too-few-public-methods
class PostReply(Command):
    """
    This class defines the Post Highlight command.
    """

    def __init__(self, updated : Highlight, previous : Highlight):
        self.post_id  : Dict[str, Optional[Dict[str, str]]] = previous.post_id
        self.updated  : Highlight     = updated
        self.previous : Highlight     = previous
        super().__init__("Post Reply", Priority.NORMAL)


    def execute(self) -> None:
        """
        Execute the command.
        """

        if self.post_id is None:
            log.error("Could not find existing post for highlight: " + str(self.previous))
            return

        if self.previous.event is None:
            log.error("Could find event for highlight: " + str(self.previous))
            return

        text : Optional[str] = self.updated.get_reply(self.previous.event)

        if text is None:
            log.error("Could not post reply - no post text.")
            return

        output.reply(self.post_id, text)
