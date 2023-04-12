"""
This module defines logging behaviour for the application.
"""

import logging
import logging.handlers
import sys

LOG_FILE = "bot.log"

class Logger:
    """
    This class defines logging behaviour for the application.
    """

    def __init__(self):

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('| %(levelname)s | %(message)s')

        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.stdout_handler.setLevel(logging.INFO)
        self.stdout_handler.setFormatter(formatter)

        self.file_handler = logging.handlers.RotatingFileHandler(LOG_FILE,
                                                                 maxBytes=1000000,
                                                                 backupCount=1)
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(formatter)

        self.logger.addHandler(self.stdout_handler)
        self.logger.addHandler(self.file_handler)


    def info(self, msg):
        """
        Log the given message at the info level.
        """
        self.logger.info(msg)


    def error(self, msg):
        """
        Log the given message at the error level.
        """
        self.logger.error(msg)


    def verbose(self, msg):
        """
        Log the given message at the debug level.
        """
        self.logger.debug(msg)


    def flush(self):
        """
        Delete the current log file.
        """
        self.file_handler.doRollover()


log = Logger()
