"""
RetailFlow Silver Pipeline Runner

Runs the Silver validation pipeline.

Usage
-----
python scripts/run_silver.py
"""

from __future__ import annotations

from core.logger import get_logger
from pipelines.silver.silver_pipeline import SilverPipeline

logger = get_logger(__name__)


def main() -> None:

    logger.info("=" * 80)
    logger.info("Starting Silver Pipeline")
    logger.info("=" * 80)

    pipeline = SilverPipeline()

    pipeline.run()

    logger.success("Silver Pipeline Completed Successfully.")


if __name__ == "__main__":
    main()