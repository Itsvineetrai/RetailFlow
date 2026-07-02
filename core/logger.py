"""
Centralized logging utility for the AeroMart Data Platform.
All project modules should import get_logger() from this file.
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml


# Project Paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOGGING_CONFIG = (
    PROJECT_ROOT
    / "configs"
    / "logging"
    / "logging.yaml"
)


def configure_logging() -> None:
    """
    Configure logging from YAML configuration.

    Falls back to a basic console logger if the configuration
    file cannot be loaded.
    """

    try:
        with LOGGING_CONFIG.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        logging.config.dictConfig(config)

    except Exception:

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )


# Configure logging once when this module is imported
configure_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance.

    Example
    -------
    >>> logger = get_logger(__name__)
    >>> logger.info("Pipeline started")
    """

    return logging.getLogger(name)