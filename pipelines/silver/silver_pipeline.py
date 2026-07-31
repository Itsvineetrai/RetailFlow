""" RetailFlow Silver Pipeline
Reads Bronze Parquet files, validates them, writes 
1. Silver 
2. Quarantine 
This is intentionally implemented as a scheduled micro-batch job. 
Later this job will be orchestrated by Airflow. 
"""

from __future__ import annotations
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
        self.spark = SparkSessionManager.get_session(app_name="RetailFlow-Silver")
        self.validator = SilverValidator()

    def run(self):
        logger.info("Loading Bronze Delta...")
        bronze_df = self.spark.read.format("delta").load(BRONZE_TRANSACTIONS_PATH)
        logger.info("Bronze loaded.")
        
        logger.info("Counting Bronze records...")
        count = bronze_df.count()
        logger.info(f"Bronze count = {count}")
        
        logger.info("Starting validation...")
        valid_df, quarantine_df = self.validator.validate(bronze_df)
        logger.info("Validation finished.")
        logger.success("Bronze Delta loaded.")
        
        # ---------------------------------------------------------
        # Write Silver Delta
        # ---------------------------------------------------------
        (
            valid_df.write
            .format("delta")
            .mode("append")
            .save(SILVER_TRANSACTIONS_PATH)
        )
        logger.success("Silver Delta written.")
        
        # ---------------------------------------------------------
        # Write Quarantine Delta
        # ---------------------------------------------------------
        (
            quarantine_df.write
            .format("delta")
            .mode("append")
            .save(QUARANTINE_TRANSACTIONS_PATH)
        )
        logger.success("Quarantine Delta written.")
        logger.success("Silver Pipeline Completed.")


def main():
    SilverPipeline().run()


if __name__ == "__main__":
    main()
