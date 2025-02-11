"""
This module defines the Game Status Check command.
"""

from typing import List

from src.command.command import Command, Priority
from src.command.command_queue import command_queue
from src.game_thread import GameThread

# pylint: disable=too-few-public-methods
class CheckGameStatus(Command):
    """
    This class defines the Post Highlight command.
    """

    def __init__(self, threads : List[GameThread]):
        super().__init__("Check Game Status", Priority.NORMAL)
        self.threads : List[GameThread] = threads


    def execute(self) -> None:
        """
        Execute the command.
        """
        if len(self.threads) > 0:
            for thread in self.threads:
                if not thread.is_game_over():
                    return
            command_queue.stop()
