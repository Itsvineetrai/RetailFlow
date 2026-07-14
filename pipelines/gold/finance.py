"""
RetailFlow Gold Financial Metrics
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    sum,
    avg,
)


class FinanceMetrics:

    @staticmethod
    def financial_summary(df: DataFrame) -> DataFrame:

        return (

            df.agg(

                sum("total_amount_cents").alias("total_revenue"),

                sum("tax_cents").alias("total_tax"),

                sum("discount_cents").alias("total_discount"),

                avg("total_amount_cents").alias("average_transaction_value"),

            )

        )

    @staticmethod
    def payment_summary(df: DataFrame) -> DataFrame:

        return (

            df.groupBy("payment_method")

            .agg(

                sum("total_amount_cents").alias("revenue"),

                sum("tax_cents").alias("tax"),

                sum("discount_cents").alias("discount"),

            )

        )