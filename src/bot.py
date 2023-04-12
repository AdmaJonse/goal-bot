"""
This module handles the main logic to check for game updates.
"""

from datetime import datetime, timedelta
from typing import List
from threading import Thread
import pause

from src import schedule
from src.command.command_queue import command_queue
from src.command.check_game_status import CheckGameStatus
from src.game_thread import GameThread
from src.logger import log


def wait_until_morning():
    """
    This function will wait until the next day.
    """
    current_time : datetime = schedule.get_current_time()
    noon         : datetime = schedule.get_noon()
    if current_time > noon:
        noon += timedelta(days=1)
    log.info("Pausing until: " + schedule.time_to_string(noon))
    pause.until(noon)


def check_game_status(threads : List[Thread]):
    """
    Enqueue a parse command every five seconds.
    """
    while threads:
        command_queue.enqueue(CheckGameStatus(threads))
        pause.seconds(30)


def check_for_updates():
    """
    This function will check for a game on the current date. If a game is
    found, it will trigger game event parsing at game time. If no game is
    found, it will pause until tomorrow.
    """
    while True:

        log.flush()
        log.info("Checking for games today...")

        games   : List[int]    = schedule.get_todays_games()
        threads : List[Thread] = []

        # Create a thread for each of today's games
        if games:
            for game in games:
                threads.append(Thread(target=GameThread(game).run))

            # Start all threads
            for thread in threads:
                thread.start()

            # Perform a periodic check to determine if the game threads have finished
            status_thread : Thread = Thread(target=check_game_status, args=[threads])
            status_thread.start()

            command_queue.start()

        threads = []

        log.info("All games are finished for the day. Pausing until tomorrow.")
        wait_until_morning()
