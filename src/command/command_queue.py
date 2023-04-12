"""
This module defines the command queue class.
"""

from enum import Enum
from typing import Optional, List

from src.command.command import Command, Priority
from src.logger import log


class State(Enum):
    """
    The state of the command queue.
    """
    STOPPED  = 1
    RUNNING  = 2
    STOPPING = 3


class ShutdownException(Exception):
    """
    Exception used to shutdown the command queue.
    """


class Shutdown(Command):
    """
    The command used to stop the command queue.
    """
    def __init__(self):
        super().__init__("Shutdown", Priority.NORMAL)

    def execute(self) -> None:
        raise ShutdownException()


class CommandQueue:
    """
    The Command Queue is responsible for executing the commands that are enqueued.
    """

    def __init__(self):
        self.queue : List  = []
        self.state : State = State.STOPPED


    def enqueue(self, command : Command):
        """
        Enqueue the given Command in the command queue.
        """
        for index, item in enumerate(self.queue):
            if command > item:
                self.queue.insert(index, command)
                return
        self.queue.append(command)


    def dequeue(self) -> Optional[Command]:
        """
        Dequeue the first element from the command queue.
        """
        if not self.empty():
            return self.queue.pop(0)
        return None


    def empty(self) -> bool:
        """
        Return a boolean indicating whether or not the queue is empty.
        """
        return not self.queue


    def start(self):
        """
        Start processing commands from the queue.
        """
        self.state = State.RUNNING
        while True:
            if not self.empty():
                try:
                    command : Optional[Command] = self.dequeue()
                    if command is not None:
                        command.execute()
                except ShutdownException:
                    log.info("Stopping the command server.")
                    self.state = State.STOPPED
                    self.queue = []
                    break


    def stop(self):
        """
        Stop processing commands from the queue.
        """
        self.state = State.STOPPING
        self.enqueue(Shutdown())


command_queue = CommandQueue()
