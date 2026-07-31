from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from delta.tables import DeltaTable

from core.logger import get_logger
from core.spark_session import SparkSessionManager
from core.constants import (
    BRONZE_TRANSACTIONS_PATH,
    SILVER_TRANSACTIONS_PATH,
    GOLD_PATH,
)

logger = get_logger(__name__)


class DeltaVerifier:

    def __init__(self):

        self.spark = SparkSessionManager.get_session(
            app_name="RetailFlow-Delta-Verification"
        )

    def verify_table(self, name: str, path: str):

        logger.info(f"Checking {name}...")

        if not DeltaTable.isDeltaTable(self.spark, path):

            raise RuntimeError(f"{name} is NOT a Delta table.")

        df = (

            self.spark.read

            .format("delta")

            .load(path)

        )

        logger.success(
            f"{name}: {df.count()} records"
        )

    def run(self):

        logger.info("=" * 60)
        logger.info("RetailFlow Delta Verification")
        logger.info("=" * 60)

        self.verify_table(
            "Bronze",
            BRONZE_TRANSACTIONS_PATH,
        )

        self.verify_table(
            "Silver",
            SILVER_TRANSACTIONS_PATH,
        )

        gold_tables = [

            "daily_sales",
            "payment_summary",
            "category_sales",
            "top_products",
            "store_sales",
            "city_sales",
            "customer_segments",
            "loyalty_analysis",
            "financial_summary",
            "payment_finance",

        ]

        for table in gold_tables:

            self.verify_table(

                table,

                f"{GOLD_PATH}/{table}",

            )

        logger.success(
            "All Delta tables verified successfully."
        )


def main():

    DeltaVerifier().run()


if __name__ == "__main__":

    main()