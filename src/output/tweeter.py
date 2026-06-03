"""
This module provides an interface to Twitter than can be used to
authenticate, tweet and reply.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import time
from os.path import join, dirname, abspath

import tweepy
import requests

from dotenv import load_dotenv

from src import schedule
from src.logger import log
from src.output import video
from src.output.outputter import Outputter

from src import utils

# maximum tweet length
MAX_LENGTH = 240 # characters

# The username of this bot's Twitter account
USERNAME = "nhl_goal_bot"
TWITTER_POST_ATTEMPTS = 3
TWITTER_POST_RETRY_DELAY_SECONDS = 2
TWITTER_REQUEST_TIMEOUT_SECONDS = 30
TWITTER_DUPLICATE_FETCH_PAGE_SIZE = 100
TWITTER_DUPLICATE_FETCH_MAX_PAGES = 10


def is_data_valid(response) -> bool:
    """
    Check the given Twitter API response to determine whether or not valid response data exists.
    """
    return response is not None and hasattr(response, "data") and response.data is not None


@dataclass
class Authentication:
    """
    This data class is used to store keys, tokens and secrets used in authentication with the
    Twitter API.
    """

    bearer_token        : str = ""
    consumer_key        : str = ""
    consumer_secret     : str = ""
    access_token        : str = ""
    access_token_secret : str = ""
    auth                : Optional[tweepy.OAuth1UserHandler] = None

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
        self.bearer_token        = os.getenv("BEARER_TOKEN", "")
        self.consumer_key        = os.getenv("CONSUMER_KEY", "")
        self.consumer_secret     = os.getenv("CONSUMER_SECRET", "")
        self.access_token        = os.getenv("ACCESS_TOKEN", "")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET", "")

        self.auth = tweepy.OAuth1UserHandler(self.consumer_key,
                                             self.consumer_secret,
                                             self.access_token,
                                             self.access_token_secret)


class Tweeter(Outputter):
    """
    This class provides an interface to Twitter than can be used to
    authenticate, tweet and reply.
    """
    user_id : int = 0

    def __init__(self) -> None:
        super().__init__()
        self.duplicate_reference_date: datetime = schedule.get_current_date()
        self.config : Authentication = Authentication()
        self.client : tweepy.Client  = tweepy.Client(self.config.bearer_token,
                                                     self.config.consumer_key,
                                                     self.config.consumer_secret,
                                                     self.config.access_token,
                                                     self.config.access_token_secret)
        self._configure_client_timeout()

        # Get the account's user ID
        try:
            user = self.client.get_user(username=USERNAME)
            if is_data_valid(user):
                self.user_id : int = user.data.get("id", 0)
        except tweepy.TweepyException as err:
            log.error("Twitter - could not retrieve user: " + str(err))

        # Load recent account posts to prevent duplicates across restarts/re-runs.
        try:
            self.posts = self.get_posts_for_reference_day()
        except tweepy.TweepyException as err:
            log.error("Twitter - could not retrieve today's posts: " + str(err))


    def name(self) -> str:
        """
        Return the name of this outputter.
        """
        return "twitter"


    def set_duplicate_reference_date(self, value: datetime) -> None:
        """
        Set the date used to query duplicate history, then refresh cache.
        """
        if value == self.duplicate_reference_date:
            return

        self.duplicate_reference_date = value
        try:
            self.posts = self.get_posts_for_reference_day()
        except tweepy.TweepyException as err:
            log.error("Twitter - could not refresh posts for duplicate checks: " + str(err))


    def _configure_client_timeout(self) -> None:
        """
        Apply a default timeout to Tweepy Client HTTP requests.
        Tweepy 4.16.0 doesn't support a timeout constructor argument.
        """
        original_request = self.client.session.request

        def request_with_timeout(*args, **kwargs):
            kwargs.setdefault("timeout", TWITTER_REQUEST_TIMEOUT_SECONDS)
            return original_request(*args, **kwargs)

        # Use object.__setattr__ to bypass type checker for dynamic method assignment
        object.__setattr__(self.client.session, "request", request_with_timeout)


    def _flush_connections(self) -> None:
        """
        Close stale TCP connections in the HTTP session so the next request
        opens a fresh connection.  This is needed after a long video upload,
        which can cause the persistent connection used by tweepy.Client to
        time out and be reset by Twitter before create_tweet is called.
        """
        self.client.session.close()


    def _create_tweet_with_retry(self,
                                 text: str,
                                 in_reply_to_tweet_id: Optional[str] = None,
                                 media_ids: Optional[List[str]] = None) -> Optional[Dict[str, str]]:
        """
        Create a tweet with limited retry for transient connection errors.
        """
        log.info("Twitter - Creating tweet.")
        for attempt in range(1, TWITTER_POST_ATTEMPTS + 1):
            try:
                log.verbose("Twitter - create_tweet attempt "
                            + str(attempt) + " of " + str(TWITTER_POST_ATTEMPTS))
                status = self.client.create_tweet(text=text,
                                                  in_reply_to_tweet_id=in_reply_to_tweet_id,
                                                  media_ids=media_ids)
                result = { "id": status.data['id'] }
                log.info("Twitter - Tweet posted successfully. id=" + result["id"])
                return result
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
                if attempt == TWITTER_POST_ATTEMPTS:
                    log.error("Twitter - network error occurred while tweeting: " + str(err))
                    return None

                log.warning("Twitter - network error while tweeting, retrying.")
                log.verbose("Twitter - will retry create_tweet attempt "
                            + str(attempt + 1) + " of " + str(TWITTER_POST_ATTEMPTS))
                time.sleep(TWITTER_POST_RETRY_DELAY_SECONDS)
            except tweepy.TweepyException as err:
                log.error("Twitter - could not send tweet: " + str(err))
                return None

        return None


    def post(self, text : str) -> Optional[Dict[str, str]]:
        """
        Send a tweet with the specified text.
        """

        result : Optional[Dict[str, str]] = None

        log.info("Twitter - Post: " + utils.strip_text(text))

        if len(text) > MAX_LENGTH:
            log.error("Twitter - tweet is longer than the maximum length")
            return None

        if self.has_posted(text):
            log.warning("Twitter - Skipping duplicate post: " + utils.strip_text(text))
            return None

        result = self._create_tweet_with_retry(text=text)
        if result is not None:
            self.add_post(text)

        return result


    def reply(self, parent : Optional[Dict[str, str]], text : str) -> Optional[Dict[str, str]]:
        """
        Send a reply to the given parent tweet with the specified text.
        """

        result : Optional[Dict[str, str]] = None

        log.info("Twitter - Reply: " + utils.strip_text(text))

        if parent is None:
            log.error("Twitter - parent post is missing")
            return None

        if parent.get("id") is None:
            log.error("Twitter - parent post is missing an ID")
            return None

        if len(text) > MAX_LENGTH:
            log.error("Twitter - tweet is longer than the maximum length")
            return None

        if self.has_posted(text):
            log.warning("Twitter - Skipping duplicate post: " + utils.strip_text(text))
            return None

        result = self._create_tweet_with_retry(text=text,
                                               in_reply_to_tweet_id=parent.get("id"))
        if result is not None:
            self.add_post(text)

        return result


    def upload_video(self, url : str) -> Optional[str]:
        """
        Download the .mp4 from the given URL, perform a media upload, clean up and then
        return the media ID string.
        """
        filename: str = url
        downloaded_here: bool = False

        if not os.path.exists(url):
            filename = "highlight" + url[-8:-3] + ".mp4"
            downloaded_here = True

            if not video.download(url, filename):
                log.error("Twitter - Could not download from url: " + url)
                return None

        try:
            log.info("Twitter - Uploading video: " + filename)
            if self.config.auth is None:
                log.error("Twitter - authentication not configured")
                return None
            api = tweepy.API(self.config.auth)
            media = api.media_upload(filename, media_category="tweet_video")
            log.info("Twitter - Video upload successful. media_id=" + media.media_id_string)
            return media.media_id_string
        finally:
            if downloaded_here and os.path.exists(filename):
                video.remove(filename)


    def post_with_media(self, text : str, media : str) -> Optional[Dict[str, str]]:
        """
        Send a tweet with the specified text.
        """
        result : Optional[Dict[str, str]] = None

        log.info("Twitter - Post with media: " + utils.strip_text(text))

        if len(text) > MAX_LENGTH:
            log.error("Twitter - tweet is longer than the maximum length")
            return None

        if self.has_posted(text):
            log.warning("Twitter - Skipping duplicate post: " + utils.strip_text(text))
            return None

        try:
            # For now we only support media uploads for video
            video_id = self.upload_video(media)
            if video_id is not None:
                self._flush_connections()
                result = self._create_tweet_with_retry(text=text, media_ids=[video_id])
                if result is not None:
                    self.add_post(text)
            else:
                log.error("Twitter - the video upload failed.")
        except tweepy.TweepyException as error:
            log.error("Twitter - could not send tweet: " + str(error))

        return result


    def reply_with_media(self,
                         parent : Optional[Dict[str, str]],
                         text : str,
                         media : str) -> Optional[Dict[str, str]]:
        """
        Send a reply to the given parent tweet with the specified text.
        """
        result : Optional[Dict[str, str]] = None

        log.info("Twitter - Reply with media: " + utils.strip_text(text))

        if parent is None:
            log.error("Twitter - parent post is missing")
            return None

        if parent.get("id") is None:
            log.error("Twitter - parent post is missing an ID")
            return None

        if len(text) > MAX_LENGTH:
            log.error("Twitter - tweet is longer than the maximum length")
            return None

        if self.has_posted(text):
            log.warning("Twitter - Skipping duplicate post: " + utils.strip_text(text))
            return None

        try:
            # For now we only support media uploads for video
            video_id = self.upload_video(media)
            if video_id is not None:
                self._flush_connections()
                result = self._create_tweet_with_retry(text=text,
                                                       in_reply_to_tweet_id=parent.get("id"),
                                                       media_ids=[video_id])
                if result is not None:
                    self.add_post(text)
            else:
                log.error("Twitter - the video upload failed.")

        except tweepy.TweepyException as err:
            log.error("Twitter - could not send reply: " + str(err))

        return result


    def get_posts_for_reference_day(self) -> List[str]:
        """
        Return account tweets from the configured duplicate reference day.
        """
        start_time = self.duplicate_reference_date
        # NHL games can cross midnight; include the following day for duplicate checks.
        end_time = start_time + timedelta(days=2)
        result = []
        pagination_token: Optional[str] = None

        for _ in range(TWITTER_DUPLICATE_FETCH_MAX_PAGES):
            try:
                posts = self.client.get_users_tweets(
                    id=self.user_id,
                    max_results=TWITTER_DUPLICATE_FETCH_PAGE_SIZE,
                    start_time=start_time,
                    end_time=end_time,
                    pagination_token=pagination_token,
                )
            except tweepy.TweepyException as err:
                log.error("Twitter - could not query recent tweets: " + str(err))
                break
            except requests.exceptions.ConnectionError:
                log.error("Twitter - connection error occurred while retrieving tweets.")
                break

            if posts is None:
                break

            if is_data_valid(posts):
                for post in posts.data:
                    normalized_text = self._normalize_post_text(post.text)
                    result.append(normalized_text)

            meta = getattr(posts, "meta", {}) or {}
            pagination_token = meta.get("next_token")
            if pagination_token is None:
                break

        return result
