"""
RetailFlow Supply Orders Bronze Runner.

Starts the Kafka → Spark → Bronze Delta
streaming pipeline for supply-chain orders.

Usage inside the Airflow container:

    python -m scripts.run_supply_orders_bronze
"""

from __future__ import annotations

from core.logger import get_logger
from pipelines.bronze.supply_orders_pipeline import (
    SupplyOrdersBronzePipeline,
)

logger = get_logger(__name__)


def main() -> None:
    """
    Start the Supply Chain Bronze streaming pipeline.
    """

    logger.info("=" * 70)
    logger.info("RetailFlow Supply Chain Bronze Pipeline")
    logger.info("=" * 70)

    try:
        pipeline = SupplyOrdersBronzePipeline()
        pipeline.start()

    except KeyboardInterrupt:
        logger.info(
            "Supply Chain Bronze pipeline stopped by user."
        )

    except Exception:
        logger.exception(
            "Supply Chain Bronze pipeline failed."
        )
        raise


if __name__ == "__main__":
    main()