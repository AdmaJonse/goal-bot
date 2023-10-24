"""
This module defines a list of all highlights that have been processed.
"""

from typing import Dict, Optional

from src.data.highlight import Highlight

class HighlightList:
    """
    This class defines a list of all highlights that have been processed.
    """

    def __init__(self):
        self.highlights : Dict[int, Highlight] = {}


    def add(self, highlight : Highlight) -> None:
        """
        Add a new highlight to the list. If it does not already exist, post the highlight.
        """
        if highlight.id not in self.highlights:
            self.highlights[highlight.id] = highlight


    def exists(self, highlight : Highlight) -> bool:
        """
        Return a boolean indicating whether or not this highlight ID exists in the list of
        processed highlights.
        """
        return highlight.id in self.highlights


    def get(self, highlight_id : int) -> Optional[Highlight]:
        """
        Return the highlight with the given ID from the list.
        """
        for highlight in self.highlights.values():
            if highlight.id == highlight_id:
                return highlight
        return None


    def clear(self) -> None:
        """
        Clear the list of highlights.
        """
        self.highlights = {}
