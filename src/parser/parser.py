"""
This  defines the interface for data parsers.
"""

from abc import ABC, abstractmethod
from typing import Any

import requests
import requests.utils
import requests.structures

from src.logger import log

NHL_API_URL : str = "https://statsapi.web.nhl.com/api/v1/game/"

class Parser(ABC):
    """
    This class defines the interface for data parsers.
    """

    def __init__(self, game_id : int, path : str, base_url : str = NHL_API_URL):
        self.url  : str = base_url + str(game_id) + path
        self.data : Any = []
        log.verbose("Parsing from: " + self.url)


    def get_data(self):
        """
        This function retrieves the latest JSON data record for the current
        game from the NHL website.
        """
        params  : str = ""
        headers : requests.structures.CaseInsensitiveDict = requests.utils.default_headers()
        try:
            request : Any = requests.get(self.url, headers=headers, params=params)
            self.data = request.json()
        except requests.exceptions.ConnectionError:
            log.error("Error occurred while pulling data from: " + self.url)


    @abstractmethod
    def parse(self):
        """
        Parse the data pulled by the data request and convert it to a usable form.
        """
