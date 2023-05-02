"""
TODO
"""

from typing import List
from src.game_thread import GameThread

class ThreadList:
    """
    TODO
    """

    def __init__(self):
        self.threads : List[GameThread] = []

    def set(self, threads : List[GameThread]) -> None:
        """
        TODO
        """
        self.threads = threads

    def append(self, thread : GameThread) -> None:
        """
        TODO
        """
        self.threads.append(thread)

    def clear(self) -> None:
        """
        TODO
        """
        self.threads = []

    def get(self) -> List[GameThread]:
        """
        TODO
        """
        return self.threads

    def is_empty(self) -> bool:
        """
        TODO
        """
        return len(self.threads) <= 0
