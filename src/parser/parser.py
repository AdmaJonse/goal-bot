"""
This defines the interface for data parsers.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import time
import random
import gzip
import json

import requests
import requests.utils
import requests.structures

from src.logger import log

NHL_API_URL: str = "https://api-web.nhle.com/v1/gamecenter/"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nhl.com/",
    "Origin": "https://www.nhl.com",
}

MAX_ATTEMPTS = 4
BASE_SLEEP = 0.4


class Parser(ABC):
    """
    Base class for NHL API data parsers. Handles retrieval, decoding, retry logic,
    and defensive checks for CDN anomalies. Subclasses implement parse() to convert
    raw API JSON into structured domain-specific objects.
    """

    def __init__(self, game_id: int, path: str,
                 base_url: str = NHL_API_URL) -> None:
        self.game_id: int = game_id
        self.url: str = base_url + str(game_id) + path
        self.data: Any = {}
        log.verbose("Parsing from: " + self.url)

    def _sleep_backoff(self, attempt: int) -> None:
        sleep_time = BASE_SLEEP * (2 ** (attempt - 1))
        sleep_time += random.uniform(0.05, 0.25)
        time.sleep(sleep_time)

    def _fetch_json_with_retry(self) -> Optional[Any]:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                resp = requests.get(
                    self.url,
                    headers=BROWSER_HEADERS,
                    timeout=10,
                )
            except requests.exceptions.Timeout:
                log.error(
                    f"Timeout occurred while pulling data from: {self.url}"
                )
                self._sleep_backoff(attempt)
                continue
            except requests.exceptions.ConnectionError:
                log.error(
                    f"Connection error occurred while pulling data from: "
                    f"{self.url}"
                )
                self._sleep_backoff(attempt)
                continue

            body = resp.content
            if not body or len(body) < 50:
                log.error(
                    f"Body too small ({len(body)} bytes) while pulling data "
                    f"from: {self.url}"
                )
                self._sleep_backoff(attempt)
                continue

            raw = body
            if raw.startswith(b"\x1f\x8b\x08"):
                try:
                    raw = gzip.decompress(raw)
                except OSError as e:
                    log.error(
                        f"Gzip decode error from {self.url}: {e}"
                    )
                    self._sleep_backoff(attempt)
                    continue

            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as e:
                snippet = raw[:200].decode(errors="ignore")
                log.error(
                    f"Unicode decode error from {self.url}: {e} | "
                    f"snippet: {snippet}"
                )
                self._sleep_backoff(attempt)
                continue

            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                snippet = text[:200]
                log.error(
                    f"JSON decode error while pulling data from {self.url}: "
                    f"{e} | snippet: {snippet}"
                )
                self._sleep_backoff(attempt)
                continue
            except ValueError as e:
                snippet = text[:200]
                log.error(
                    f"Invalid JSON structure from {self.url}: {e} | "
                    f"snippet: {snippet}"
                )
                self._sleep_backoff(attempt)
                continue

        log.error(f"All attempts to fetch data from {self.url} failed.")
        return None

    def get_data(self) -> None:
        """
        Retrieve JSON data for the associated game. Handles retries, CDN anomalies,
        decode failures, and assigns the parsed result to self.data. If retrieval
        fails after all attempts, self.data is set to an empty dict.
        """
        result = self._fetch_json_with_retry()
        if result is None:
            log.error(f"Game data is null for game: {self.game_id}")
            self.data = {}
        else:
            self.data = result

    @abstractmethod
    def parse(self):
        """
        Parse the fetched JSON data.
        """
