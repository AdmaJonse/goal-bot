"""
This module defines the application health check command.
"""

import threading

from src.command.command import Command, Priority
from src.logger import log

# pylint: disable=too-few-public-methods
class CheckHealth(Command):
    """
    This class defines the Post Highlight command.
    """

    def __init__(self):
        super().__init__("Check Health", Priority.HIGH)
        self._event = threading.Event()


    def execute(self) -> None:
        """
        Execute the command.
        """
        log.info("Checking health of application.")
        self._event.set()

    @property
    def event(self) -> threading.Event:
        """
        Return the event for the command.
        """
        return self._event
