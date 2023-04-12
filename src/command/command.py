"""
This module defines the Command interface.
"""

from abc import ABC, abstractmethod
from enum import Enum


class Priority(Enum):
    """
    The priority of the Command.
    """
    HIGH   = 1
    NORMAL = 2


class Command(ABC):
    """
    The Command interface defines the method for executing the command.
    """

    def __init__(self, name : str, priority : Priority):
        self.name     : str      = name
        self.priority : Priority = priority


    def __str__(self) -> str:
        return "Command: " + self.name


    @abstractmethod
    def execute(self) -> None:
        """
        Execute the command.
        """


    def __lt__(self, other) -> bool:
        return self.priority == Priority.NORMAL and other.priority != Priority.NORMAL
