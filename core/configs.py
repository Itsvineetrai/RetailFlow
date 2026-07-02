"""
Configuration Manager for AeroMart Data Platform.

Loads application configuration from YAML
and exposes it as a singleton object.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = (
    PROJECT_ROOT
    / "configs"
    / "application"
    / "app_config.yaml"
)

class Config:
    """
    Wrapper around the application YAML configuration.
    """

    def __init__(self) -> None:

        with CONFIG_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            self._config = yaml.safe_load(file)

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Read nested configuration values.

        Example:

        config.get(
            "kafka",
            "bootstrap_servers"
        )
        """
        value = self._config
        for key in keys:

            if not isinstance(value, dict):
                return default

            value = value.get(key)
            
            if value is None:
                return default

        return value


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Returns singleton configuration.
    """

    return Config()