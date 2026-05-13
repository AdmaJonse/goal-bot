"""
This module contains the Outputter class, which is the base class for output interfaces.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from src import utils

class Outputter(ABC):
    """
    The Outputter class is the base class for output interfaces, such as the tweeter and
    printer classes.
    """
    posts : List[str] = []

    def __init__(self):
        self.posts = []

    @abstractmethod
    def name(self) -> str:
        """
        Return the name of this outputter.
        """

    @abstractmethod
    def post(self, _text : str) -> Optional[Dict[str, str]]:
        """
        Send a post with the specified text.
        """

    @abstractmethod
    def reply(self, _parent : Optional[Dict[str, str]], _text : str) -> Optional[Dict[str, str]]:
        """
        Send a reply to the given parent with the specified text.
        """

    @abstractmethod
    def post_with_media(self, _text : str, _media : str) -> Optional[Dict[str, str]]:
        """
        Send a post with the specified text and media attachment.
        """

    @abstractmethod
    def reply_with_media(self,
                         _parent : Optional[Dict[str, str]],
                         _text : str,
                         _media : str) -> Optional[Dict[str, str]]:
        """
        Send a reply to the given parent with the specified text and media attachment.
        """

    def has_posted_today(self, query : str = "") -> bool:
        """
        Return a boolean indicating whether or not a tweet has been sent today.
        """
        score_query = utils.strip_text(query)
        normalized_query = self._normalize_post_text(query)

        for post in self.posts:
            if score_query != "":
                if utils.strip_text(post) == score_query:
                    return True
                continue

            if normalized_query in post:
                return True
        return False

    def set_duplicate_reference_date(self, _value: datetime) -> None:
        """
        Configure which day should be used for duplicate history.
        Outputters that query remote history can override this.
        """

    @staticmethod
    def _normalize_post_text(text: str) -> str:
        """
        Normalize post text for reliable duplicate matching.
        """
        return "\n".join(line.rstrip() for line in text.strip().splitlines())

    def add_post(self, text : str) -> None:
        """
        Add the given post to our list of posts.
        """
        self.posts.append(self._normalize_post_text(text))

    def clear_posts(self) -> None:
        """
        Clear the list of posts.
        """
        self.posts = []

    def has_posted(self, text: str) -> bool:
        """
        Return a boolean indicating whether or not the given text has been posted.
        """
        score_text = utils.strip_text(text)
        if score_text != "":
            for post in self.posts:
                if utils.strip_text(post) == score_text:
                    return True

        normalized_text = self._normalize_post_text(text)
        return normalized_text in self.posts
