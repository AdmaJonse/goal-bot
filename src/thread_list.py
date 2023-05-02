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

    def set(self, threads : List[GameThread]):
        """
        TODO
        """
        self.threads = threads

    def append(self, thread : GameThread):
        """
        TODO
        """
        self.threads.append(thread)

    def clear(self):
        """
        TODO
        """
        self.threads = []

    def get(self):
        """
        TODO
        """
        return self.threads

    def is_empty(self):
        """
        TODO
        """
        return len(self.threads) <= 0
