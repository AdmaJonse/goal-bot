"""
This module provides an interface to Twitter than can be used to
    authenticate, tweet and reply.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import os
from os.path import join, dirname, abspath
from dotenv import load_dotenv
import tweepy
import pytz
import requests
import youtube_dl

from src.logger import log
from src.output.outputter import Outputter

# maximum tweet length
MAX_LENGTH = 240 # characters

class Tweeter(Outputter):
    """
    This class provides an interface to Twitter than can be used to
        authenticate, tweet and reply.
    """

    def read_config(self):
        """
        Read authentication details from the .env file.
        """

        # load constants from .env
        parent_dir  : str = dirname(dirname(dirname(abspath(__file__))))
        config_dir  : str = join(parent_dir, "config")
        dotenv_file : str = join(config_dir, '.env')
        load_dotenv(dotenv_file)

        # read the authentication keys
        self.bearer_token        : str = os.getenv("BEARER_TOKEN")
        self.consumer_key        : str = os.getenv("CONSUMER_KEY")
        self.consumer_secret     : str = os.getenv("CONSUMER_SECRET")
        self.access_token        : str = os.getenv("ACCESS_TOKEN")
        self.access_token_secret : str = os.getenv("ACCESS_TOKEN_SECRET")

    def __init__(self):
        self.read_config()
        self.client : tweepy.Client = tweepy.Client(self.bearer_token,
                                                    self.consumer_key,
                                                    self.consumer_secret,
                                                    self.access_token,
                                                    self.access_token_secret)

        auth : tweepy.OAuth1UserHandler = tweepy.OAuth1UserHandler(self.consumer_key,
                                                                   self.consumer_secret,
                                                                   self.access_token,
                                                                   self.access_token_secret)
        self.api : tweepy.API = tweepy.API(auth)


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
            except tweepy.TweepyException:
                log.error("error - could not send tweet")
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
                except tweepy.TweepyException:
                    log.error("error - could not send reply")
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
        filename : str = "highlight.mp4"
        with youtube_dl.YoutubeDL({"outtmpl": filename}) as ydl:
            ydl.download([url])

        log.info("Performing media upload of " + filename)
        media = self.api.media_upload(filename, media_category="tweet_video")
        print(str(media))

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
                    except tweepy.TweepyException:
                        log.error("error - could not send tweet")
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
                        except tweepy.TweepyException:
                            log.error("error - could not send tweet")
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


    def get_today_posts(self, query : str = "") -> List[tweepy.Tweet]:
        """
        Return a list of tweets that were created today. If a query is
        provided, return only tweets that include the query as a substring.
        """
        all_tweets   : List[tweepy.Tweet] = self.api.user_timeline(count=50, exclude_replies=True)
        today_tweets : List[tweepy.Tweet] = []
        period       : timedelta          = timedelta(hours=23, minutes=59)

        for tweet in all_tweets:
            if ((datetime.now(pytz.utc) - tweet.created_at) < period and
                query in tweet.text):
                today_tweets.append(tweet)

        return today_tweets


    def has_posted_today(self, query : str = "") -> bool:
        """
        Return a boolean indicating whether or not a tweet has been sent today.
        """
        tweets = self.get_today_posts(query)
        return len(tweets) > 0
