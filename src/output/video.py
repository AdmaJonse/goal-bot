"""
This module contains functions for downloading, trimming, and normalizing videos.
"""

import os
import time

from typing import Optional

import urllib
import pymediainfo
import youtube_dl

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from src.logger import log

MAXIMUM_DURATION=60 # seconds
MAXIMUM_SIZE=50000000 # bytes

def download_file(url : str, filename : str) -> bool:
    """
    Download the .mp4 from the given URL.
    """
    success : bool = False
    with youtube_dl.YoutubeDL({"outtmpl": filename, "quiet": True}) as ydl:
        try:
            ydl.download([url])
            success = True
        except urllib.error.HTTPError:
            log.error("HTTP error occurred while attempting download.")
        except youtube_dl.utils.ExtractorError:
            log.error("Extractor error occurred while attempting download.")
        except youtube_dl.utils.DownloadError:
            log.error("Download error occurred while attempting download.")
    return success

def download(url : str, filename : str) -> None:
    """
    Download the .mp4 from the given URL. Retry up to five times if the download fails.
    """
    is_downloaded : bool = False
    max_attempts  : int  = 5

    # Attempt to download until the download is successful. Give up if we exceed the maximum
    # number of attempts.
    log.verbose("Attempting download from url: " + url)
    for _ in range(max_attempts):
        is_downloaded = download_file(url, filename)
        if is_downloaded:
            break
        time.sleep(2)


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
    os.remove(file)
