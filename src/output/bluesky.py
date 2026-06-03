"""
This module provides an interface to Bluesky than can be used to
authenticate, post and reply.
"""

import os
import socket
import time
import re

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from os.path import join, dirname, abspath
from typing import Any, Dict, List, Optional

from dateutil import parser

import atproto
import requests

from dotenv import load_dotenv

from src.logger import log
from src.output.outputter import Outputter
from src.output import video
from src import schedule
from src import utils

# maximum post length
MAX_LENGTH = 240 # characters

# Bluesky API base URL
BASE_URL = "https://bsky.social/xrpc/"

REQUEST_TIMEOUT = 30


def now() -> str:
    """
    Return the current date and time in ISO format.
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

HASHTAG_RE = re.compile(r"#\w+")

def get_tag_indices(text: str) -> list[tuple[int, int]]:
    """
    Bluesky doesn't just automatically parse hashtag locations,
    so you need to parse the text of your post and find any hashtags.
    Then you need to return the start and end indices of each
    hashtag. This is then sent in the post request as a facet.
    """

    indices: list[tuple[int, int]] = []

    for match in HASHTAG_RE.finditer(text):
        char_start, char_end = match.span()

        byte_start = len(text[:char_start].encode("utf-8"))
        byte_end = len(text[:char_end].encode("utf-8"))

        indices.append((byte_start, byte_end))

    return indices

def parse_tags(text : str) -> List:
    """
    Find the tag indices in the text, then add facets specifying
    the start adn end characters of each.
    """
    facets  : List = []
    indices : List[tuple[int,int]] = get_tag_indices(text)
    for start, end in indices:
        facets.append({
            "index": {
                "byteStart": start,
                "byteEnd": end,
            },
            "features": [
                {
                    "$type": "app.bsky.richtext.facet#tag",
                    "tag": text.encode("utf-8")[start:end].decode("utf-8")[1:]
                }
            ]})
    return facets


@dataclass
class Authentication:
    """
    This data class is used to store keys, tokens and secrets used in
    authentication with the Bluesky API.
    """

    handle        : str = ""
    password      : str = ""
    access_token  : str = ""
    refresh_token : str = ""
    user_id       : str = ""

    def __init__(self) -> None:
        """
        Read authentication details from the .env file.
        """

        # load constants from .env
        parent_dir  : str = dirname(dirname(dirname(abspath(__file__))))
        config_dir  : str = join(parent_dir, "config")
        dotenv_file : str = join(config_dir, '.env')
        load_dotenv(dotenv_file)

        # read the authentication keys
        self.handle   = os.getenv("HANDLE", "")
        self.password = os.getenv("PASSWORD", "")


class BlueSky(Outputter):
    """
    This class provides an interface to Bluesky than can be used to
    authenticate, post and reply.
    """

    def __init__(self) -> None:
        super().__init__()
        self.duplicate_reference_date: datetime = schedule.get_current_date()
        self.auth         : Authentication = Authentication()
        self.session      : Optional[dict] = None
        self.client       : atproto.Client = atproto.Client()
        self._session_tokens: dict = {}
        self.posts        : List[str] = []
        self._initialized : bool = False


    def _clear_session_state(self) -> None:
        """
        Clear in-memory session and token state after auth failures.
        """
        self.session = None
        self._session_tokens = {}


    def name(self) -> str:
        """
        Return the name of this outputter.
        """
        return "bluesky"


    def _ensure_initialized(self) -> None:
        """
        Perform one-time network setup: create an API session and load
        reference-day posts for duplicate detection.
        Called lazily on the first post or reply so that importing this module
        does not require live credentials.
        """
        if not self._initialized:
            if not self.create_session():
                return
            self.posts = self.get_posts_for_reference_day()
            self._initialized = True


    def set_duplicate_reference_date(self, value: datetime) -> None:
        """
        Set the date used to query duplicate history, then refresh cache.
        """
        self.duplicate_reference_date = value
        if self._initialized:
            self.posts = self.get_posts_for_reference_day()


    def create_session(self) -> bool:
        """
        Create a new session with the Bluesky API.
        """
        try:
            response = requests.post(
                BASE_URL + "com.atproto.server.createSession",
                json={
                    "identifier": self.auth.handle,
                    "password": self.auth.password
                    },
                timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as error:
            log.error("Bluesky - createSession request failed: " + str(error))
            self._clear_session_state()
            return False

        if not response.ok:
            log.error(
                "Bluesky - createSession failed with status "
                + str(response.status_code)
                + ": "
                + response.text
            )
            self._clear_session_state()
            return False

        try:
            session_payload = response.json()
        except ValueError:
            log.error("Bluesky - createSession returned invalid JSON response.")
            self._clear_session_state()
            return False

        access_token = session_payload.get("accessJwt")
        refresh_token = session_payload.get("refreshJwt")

        if access_token is None or refresh_token is None:
            log.error(
                "Bluesky - createSession missing required token fields. "
                + "response="
                + str(session_payload)
            )
            self._clear_session_state()
            return False

        self.session = session_payload
        self._session_tokens = {
            "access": access_token,
            "refresh": refresh_token,
        }
        return True


    def has_posted(self, text: str) -> bool:
        """
        Ensure Bluesky state is initialized before duplicate checks.
        This allows output-level duplicate filtering to work before media download.
        """
        self._ensure_initialized()
        return super().has_posted(text)


    def request(self, post : dict) -> Optional[Dict[str, str]]:
        """
        Send a POST request to the Bluesky API with the given post data.
        """

        if not self.create_session() or self.session is None:
            return None

        did = self.session.get("did")
        if did is None:
            log.error("Bluesky - Session missing did.")
            return None

        access_token = self._session_tokens.get("access", "")
        response = requests.post(
                    BASE_URL + "com.atproto.repo.createRecord",
                    headers={"Authorization": "Bearer " + access_token},
                    json={
                        "repo": did,
                        "collection": "app.bsky.feed.post",
                        "record": post,
                    },
                    timeout=REQUEST_TIMEOUT)

        if response.ok:
            self.add_post(post["text"])
            result = {
                "uri": response.json()["uri"],
                "cid": response.json()["cid"]
            }
            log.info("Bluesky - Post created successfully. uri=" + result["uri"])
            return result

        log.error("The request failed: " + response.text)
        return None


    def post(self, text : str) -> Optional[Dict[str, str]]:
        """
        Post with the specified text.
        """

        log.info("Bluesky - Post: " + utils.strip_text(text))

        self._ensure_initialized()
        if self.session is None:
            return None

        if len(text) > MAX_LENGTH:
            log.error("Bluesky - post is longer than the maximum length")
            return None

        if self.has_posted(text):
            log.warning("Bluesky - Skipping duplicate post: " + utils.strip_text(text))
            return None

        post : dict[Any, Any] = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now(),
            "facets": parse_tags(text)
        }

        return self.request(post)


    def reply(self, parent : Optional[Dict[str, str]], text : str) -> Optional[Dict[str, str]]:
        """
        Send a reply to the given parent post with the specified text.
        """

        log.info("Bluesky - Reply: " + utils.strip_text(text))

        self._ensure_initialized()
        if self.session is None:
            return None

        if parent is None:
            log.error("Bluesky - parent post is missing")
            return None

        if len(text) > MAX_LENGTH:
            log.error("Bluesky - post is longer than the maximum length")
            return None

        if self.has_posted(text):
            log.warning("Bluesky - Skipping duplicate post: " + utils.strip_text(text))
            return None

        if "cid" not in parent or "uri" not in parent:
            log.error("Bluesky - parent post is missing cid or uri")
            return None

        post : dict[Any, Any] = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now(),
            "facets": parse_tags(text),
            "reply": {
                "root": {
                    "uri": parent["uri"],
                    "cid": parent["cid"]
                },
                "parent": {
                    "uri": parent["uri"],
                    "cid": parent["cid"]
                }
            }
        }

        return self.request(post)


    def _perform_blob_upload(self, data: bytes) -> Optional[requests.Response]:
        """Helper method to perform blob upload with retries."""
        upload_attempts = 3
        response = None
        for attempt in range(1, upload_attempts + 1):
            if not self.create_session():
                attempt_str = f"{attempt}/{upload_attempts}"
                msg = f"Could not create session for video upload attempt {attempt_str}."
                log.error("Bluesky - " + msg)
                if attempt < upload_attempts:
                    time.sleep(10)
                continue
            try:
                socket.setdefaulttimeout(120)
                access_token = self._session_tokens.get("access", "")
                response = requests.post(
                    BASE_URL + "com.atproto.repo.uploadBlob",
                    headers={
                        "Content-Type": "video/mp4",
                        "Authorization": "Bearer " + access_token,
                    },
                    data=data,
                    timeout=120)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                log.error(f"Bluesky - Video upload attempt {attempt} failed: {e}")
                if attempt < upload_attempts:
                    time.sleep(10)
            finally:
                socket.setdefaulttimeout(None)
        return response


    def upload_video(self, url : str) -> Optional[str]:
        """
        Download the .mp4 from the given URL, perform a media upload,
        clean up and then return the media ID string.
        """
        filename: str = url
        downloaded_here: bool = False
        data: Optional[bytes] = None

        if not os.path.exists(url):
            filename = "highlight" + url[-8:-3] + ".mp4"
            downloaded_here = True

            if not video.download(url, filename):
                log.error("Bluesky - Could not download from url: " + url)
                return None

        log.info("Bluesky - uploading video: " + filename)

        try:
            video.normalize_video(filename)
            data = video.read(filename)

            if data is None:
                log.error("Bluesky - Failed to read video file: " + filename)
                return None

            response = self._perform_blob_upload(data)

            if response is None:
                log.error("Bluesky - All upload attempts failed: " + filename)
                return None

            if not response.ok:
                log.error("Bluesky - Failed to upload blob: " + filename)
                return None

            blob = response.json()["blob"]
            log.info("Bluesky - Blob uploaded: " + str(blob))

            log.info("Bluesky - Waiting for blob upload to complete...")
            time.sleep(30)

            return blob
        finally:
            if downloaded_here and os.path.exists(filename):
                video.remove(filename)


    def post_with_media(self, text : str, media : str) -> Optional[Dict[str, str]]:
        """
        Send a post with the specified text.
        """

        log.info("Bluesky - Post with media: " + utils.strip_text(text))

        self._ensure_initialized()
        if self.session is None:
            return None

        if len(text) > MAX_LENGTH:
            log.error("Bluesky - post is longer than the maximum length")
            return None

        blob = self.upload_video(media)
        if blob is None:
            log.error("Bluesky - the video upload failed.")
            return None

        post : dict[Any, Any] = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now(),
            "facets": parse_tags(text),
            "embed": {
                "$type": "app.bsky.embed.video",
                "video": blob,
                "alt": text,
                "aspectRatio": { "height": 9, "width": 16 }
            }
        }

        return self.request(post)


    def reply_with_media(self,
                         parent : Optional[Dict[str, str]],
                         text : str, media : str) -> Optional[Dict[str, str]]:
        """
        Send a reply to the given parent post with the specified text.
        """

        log.info("Bluesky - Reply with media: " + utils.strip_text(text))

        self._ensure_initialized()
        if self.session is None:
            return None

        if parent is None:
            log.error("Bluesky - parent post is missing")
            return None

        if len(text) > MAX_LENGTH:
            log.error("Bluesky - post is longer than the maximum length")
            return None

        if "cid" not in parent or "uri" not in parent:
            log.error("Bluesky - parent post is missing cid or uri")
            return None

        blob = self.upload_video(media)
        if blob is None:
            log.error("Bluesky - the video upload failed.")
            return None

        post : dict[Any, Any] = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now(),
            "facets": parse_tags(text),
            "reply": {
                "root": {
                    "uri": parent["uri"],
                    "cid": parent["cid"]
                },
                "parent": {
                    "uri": parent["uri"],
                    "cid": parent["cid"]
                }
            },
            "embed": {
                "$type": "app.bsky.embed.video",
                "video": blob,
                "alt": text,
                "aspectRatio": { "height": 9, "width": 16 }
            }
        }

        return self.request(post)


    def _fetch_author_feed(self) -> Optional[dict]:
        """
        Retrieve author feed payload for the authenticated account.
        """
        if self.session is None:
            return None

        did = self.session.get("did")
        if did is None:
            log.error("Bluesky - Could not retrieve today's posts.")
            return None

        access_token = self._session_tokens.get("access", "")
        if access_token == "":
            log.error("Bluesky - Missing access token for author feed lookup.")
            return None

        try:
            response = requests.get(
                BASE_URL + "app.bsky.feed.getAuthorFeed",
                params={
                    "actor": did,
                    "includePins": "false",
                    "limit": 100,
                },
                headers={"Authorization": "Bearer " + access_token},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            log.error("Bluesky - Could not retrieve author feed: " + str(error))
            return None


    def _extract_reference_day_posts(self, feed_payload: dict) -> List[str]:
        """
        Extract normalized post text for the configured local reference-day window.
        """
        result: List[str] = []
        target_day = self.duplicate_reference_date.date()
        next_day = (self.duplicate_reference_date + timedelta(days=1)).date()

        for feed_item in feed_payload.get("feed", []):
            record = feed_item.get("post", {}).get("record", {})
            created_at = record.get("createdAt")
            text = record.get("text")
            if created_at is None or text is None:
                continue

            utc_time = parser.parse(created_at)
            post_date = schedule.utc_to_local(utc_time).date()
            if post_date in (target_day, next_day):
                result.append(self._normalize_post_text(text))

        return result


    def get_posts_for_reference_day(self) -> List[str]:
        """
        Return account posts from the configured duplicate reference day.
        """
        feed_payload = self._fetch_author_feed()
        if feed_payload is None:
            return []

        return self._extract_reference_day_posts(feed_payload)
