"""
RetailFlow Gold Product Metrics
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    sum,
    count,
)


class ProductMetrics:

    @staticmethod
    def category_sales(df: DataFrame) -> DataFrame:

        return (

            df.groupBy("category")

            .agg(

                sum("total_amount_cents").alias("revenue"),

                count("*").alias("orders"),

            )

        )

    @staticmethod
    def top_products(df: DataFrame) -> DataFrame:

        return (

            df.groupBy(

                "product_id",
                "product_name",

            )

            .agg(

                sum("quantity").alias("quantity_sold"),

                sum("total_amount_cents").alias("revenue"),

            )

            .orderBy("revenue", ascending=False)

        )