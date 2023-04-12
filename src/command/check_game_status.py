"""
This module defines the Game Status Check command.
"""

from threading import Thread
from typing import List

from src.command.command import Command, Priority
from src.command.command_queue import command_queue

class CheckGameStatus(Command):
    """
    This class defines the Post Highlight command.
    """

    def __init__(self, threads : List[Thread]):
        super().__init__("Check Game Status", Priority.NORMAL)
        self.threads : List[Thread] = threads


    def execute(self) -> None:
        """
        Execute the command.
        """
        for thread in self.threads:
            if thread.is_alive():
                return
        command_queue.stop()
