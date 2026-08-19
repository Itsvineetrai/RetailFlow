"""
RetailFlow Silver Pipeline

Reads Bronze Delta, validates records, and merges valid transactions
into Silver Delta using transaction_id as the idempotency key.

Silver guarantees:
    1. Valid business records only
    2. One record per transaction_id
    3. Re-running the same Bronze data does not create duplicates
    4. New transactions are inserted
    5. Existing transactions are not duplicated
"""

from __future__ import annotations

from delta.tables import DeltaTable

from core.constants import (
    BRONZE_TRANSACTIONS_PATH,
    SILVER_TRANSACTIONS_PATH,
    QUARANTINE_TRANSACTIONS_PATH,
)
from core.logger import get_logger
from core.spark_session import SparkSessionManager
from pipelines.silver.validator import SilverValidator


logger = get_logger(__name__)


class SilverPipeline:

    def __init__(self):
        self.spark = SparkSessionManager.get_session(
            app_name="RetailFlow-Silver"
        )
        self.validator = SilverValidator()

    def run(self):

        logger.info("Loading Bronze Delta...")

        bronze_df = (
            self.spark.read
            .format("delta")
            .load(BRONZE_TRANSACTIONS_PATH)
        )

        logger.success("Bronze Delta loaded.")

        bronze_count = bronze_df.count()

        logger.info(
            f"Bronze records available: {bronze_count}"
        )

        if bronze_count == 0:
            logger.info("No Bronze records available.")
            return

        logger.info("Starting Silver validation...")

        valid_df, quarantine_df = self.validator.validate(
            bronze_df
        )

        logger.success("Silver validation completed.")

        valid_count = valid_df.count()

        logger.info(
            f"Validated records: {valid_count}"
        )

        if valid_count == 0:
            logger.warning(
                "No valid records available for Silver."
            )
        else:

            logger.info(
                "Merging validated records into Silver Delta..."
            )

            silver_table = DeltaTable.forPath(
                self.spark,
                SILVER_TRANSACTIONS_PATH,
            )

            (
                silver_table.alias("target")
                .merge(
                    valid_df.alias("source"),
                    "target.transaction_id = source.transaction_id",
                )
                .whenNotMatchedInsertAll()
                .execute()
            )

            logger.success(
                "Silver Delta merge completed."
            )

        quarantine_count = quarantine_df.count()

        logger.info(
            f"Quarantine records: {quarantine_count}"
        )

        if quarantine_count > 0:

            (
                quarantine_df.write
                .format("delta")
                .mode("append")
                .save(QUARANTINE_TRANSACTIONS_PATH)
            )

            logger.success(
                "Quarantine Delta written."
            )

        logger.success(
            "Silver Pipeline completed successfully."
        )


def main():
    SilverPipeline().run()


if __name__ == "__main__":
    main()