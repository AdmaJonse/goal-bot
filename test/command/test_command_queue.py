"""
Tests for the command queue worker.
"""

import time

from src import bot
from src.command.check_health import CheckHealth
from src.command.command_queue import CommandQueue, State


def test_background_queue_processes_health_check() -> None:
    """
    The queue should process commands even when no game loop is actively blocking on it.
    """
    queue = CommandQueue()
    health_check = CheckHealth()

    queue.start_in_background()
    queue.enqueue(health_check)

    assert health_check.event.wait(1.0)

    queue.stop()

    deadline = time.time() + 1.0
    while time.time() < deadline and queue.state != State.STOPPED:
        time.sleep(0.01)

    assert queue.state == State.STOPPED


def test_health_check_passes_when_queue_not_running(monkeypatch) -> None:
    """
    Health checks should not fail just because the command queue is idle.
    """
    queue = CommandQueue()

    monkeypatch.setattr(bot, "command_queue", queue)

    assert bot.check_health() is True
