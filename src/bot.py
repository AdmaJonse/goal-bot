"""
This module handles the main logic to check for game updates.
"""

from datetime import datetime, timedelta
from threading import Thread
from typing import List, Optional
import pause

from src import schedule
from src.command.command_queue import command_queue
from src.command.check_game_status import CheckGameStatus
from src.command.check_health import CheckHealth
from src.game_thread import GameThread
from src.logger import log
from src.output import output
from src.thread_list import ThreadList

threads : ThreadList = ThreadList()

def wait_until_morning() -> None:
    """
    This function will wait until the next day.
    """
    current_time : datetime = schedule.get_current_time()
    morning      : datetime = schedule.get_morning()
    if current_time > morning:
        morning += timedelta(days=1)
    log.info("Pausing until: " + schedule.time_to_string(morning))
    pause.until(morning)


def check_game_status() -> None:
    """
    Enqueue a parse command every five seconds.
    """
    while not threads.is_empty():
        command_queue.enqueue(CheckGameStatus(threads.get()))
        pause.seconds(30)
    log.info("Exiting status thread")


def check_health() -> bool:
    """
    Check the health of the application by enqueueing a command and
    ensuring that it is processed in a reasonable amount of time.
    """
    health_check = CheckHealth()
    command_queue.enqueue(health_check)
    result = health_check.event.wait(1)
    return result


def check_for_updates() -> None:
    """
    This function will check for a game on the current date. If a game is
    found, it will trigger game event parsing at game time. If no game is
    found, it will pause until tomorrow.
    """
    while True:

        log.flush()
        log.info("Checking for games today...")

        games : Optional[List[int]] = schedule.get_todays_games()

        # Create a thread for each of today's games
        if games:
            for game in games:
                threads.append(GameThread(game))

            # Start all threads
            for thread in threads.get():
                thread.start()

            # Perform a periodic check to determine if the game threads have finished
            status_thread : Thread = Thread(target=check_game_status)
            status_thread.start()

            # Start the command server. This call will block until the shutdown command is executed.
            command_queue.start()

            # Stop checking the status of games
            threads.clear()
            output.clear_posts()
            status_thread.join()
            log.info("All games are finished for the day. Pausing until tomorrow.")

        else:
            log.info("There are no games today. Pausing until tomorrow.")

        wait_until_morning()
