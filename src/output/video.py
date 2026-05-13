"""
This module contains functions for downloading, trimming, and normalizing videos.
"""

import os
import time
import urllib
from typing import Optional

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import imageio_ffmpeg
import pymediainfo
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

from src.logger import log

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
os.environ.setdefault("IMAGEIO_FFMPEG_EXE", FFMPEG_PATH)

MAXIMUM_DURATION=100 # seconds
MAXIMUM_SIZE=100000000 # bytes

DOWNLOAD_RETRY_DELAY_SECONDS = 10
DELETE_RETRY_ATTEMPTS = 5
DELETE_RETRY_DELAY_SECONDS = 0.5


def download_file(url : str, filename : str) -> bool:
    """
    Download the .mp4 from the given URL.
    """
    options = {
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "retries": 3,
        "ffmpeg_location": FFMPEG_PATH,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            ydl.download([url])
            return True
        except urllib.error.HTTPError:
            log.error("HTTP error occurred while attempting download.")
        except ExtractorError:
            log.error("Extractor error occurred while attempting download.")
        except DownloadError:
            log.error("Download error occurred while attempting download.")
    return False

def download(url : str, filename : str) -> bool:
    """
    Download the .mp4 from the given URL. Retry up to five times if the download fails.
    Returns true when a file was downloaded successfully.
    """
    is_downloaded : bool = False
    max_attempts  : int  = 5

    # Attempt to download until the download is successful. Give up if we exceed the maximum
    # number of attempts.
    log.info("Attempting download from url: " + url)
    for _ in range(max_attempts):
        is_downloaded = download_file(url, filename)
        if is_downloaded:
            break
        time.sleep(DOWNLOAD_RETRY_DELAY_SECONDS)

    return is_downloaded


def trim(file : str, start : float, end : float) -> str:
    """
    Trim the video from the start time to the end time.
    """
    output_file : str = file.replace(".mp4", "_trimmed.mp4")
    ffmpeg_extract_subclip(file, start, end, output_file)
    return output_file


def get_duration(file : str) -> float:
    """
    Return the duration of the video in seconds.
    """
    media_info = pymediainfo.MediaInfo.parse(file)
    for track in media_info.tracks:
        if track.track_type == "Video":
            if track.duration is None:
                continue
            return float(track.duration) / 1000
    return 0


def get_size(file : str) -> int:
    """
    Return the size of the video in bytes.
    """
    return os.path.getsize(file)


def normalize_video(file : str):
    """
    Normalize the video by trimming it if it exceeds the maximum duration or size.
    """

    duration = get_duration(file)
    if duration > MAXIMUM_DURATION:
        log.error("Video exceeds maximum duration: " + str(duration))
        trimmed = trim(file, duration - MAXIMUM_DURATION, duration)
        os.remove(file)
        os.rename(trimmed, file)

    size = get_size(file)
    if size > MAXIMUM_SIZE:
        log.error("Video exceeds maximum size: " + str(size))
        # For now we just log an error, but we could compress this video in the future if needed.


def read(file : str) -> Optional[bytes]:
    """
    Read the contents of the file.
    """
    data = None
    if not os.path.exists(file):
        log.error("File does not exist: " + file)
        return None

    with open(file, 'rb') as f:
        data = f.read()

    return data


def remove(file : str) -> None:
    """
    Remove the file.
    """
    for attempt in range(1, DELETE_RETRY_ATTEMPTS + 1):
        try:
            os.remove(file)
            return
        except FileNotFoundError:
            # Another code path may have already removed the temp media.
            log.warning("File already removed: " + file)
            return
        except PermissionError as err:
            if attempt < DELETE_RETRY_ATTEMPTS:
                time.sleep(DELETE_RETRY_DELAY_SECONDS)
                continue
            # Cleanup failures should not terminate the posting thread.
            log.error("Failed to remove file: " + file + " - " + str(err))
            return
        except OSError as err:
            # Cleanup failures should not terminate the posting thread.
            log.error("Failed to remove file: " + file + " - " + str(err))
            return
