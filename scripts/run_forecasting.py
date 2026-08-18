from __future__ import annotations

from core.logger import get_logger
from pipelines.gold.gold_pipeline import GoldPipeline


logger = get_logger(__name__)


def main() -> None:

    logger.info("Starting RetailFlow forecasting dataset...")

    pipeline = GoldPipeline()

    pipeline.run_forecasting()

    logger.success(
        "RetailFlow forecasting dataset completed."
    )


if __name__ == "__main__":
    main()