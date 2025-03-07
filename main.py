"""
The main process for the NHL twitter bot application.
"""

import threading
import logging
import signal
import sys

from os import path
from flask import Flask
from waitress import serve

from src import bot
from src import logger

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

@app.route('/health')
def health():
    """
    Health check endpoint.
    """
    if not bot.check_health():
        return "Health check failed", 503
    return "Healthy", 200

def shutdown(_signum, _frame):
    """
    Shutdown the bot and the web application.
    """
    logger.log.info("Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)

if __name__ == '__main__':

    # Run the twitter bot in the background
    bot_thread = threading.Thread (target = bot.check_for_updates, daemon = True)
    bot_thread.start()

    # Run the front-end web application
    serve(app, host="0.0.0.0", port=5000, _quiet=True)
