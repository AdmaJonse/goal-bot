"""
This module defines the output method.
"""

from typing import Optional

from src.output.outputter import Outputter
from src.output.printer import Printer
from src.output.tweeter import Tweeter


class Output:
    """
    This class defines the output method to be used and any internal state of the
        output interface.
    """

    def __init__(self):
        self._dry_run   : bool = False
        self._outputter : Outputter = Tweeter()

        if self.dry_run:
            self._outputter = Printer()
        else:
            self._outputter = Tweeter()

    @property
    def dry_run(self) -> bool:
        """
        Return a boolean indicating whether or not we're in dry run mode.
        """
        return self._dry_run

    @dry_run.setter
    def dry_run(self, flag: bool):
        """
        Set the dry run flag.
        """
        self._dry_run = flag

        if self.dry_run:
            self._outputter = Printer()
        else:
            self._outputter = Tweeter()

    @property
    def outputter(self) -> Outputter:
        """
        Return the registered outputter instance.
        """
        return self._outputter


output = Output()


def post(text: str) -> Optional[int]:
    """
    Public function that will send a tweet with the specified text.
    """
    return output.outputter.post(text)


def reply(parent: Optional[int], text: str) -> Optional[int]:
    """
    Public function that will send a reply with the specified text to the
    tweet with the given parent.
    """
    return output.outputter.reply(parent, text)


def post_with_media(text: str, media: str) -> Optional[int]:
    """
    Send a tweet with the specified text.
    """
    return output.outputter.post_with_media(text, media)


def reply_with_media(parent: Optional[int], text: str, media: str) -> Optional[int]:
    """
    Send a reply to the given parent tweet with the specified text.
    """
    return output.outputter.reply_with_media(parent, text, media)


def has_posted_today(query: str = "") -> bool:
    """
    Return a boolean indicating whether or not we've posted today.
    """
    return output.outputter.has_posted_today(query)


def clear_posts() -> None:
    """
    Clear the list of today's posts.
    """
    output.outputter.clear_posts()
