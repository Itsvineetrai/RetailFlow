"""
RetailFlow Bronze Pipeline Runner

Starts the Bronze streaming pipeline.

Usage
-----
python scripts/run_bronze.py
"""

from __future__ import annotations

from core.logger import get_logger
from pipelines.bronze.bronze_pipeline import BronzePipeline

logger = get_logger(__name__)


def main() -> None:

    logger.info("=" * 80)
    logger.info("Starting Bronze Pipeline")
    logger.info("=" * 80)

    pipeline = BronzePipeline()

    pipeline.start()


if __name__ == "__main__":
    main()