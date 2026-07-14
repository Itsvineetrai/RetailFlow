"""
RetailFlow Gold Store Metrics
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    sum,
    count,
    avg,
)


class StoreMetrics:

    @staticmethod
    def revenue_by_store(df: DataFrame) -> DataFrame:

        return (

            df.groupBy(

                "store_id",
                "store_name",

            )

            .agg(

                sum("total_amount_cents").alias("revenue"),

                count("*").alias("transactions"),

                avg("total_amount_cents").alias("average_sale"),

            )

        )

    @staticmethod
    def revenue_by_city(df: DataFrame) -> DataFrame:

        return (

            df.groupBy("city")

            .agg(

                sum("total_amount_cents").alias("revenue"),

                count("*").alias("transactions"),

            )

        )