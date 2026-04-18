"""
This module defines the command queue class.
"""

from enum import Enum
from threading import Condition, Thread
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

# pylint: disable=too-few-public-methods
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

    def __init__(self) -> None:
        self.queue : List[Command] = []
        self.state : State = State.STOPPED
        self.condition : Condition = Condition()
        self.worker_thread : Optional[Thread] = None


    def enqueue(self, command : Command):
        """
        Enqueue the given Command in the command queue.
        """
        with self.condition:
            for index, item in enumerate(self.queue):
                if command > item:
                    self.queue.insert(index, command)
                    self.condition.notify()
                    return
            self.queue.append(command)
            self.condition.notify()


    def dequeue(self) -> Optional[Command]:
        """
        Dequeue the first element from the command queue.
        """
        with self.condition:
            return self._dequeue_locked()


    def empty(self) -> bool:
        """
        Return a boolean indicating whether or not the queue is empty.
        """
        with self.condition:
            return self._empty_locked()


    def _dequeue_locked(self) -> Optional[Command]:
        """
        Dequeue the first element from the command queue.
        """
        if not self._empty_locked():
            return self.queue.pop(0)
        return None


    def _empty_locked(self) -> bool:
        """
        Return a boolean indicating whether or not the queue is empty.
        """
        return not self.queue


    def start(self) -> None:
        """
        Start processing commands from the queue.
        """
        with self.condition:
            if self.state == State.RUNNING:
                return
            self.state = State.RUNNING

        while True:
            try:
                command : Optional[Command] = self.wait_for_command()
                if command is None:
                    log.info("Stopping the command server.")
                    with self.condition:
                        self.state = State.STOPPED
                        self.queue = []
                        self.worker_thread = None
                    break
                command.execute()
            except ShutdownException:
                log.info("Stopping the command server.")
                with self.condition:
                    self.state = State.STOPPED
                    self.queue = []
                    self.worker_thread = None
                    break


    def wait_for_command(self) -> Optional[Command]:
        """
        Block until there is a command to process or the queue is stopped.
        """
        with self.condition:
            while self._empty_locked():
                if self.state != State.RUNNING:
                    return None
                self.condition.wait()
            return self._dequeue_locked()


    def start_in_background(self) -> None:
        """
        Start processing commands in a daemon thread.
        """
        with self.condition:
            if self.worker_thread is not None and self.worker_thread.is_alive():
                return

            self.worker_thread = Thread(target=self.start, daemon=True, name="command-queue")
            worker_thread = self.worker_thread

        worker_thread.start()


    def stop(self) -> None:
        """
        Stop processing commands from the queue.
        """
        with self.condition:
            if self.state != State.RUNNING:
                return
            self.state = State.STOPPING

        self.enqueue(Shutdown())


command_queue = CommandQueue()
