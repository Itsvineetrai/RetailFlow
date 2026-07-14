"""
RetailFlow Gold Customer Metrics
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    sum,
    count,
    avg,
)


class CustomerMetrics:

    @staticmethod
    def customer_segments(df: DataFrame) -> DataFrame:

        return (

            df.groupBy("customer_segment")

            .agg(

                count("*").alias("transactions"),

                sum("total_amount_cents").alias("revenue"),

                avg("total_amount_cents").alias("average_order_value"),

            )

        )

    @staticmethod
    def loyalty_analysis(df: DataFrame) -> DataFrame:

        return (

            df.groupBy("loyalty_member")

            .agg(

                count("*").alias("transactions"),

                sum("total_amount_cents").alias("revenue"),

                avg("total_amount_cents").alias("average_order_value"),

            )

        )