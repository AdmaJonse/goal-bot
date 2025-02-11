"""
This module defines the output method.
"""

from typing import Dict, List, Optional

from src.logger import log
from src.output.outputter import Outputter
from src.output.printer import Printer
from src.output.bluesky import BlueSky
from src.output.tweeter import Tweeter


class Output:
    """
    This class defines the output method to be used and any internal state of the
    output interface.
    """

    def __init__(self) -> None:
        self._dry_run: bool = False
        self._outputters: List[Outputter] = []

        if self.dry_run:
            self._outputters.append(Printer())
        else:
            self._outputters.append(BlueSky())
            self._outputters.append(Tweeter())

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

    @property
    def outputters(self) -> List[Outputter]:
        """
        Return the registered outputter instance.
        """
        return self._outputters


output = Output()


def post(text: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a post with the specified text.
    """
    log.info("Post:\n" + text)
    post_ids: Dict[str, Optional[Dict[str, str]]] = {}
    for outputter in output.outputters:
        post_id : Optional[Dict[str, str]] = outputter.post(text)
        post_ids[outputter.name()] = post_id
    return post_ids


def reply(parents : Dict[str, Optional[Dict[str, str]]],
          text: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a post with the specified text as a reply to the given parent.
    """
    log.info("Reply:\n" + text)
    post_ids: Dict[str, Optional[Dict[str, str]]] = {}
    for outputter in output.outputters:
        parent : Optional[Dict[str, str]] = parents.get(outputter.name())
        if parent is not None:
            post_id: Optional[Dict[str, str]] = outputter.reply(parent, text)
            post_ids[outputter.name()] = post_id
    return post_ids


def post_with_media(text: str, media: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a post with the specified text and media.
    """
    log.info("Post:\n" + text)
    post_ids : Dict[str, Optional[Dict[str, str]]] = {}
    for outputter in output.outputters:
        post_id : Optional[Dict[str, str]] = outputter.post_with_media(text, media)
        post_ids[outputter.name()] = post_id
    return post_ids


def reply_with_media(
    parents: Dict[str, Optional[Dict[str, str]]],
    text: str,
    media: str
) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a reply to the given parent tweet with the specified text.
    """
    log.info("Reply:\n" + text)
    post_ids: Dict[str, Optional[Dict[str, str]]] = {}
    for outputter in output.outputters:
        parent: Optional[Dict[str, str]] = parents.get(outputter.name())
        if parent is not None:
            post_id : Optional[Dict[str, str]] = outputter.reply_with_media(parent, text, media)
            post_ids[outputter.name()] = post_id
    return post_ids


def has_posted_today(query: str = "") -> Dict[str, bool]:
    """
    Return a boolean indicating whether or not we've posted today.
    """
    has_posted: Dict[str, bool] = {}
    for outputter in output.outputters:
        has_posted[outputter.name()] = outputter.has_posted_today(query)
    return has_posted


def clear_posts() -> None:
    """
    Clear the list of today's posts.
    """
    for outputter in output.outputters:
        outputter.clear_posts()
