"""
RetailFlow Gold Sales Metrics
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    sum,
    count,
    avg,
    to_date,
)


class SalesMetrics:

    @staticmethod
    def daily_sales(df: DataFrame) -> DataFrame:

        return (
            df
            .groupBy(
                to_date(
                    "transaction_timestamp"
                ).alias("date")
            )
            .agg(
                sum(
                    "total_amount_cents"
                ).alias("revenue"),

                count("*").alias(
                    "transactions"
                ),

                avg(
                    "total_amount_cents"
                ).alias(
                    "average_order_value"
                ),
            )
        )

    @staticmethod
    def revenue_by_payment(
        df: DataFrame,
    ) -> DataFrame:

        return (
            df
            .groupBy(
                "payment_method"
            )
            .agg(
                sum(
                    "total_amount_cents"
                ).alias("revenue"),

                count("*").alias(
                    "transactions"
                ),
            )
        )