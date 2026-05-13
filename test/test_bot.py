"""
Tests for the bot update loop.
"""

import pytest

from src import bot
from src.thread_list import ThreadList


class _DummyGameThread:
    """
    Minimal game thread stub for the update loop test.
    """

    def __init__(self, _game_id: int):
        self.started = False

    def start(self) -> None:
        self.started = True


class _StatusThreadAssertsClearBeforeJoin:
    """
    Fake status thread that verifies join happens after thread list clear.
    """

    def __init__(self, target):
        self.target = target

    def start(self) -> None:
        # Intentionally do not run the target loop; this is an ordering test.
        return

    def join(self) -> None:
        assert bot.threads.is_empty(), "threads must be cleared before status join"


def test_check_for_updates_clears_threads_before_join(monkeypatch) -> None:
    """
    The daily loop should clear shared game threads before joining the status thread,
    otherwise it can deadlock and never reach the next-day pause.
    """

    monkeypatch.setattr(bot, "threads", ThreadList())
    monkeypatch.setattr(bot, "GameThread", _DummyGameThread)
    monkeypatch.setattr(bot, "Thread", _StatusThreadAssertsClearBeforeJoin)
    monkeypatch.setattr(bot.schedule, "get_todays_games", lambda: [12345])
    monkeypatch.setattr(bot.command_queue, "start", lambda: None)
    monkeypatch.setattr(bot.output, "clear_posts", lambda: None)

    def _stop_after_first_cycle() -> None:
        raise RuntimeError("stop-loop")

    monkeypatch.setattr(bot, "wait_until_morning", _stop_after_first_cycle)

    with pytest.raises(RuntimeError, match="stop-loop"):
        bot.check_for_updates()
