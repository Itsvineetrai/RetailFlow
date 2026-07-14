"""
RetailFlow Silver Pipeline

Reads Bronze Parquet files,
validates them,
writes

1. Silver
2. Quarantine

This is intentionally implemented as a
scheduled micro-batch job.

Later this job will be orchestrated by Airflow.
"""

from __future__ import annotations

from core.logger import get_logger
from core.spark_session import SparkSessionManager
from core.constants import (
    BRONZE_TRANSACTIONS_PATH,
    SILVER_TRANSACTIONS_PATH,
    QUARANTINE_TRANSACTIONS_PATH
)

from pipelines.silver.validator import SilverValidator

logger = get_logger(__name__)


class SilverPipeline:

    def __init__(self):

        self.spark = SparkSessionManager.get_session(
            app_name="RetailFlow-Silver"
        )

        self.validator = SilverValidator()

    def run(self):

        logger.info("Starting Silver Pipeline...")

        # -------------------------------------------------
        # Read Bronze
        # -------------------------------------------------

        bronze_df = (

            self.spark.read

            .format("parquet")

            .load(
                BRONZE_TRANSACTIONS_PATH
            )

        )

        logger.success(
            f"Bronze Records : {bronze_df.count()}"
        )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        valid_df, quarantine_df = (

            self.validator.validate(
                bronze_df
            )

        )

        # -------------------------------------------------
        # Write Silver
        # -------------------------------------------------

        (

            valid_df.write

            .mode("append")

            .format("parquet")

            .save(
                SILVER_TRANSACTIONS_PATH
            )

        )

        logger.success(
            "Silver layer written."
        )

        # -------------------------------------------------
        # Write Quarantine
        # -------------------------------------------------

        (

            quarantine_df.write

            .mode("append")

            .format("parquet")

            .save(
                QUARANTINE_TRANSACTIONS_PATH
            )

        )

        logger.success(
            "Quarantine layer written."
        )

        logger.success(
            "Silver Pipeline Completed."
        )


def main():

    SilverPipeline().run()


if __name__ == "__main__":

    main()