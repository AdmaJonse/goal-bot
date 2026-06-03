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
        self.add_post(text)
        log.info("DRY RUN - Post payload:\n" + text)
        return tweet_id

    def reply(self, parent : Optional[Dict[str, str]], text : str) -> Optional[Dict[str, str]]:
        """
        Print a reply to the given parent with the specified text.
        """
        reply_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        self.add_post(text)
        if parent is not None and "id" in parent:
            log.info(
                "DRY RUN - Reply payload (parent id="
                + parent.get("id", "")
                + "):\n"
                + text
            )
        else:
            log.info("DRY RUN - Reply payload:\n" + text)
        return reply_id

    def post_with_media(self, text : str, media : str) -> Optional[Dict[str, str]]:
        """
        Print the specified text.
        """
        tweet_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        self.add_post(text)
        log.info(
            "DRY RUN - Post with media payload:\n"
            + text
            + "\nDRY RUN - Media source: "
            + media
        )
        return tweet_id

    def reply_with_media(self,
                         parent : Optional[Dict[str, str]],
                         text : str, media : str) -> Optional[Dict[str, str]]:
        """
        Print a reply to the given parent with the specified text.
        """
        reply_id : Optional[Dict[str, str]] = { "id": str(uuid.uuid1().int) }
        self.add_post(text)
        if parent is not None and "id" in parent:
            log.info(
                "DRY RUN - Reply with media payload (parent id="
                + parent.get("id", "")
                + "):\n"
                + text
                + "\nDRY RUN - Media source: "
                + media
            )
        else:
            log.info(
                "DRY RUN - Reply with media payload:\n"
                + text
                + "\nDRY RUN - Media source: "
                + media
            )
        return reply_id
