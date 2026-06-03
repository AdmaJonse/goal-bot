"""
The main process for the NHL twitter bot application.
"""

import argparse
from datetime import timedelta
import threading
import logging
import signal
import sys

from os import path
from flask import Flask
from waitress import serve

from src import logger
from src import schedule
from src import bot
from src import health
from src.output.output import output

app = Flask(__name__)

# prevent flask from logging requests
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/", methods=["GET"])
def home():
    """
    Front-end of the web application.
    """
    if not path.exists ("bot.log"):
        return ""

    with open("bot.log", encoding="utf-8") as log_file:
        return "<xmp>" + log_file.read() + "</xmp>"

def shutdown(_signum, _frame):
    """
    Shutdown the bot and the web application.
    """
    logger.log.info("Shutting down...")
    sys.exit(0)


health.register_health_route(app)

signal.signal(signal.SIGTERM, shutdown)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="NHL goal bot")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without posting to Bluesky/Twitter; log output locally only.",
    )
    parser.add_argument(
        "--yesterday",
        action="store_true",
        help="Process yesterday's games once and exit.",
    )

    args = parser.parse_args()

    if args.dry_run:
        output.dry_run = True
        logger.log.info("Dry run enabled. Using Printer output only.")

    if args.yesterday:
        yesterday = schedule.get_current_date() - timedelta(days=1)
        output.set_duplicate_reference_date(yesterday)
        bot.run_for_date(yesterday)
        sys.exit(0)

    # Run the twitter bot in the background
    bot_thread = threading.Thread (target = bot.check_for_updates, daemon = True)
    bot_thread.start()

    health.start_health_watchdog()

    # Run the front-end web application
    serve(app, host="0.0.0.0", port=5000, _quiet=True)
