"""
This module provides an interface to Twitter than can be used to
    authenticate, tweet and reply.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import os
from os.path import join, dirname, abspath
from dotenv import load_dotenv
import tweepy
import requests
import youtube_dl

from src import schedule
from src.logger import log
from src.output.outputter import Outputter

# maximum tweet length
MAX_LENGTH = 240 # characters

# The username of this bot's Twitter account
USERNAME = "nhl_goal_bot"


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

    def __init__(self):
        """
        Read authentication details from the .env file.
        """

        # load constants from .env
        parent_dir  : str = dirname(dirname(dirname(abspath(__file__))))
        config_dir  : str = join(parent_dir, "config")
        dotenv_file : str = join(config_dir, '.env')
        load_dotenv(dotenv_file)

        # read the authentication keys
        self.bearer_token        = os.getenv("BEARER_TOKEN")
        self.consumer_key        = os.getenv("CONSUMER_KEY")
        self.consumer_secret     = os.getenv("CONSUMER_SECRET")
        self.access_token        = os.getenv("ACCESS_TOKEN")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

        self.auth = tweepy.OAuth1UserHandler(self.consumer_key,
                                             self.consumer_secret,
                                             self.access_token,
                                             self.access_token_secret)


class Tweeter(Outputter):
    """
    This class provides an interface to Twitter than can be used to
        authenticate, tweet and reply.
    """
    user_id : int       = 0
    posts   : List[str] = []

    def __init__(self):
        self.config : Authentication = Authentication()
        self.api    : tweepy.API     = tweepy.API(self.config.auth)
        self.client : tweepy.Client  = tweepy.Client(self.config.bearer_token,
                                                     self.config.consumer_key,
                                                     self.config.consumer_secret,
                                                     self.config.access_token,
                                                     self.config.access_token_secret)

        # Get the account's user ID
        user = self.client.get_user(username=USERNAME)
        if is_data_valid(user):
            self.user_id : int = user.data.get("id", 0)

        # Get any posts made my the account so far today
        self.posts = self.get_today_posts()


    def post(self, text : str) -> Optional[int]:
        """
        Send a tweet with the specified text.
        """

        tweet_id : Optional[int] = None

        if len(text) <= MAX_LENGTH:

            log.info("Tweet:\n" + text)

            try:
                status   = self.client.create_tweet(text=text)
                tweet_id = int(status.data['id'])
                self.add_post(text)
            except tweepy.TweepyException as err:
                log.error("error - could not send tweet: " + str(err))
            except requests.exceptions.ConnectionError:
                log.error("error - connection error occurred while tweeting.")

        else:
            log.error("error - tweet is longer than the maximum length")

        return tweet_id


    def reply(self, parent : Optional[int], text : str) -> Optional[int]:
        """
        Send a reply to the given parent tweet with the specified text.
        """

        reply_id : Optional[int] = None

        if parent is not None and parent > 0:
            if len(text) <= MAX_LENGTH:

                log.info("Reply to tweet " + str(parent) + ":\n" + text)

                try:
                    status   = self.client.create_tweet(text=text, in_reply_to_tweet_id=parent)
                    reply_id = int(status.data['id'])
                    self.add_post(text)
                except tweepy.TweepyException as err:
                    log.error("error - could not send reply: " + str(err))
                except requests.exceptions.ConnectionError:
                    log.error("error - connection error occurred while replying.")

            else:
                log.error("error - tweet is longer than the maximum length")
        else:
            log.error("error - could not reply to tweet with invalid ID: " + str(parent))

        return reply_id


    def upload_video(self, url : str) -> Optional[str]:
        """
        Download the .mp4 from the given URL, perform a media upload, clean up and then
        return the media ID string.
        """
        filename : str = "highlight" + url[-8:-3] + ".mp4"
        with youtube_dl.YoutubeDL({"outtmpl": filename}) as ydl:
            ydl.download([url])

        log.info("Performing media upload of " + filename)
        media = self.api.media_upload(filename, media_category="tweet_video")

        log.info("Deleting " + filename)
        os.remove(filename)
        log.info("return media ID string: " + media.media_id_string)
        return media.media_id_string


    def post_with_media(self, text : str, media : str) -> Optional[int]:
        """
        Send a tweet with the specified text.
        """
        tweet_id : Optional[int] = None

        if len(text) <= MAX_LENGTH:

            log.info("Tweet:\n" + text)

            try:
                # For now we only support media uploads for video
                video_id = self.upload_video(media)
                if video_id is not None:
                    try:
                        status   = self.client.create_tweet(text=text, media_ids=[video_id])
                        tweet_id = int(status.data['id'])
                        self.add_post(text)
                    except tweepy.TweepyException as err:
                        log.error("error - could not send tweet: " + str(err))
                    except requests.exceptions.ConnectionError:
                        log.error("error - connection error occurred while tweeting.")
                else:
                    log.error("error - the video upload failed.")
            except tweepy.TweepyException as error:
                log.error("error - could not send tweet: " + str(error))

        else:
            log.error("error - tweet is longer than the maximum length")

        return tweet_id


    def reply_with_media(self, parent : Optional[int], text : str, media : str) -> Optional[int]:
        """
        Send a reply to the given parent tweet with the specified text.
        """
        reply_id : Optional[int] = None

        if parent is not None and parent > 0:
            if len(text) <= MAX_LENGTH:

                log.info("Reply to tweet " + str(parent) + ":\n" + text)

                try:
                    # For now we only support media uploads for video
                    video_id = self.upload_video(media)
                    if video_id is not None:
                        try:
                            status   = self.client.create_tweet(text=text,
                                                                in_reply_to_tweet_id=parent,
                                                                media_ids=[video_id])
                            reply_id = int(status.data['id'])
                            self.add_post(text)
                        except tweepy.TweepyException as err:
                            log.error("error - could not send reply: " + str(err))
                        except requests.exceptions.ConnectionError:
                            log.error("error - connection error occurred while tweeting.")
                    else:
                        log.error("error - the video upload failed.")

                except tweepy.TweepyException:
                    log.error("error - could not send reply")

            else:
                log.error("error - tweet is longer than the maximum length")
        else:
            log.error("error - could not reply to tweet with invalid ID: " + str(parent))

        return reply_id


    def add_post(self, text : str):
        """
        Add the given post to our list of posts.
        """
        self.posts.append(text)


    def clear_posts(self):
        """
        Clear the list of posts.
        """
        self.posts = []


    def get_today_posts(self) -> List[str]:
        """
        Return a list of tweets that were created today. If a query is
        provided, return only tweets that include the query as a substring.
        """
        today : datetime = schedule.get_current_date()
        posts = None
        try:
            posts = self.client.get_users_tweets(id = self.user_id,
                                                 max_results = 75,
                                                 start_time = today)
        except tweepy.TweepyException as err:
            log.error("error - could not user tweets: " + str(err))
        except requests.exceptions.ConnectionError:
            log.error("error - connection error occurred while retrieving tweets.")

        result = []
        if posts is not None and is_data_valid(posts):
            for post in posts.data:
                result.append(post.text)
        return result


    def has_posted_today(self, query : str = "") -> bool:
        """
        Return a boolean indicating whether or not a tweet has been sent today.
        """
        for post in self.posts:
            if query in post:
                return True
        return False
