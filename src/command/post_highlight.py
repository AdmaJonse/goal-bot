"""
This module defines the Post Highlight command.
"""

from typing import Optional

from src.command.command import Command, Priority
from src.data.highlight import Highlight
from src.output import output

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
        text   : Optional[str] = self.highlight.get_post()
        footer : Optional[str] = self.highlight.get_footer()
        if (text is not None and
            footer is not None and
            not output.has_posted_today(footer.strip())):
            output.post_with_media(text, self.highlight.video)
