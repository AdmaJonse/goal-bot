"""
This module defines the list of game threads.
"""

from typing import List
from src.game_thread import GameThread

class ThreadList:
    """
    This class defines the list of game threads.
    """

    def __init__(self) -> None:
        self.threads : List[GameThread] = []

    def set(self, threads : List[GameThread]) -> None:
        """
        Set the stored list of game threads.
        """
        self.threads = threads

    def append(self, thread : GameThread) -> None:
        """
        Append a thread to the list of game threads.
        """
        self.threads.append(thread)

    def clear(self) -> None:
        """
        Clear the list of game threads.
        """
        self.threads = []

    def get(self) -> List[GameThread]:
        """
        Return the list of game threads.
        """
        return self.threads

    def is_empty(self) -> bool:
        """
        Return a boolean indicating whether or not the list of game threads is empty.
        """
        return len(self.threads) <= 0
