"""
RetailFlow Logger

Centralized logging configuration for the entire project.

All modules should import the logger using:

    from core.logger import get_logger

Example:
    logger = get_logger(__name__)
    logger.info("Application started")
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

# -----------------------------------------------------------------------------
# Log Directory
# -----------------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "retailflow.log"

# -----------------------------------------------------------------------------
# Default Configuration
# -----------------------------------------------------------------------------

logger.remove()

# Console Logger
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=False,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
)

# File Logger
logger.add(
    LOG_FILE,
    level="DEBUG",
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=False,
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level:<8} | "
        "{process.name}:{thread.name} | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)


def get_logger(name: str):
    """
    Returns a logger bound to the module name.

    Args:
        name: Usually __name__

    Returns:
        loguru.Logger
    """
    return logger.bind(module=name)