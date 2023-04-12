"""
This is an output interface intended for dry runs. Rather than tweeting, it will
    simply print the any tweets to the logs.
"""

import uuid
from typing import Optional

from src.logger import log
from src.output.outputter import Outputter

class Printer(Outputter):
    """
    This class provides an interface to Twitter than can be used to
        authenticate, tweet and reply.
    """

    def post(self, text : str) -> Optional[int]:
        """
        Print the specified text.
        """
        tweet_id : Optional[int] = uuid.uuid1().int
        log.info("Tweet:\n" + text)
        return tweet_id


    def reply(self, parent : Optional[int], text : str) -> Optional[int]:
        """
        Print a reply to the given parent with the specified text.
        """
        reply_id : Optional[int] = uuid.uuid1().int
        if parent is not None and parent > 0:
            log.info("Reply to parent " + str(parent) + ":\n" + text)
        return reply_id


    def post_with_media(self, text : str, _media : str) -> Optional[int]:
        """
        Print the specified text.
        """
        tweet_id : Optional[int] = uuid.uuid1().int
        log.info("Tweet:\n" + text)
        return tweet_id


    def reply_with_media(self, parent : Optional[int], text : str, _media : str) -> Optional[int]:
        """
        Print a reply to the given parent with the specified text.
        """
        reply_id : Optional[int] = uuid.uuid1().int
        if parent is not None and parent > 0:
            log.info("Reply to parent " + str(parent) + ":\n" + text)
        return reply_id


    def has_posted_today(self, _query : str = ""):
        """
        Return a boolean indicating whether or not we've posted today.
        """
        return True
