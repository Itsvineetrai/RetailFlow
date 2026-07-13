"""
RetailFlow Utility Functions

Shared utility functions used across the RetailFlow platform.

Rules:
- Keep utilities generic.
- Do not add Spark, Kafka, or MinIO specific logic.
- Do not add business logic here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def generate_uuid() -> str:
    """
    Generate a UUID4 string.

    Returns
    -------
    str
        Random UUID.
    """

    return str(uuid4())


def utc_now() -> datetime:
    """
    Returns the current UTC datetime.

    Returns
    -------
    datetime
    """

    return datetime.now(timezone.utc)


def utc_timestamp() -> str:
    """
    Returns an ISO-8601 UTC timestamp.

    Example
    -------
    2026-07-11T09:15:42.123456+00:00
    """

    return utc_now().isoformat()


def ensure_directory(directory: str | Path) -> Path:
    """
    Create directory if it does not exist.

    Parameters
    ----------
    directory : str | Path

    Returns
    -------
    Path
    """

    path = Path(directory)

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def file_exists(file_path: str | Path) -> bool:
    """
    Check whether a file exists.

    Parameters
    ----------
    file_path : str | Path

    Returns
    -------
    bool
    """

    return Path(file_path).is_file()


def directory_exists(directory: str | Path) -> bool:
    """
    Check whether a directory exists.

    Parameters
    ----------
    directory : str | Path

    Returns
    -------
    bool
    """

    return Path(directory).is_dir()


def bytes_to_mb(size: int) -> float:
    """
    Convert bytes to MB.

    Parameters
    ----------
    size : int

    Returns
    -------
    float
    """

    return round(size / (1024 * 1024), 2)


def format_duration(seconds: float) -> str:
    """
    Format duration.

    Examples
    --------
    65 -> 1m 5s
    3665 -> 1h 1m 5s
    """

    seconds = int(seconds)

    hours, remainder = divmod(seconds, 3600)

    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes}m {secs}s"

    if minutes:
        return f"{minutes}m {secs}s"

    return f"{secs}s"