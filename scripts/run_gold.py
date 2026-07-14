"""
RetailFlow Gold Pipeline Runner

Runs the Gold analytics pipeline.

Usage
-----
python -m scripts.run_gold
"""

from __future__ import annotations

from core.logger import get_logger
from pipelines.gold.gold_pipeline import GoldPipeline

logger = get_logger(__name__)


def main() -> None:

    logger.info("=" * 80)
    logger.info("Starting Gold Pipeline")
    logger.info("=" * 80)

    pipeline = GoldPipeline()

    pipeline.run()

    logger.success("Gold Pipeline Completed Successfully.")


if __name__ == "__main__":
    main()