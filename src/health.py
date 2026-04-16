"""
Health check endpoint and watchdog behavior.
"""

import os
import threading
import time

from src import bot
from src import logger
from src.config import HealthConfig, load_health_config

HEALTH_CONFIG: HealthConfig = load_health_config()


def health() -> tuple[str, int]:
    """
    Health check endpoint.
    """
    if not bot.check_health(HEALTH_CONFIG.timeout_seconds):
        logger.log.error(
            "Health check command was not processed within "
            f"{HEALTH_CONFIG.timeout_seconds:.2f} seconds"
        )
        return "Health check failed", 503
    return "Healthy", 200


def register_health_route(app) -> None:
    """
    Register the health check endpoint on the given Flask app.
    """
    app.add_url_rule("/health", endpoint="health", view_func=health)


def health_watchdog() -> None:
    """
    Exit the process if queue-backed health checks fail repeatedly.
    """

    if HEALTH_CONFIG.watchdog_startup_delay_seconds > 0:
        time.sleep(HEALTH_CONFIG.watchdog_startup_delay_seconds)

    consecutive_failures = 0
    while True:
        healthy = bot.check_health(HEALTH_CONFIG.timeout_seconds)
        if healthy:
            if consecutive_failures > 0:
                logger.log.info("Health watchdog recovered after transient failures")
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            logger.log.error(
                "Health watchdog failure "
                f"{consecutive_failures}/{HEALTH_CONFIG.watchdog_failures}"
            )
            if consecutive_failures >= HEALTH_CONFIG.watchdog_failures:
                logger.log.error("Health watchdog forcing process exit for container restart")
                os._exit(1)

        time.sleep(HEALTH_CONFIG.watchdog_interval_seconds)


def start_health_watchdog() -> None:
    """
    Start the watchdog thread when enabled by configuration.
    """
    if HEALTH_CONFIG.watchdog_enabled:
        watchdog_thread = threading.Thread(target=health_watchdog, daemon=True)
        watchdog_thread.start()
