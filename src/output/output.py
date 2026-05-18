"""
This module defines the output method.
"""

import os
from datetime import datetime

from typing import Dict, List, Optional

from src import schedule
from src.output.outputter import Outputter
from src.output.printer import Printer
from src.output.bluesky import BlueSky
from src.output.tweeter import Tweeter
from src.output import video
from src.logger import log
from src import utils


class Output:
    """
    This class defines the output method to be used and any internal state of the
    output interface.
    """

    def __init__(self) -> None:
        self._dry_run: bool = False
        self._duplicate_reference_date: datetime = schedule.get_current_date()
        self._outputters: List[Outputter] = []
        self._configure_outputters()

    def _configure_outputters(self) -> None:
        """
        Configure outputters based on the current dry run mode.
        """
        self._outputters = []
        if self._dry_run:
            self._outputters.append(Printer())
            return

        self._outputters.append(BlueSky())
        self._outputters.append(Tweeter())

        for outputter in self._outputters:
            outputter.set_duplicate_reference_date(self._duplicate_reference_date)

    @property
    def dry_run(self) -> bool:
        """
        Return a boolean indicating whether or not we're in dry run mode.
        """
        return self._dry_run

    @dry_run.setter
    def dry_run(self, flag: bool):
        """
        Set the dry run flag.
        """
        if self._dry_run == flag:
            return

        self._dry_run = flag
        self._configure_outputters()

    @property
    def outputters(self) -> List[Outputter]:
        """
        Return the registered outputter instance.
        """
        return self._outputters

    def set_duplicate_reference_date(self, value: datetime) -> None:
        """
        Configure outputters to query duplicate history for this date.
        """
        self._duplicate_reference_date = value
        self._configure_outputters()


output = Output()


def post(text: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a post with the specified text.
    """
    post_ids: Dict[str, Optional[Dict[str, str]]] = {}
    for outputter in output.outputters:
        post_id : Optional[Dict[str, str]] = outputter.post(text)
        post_ids[outputter.name()] = post_id
    return post_ids


def reply(parents : Dict[str, Optional[Dict[str, str]]],
          text: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a post with the specified text as a reply to the given parent.
    """
    post_ids: Dict[str, Optional[Dict[str, str]]] = {}
    for outputter in output.outputters:
        parent : Optional[Dict[str, str]] = parents.get(outputter.name())
        if parent is not None:
            post_id: Optional[Dict[str, str]] = outputter.reply(parent, text)
            post_ids[outputter.name()] = post_id
    return post_ids


def post_with_media(
    text: str,
    media: str,
    duplicate_status: Optional[Dict[str, bool]] = None,
) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a post with the specified text and media.
    """
    post_ids : Dict[str, Optional[Dict[str, str]]] = {}
    outputters_to_send: List[Outputter] = []
    short_text = utils.strip_text(text)

    for outputter in output.outputters:
        outputter_name = outputter.name()
        has_posted = duplicate_status.get(outputter_name, False) if duplicate_status is not None else outputter.has_posted(text)

        if has_posted:
            log.warning(outputter.name().capitalize()
                        + " - Skipping duplicate post: " + short_text)
            post_ids[outputter_name] = None
            continue
        outputters_to_send.append(outputter)

    if len(outputters_to_send) == 0:
        log.info("All outputs reported duplicate content. Skipping media download/upload.")
        return post_ids

    downloaded_media = _download_media_once(media)

    if media and downloaded_media is None and not output.dry_run:
        for outputter in outputters_to_send:
            post_ids[outputter.name()] = None
        return post_ids

    try:
        media_source = downloaded_media if downloaded_media is not None else media
        for outputter in outputters_to_send:
            post_id : Optional[Dict[str, str]] = outputter.post_with_media(text, media_source)
            post_ids[outputter.name()] = post_id

    finally:
        if downloaded_media is not None and os.path.exists(downloaded_media):
            video.remove(downloaded_media)

    return post_ids


def reply_with_media(
    parents: Dict[str, Optional[Dict[str, str]]],
    text: str,
    media: str
) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Send a reply to the given parent tweet with the specified text.
    """
    post_ids: Dict[str, Optional[Dict[str, str]]] = {}
    outputters_to_send: List[Outputter] = []
    short_text = utils.strip_text(text)

    for outputter in output.outputters:
        parent: Optional[Dict[str, str]] = parents.get(outputter.name())
        if parent is None:
            continue

        if outputter.has_posted(text):
            log.warning(outputter.name().capitalize()
                        + " - Skipping duplicate post: " + short_text)
            post_ids[outputter.name()] = None
            continue

        outputters_to_send.append(outputter)

    if len(outputters_to_send) == 0:
        log.info("All outputs reported duplicate content. Skipping media download/upload.")
        return post_ids

    downloaded_media = _download_media_once(media)

    if media and downloaded_media is None and not output.dry_run:
        for outputter in outputters_to_send:
            post_ids[outputter.name()] = None
        return post_ids

    try:
        media_source = downloaded_media if downloaded_media is not None else media
        for outputter in outputters_to_send:
            reply_parent: Optional[Dict[str, str]] = parents.get(outputter.name())
            if reply_parent is not None:
                post_id : Optional[Dict[str, str]] = outputter.reply_with_media(
                    reply_parent,
                    text,
                    media_source,
                )
                post_ids[outputter.name()] = post_id

    finally:
        if downloaded_media is not None and os.path.exists(downloaded_media):
            video.remove(downloaded_media)

    return post_ids


def _download_media_once(media: str) -> Optional[str]:
    """
    Download the media once for all outputters and return a local filename.
    If the media is already a local file, reuse it directly.
    """
    if output.dry_run or media == "":
        return None

    if not _is_remote_media(media):
        if os.path.exists(media):
            return media
        log.error("Shared media file does not exist: " + media)
        return None

    if os.path.exists(media):
        return media

    filename = "highlight" + media[-8:-3] + ".mp4"
    log.info("Attempting shared download from url: " + media)

    if not video.download(media, filename):
        log.error("Shared media download failed. Skipping media post for all outputters.")
        return None

    return filename


def _is_remote_media(media: str) -> bool:
    """
    Return True when media is a URL that requires downloading.
    """
    return media.startswith("http://") or media.startswith("https://")


def has_posted_today(query: str = "") -> Dict[str, bool]:
    """
    Return a boolean indicating whether or not we've posted today.
    """
    has_posted: Dict[str, bool] = {}
    for outputter in output.outputters:
        has_posted[outputter.name()] = outputter.has_posted_today(query)
    return has_posted


def clear_posts() -> None:
    """
    Clear the list of today's posts.
    """
    for outputter in output.outputters:
        outputter.clear_posts()
