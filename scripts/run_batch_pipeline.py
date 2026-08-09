from __future__ import annotations

import argparse
import sys
from core.logger import get_logger
from ingestion.pos_batch.pipeline import POSBatchPipeline

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run RetailFlow POS batch ingestion."
    )

    parser.add_argument(
        "file",
        type=str,
        help=(
            "Path to a POS CSV, JSON, or Parquet file."
        ),
    )

    return parser.parse_args()


def main() -> int:

    args = parse_args()

    try:

        pipeline = POSBatchPipeline()

        dataframe = pipeline.run(
            args.file
        )

        logger.info(
            f"Final batch schema: {dataframe.schema.simpleString()}"
        )

        logger.success(
            "Batch ingestion completed successfully."
        )

        return 0

    except Exception:

        logger.exception(
            "Batch ingestion failed."
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())