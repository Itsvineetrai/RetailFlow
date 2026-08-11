"""
RetailFlow Supply Chain API Ingestion Runner.

Usage:

    python -m scripts.run_supply_chain_api
"""

from __future__ import annotations

import sys

from core.logger import get_logger
from ingestion.supply_chain_api.pipeline import (
    SupplyChainAPIPipeline,
)

logger = get_logger(__name__)


def main() -> int:
    """
    Execute the Supply Chain API ingestion pipeline.
    """

    try:

        pipeline = SupplyChainAPIPipeline()

        published_count = pipeline.run()

        logger.success(
            "Supply Chain API ingestion finished. "
            f"Records published: {published_count}"
        )

        return 0

    except Exception:

        logger.exception(
            "Supply Chain API ingestion failed."
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())