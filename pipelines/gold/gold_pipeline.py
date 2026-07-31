"""
RetailFlow Gold Pipeline

Creates Gold analytical datasets
from the Silver layer.
"""

from core.logger import get_logger
from core.spark_session import SparkSessionManager

from core.constants import (
    SILVER_TRANSACTIONS_PATH,
    GOLD_PATH,
)

from pipelines.gold.sales import SalesMetrics
from pipelines.gold.products import ProductMetrics
from pipelines.gold.stores import StoreMetrics
from pipelines.gold.customers import CustomerMetrics
from pipelines.gold.finance import FinanceMetrics

logger = get_logger(__name__)


class GoldPipeline:

    def __init__(self):

        self.spark = SparkSessionManager.get_session(
            app_name="RetailFlow-Gold"
        )

    def run(self):

        logger.info("Starting Gold Delta Pipeline...")

        # ---------------------------------------------------------
        # Read Silver Delta
        # ---------------------------------------------------------

        df = (

            self.spark.read

            .format("delta")

            .load(
                SILVER_TRANSACTIONS_PATH
            )

            # .cache()

        )

        logger.success("Silver Delta Loaded.")

        datasets = {

            "daily_sales":
                SalesMetrics.daily_sales(df),

            "payment_summary":
                SalesMetrics.revenue_by_payment(df),

            "category_sales":
                ProductMetrics.category_sales(df),

            "top_products":
                ProductMetrics.top_products(df),

            "store_sales":
                StoreMetrics.revenue_by_store(df),

            "city_sales":
                StoreMetrics.revenue_by_city(df),

            "customer_segments":
                CustomerMetrics.customer_segments(df),

            "loyalty_analysis":
                CustomerMetrics.loyalty_analysis(df),

            "financial_summary":
                FinanceMetrics.financial_summary(df),

            "payment_finance":
                FinanceMetrics.payment_summary(df),

        }

        # ---------------------------------------------------------
        # Write Gold Delta Datasets
        # ---------------------------------------------------------

        for dataset_name, dataset_df in datasets.items():

            logger.info(f"Writing {dataset_name}...")

            (

                dataset_df.write

                .format("delta")

                .mode("overwrite")

                .save(
                    f"{GOLD_PATH}/{dataset_name}"
                )

            )

        logger.success(
            "Gold Delta Pipeline Completed Successfully."
        )

        df.unpersist()


def main():

    GoldPipeline().run()


if __name__ == "__main__":

    main()