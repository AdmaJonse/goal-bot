"""
Configuration for the health check endpoint and watchdog.
"""

import os
from dataclasses import dataclass

from src.logger import log


@dataclass(frozen=True)
class HealthConfig:
    """
    Configuration for the health check endpoint and watchdog.
    """
    timeout_seconds: float
    watchdog_enabled: bool
    watchdog_interval_seconds: float
    watchdog_failures: int
    watchdog_startup_delay_seconds: float


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        log.warning(f"Invalid {name} value {value!r}; using default {default}")
        return default


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        log.warning(f"Invalid {name} value {value!r}; using default {default}")
        return default


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    log.warning(f"Invalid {name} value {value!r}; using default {default}")
    return default


def load_health_config() -> HealthConfig:
    """
    Load health configuration from environment variables.
    """
    return HealthConfig(
        timeout_seconds=_get_float_env("HEALTH_TIMEOUT_SECONDS", 5.0),
        watchdog_enabled=_get_bool_env("HEALTH_WATCHDOG_ENABLED", False),
        watchdog_interval_seconds=_get_float_env("HEALTH_WATCHDOG_INTERVAL_SECONDS", 30.0),
        watchdog_failures=_get_int_env("HEALTH_WATCHDOG_FAILURES", 3),
        watchdog_startup_delay_seconds=_get_float_env("HEALTH_WATCHDOG_STARTUP_DELAY_SECONDS", 0.0),
    )
