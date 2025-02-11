"""
This is an output interface intended for dry runs. Rather than tweeting, it will
simply print the any tweets to the logs.
"""

import uuid
from typing import Dict, Optional

from src.logger import log
from src.output.outputter import Outputter

class Printer(Outputter):
    """
    This class defines an outputter that prints to the logs.
    """

    def name(self) -> str:
        """
        Return the name of this outputter.
        """
        return "printer"

    def post(self, text : str) -> Optional[Dict[str, str]]:
        """
        Print the specified text.
        """
        tweet_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        log.info("Post:\n" + text)
        return tweet_id

    def reply(self, parent : Optional[Dict[str, str]], text : str) -> Optional[Dict[str, str]]:
        """
        Print a reply to the given parent with the specified text.
        """
        reply_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        if parent is not None and "id" in parent:
            log.info("Reply to parent " + parent.get("id", "") + ":\n" + text)
        return reply_id

    def post_with_media(self, text : str, _media : str) -> Optional[Dict[str, str]]:
        """
        Print the specified text.
        """
        tweet_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        log.info("Tweet:\n" + text)
        return tweet_id

    def reply_with_media(self,
                         parent : Optional[Dict[str, str]],
                         text : str, _media : str) -> Optional[Dict[str, str]]:
        """
        Print a reply to the given parent with the specified text.
        """
        reply_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        if parent is not None and "id" in parent:
            log.info("Reply to parent " + parent.get("id", "") + ":\n" + text)
        return reply_id
