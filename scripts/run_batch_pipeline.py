from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


# =============================================================================
# RUNTIME DETECTION
# =============================================================================

def running_inside_docker() -> bool:
    """
    Detect whether this script is running inside a Docker container.
    """
    return Path("/.dockerenv").exists()


def configure_runtime() -> None:
    """
    Configure runtime-specific infrastructure endpoints.

    Docker:
        Spark  -> spark://spark-master:7077
        MinIO  -> minio:9000

    Windows host:
        Spark  -> local[*]
        MinIO  -> localhost:9000

    These values are intentionally set before importing the pipeline because
    core.config.Settings reads environment variables during initialization.
    """

    if running_inside_docker():

        os.environ["SPARK_MASTER"] = "spark://spark-master:7077"
        os.environ["MINIO_ENDPOINT"] = "minio:9000"

    else:

        os.environ["SPARK_MASTER"] = "local[*]"
        os.environ["MINIO_ENDPOINT"] = "localhost:9000"


# IMPORTANT:
# Configure the runtime BEFORE importing anything that loads core.config.
configure_runtime()


# =============================================================================
# PROJECT IMPORTS
# =============================================================================

from core.constants import POS_BATCH_INPUT_PATH
from core.logger import get_logger
from ingestion.pos_batch.pipeline import POSBatchPipeline


logger = get_logger(__name__)


# =============================================================================
# ARGUMENTS
# =============================================================================

def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Run RetailFlow POS batch ingestion."
    )

    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default=POS_BATCH_INPUT_PATH,
        help=(
            "Optional POS batch file path or S3A URI. "
            f"Default: {POS_BATCH_INPUT_PATH}"
        ),
    )

    return parser.parse_args()


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:

    args = parse_args()

    runtime = (
        "Docker"
        if running_inside_docker()
        else "Windows/Host"
    )

    logger.info(
        f"Runtime detected: {runtime}"
    )

    logger.info(
        f"Spark master: {os.environ['SPARK_MASTER']}"
    )

    logger.info(
        f"MinIO endpoint: {os.environ['MINIO_ENDPOINT']}"
    )

    logger.info(
        f"POS batch input: {args.file}"
    )

    try:

        pipeline = POSBatchPipeline()

        dataframe = pipeline.run(
            args.file
        )

        logger.info(
            f"Final batch schema: "
            f"{dataframe.schema.simpleString()}"
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
    

