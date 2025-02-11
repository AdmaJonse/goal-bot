"""
This module provides an interface to Twitter than can be used to
authenticate, post and reply.
"""

import os
import re
import time

from dataclasses import dataclass
from datetime import datetime, timezone
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


def get_tag_indices(text : str) -> List[tuple[int,int]]:
    """
    Parse the tags from the given text.
    """
    indices : List[tuple[int,int]] = []
    for word in text.split():
        if word.startswith("#"):
            start = text.find(word)
            end   = start + len(word)
            indices.append((start, end))
    return indices


def parse_tags(text : str) -> List:
    """
    Parse the tags from the given text.
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
                    "tag": text[start+1:end]
                }
            ]})
    return facets


def strip_text(text : str) -> str:
    """
    Strip the text of any tags.
    """
    result  : str = ""
    pattern : str = r"^.*\: \d{1,2}$\n^.*\: \d{1,2}$"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        result = match.group(0).strip().replace('\n', ' ')
    return result

@dataclass
class Authentication:
    """
    This data class is used to store keys, tokens and secrets used in authentication with the
    Twitter API.
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
        self.auth         : Authentication = Authentication()
        self.session      : Optional[dict] = None
        self.client       : atproto.Client = atproto.Client()
        self.client.login(self.auth.handle, self.auth.password)
        self.user_id = ""
        self.access_token = ""
        self.create_session()

        # Get any posts made my the account so far today
        self.posts = self.get_today_posts()


    def name(self) -> str:
        """
        Return the name of this outputter.
        """
        return "bluesky"


    def create_session(self):
        """
        Create a new session with the Bluesky API.
        """
        response = requests.post(
            BASE_URL + "com.atproto.server.createSession",
            json={
                "identifier": self.auth.handle,
                "password": self.auth.password
                },
            timeout=REQUEST_TIMEOUT)
        self.session       = response.json()
        self.access_token  = self.session["accessJwt"]
        self.refresh_token = self.session["refreshJwt"]


    def request(self, post : dict) -> Optional[Dict[str, str]]:
        """
        Send a POST request to the Bluesky API with the given post data.
        """

        self.create_session()

        if self.session is None:
            log.error("Could not create session.")
            return None

        response = requests.post(
                    BASE_URL + "com.atproto.repo.createRecord",
                    headers={"Authorization": "Bearer " + self.access_token},
                    json={
                        "repo": self.session["did"],
                        "collection": "app.bsky.feed.post",
                        "record": post,
                    },
                    timeout=REQUEST_TIMEOUT)

        if response.ok:
            log.info("Post:\n" + post["text"])
            self.add_post(post["text"])
            return {
                "uri": response.json()["uri"],
                "cid": response.json()["cid"]
            }

        log.error("The request failed: " + response.text)
        return None


    def post(self, text : str) -> Optional[Dict[str, str]]:
        """
        Post with the specified text.
        """
        if len(text) > MAX_LENGTH:
            log.error("error - post is longer than the maximum length")
            return None

        if text in self.posts:
            log.error("Skipping duplicate post")
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

        if parent is None:
            log.error("error - parent post is missing")
            return None

        if len(text) > MAX_LENGTH:
            log.error("error - post is longer than the maximum length")
            return None

        if text in self.posts:
            log.error("Skipping duplicate post")
            return None

        if "cid" not in parent or "uri" not in parent:
            log.error("error - parent post is missing cid or uri")
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


    def upload_video(self, url : str) -> Optional[str]:
        """
        Download the .mp4 from the given URL, perform a media upload, clean up and then
        return the media ID string.
        """
        filename : str  = "highlight" + url[-8:-3] + ".mp4"
        data     : Optional[bytes] = None

        video.download(url, filename)

        if not os.path.exists(filename):
            log.error("Could not download from url: " + url)
            return None

        video.normalize_video(filename)
        data = video.read(filename)

        if data is None:
            log.error("Failed to read video file: " + filename)
            return None

        self.create_session()
        response = requests.post(
            BASE_URL + "com.atproto.repo.uploadBlob",
            headers={
                "Content-Type": "video/mp4",
                "Authorization": "Bearer " + self.access_token,
            },
            data=data,
            timeout=300)

        video.remove(filename)

        if not response.ok:
            log.error("Failed to upload blob: " + filename)
            return None

        blob = response.json()["blob"]
        log.info("Blob uploaded: " + str(blob))

        log.info("Waiting for blob upload to complete...")
        time.sleep(30)

        return blob


    def post_with_media(self, text : str, media : str) -> Optional[Dict[str, str]]:
        """
        Send a post with the specified text.
        """

        if len(text) > MAX_LENGTH:
            log.error("error - post is longer than the maximum length")
            return None

        if strip_text(text) in self.posts:
            log.error("Skipping duplicate post: " + strip_text(text))
            return None

        blob = self.upload_video(media)
        if blob is None:
            log.error("error - the video upload failed.")
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

        if parent is None:
            log.error("error - parent post is missing")
            return None

        if len(text) > MAX_LENGTH:
            log.error("error - post is longer than the maximum length")
            return None

        if strip_text(text) in self.posts:
            log.error("Skipping duplicate post: " + strip_text(text))
            return None

        if "cid" not in parent or "uri" not in parent:
            log.error("error - parent post is missing cid or uri")
            return None

        blob = self.upload_video(media)
        if blob is None:
            log.error("error - the video upload failed.")
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


    def add_post(self, text : str):
        """
        Add the given post to our list of posts.
        """
        self.posts.append(strip_text(text))


    def clear_posts(self):
        """
        Clear the list of posts.
        """
        self.posts = []


    def get_today_posts(self) -> List[str]:
        """
        Return a list of posts that were created today. If a query is
        provided, return only posts that include the query as a substring.
        """
        if self.session is None:
            return []

        did = self.session.get("did")
        if did is None:
            log.error("Could not retrieve today's posts.")
            return []

        feed = self.client.get_author_feed(actor=did, limit=100)
        result = []
        if feed is not None:
            for post in feed.feed:
                utc_time     = parser.parse(post.post.record.created_at)
                post_date    = schedule.utc_to_local(utc_time).date()
                current_date = schedule.get_current_date().date()
                if post_date == current_date:
                    result.append(strip_text(post.post.record.text))
        return result
